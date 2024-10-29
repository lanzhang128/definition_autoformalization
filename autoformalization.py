import json
import argparse
import os.path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
from openai import OpenAI
import tenacity
from isabelle import parse_error_file


class OpenAIModel:
    def __init__(self, api_key, engine):
        self.api_key = api_key
        self.engine = engine
        self.client = OpenAI(api_key=self.api_key)

    @tenacity.retry(wait=tenacity.wait_exponential(
        multiplier=1, min=4, max=30))
    def completion_with_backoff(self, **kwargs):
        try:
            return self.client.chat.completions.create(**kwargs)
        except Exception as e:
            print(e)
            raise e

    def chat(self, messages):
        try:
            response = self.completion_with_backoff(
                model=self.engine,
                temperature=0,
                max_tokens=1000,
                messages=messages
            )
        except Exception as e:
            print('Error:', e)
            return

        return response.choices[0].message.content


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Autoformalization with LLMs')
    parser.add_argument('--model_name', default='gpt-4o-2024-05-13',
                        help='name of the LLM')
    parser.add_argument('--result_json', default='results/def_wiki/gpt_4o_zs.json',
                        help='json file to store results')
    parser.add_argument('--prompt_json', default='prompts/zs.json',
                        help='json file to store prompt')
    parser.add_argument('--test_json', default='data/def_wiki.json',
                        help='json file containing test data')
    parser.add_argument('--formal_def_json', default='data/formal_def.json',
                        help='json file containing grounded formal definitions')
    parser.add_argument('--previous_json', default='results/def_wiki/gpt_4o_zs.json',
                        help='json file containing previous results')
    parser.add_argument('--openai_api', default='api_key.txt',
                        help='openai api key txt file')
    args = parser.parse_args()

    model_name = args.model_name

    with open(args.test_json, 'r', encoding='utf-8') as f:
        json_dic = json.load(f)

    with open(args.formal_def_json, 'r', encoding='utf-8') as f:
        defs_dic = json.load(f)

    with open('prompts/instructions.json', 'r', encoding='utf-8') as f:
        instructions = json.load(f)

    with open(args.prompt_json, 'r', encoding='utf-8') as f:
        prompt = json.load(f)
    prompt_content = prompt['user']
    for inst in ['General Instruction', 'Stylistic Instruction', 'Output Instruction']:
        if inst == 'General Instruction' and 'minif2f' in args.test_json:
            prompt_content = prompt_content.replace('{' + inst + '}', instructions[inst] + ' Do not give any proof.')
            prompt_content = prompt_content.replace('definition', 'statement')
        else:
            prompt_content = prompt_content.replace('{'+inst+'}', instructions[inst])
    add_inst = ''
    for i in range(len(prompt['Additional Instructions'])):
        inst = prompt['Additional Instructions'][i]
        add_inst = add_inst + f'{i+1}. ' + instructions['Additional Instructions'][inst]+'\n'
    prompt_content = prompt_content.replace('{Additional Instructions}', add_inst)

    if '{{previous}}' in prompt_content:
        previous = True
        error_files_dir = args.previous_json[:-5] + '_all'
        if not os.path.exists(error_files_dir):
            raise FileNotFoundError(f'{error_files_dir} does not exist.')
    else:
        previous = False

    result_dic = {}
    if 'gpt' in model_name:
        with open(args.openai_api, 'r', encoding='utf-8') as f:
            api_key = f.read()

        model = OpenAIModel(api_key=api_key, engine=model_name)
    else:
        if model_name == 'deepseek':
            model_id = 'deepseek-ai/deepseek-math-7b-instruct'
        elif model_name == 'llama':
            model_id = 'meta-llama/Meta-Llama-3-8B-Instruct'
        else:
            raise NotImplementedError

        model = AutoModelForCausalLM.from_pretrained(model_id, device_map='auto', torch_dtype=torch.float16)
        tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)

    for key in tqdm(json_dic.keys()):
        latex = json_dic[key]['latex']
        preliminary = json_dic[key]['preliminary']
        def_keys = json_dic[key]['possible_related_formal_defs']

        formal_defs = ''
        for def_key in def_keys:
            formal_defs += defs_dic[def_key]['formal_code'] + '\n\n'

        user_content = prompt_content.replace('{latex}', latex)
        user_content = user_content.replace('{preliminary}', preliminary)
        user_content = user_content.replace('{formal_defs}', formal_defs)
        if previous:
            thy_file_path = os.path.join(error_files_dir, f'test_{key}.thy')
            error_log_path = os.path.join(error_files_dir, f'test_{key}.error.log')
            with open(thy_file_path, 'r', encoding='utf-8') as f:
                previous_code = f.read()
            user_content = user_content.replace('{previous}', previous_code)

            validity, first_syntax_error, all_syntax_error = parse_error_file(error_log_path, thy_file_path)
            user_content = user_content.replace('{correctness}', str(validity))
            user_content = user_content.replace('{error_details}', all_syntax_error)
        messages = [{'role': 'user', 'content': user_content}]

        if 'gpt' in model_name:
            formal = model.chat(messages)
        else:
            encodeds = tokenizer.apply_chat_template(messages, return_tensors='pt')
            model_inputs = encodeds.to('cuda')
            generated_ids = model.generate(model_inputs, max_new_tokens=1000,
                                           do_sample=False, pad_token_id=tokenizer.eos_token_id)
            decoded = tokenizer.batch_decode(generated_ids)

            formal = decoded[0]
            template = tokenizer.batch_decode(encodeds)[0]
            formal = formal[formal.find(template) + len(template):]

            if model_name == 'deepseek':
                eos = '<｜end▁of▁sentence｜>'
                if formal[-len(eos):] == eos:
                    formal = formal[:-len(eos)]

        result_dic[key] = {'latex': latex, 'preliminary': preliminary, 'statement': formal}

        with open(args.result_json, 'w', encoding='utf-8') as f:
            json.dump(result_dic, f, ensure_ascii=False, indent=4)
