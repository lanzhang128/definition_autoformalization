import ast
import json
import argparse
import os.path
from tqdm import tqdm
from autoformalization import OpenAIModel


def parse_error_file(error_log_path, lean4_file_path):
    if os.path.exists(error_log_path):
        with open(error_log_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if 'error lines: ' in line:
                    error_lines = ast.literal_eval(line[len('error lines: '):])
                if 'errors details: ' in line:
                    errors_details = ast.literal_eval(line[len('errors details: '):])
                if 'logical validity: ' in line:
                    validity = ast.literal_eval(line[len('logical validity: '):])

        with open(lean4_file_path, 'r', encoding='utf-8') as f:
            thy_lines = f.readlines()

        all_syntax_error = ''
        first_syntax_error = ''
        for i, line_number in enumerate(error_lines):
            if error_lines[i] > len(thy_lines):
                continue

            detail = errors_details[i]
            line = int(detail.split()[3][:-1])
            assert line == error_lines[i]
            message = detail[detail.find(':')+2:]
            syntax_error = (f'Identified error on line: {line}\n'
                            f'Error message: {message}\n')

            all_syntax_error += f'{syntax_error}\n'
            if i == 0:
                first_syntax_error += syntax_error
    else:
        validity = False
        all_syntax_error = ''
        first_syntax_error = ''

    return validity, first_syntax_error, all_syntax_error


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Autoformalization with LLMs')
    parser.add_argument('--model_name', default='gpt-4o-2024-05-13',
                        help='name of the LLM')
    parser.add_argument('--result_json', default='results/def_wiki/lean4_gpt_4o_det.json',
                        help='json file to store results')
    parser.add_argument('--prompt_txt', default='prompts/lean_det.txt',
                        help='text file to store prompt')
    parser.add_argument('--test_json', default='data/def_wiki.json',
                        help='json file containing test data')
    parser.add_argument('--previous_json', default='results/def_wiki/lean4_gpt_4o_zs.json',
                        help='json file containing previous results')
    parser.add_argument('--openai_api', default='api_key.txt',
                        help='openai api key txt file')
    args = parser.parse_args()

    model_name = args.model_name

    with open(args.test_json, 'r', encoding='utf-8') as f:
        json_dic = json.load(f)

    with open(args.prompt_txt, 'r', encoding='utf-8') as f:
        prompt_content = f.read()

    if 'minif2f' in args.test_json:
        prompt_content = prompt_content.replace('{no_proof}', ' Do not give any proof.')
        prompt_content = prompt_content.replace('definition', 'statement')
    else:
        prompt_content = prompt_content.replace('{no_proof}', '')

    if '{{previous}}' in prompt_content:
        previous = True
        error_files_dir = args.previous_json[:-5]
        if not os.path.exists(error_files_dir):
            raise FileNotFoundError(f'{error_files_dir} does not exist.')
    else:
        previous = False

    result_dic = {}
    with open(args.openai_api, 'r', encoding='utf-8') as f:
        api_key = f.read()

    model = OpenAIModel(api_key=api_key, engine=model_name)

    for key in tqdm(json_dic.keys()):
        latex = json_dic[key]['latex']
        preliminary = json_dic[key]['preliminary']

        user_content = prompt_content.replace('{latex}', latex)
        user_content = user_content.replace('{preliminary}', preliminary)
        if previous:
            lean4_file_path = os.path.join(error_files_dir, f'test_{key}.lean')
            error_log_path = os.path.join(error_files_dir, f'test_{key}.error.log')
            with open(lean4_file_path, 'r', encoding='utf-8') as f:
                previous_code = f.read()
            user_content = user_content.replace('{previous}', previous_code)

            validity, _, all_syntax_error = parse_error_file(error_log_path, lean4_file_path)
            if len(all_syntax_error) > 15000:
                all_syntax_error = all_syntax_error[:15000]
            user_content = user_content.replace('{correctness}', str(validity))
            user_content = user_content.replace('{error_details}', all_syntax_error)
        messages = [{'role': 'user', 'content': user_content}]

        formal = model.chat(messages)

        result_dic[key] = {'latex': latex, 'preliminary': preliminary, 'statement': formal}

        with open(args.result_json, 'w', encoding='utf-8') as f:
            json.dump(result_dic, f, ensure_ascii=False, indent=4)
