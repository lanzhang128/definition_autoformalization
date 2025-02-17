import os
import json
import numpy as np
from transformers import AutoTokenizer
from autoformalization import OpenAIModel


def extract_number(response):
    res = -1
    if response.find('NUMBER=') != -1:
        count = response[response.find('NUMBER=') + 7:]
        if len(count) != 0:
            i = 0
            while i < len(count):
                if 48 <= ord(count[i]) <= 57:
                    i += 1
                else:
                    break
            if i > 0:
                res = int(count[:i])
    return res


if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    with open('../api_key.txt', 'r', encoding='utf-8') as f:
        api_key = f.read()
    prompt_object = ('Given the following statement written in LaTeX: {{latex}} '
                     'How many mathematical objects excluding explicit numbers and variables '
                     'are mentioned directly in this statement? '
                     'You can think it step by step. '
                     'Give me the final number as NUMBER={the number}')
    prompt_formula = ('Given the following statement written in LaTeX: {{latex}} '
                      'How many mathematical formulae are mentioned directly in this statement? '
                      'You can think it step by step. '
                      'Give me the final number as NUMBER={the number}')
    model = OpenAIModel(api_key=api_key, engine='gpt-4o')
    for file in ['minif2f_test', 'def_wiki', 'def_arxiv']:
        with open(f'{file}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not os.path.exists(f'{file}.stat.json'):
            with open(f'{file}.stat.json', 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        with open(f'{file}.stat.json', 'r', encoding='utf-8') as f:
            stat = json.load(f)

        count_tokens = []
        count_objects = []
        count_formulae = []
        for key in data.keys():
            latex = data[key]['latex']
            count_tokens.append(len(tokenizer(latex)["input_ids"]))
            try:
                response_object = stat[key]['objects']
                response_formula = stat[key]['formulae']
            except KeyError:
                messages = [{'role': 'user', 'content': prompt_object.replace('{latex}', latex)}]
                response_object = model.chat(messages)
                messages = [{'role': 'user', 'content': prompt_formula.replace('{latex}', latex)}]
                response_formula = model.chat(messages)
                stat[key] = {
                    'id': data[key]['id'],
                    'latex': data[key]['latex'],
                    'objects': response_object,
                    'formulae': response_formula
                }
                with open(f'{file}.stat.json', 'w', encoding='utf-8') as f:
                    json.dump(stat, f, ensure_ascii=False, indent=4)
            num = extract_number(response_object)
            if num != -1:
                count_objects.append(num)
            else:
                print(file, key)

            num = extract_number(response_formula)
            if num != -1:
                count_formulae.append(num)
            else:
                print(file, key)

        print(file)
        count_tokens = np.array(count_tokens)
        print('No. Tokens: ', len(count_tokens), np.mean(count_tokens), np.std(count_tokens))
        count_objects = np.array(count_objects)
        print('No. Objects', len(count_objects), np.mean(count_objects), np.std(count_objects))
        count_formulae = np.array(count_formulae)
        print('No. Formulae', len(count_formulae), np.mean(count_formulae), np.std(count_formulae))
