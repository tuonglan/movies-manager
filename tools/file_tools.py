import os, glob, json, shutil


def read_json(json_file):
    with open(json_file) as sin:
        return json.load(sin)

def write_json(dic, path):
    with open(path, 'w') as sout:
        json.dump(dic, sout, indent=4, sort_keys=True)

def copy(src, dst):
    shutil.copy(src, dst)

def files_with_extensions(path, extensions):
    files = []
    for e in extensions:
        files.extend(glob.glob(os.path.join(glob.escape(path), "*.%s" % e)))

    return files

