import ast
import os
import re


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

        symbols = isabelle_symbols(thy_file_path)

        all_syntax_error = ''
        first_syntax_error = ''
        for i, line_number in enumerate(error_lines):
            if error_lines[i] > len(thy_lines):
                continue

            detail = errors_details[i]
            line, start, end = int(detail.split()[3][:-1]), int(detail.split()[5][:-1]), int(detail.split()[7][:-1])
            assert line == error_lines[i]
            trigger = ''.join(symbols[start-1:end-1])
            message = detail[detail.find(':')+2:]
            syntax_error = (f'Identified error on line: {line}, trigger: {trigger}\n'
                            f'Error message: {message}\n')

            all_syntax_error += f'{syntax_error}\n'
            if i == 0:
                first_syntax_error += syntax_error
    else:
        validity = False
        all_syntax_error = ''
        first_syntax_error = ''

    return validity, first_syntax_error, all_syntax_error


def isabelle_symbols(thy_file_path):
    with open(thy_file_path, 'r', encoding='utf-8') as f:
        isabelle_text = f.read()
    symbols = []
    i = 0
    while i < len(isabelle_text):
        if isabelle_text[i] != '\\':
            symbols.append(isabelle_text[i])
            i += 1
        else:
            if i == len(isabelle_text) - 1:
                symbols.append(isabelle_text[i])
                i += 1
                continue
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
                if j == len(isabelle_text):
                    symbols.append(isabelle_text[i])
                    i = i + 1
                    continue
    return symbols


def fix_bracket(code):
    new_code = ''
    while len(code) > 0:
        start = code.find('\\<')
        if start != -1:
            end = start + 2
            length = len(code)
            if end < length:
                if code[end] == '^':
                    end += 1
                while end < length:
                    if code[end] == '>':
                        new_code += code[:end+1]
                        code = code[end+1:]
                        break
                    elif 65 <= ord(code[end]) <= 90 or 97 <= ord(code[end]) <= 122:
                        end = end + 1
                    else:
                        new_code += code[:end]+'>'
                        code = code[end:]
                        break
                if end == length:
                    new_code += code[:end] + '>'
                    code = code[end:]
            else:
                break
        else:
            new_code += code
            code = ''
    return new_code


map_latex_math_to_isabelle = {}
for i in range(65, 91):
    map_latex_math_to_isabelle['\\<mathcal>{' + chr(i) + '}'] = '\\<' + chr(i) + '>'
    map_latex_math_to_isabelle['\\<mathfrak>{' + chr(i) + '}'] = '\\<' + chr(i) + chr(i) + '>'
    map_latex_math_to_isabelle['\\<mathfrak>{' + chr(i + 32) + '}'] = '\\<' + chr(i + 32) + chr(i + 32) + '>'
    map_latex_math_to_isabelle['\\<mathbb>{' + chr(i) + '}'] = '\\<bbb' + chr(i) + '>'
    map_latex_math_to_isabelle['\\<mathbf>{' + chr(i) + '}'] = '\\<^bold>' + chr(i)
    map_latex_math_to_isabelle['\\<mathbf>{' + chr(i + 32) + '}'] = '\\<^bold>' + chr(i + 32)
    map_latex_math_to_isabelle['\\<mathit>{' + chr(i) + '}'] = chr(i)
    map_latex_math_to_isabelle['\\<mathit>{' + chr(i + 32) + '}'] = chr(i + 32)
map_latex_math_to_isabelle['\\<mathbb>{B}'] = '\\<bool>'
map_latex_math_to_isabelle['\\<mathbb>{C}'] = '\\<complex>'
map_latex_math_to_isabelle['\\<mathbb>{N}'] = '\\<nat>'
map_latex_math_to_isabelle['\\<mathbb>{Q}'] = '\\<rat>'
map_latex_math_to_isabelle['\\<mathbb>{R}'] = '\\<real>'
map_latex_math_to_isabelle['\\<mathbb>{Z}'] = '\\<int>'


def fix_mapping_math(code):
    new_code = code
    symbols = re.findall(r'\\<mathcal>\{.*?\}|\\<mathfrak>\{.*?\}|\\<mathbb>\{.*?\}', code, flags=re.DOTALL)
    if symbols:
        for symbol in list(set(symbols)):
            try:
                new_code = new_code.replace(symbol, map_latex_math_to_isabelle[symbol])
            except KeyError:
                print(f'{symbol} is not in Isabelle.')

    new_code = new_code.replace('\\<mathcal>', '')
    new_code = new_code.replace('\\<mathfrak>', '')
    new_code = new_code.replace('\\<mathbb>', '')
    new_code = new_code.replace('\\<mathbf>', '')
    new_code = new_code.replace('\\<mathit>', '')
    return new_code
