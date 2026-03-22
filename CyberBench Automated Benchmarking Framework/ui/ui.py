import os
import json
from typing import List
from flask import Flask, render_template, request, abort, send_file
from evaluator.llm_evaluator import LLMEvaluator
from evaluator.regex_evaluator import RegexEvaluator
from executor.api_executor import APIExecutor
from llms.DeepSeekClient import DeepSeekClient
from models.baseprompt import BasePrompt
from generator.manual_testcase_generator import ManualTestCaseGenerator
from generator.automatic_testcase_generator import AutomaticTestCaseGenerator
from generator.smart_testcase_generator import SmartTestCaseGenerator
from benchmarks.cyberbench.taxonomies import CYBERBENCH_TAXONOMY, PROMPT_INJECTION_STRATEGIES
from benchmarks.cyberbench.template_strategies import ALL_TEMPLATE_STRATEGIES
from models.testcase import TestCase

app = Flask(__name__)

# Base folder of this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Convert hierarchy to Treeselect format
def to_treeselect_options(hierarchy):
    def build(node):
        if isinstance(node, dict):
            return [
                {
                    "name": key,
                    "value": key,
                    "isGroupSelectable": True,
                    "children": build(value)
                }
                for key, value in node.items()
            ]
        elif isinstance(node, list):
            return [{"name": item, "value": item} for item in node]
        else:
            return [{"name": node, "value": node}]
    return build(hierarchy)


