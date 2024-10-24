import ast
import os
import json
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm


class Checker:
    def __init__(self):
        self.errors = {
            'Inner syntax error': 'SYN',
            'Outer syntax error': 'SYN',
            'Inner lexical error': 'SYN',
            'Malformed command syntax': 'SYN',
            'Bad name': 'SYN',
            'Bad number of arguments': 'SYN',
            'Extra free type variable(s)': 'SYN',
            'Undefined type name': 'UDF',
            'Undeclared class': 'UDF',
            'Undefined locale': 'UDF',
            'Undefined constant': 'UDF',
            'No type arity': 'UDF',
            'Extra variables on rhs': 'UDF',
            'Type unification failed': 'TUF'
        }
        self.count_errors = {
            'valid': [],
            'invalid': [],
            'Time Run-Out': [],
            'Fake Non-Exist Theory': []}
        for err in self.errors.keys():
            self.count_errors[err] = {'case': [], 'occur': []}
        for cat in self.errors.values():
            self.count_errors[cat] = {'case': [], 'occur': []}
        self.count_errors['Import Problem'] = []
        self.count_errors['First Error Occurrence'] = {}

    def error_occurrence(self, lines, key):
        error_list = ast.literal_eval(lines[2][lines[2].find('['):-1])
        for err in self.errors.keys():
            for error in error_list:
                if err in error.split(':')[1]:
                    self.count_errors[err]['case'].append(f'test_{key}')
                    self.count_errors[err]['occur'].append(0)
                    if f'test_{key}' not in self.count_errors[self.errors[err]]['case']:
                        self.count_errors[self.errors[err]]['case'].append(f'test_{key}')
                        self.count_errors[self.errors[err]]['occur'].append(0)
                    break

        print_state = False
        for error in error_list:
            not_in_list_state = True
            for err in self.errors.keys():
                if err in error.split(':')[1]:
                    self.count_errors[err]['occur'][-1] += 1
                    self.count_errors[self.errors[err]]['occur'][-1] += 1
                    not_in_list_state = False
                    break
            if not_in_list_state:
                print_state = True
        return print_state

    def check_timeout(self, lines, key):
        if 'error lines: []' in lines[1]:
            timeout = float(lines[3][25:-1])
            if timeout > 60:
                self.count_errors['Time Run-Out'].append(f'test_{key}')
                self.count_errors['First Error Occurrence'][f'test_{key}'] = 0
            else:
                self.count_errors['Fake Non-Exist Theory'].append(f'test_{key}')
                self.count_errors['First Error Occurrence'][f'test_{key}'] = 0
            return True
        return False

    def check_first_error_occurrence(self, error_lines, thy_path):
        with open(thy_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if max(error_lines) > len(lines):
            self.count_errors['Import Problem'].append(os.path.basename(thy_path)[:-4])
        if error_lines[0] > len(lines):
            return 0

        header = 0
        while header < len(lines):
            if lines[header][:5] == 'begin':
                header += 1
                break
            else:
                header += 1
        first_error_line_index = error_lines[0] - header - 1
        main_body = lines[header:-1]
        num_correct_lines = first_error_line_index
        blank_lines = []
        for i in range(len(main_body)):
            if not main_body[i].split():
                blank_lines.append(i)
                if first_error_line_index > i:
                    num_correct_lines -= 1

        return num_correct_lines / (len(main_body) - len(blank_lines))

    def check(self, keys, files_dir):
        for key in tqdm(keys):
            error_log_path = os.path.join(files_dir, f'test_{key}.error.log')
            with open(error_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            is_valid = lines[0].split()[-1]
            is_valid = True if is_valid == 'True' else False
            if is_valid:
                self.count_errors['valid'].append(f'test_{key}')
                self.count_errors['First Error Occurrence'][f'test_{key}'] = 1
            else:
                if not self.check_timeout(lines, key):
                    print_state = self.error_occurrence(lines, key)
                    if print_state:
                        print(error_log_path)

                    error_lines = ast.literal_eval(lines[1][lines[1].find('['):-1])
                    feo = self.check_first_error_occurrence(error_lines, error_log_path[:-9] + 'thy')
                    self.count_errors['First Error Occurrence'][f'test_{key}'] = feo

                self.count_errors['invalid'].append(f'test_{key}')

    def error_statistics(self, total):
        num_zeros = (len(self.count_errors['invalid']) - len(self.count_errors['Time Run-Out'])
                     - len(self.count_errors['Fake Non-Exist Theory']))
        res_dic = {}
        for err in self.errors.keys():
            res_dic[err] = {
                'case': len(self.count_errors[err]['case']),
                'occur': sum(self.count_errors[err]['occur']),
                'percentage': len(self.count_errors[err]['case']) / total
            }
            occur = self.count_errors[err]['occur'] + [0] * (num_zeros - len(self.count_errors[err]['case']))
            res_dic[err]['mean'] = np.mean(occur)
            res_dic[err]['std'] = np.std(occur)
        return res_dic

    def category_statistics(self, total):
        num_zeros = (len(self.count_errors['invalid']) - len(self.count_errors['Time Run-Out'])
                     - len(self.count_errors['Fake Non-Exist Theory']))
        res_dic = {}
        for cat in self.errors.values():
            res_dic[cat] = {
                'case': len(self.count_errors[cat]['case']),
                'occur': sum(self.count_errors[cat]['occur']),
                'percentage': len(self.count_errors[cat]['case']) / total
            }
            occur = self.count_errors[cat]['occur'] + [0] * (num_zeros - len(self.count_errors[cat]['case']))
            res_dic[cat]['mean'] = np.mean(occur)
            res_dic[cat]['std'] = np.std(occur)
        return res_dic

    def percent_statistics(self, total):
        percent = {
            'Valid': len(self.count_errors['valid']) / total,
            'First Error Occurrence': sum(self.count_errors['First Error Occurrence'].values())
                                      / len(self.count_errors['First Error Occurrence'].values()),
            'Time Run-Out': len(self.count_errors['Time Run-Out']) / total,
            'Fake Non-Exist Theory': len(self.count_errors['Fake Non-Exist Theory']) / total
        }
        return percent

    def print_result(self, files_dir):
        total = len(self.count_errors['valid']) + len(self.count_errors['invalid'])
        print(self.percent_statistics(total))
        res = {}
        res.update(self.error_statistics(total))
        res.update(self.category_statistics(total))
        pd.DataFrame(res).to_csv(os.path.join(files_dir, 'statistics.csv'))
        return total


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='model evaluation')
    parser.add_argument('--folder', default='results/gpt_4o_wiki_zs_all',
                        help='folder containing error log files')
    parser.add_argument('--test_json', default='data/def_wiki_test.json',
                        help='json file containing test data')
    args = parser.parse_args()

    files_dir = args.folder
    with open(args.test_json, 'r', encoding='utf-8') as f:
        keys = json.load(f).keys()

    checker = Checker()
    checker.check(keys, files_dir)
    assert checker.print_result(files_dir) == len(keys)
