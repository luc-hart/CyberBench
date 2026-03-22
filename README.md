# CyberBench

**CyberBench** is a research artifact accompanying an MSc thesis on the automated benchmarking of **direct security risks in LLM-based systems**.  
It provides a **risk taxonomy**, a **static benchmark dataset**, and an **automated benchmarking framework**, grounded in and aligned with the OWASP Top 10 for LLMs.

This repository hosts the artifacts used to systematically generate, execute, and evaluate adversarial prompts targeting real-world LLM-based systems.

---

## Repository Structure

```
.
├── CyberBench Taxonomy/
│   └── cyberbench_taxonomy.pdf
│
├── CyberBench Dataset/
│   ├── cyberbench_dataset.json
│   ├── cyberbench_dataset-prompt_objectives.json
│   └── cyberbench_dataset-prompt_injection_templates.json
│
└── CyberBench Automated Benchmarking Framework/
    └── (framework source code)
```

---

## CyberBench Taxonomy

The **CyberBench Taxonomy** is a multi-level taxonomy that categorizes **direct security risks** affecting LLM-based systems, such as system prompt leakage, sensitive information disclosure, excessive agency, and resource abuse.

The taxonomy:
- focuses exclusively on **direct system-level risks** rather than indirect misuse,
- is designed to be **fine-grained, extensible, and practically actionable**,
- is fully **mappable to the OWASP Top 10 for LLMs**,
- serves as the conceptual foundation for both the dataset and the automated framework.

The taxonomy is provided as a standalone PDF:

- **`CyberBench Taxonomy/cyberbench_taxonomy.pdf`**

---

## CyberBench Dataset

The **CyberBench Dataset** is a large-scale static benchmark consisting of **10,000 adversarial prompts** grounded in the CyberBench Taxonomy and designed to elicit **direct security risks** in LLM-based systems (e.g., system prompt leakage, sensitive data disclosure, database abuse).

To promote **reusability, extensibility, and transparency**, the dataset is released in a **decomposed form**:

### Dataset Files

- **`cyberbench_dataset.json`**  
  The full dataset of 10,000 adversarial prompts, each constructed by combining a prompt objective with a prompt injection strategy.

- **`cyberbench_dataset-prompt_objectives.json`**  
  A curated collection of *prompt objectives* representing the attacker’s intent (e.g., *reveal the system prompt*, *extract database records*), independent of any injection technique.

- **`cyberbench_dataset-prompt_injection_templates.json`**  
  A set of reusable *prompt injection templates* capturing common attack strategies (e.g., instruction overriding, role confusion, context smuggling).

This separation allows future work to:
- extend the dataset with new objectives or attack strategies,
- recombine components without rewriting full prompts,
- analyze objectives and injection techniques independently.

---

## CyberBench Automated Benchmarking Framework

The **CyberBench Automated Benchmarking Framework** provides an end-to-end pipeline for:

1. **Generating** benchmark test cases (static or dynamically adapted),
2. **Executing** them against arbitrary LLM-based systems,
3. **Evaluating** model responses using automated (LLM-based) and rule-based evaluators.

The framework is designed to:
- convert static datasets into **dynamic, context-aware benchmarks**,
- support multiple benchmarking modes (manual, automatic, smart),
- scale across models, prompts, and system configurations,
- be usable by both programmers and non-programmers via a user interface.

All experiments reported in the accompanying thesis were conducted using this framework.

---

### Docker Setup

1. **Clone the repository**

```bash
git clone https://github.com/luc-hart/CyberBench.git
cd "CyberBench Automated Benchmarking Framework"
```

2. **Populate environment variables**  

Edit the existing `.env` file in the project root and add your API keys (either OPENAI or DEEPSEEK. DEEPSEEK is used by default.) if you want to use the smart generator or LLM evaluator:

```env
DEESEEK_API_KEY=<your_deepseek_api_key>
OPENAI_API_KEY=<your_openai_api_key>
```

3. **Start the framework and database**

```bash
docker compose up --build
```

This will:

- Set up a PostgreSQL database and populate it with the CyberBench dataset  
- Build the framework source code into a container  
- Run the Flask web UI to orchestrate the framework

4. **Access the web UI**

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## Artifact Availability

The CyberBench Taxonomy, Dataset, and Automated Benchmarking Framework will be made publicly available upon acceptance of the associated thesis.  
The repository is currently undergoing final stabilization and documentation to ensure usability and reproducibility prior to public release.

---

## Citation

If you use CyberBench in academic work, please cite the corresponding thesis:

```
@mastersthesis{hartmans2026cyberbench,
  title  = {CyberBench: A Taxonomy, Dataset and Framework for Automated Benchmarking of Direct Security Risks in LLM-based Systems},
  author = {Lucas Hartmans},
  year   = {2026},
  school = {University of Twente}
}
```

---

## License

License information will be added upon public release.
