import os
import re
import pandas as pd


def parse_thy_file(file_name, keywords):
    assert file_name[-4:] == '.thy'
    print(file_name)
    source = file_name[file_name.find('HOL')+4:]
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.read()

    new_lines = re.sub(r'\(in.*?\)', ' ', lines)
    new_lines = re.sub(r'\[.*?\]', ' ', new_lines)
    lines = new_lines.split('\n')
    i = 0
    items = []
    while i < len(lines):
        line = lines[i]
        if not line.split():
            i = i + 1
            continue
        for key in keywords:
            temp_key = line[:len(key)]
            if temp_key == key:
                start = len(key)
                while start < len(line):
                    if line[start] == ' ' or line[start] == '\"':
                        start += 1
                    else:
                        end = start + 1
                        while end < len(line):
                            if line[end] == ' ' or line[end] == ':' or line[end] == '\"':
                                break
                            end += 1
                        items.append((key, line[start:end], source))
                        break
                if start == len(line):
                    i = i + 1
                    line = lines[i]
                    start = 0
                    while start < len(line):
                        if line[start] == ' ' or line[start] == '\"':
                            start += 1
                        else:
                            end = start + 1
                            while end < len(line):
                                if line[end] == ' ' or line[end] == ':' or line[end] == '\"':
                                    break
                                end += 1
                            items.append((key, line[start:end], source))
                            break
                break
        i = i + 1

    return items


if __name__ == '__main__':
    dic = {'type': [], 'name': [], 'source': []}
    keywords = ['typedef',
                'type_synonym',
                'definition',
                'abbreviation',
                'fun',
                'function'
                'inductive',
                'locale',
                'class']
    for root, _, files in os.walk('../Isabelle2024/Isabelle2024/src/HOL'):
        files.sort()
        for file in files:
            if file[-4:] == '.thy':
                items = parse_thy_file(os.path.join(root, file), keywords)
                for item in items:
                    dic['type'].append(item[0])
                    dic['name'].append(item[1])
                    dic['source'].append(item[2])

    df = pd.DataFrame(dic)
    df.to_csv('data/raw_extraction.csv', index=False, sep=' ')