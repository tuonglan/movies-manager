import os, json, re

ROMAN = re.compile('^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$')

def key_to_name(key):
    def cap(w):
        if ROMAN.match(w.upper()):
            return w.upper()
        else:
            return w.capitalize()

    ls = key.split('.')
    name = ' '.join([cap(w) for w in ls[0:-1]])
    return "%s (%s)" % (name, ls[-1])


def standardize(data, exe=False):
    for key, path in data.items():
        name = key_to_name(key)   
        dir_name = os.path.dirname(path)
        new_path = os.path.join(dir_name, name)

        print("Rename: %s -> %s" % (path, new_path))
        if exe:
            os.rename(path, new_path)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, help='Input json file for standardize name')
    parser.add_argument('--exe', action='store_true', help='Execute or just show the execution')
    args = parser.parse_args()

    with open(args.input) as sin:
        movies_db = json.load(sin)

    standardize(movies_db['tree'], args.exe)

