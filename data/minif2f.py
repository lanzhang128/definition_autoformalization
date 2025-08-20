import os
import json

if __name__ == '__main__':
    informal_dir = 'miniF2F/informal/test'
    id = 0
    res = {}
    for root, _, files in os.walk(informal_dir):
        for file in files:
            with open(os.path.join(informal_dir, file), 'r', encoding='utf-8') as f:
                informal = json.load(f)['informal_statement']
            res[str(id)] = {
                'id': id,
                'source': informal_dir + '/' + file,
                'latex': informal,
                'preliminary': '',
                'possible_related_formal_defs': ['real', 'complex']
            }
            id += 1

    with open('minif2f_test.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
