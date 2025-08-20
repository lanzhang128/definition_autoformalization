import os
import json
import argparse
from tqdm import tqdm
from autoformalization_lean import parse_error_file
from agent import HardCritiqueAgent


def gpt_postprocess(text):
    return text.replace('```lean', '').replace('```', '')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='model evaluation')
    parser.add_argument('--result_json', default='results/def_wiki/lean4_gpt_4o_zs.json',
                        help='json file to store results')
    args = parser.parse_args()

    with open(args.result_json, 'r', encoding='utf-8') as f:
        res_dic = json.load(f)

    if 'gpt' in args.result_json:
        postprocess_fn = gpt_postprocess
    else:
        raise NotImplementedError

    files_dir = args.result_json[:-5]

    if not os.path.exists(files_dir):
        os.mkdir(files_dir)

    lean4 = HardCritiqueAgent(formal_language='Lean4', file_dir=files_dir)

    count = 0
    pass_count = 0
    for key in tqdm(res_dic.keys()):
        statement = postprocess_fn(res_dic[key]['statement'])
        lean4_file_path = os.path.join(files_dir, f'test_{key}.lean')
        error_log_path = os.path.join(files_dir, f'test_{key}.error.log')
        if not os.path.exists(error_log_path):
            correctness, _ = lean4(formalization=statement, file_prefix=f'test_{key}')
        else:
            correctness, _, all_syntax_error = parse_error_file(error_log_path, lean4_file_path)

        count += 1
        if str(correctness) == 'True':
            pass_count += 1
            print(key)

    print(pass_count / count)