def make_file_path(filename: str):
    path = os.path.join(BASE_DIR, "output_files", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


@app.route("/", methods=["GET", "POST"])
def index():
    test_cases = []
    mode = request.form.get("mode", "automatic")
    file_path = None

    if request.method == "POST":
        file_path = make_file_path(f"testcases_{__import__('datetime').datetime.now():%Y%m%d_%H%M%S}.json")

        if mode == "manual":
            prompt_text = request.form.get("manual_prompt", "")
            prompt_goal = request.form.get("manual_goal", "")
            prompt_object = request.form.get("manual_object", "")
            sample_size = int(request.form.get("manual_sample_size", 1))
            raw = request.form.get("manual_strategies", "[]")
            try:
                strategies = json.loads(raw)
            except json.JSONDecodeError:
                strategies = []

            bp = BasePrompt(
                prompt=prompt_text,
                prompt_goal=prompt_goal,
                prompt_object=prompt_object,
                categories=[],
            )
            generator = ManualTestCaseGenerator()
            test_cases = generator.generate_to_json(
                file_path=file_path,
                base_prompt=bp,
                strategies=strategies,
                sample_size=sample_size,
            )

        elif mode == "automatic":
            raw = request.form.get("auto_category_json", "[]")
            try:
                categories = json.loads(raw)
            except json.JSONDecodeError:
                categories = ["Secrets Leakage"]

            raw = request.form.get("auto_strategies", "[]")
            try:
                strategies = json.loads(raw)
            except json.JSONDecodeError:
                strategies = []

            testcases_per_category = int(request.form.get("auto_count", 1))
            generator = AutomaticTestCaseGenerator()
            test_cases = generator.generate_to_json(
                file_path=file_path,
                categories=categories,
                template_strategies=strategies,
                testcases_per_category=testcases_per_category,
            )

        elif mode == "smart":
            context = request.form.get("smart_context", "")
            objective = request.form.get("smart_objective", "")
            sample_size = int(request.form.get("smart_sample_size", 1))
            generator = SmartTestCaseGenerator(llm=DeepSeekClient(api_key=os.getenv("DEEPSEEK_API_KEY", "SK-XXX")))
            test_cases = generator.generate_to_json(
                file_path=file_path,
                context=context,
                objective=objective,
                testcases_per_category=sample_size
            )

    return render_template(
        "generator.html",
        strategies=ALL_TEMPLATE_STRATEGIES,
        test_cases=test_cases,
        current_mode=mode,
        treeselect_options=to_treeselect_options(CYBERBENCH_TAXONOMY),
        strategy_options=to_treeselect_options(PROMPT_INJECTION_STRATEGIES),
        file_path=file_path
    )


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("dashboard.html")


@app.route("/generator", methods=["GET"])
def generator_route():
    return index()


@app.route("/executor", methods=["GET", "POST"])
def executor():
    mode = request.form.get("mode", "")
    test_cases: List[TestCase] = []
    file_path = None

    if request.method == "POST" and mode == "api":
        file_path = make_file_path(f"executed-testcases_{__import__('datetime').datetime.now():%Y%m%d_%H%M%S}.json")
        api_url = request.form.get("api_url", "")
        headers_json = json.loads(request.form.get("headers", "{}"))
        params_json = json.loads(request.form.get("model_params", "{}"))
        threads = int(request.form.get("threads", 1))

        uploaded_file = request.files.get("testcase_file")
        if uploaded_file:
            filename = uploaded_file.filename.lower()
            content = uploaded_file.read()
            try:
                if filename.endswith(".json"):
                    test_cases = TestCase.from_json(content)
                elif filename.endswith((".yml", ".yaml")):
                    test_cases = TestCase.from_yaml(content)
                else:
                    raise ValueError("Unsupported file type")
            except Exception as e:
                print("Error parsing uploaded test cases:", e)

            testcase_executor = APIExecutor(api_url=api_url, headers=headers_json)
            results = testcase_executor.execute_to_json(test_cases=test_cases, file_path=file_path, threads=threads, **params_json)

    return render_template(
        "executor.html",
        strategies=ALL_TEMPLATE_STRATEGIES,
        test_cases=test_cases,
        current_mode="api",
        file_path=file_path,
        treeselect_options=to_treeselect_options(CYBERBENCH_TAXONOMY),
        strategy_options=to_treeselect_options(PROMPT_INJECTION_STRATEGIES),
    )


@app.route("/evaluator", methods=["GET", "POST"])
def evaluator_route():
    mode = request.form.get("mode", "")
    test_cases: List[TestCase] = []
    file_path = None

    if request.method == "POST" and mode == "regex":
        file_path = make_file_path(f"evaluated-testcases_{__import__('datetime').datetime.now():%Y%m%d_%H%M%S}.json")
        regex = request.form.get("regex", "")
        threads = int(request.form.get("threads", 1))

        uploaded_file = request.files.get("testcase_file_regex")
        if uploaded_file:
            filename = uploaded_file.filename.lower()
            content = uploaded_file.read()
            try:
                if filename.endswith(".json"):
                    test_cases = TestCase.from_json(content)
                elif filename.endswith((".yml", ".yaml")):
                    test_cases = TestCase.from_yaml(content)
                else:
                    raise ValueError("Unsupported file type")
            except Exception as e:
                print("Error parsing uploaded test cases:", e)

            testcase_evaluator = RegexEvaluator()
            results = testcase_evaluator.evaluate_to_json(
                test_cases=test_cases, file_path=file_path, regex=fr"{regex}"
            )

    elif request.method == "POST" and mode == "llm":
        file_path = make_file_path(f"evaluated-testcases_{__import__('datetime').datetime.now():%Y%m%d_%H%M%S}.json")
        batch_size = request.form.get("batch_size", "")

        uploaded_file = request.files.get("testcase_file_llm")
        if uploaded_file:
            filename = uploaded_file.filename.lower()
            content = uploaded_file.read()
            try:
                if filename.endswith(".json"):
                    test_cases = TestCase.from_json(content)
                elif filename.endswith((".yml", ".yaml")):
                    test_cases = TestCase.from_yaml(content)
                else:
                    raise ValueError("Unsupported file type")
            except Exception as e:
                print("Error parsing uploaded test cases:", e)

            testcase_evaluator = LLMEvaluator(DeepSeekClient(api_key=os.getenv("DEEPSEEK_API_KEY", "sk-XXX")))
            results = testcase_evaluator.evaluate_to_json(test_cases=test_cases, file_path=file_path, batch_size=batch_size)

    return render_template(
        "evaluator.html",
        strategies=ALL_TEMPLATE_STRATEGIES,
        test_cases=test_cases,
        current_mode=mode,
        file_path=file_path,
        treeselect_options=to_treeselect_options(CYBERBENCH_TAXONOMY),
        strategy_options=to_treeselect_options(PROMPT_INJECTION_STRATEGIES),
    )


@app.route("/download", methods=["GET"])
def download_file():
    filepath = request.args.get("filepath")
    if not filepath or not os.path.isfile(filepath):
        return abort(404, description="File not found")
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)