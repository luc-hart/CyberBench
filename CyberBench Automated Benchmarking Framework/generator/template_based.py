import base64
from jinja2 import Template, Environment, meta
from typing import List, Union, Optional, Any
#from googletrans import Translator
from deep_translator import GoogleTranslator
import morse_talk as mt
import codecs
import random
from benchmarks.cyberbench.cyberbench_dataset_connector import CyberBenchDataSetConnector
import re
from models.baseprompt import BasePrompt   # adjust import path


class PromptTemplater:
    def __init__(self):
        self.db = CyberBenchDataSetConnector()
        #self.translator = Translator()

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def translate_prompt(self, prompt: str, language: str) -> str:
        lang_map = {
            "Spanish": "es", "French": "fr", "Italian": "it", "German": "de",
            "Japanese": "ja", "Korean": "ko", "Hindi": "hi", "Portuguese": "pt",
            "Russian": "ru", "Arabic": "ar", "Indonesian": "id"
        }

        leetspeak_map = str.maketrans({
            'a': '4', 'A': '4',
            'e': '3', 'E': '3',
            'i': '1', 'I': '1',
            'o': '0', 'O': '0',
            's': '5', 'S': '5',
            't': '7', 'T': '7'
        })

        homoglyph_map = str.maketrans({
            'a': '\u0430', 'A': '\u0410',
            'e': '\u0435', 'E': '\u0415',
            'o': '\u043E', 'O': '\u041E',
            'p': '\u0440', 'P': '\u0420',
            'x': '\u0445', 'X': '\u0425',
            'c': '\u0441', 'C': '\u0421',
            'y': '\u0443', 'Y': '\u0423',
            'h': '\u043D', 'H': '\u041D',
            'k': '\u043A', 'K': '\u041A',
            'm': '\u043C', 'M': '\u041C',
            't': '\u0442', 'T': '\u0422',
            'b': '\u044C', 'B': '\u0412',
            'n': '\u0438', 'N': '\u0418',
            'v': '\u03BD', 'V': '\u039D',
            'i': '\u03B9', 'I': '\u0399',
            'l': '\u03B9', 'L': '\u0399',
            'u': '\u03C5', 'U': '\u03A5',
            'w': '\u03C9', 'W': '\u03A9',
            'f': '\u03C6', 'F': '\u03A6',
            'g': '\u0261',
            'd': '\u0501', 'D': '\u0500',
        })

        try:
            if language in lang_map:
                try:
                    if language in lang_map:
                        return GoogleTranslator(source='auto', target=lang_map[language]).translate(prompt)
                except:
                    return "failed"
                #return self.translator.translate(prompt, dest=lang_map[language]).text
            elif language == "Morse":
                return mt.encode(prompt)
            elif language == "Pig Latin":
                return ' '.join([word[1:] + word[0] + 'ay' for word in prompt.split()])
            elif language == "ROT13":
                return codecs.encode(prompt, 'rot_13')
            elif language == "Hexadecimal":
                return prompt.encode('utf-8').hex()
            elif language == "Binary":
                return ' '.join(format(ord(char), '08b') for char in prompt)
            elif language == "Caesar Cipher":
                return ''.join(
                    chr(((ord(char) - 97 + 3) % 26) + 97) if char.islower()
                    else chr(((ord(char) - 65 + 3) % 26) + 65) if char.isupper()
                    else char for char in prompt
                )
            elif language == "Leetspeak":
                return prompt.translate(leetspeak_map)
            elif language == "Base64":
                return base64.b64encode(prompt.encode('utf-8')).decode('utf-8')
            elif language == "Homoglyph":
                return prompt.translate(homoglyph_map)

        except Exception as e:
            print(f"Translation/encoding failed ({language}): {e}")

        return prompt

    def apply_single_strategy(self, input_prompt: BasePrompt, strategy: str, sample_size: Optional[int] = None) -> List[str]:
        templates = self.db.get_templates_by_strategy(strategy)
        if not templates:
            raise ValueError(f"No templates found for strategy '{strategy}'")

        if sample_size:
            templates = random.sample(templates, min(sample_size, len(templates)))

        outputs = []
        env = Environment()

        for tpl in templates:
            translated_prompt = self.translate_prompt(input_prompt.prompt, tpl['language'])
            translated_goal = self.translate_prompt(input_prompt.prompt_goal, tpl['language'])
            translated_object = self.translate_prompt(input_prompt.prompt_object, tpl['language'])

            template_obj = env.from_string(tpl['template'])
            parsed_content = env.parse(tpl['template'])
            template_vars = meta.find_undeclared_variables(parsed_content)

            if strategy == 'payload_splitting':
                part_vars = sorted([v for v in template_vars if re.match(r'prompt_part_\d+', v)],
                                   key=lambda x: int(x.split('_')[-1]))
                num_parts = len(part_vars)

                prompt_words = translated_prompt.split()
                split_prompts = []
                base, extra = divmod(len(prompt_words), num_parts)
                start = 0
                for i in range(num_parts):
                    end = start + base + (1 if i < extra else 0)
                    split_prompts.append(' '.join(prompt_words[start:end]))
                    start = end

                render_kwargs = {part_vars[i]: split_prompts[i] for i in range(num_parts)}
                if 'prompt_goal' in template_vars:
                    render_kwargs['prompt_goal'] = translated_goal
                if 'prompt_object' in template_vars:
                    render_kwargs['prompt_object'] = translated_object

                output = template_obj.render(**render_kwargs)
            else:
                output = template_obj.render(
                    prompt=translated_prompt,
                    prompt_goal=translated_goal,
                    prompt_object=translated_object
                )

            outputs.append(output)

        return outputs

    def apply_chained_templates(self, input_prompt: BasePrompt, strategies: List[str], sample_size: int = 5) -> List[str]:
        templates_by_strategy = self.db.get_templates_by_strategies(strategies)
        final_outputs = []
        env = Environment()

        for _ in range(sample_size):
            output = input_prompt.prompt
            for strategy in strategies:
                if strategy not in templates_by_strategy:
                    raise ValueError(f"No templates found for strategy '{strategy}'")
                tpl = random.choice(templates_by_strategy[strategy])
                translated_prompt = self.translate_prompt(output, tpl['language'])

                translated_goal = self.translate_prompt(input_prompt.prompt_goal, tpl['language']) if input_prompt.prompt_goal else ''
                translated_object = self.translate_prompt(input_prompt.prompt_object, tpl['language']) if input_prompt.prompt_object else ''

                template_obj = env.from_string(tpl['template'])
                parsed_content = env.parse(tpl['template'])
                template_vars = meta.find_undeclared_variables(parsed_content)

                if strategy == 'payload_splitting':
                    part_vars = sorted([v for v in template_vars if re.match(r'prompt_part_\d+', v)],
                                       key=lambda x: int(x.split('_')[-1]))
                    num_parts = len(part_vars)

                    if num_parts == 0:
                        output = template_obj.render(
                            prompt=translated_prompt,
                            prompt_goal=translated_goal,
                            prompt_object=translated_object
                        )
                    else:
                        prompt_words = translated_prompt.split()
                        base, extra = divmod(len(prompt_words), num_parts)
                        split_prompts = []
                        start = 0
                        for i in range(num_parts):
                            end = start + base + (1 if i < extra else 0)
                            split_prompts.append(' '.join(prompt_words[start:end]))
                            start = end

                        render_kwargs = {part_vars[i]: split_prompts[i] for i in range(num_parts)}
                        if 'prompt_goal' in template_vars:
                            render_kwargs['prompt_goal'] = translated_goal
                        if 'prompt_object' in template_vars:
                            render_kwargs['prompt_object'] = translated_object

                        output = template_obj.render(**render_kwargs)
                else:
                    output = template_obj.render(
                        prompt=translated_prompt,
                        prompt_goal=translated_goal,
                        prompt_object=translated_object
                    )

            final_outputs.append(output)

        return final_outputs

    def apply_templates(self, input_prompt: BasePrompt, strategies: Union[str, List[str], None] = None, sample_size: int = None) -> List[str]:
        if strategies is None:
            raise ValueError("At least one strategy must be provided")

        if isinstance(strategies, str):
            strategies = [strategies]

        if len(strategies) == 1:
            return self.apply_single_strategy(input_prompt, strategies[0], sample_size)
        else:
            return self.apply_chained_templates(input_prompt, strategies, sample_size)


if __name__ == '__main__':
    pt = PromptTemplater()
    bp = BasePrompt(prompt="hello world", prompt_goal="", prompt_object="")
    language = "Caesar Cipher"

    translated = pt.translate_prompt(bp.prompt, language)
    print(f"Original: {bp.prompt}")
    print(f"Translated ({language}): {translated}")
