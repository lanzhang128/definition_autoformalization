import ast
import os


def write_to_thy_file(file_path, theory_name, import_thy, code):
    if import_thy:
        with open(file_path, 'w', encoding='utf-8') as f:
            imports = '\n'.join(import_thy)
            f.write(f'theory {theory_name}\nimports\n{imports}\n{code}')
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f'theory {theory_name}\n{code}')


def write_error_to_file(file_path, is_valid, error_lines, error_details, inference_time):
    with open(file_path, 'w', encoding='utf-8') as file:
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

            error_code = thy_lines[error_lines[i]-1].rstrip()
            detail = errors_details[i]
            line, start, end = int(detail.split()[3][:-1]), int(detail.split()[5][:-1]), int(detail.split()[7][:-1])
            assert line == error_lines[i]
            trigger = offset_transfer(thy_file_path, start, end)
            message = detail[detail.find(':')+2:]
            syntax_error = (f'Identified error on line: {line}, trigger: {trigger}\n'
                            f'Error message: {message}\n'
                            f'Code Causing Error: \n{error_code}\n')

            all_syntax_error += f'{syntax_error}\n'
            if i == 0:
                first_syntax_error += syntax_error
    else:
        validity = False
        all_syntax_error = ''
        first_syntax_error = ''

    return validity, first_syntax_error, all_syntax_error


def offset_transfer(thy_file_path, start, end):
    with open(thy_file_path, 'r', encoding='utf-8') as f:
        isabelle_text = f.read()
    symbols = []
    i = 0
    while i < len(isabelle_text):
        if isabelle_text[i] != '\\':
            symbols.append(isabelle_text[i])
            i += 1
        else:
            if isabelle_text[i+1] != '<':
                symbols.append(isabelle_text[i])
                i += 1
            else:
                j = i + 2
                while j < len(isabelle_text):
                    if isabelle_text[j] != '>':
                        if isabelle_text[j] == ' ':
                            symbols.append(isabelle_text[i])
                            i = i + 1
                            break
                        else:
                            j += 1
                    else:
                        symbols.append(isabelle_text[i:j+1])
                        i = j + 1
                        break
    return ''.join(symbols[start-1:end-1])
