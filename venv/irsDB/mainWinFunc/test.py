from opcua import Client, ua
import json

def find_children(node):
    children = node.get_children()
    dict = {}
    for child in children:
        ans = find_children(child)
        dict.update([(str(child.get_browse_name())[14:-1],ans)])
    return dict

def analize(name, root):
    print("Анализ тегов: может занять некоторое время")
    d = find_children(root)
    with open(name.replace(".","")+".json", "w") as write_file:
        json.dump(d, write_file, indent=4)
    print("Анализ завершён")