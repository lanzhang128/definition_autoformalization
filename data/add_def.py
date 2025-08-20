import os
import json


def add_def(def_dic, id, source, latex, preliminary=''):
    def_dic[str(id)] = {
        'id': id,
        'source': source,
        'latex': latex,
        'preliminary': preliminary
    }


if __name__ == '__main__':
    json_file = 'def_wiki.json'
    id = -1
    source = ''
    with open('latex.txt', 'r', encoding='utf-8') as f:
        latex = f.read()
    with open('preliminary.txt', 'r', encoding='utf-8') as f:
        preliminary = f.read()

    if not os.path.exists(json_file):
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open(json_file, 'r', encoding='utf-8') as f:
        def_dic = json.load(f)

    if id in def_dic.keys() or id < 0:
        raise KeyError

    add_def(def_dic, id, source, latex, preliminary)

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(def_dic, f, ensure_ascii=False, indent=4)
