import os
import json
import argparse
from tqdm import tqdm
from isabelle import Isabelle, write_to_thy_file, write_error_to_file
import signal
import re


def gpt_postprocess(text):
    return text.replace('```isabelle', '').replace('```', '')


def handler(signum, frame):
    raise Exception('Isabelle response timed out at: ')


class IsabelleChecker:
    def __init__(self,
                 session_name='HOL',
                 server_log_file='server.log',
                 isabelle_dirs=None,
                 watchdog_timeout=60,
                 timeout=120):
        self.checker = Isabelle(session_name=session_name,
                                log_file=server_log_file,
                                dirs=isabelle_dirs,
                                watchdog_timeout=watchdog_timeout)
        self.timeout = timeout
        self.imports_time = {
            "HOL-Analysis": 300,
            "HOL-Matrix_LP": 20,
            "HOL-Probability": 600
        }

    def evaluate(self, files_dir, keys, imports, codes):
        if not os.path.exists(files_dir):
            os.mkdir(files_dir)
        if len(codes) == 0:
            raise ValueError('Codes are empty!')

        count = 0
        pass_count = 0
        for key, import_thy, code in zip(tqdm(keys), imports, codes):
            thy_file_path = os.path.join(files_dir, f'test_{key}.thy')
            error_log_path = os.path.join(files_dir, f'test_{key}.error.log')

            if os.path.exists(error_log_path):
                with open(error_log_path, 'r') as f:
                    is_valid = f.readlines()[0].split()[-1]
                is_valid = True if is_valid == 'True' else False

            else:
                write_to_thy_file(thy_file_path, f'test_{key}', import_thy, code)

                if self.timeout > 0:
                    with open(thy_file_path, 'r', encoding='utf-8') as f:
                        texts = f.read()
                    timeout = self.timeout
                    for item in self.imports_time.keys():
                        if item in texts:
                            timeout += self.imports_time[item]
                else:
                    timeout = -self.timeout

                signal.signal(signal.SIGALRM, handler)
                signal.alarm(timeout)

                try:
                    response, inference_time = self.checker.get_response(theories=[f'test_{key}'], master_dir=files_dir)
                    signal.alarm(0)
                except Exception as e:
                    print(e, end=f'test_{key}.thy\n')
                    response, inference_time = [], timeout
                    self.checker.shutdown()
                    self.checker.restart()

                is_valid, error_lines, error_details = self.checker.check_error(isabelle_response=response)

                write_error_to_file(error_log_path, is_valid, error_lines, error_details, inference_time)

            count += 1
            if is_valid:
                pass_count += 1
        return {'Pass Count': pass_count, 'Pass Rate': pass_count / count}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='model evaluation')
    parser.add_argument('--result_json', default='results/gpt_4o_wiki_zs.json',
                        help='json file to store results')
    parser.add_argument('--test_json', default='data/def_wiki.json',
                        help='json file containing test data')
    parser.add_argument('--formal_def_json', default='data/formal_def.json',
                        help='json file containing test data')
    parser.add_argument('--timeout', type=int, default=120,
                        help='main body timeout in seconds\n'
                             'if positive then enable addition of imports time\n'
                             'if negative then its absolute value is used as the timeout for all')
    parser.add_argument('--main_body', action='store_true',
                        help='only extract main body code from results')
    args = parser.parse_args()

    with open(args.test_json, 'r', encoding='utf-8') as f:
        json_dic = json.load(f)

    with open(args.formal_def_json, 'r', encoding='utf-8') as f:
        defs_dic = json.load(f)

    with open(args.result_json, 'r', encoding='utf-8') as f:
        res_dic = json.load(f)

    imports = []
    codes = []
    for key in res_dic.keys():
        temp_imports = []
        statement = gpt_postprocess(res_dic[key]['statement'])
        if args.main_body:
            temp_imports.append('Main')
            defs = json_dic[key]['possible_related_formal_defs']
            for d in defs:
                temp_imports.append('\"' + defs_dic[d]['import_thy'] + '\"')
            code = re.findall('begin.*end', statement, flags=re.DOTALL)
            if code:
                code = code[0]
            else:
                code = 'begin\n' + statement + '\nend'
        else:
            code = re.findall('imports.*end', statement, flags=re.DOTALL)
            if code:
                code = code[0]
            else:
                code = 'imports Main\nbegin\n' + statement + '\nend'
        imports.append(list(set(temp_imports)))
        codes.append(code)

    score_dic = {}
    print(f'Evaluating syntactic correctness.')
    checker = IsabelleChecker(session_name='HOL',
                              server_log_file=args.result_json[:-4] + 'log',
                              timeout=args.timeout)
    files_dir = args.result_json[:-5]
    if args.main_body:
        files_dir += '_main'
    else:
        files_dir += '_all'
    score_dic.update(checker.evaluate(files_dir=files_dir,
                                      keys=res_dic.keys(),
                                      imports=imports,
                                      codes=codes))
    checker.checker.shutdown()
    print(score_dic)
