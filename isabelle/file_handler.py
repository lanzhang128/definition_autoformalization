import ast
import os


def write_to_thy_file(file_path, theory_name, import_thy, code):
    if import_thy:
        with open(file_path, 'w') as f:
            imports = '\n'.join(import_thy)
            f.write(f'theory {theory_name}\nimports\n{imports}\n{code}')
    else:
        with open(file_path, 'w') as f:
            f.write(f'theory {theory_name}\n{code}')


def write_error_to_file(file_path, is_valid, error_lines, error_details, inference_time):
    with open(file_path, 'w') as file:
        file.write(f'logical validity: {is_valid}\n')
        file.write(f'error lines: {error_lines}\n')
        file.write(f'errors details: {error_details}\n')
        file.write(f'isabelle inference time: {inference_time:.2f}s')


def parse_error_file(error_log_path, thy_file_path):
    if os.path.exists(error_log_path):
        with open(error_log_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if 'error lines: ' in line:
                    error_lines = ast.literal_eval(line[len('error lines: '):])
                if 'errors details: ' in line:
                    errors_details = ast.literal_eval(line[len('errors details: '):])
                if 'logical validity: ' in line:
                    validity = ast.literal_eval(line[len('logical validity: '):])

        with open(thy_file_path, 'r', encoding='utf-8') as f:
            thy_lines = f.readlines()

        all_syntax_error = ''
        first_syntax_error = ''
        for i, line_number in enumerate(error_lines):
            if error_lines[i] > len(thy_lines):
                continue
            syntax_error = f'Identified Syntactic Error: \n{errors_details[i]}\n'

            all_syntax_error += f'{syntax_error}\n'
            if i == 0:
                first_syntax_error += syntax_error
    else:
        validity = False
        all_syntax_error = ''
        first_syntax_error = ''

    return validity, first_syntax_error, all_syntax_error
