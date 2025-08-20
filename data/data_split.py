import json


if __name__ == '__main__':
    json_file = 'def_wiki.json'
    ids = ['0', '3', '8', '11', '22', '27', '30', '35', '40', '48']
    with open(json_file, 'r', encoding='utf-8') as f:
        data_dic = json.load(f)

    dev_dic = {}
    test_dic = {}
    for key in data_dic.keys():
        if key in ids:
            dev_dic[key] = data_dic[key]
        else:
            test_dic[key] = data_dic[key]

    with open(json_file[:-5]+'_dev.json', 'w', encoding='utf-8') as f:
        json.dump(dev_dic, f, ensure_ascii=False, indent=4)
    with open(json_file[:-5] + '_test.json', 'w', encoding='utf-8') as f:
        json.dump(test_dic, f, ensure_ascii=False, indent=4)
