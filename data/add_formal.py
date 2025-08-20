import os
import json


if __name__ == '__main__':
    json_file = 'formal_def.json'
    name = 'field'
    import_thy = 'HOL.Fields'
    with open('formal.txt', 'r', encoding='utf-8') as f:
        formal = f.read()

    if not os.path.exists(json_file):
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open(json_file, 'r', encoding='utf-8') as f:
        def_dic = json.load(f)

    if name in def_dic.keys() or name == '':
        raise KeyError
    def_dic[name] = {'import_thy': import_thy, 'formal_code': formal}

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(def_dic, f, ensure_ascii=False, indent=4)
