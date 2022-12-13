from typing import List, Optional, OrderedDict
from os.path import isdir, isfile, join
import re
import os
import json
import string
import yaml
import random
from typing import Union

def read_json(json_filepath):
    with open(json_filepath, "r") as fd:
        return json.load(fd)

def read_yaml(file: str):
    with open(file) as fd:
        return yaml.safe_load(fd)

def write_yaml(data, file):
    with open(file, "w") as fd:
        return yaml.safe_dump(data, fd)


def write_json(data, file):
    with open(file, "w") as fd:
        return json.dump(data, fd, separators=(",", ":"))

def randstr(len: int = 32):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(len))

def randsubdirs(rootdir: str, len= 0, baselen=0):
    return [join(rootdir, randstr(baselen)) for _ in range(len)]

def listdirs(rootdir: str):
    try:
        return [dir for dir in os.listdir(rootdir) if isdir(join(rootdir, dir))]
    except FileNotFoundError:
        return []


def listfiles(rootdir: str):
    try:
        return [file for file in os.listdir(rootdir) if isfile(join(rootdir, file))]
    except FileNotFoundError:
        return []




def makenumberedsubdirs(rootdir: str, t: int, f: int = 1, override_names: bool = False):
    subdirs = listdirs(rootdir)
    offset = 0
    if not override_names and len(subdirs) > 0:
        num_dirs = sorted([dir for dir in subdirs if dir.isdigit()], reverse=True)
        if len(num_dirs) > 0:
            offset = int(num_dirs[0])

    return [join(rootdir, str(dir)) for dir in range(offset + f, offset + t + f)]

def dictList2ListDict(dictlist: dict):
    list_dict, dictlist_idxs = [], {k:0 for k, v in dictlist.items() if type(v) == list}
    done = False
    while not done:
        d = {}
        for k, v in dictlist.items():
            d[k] = v if type(v) != list else v[dictlist_idxs[k]]

        for idx ,k in enumerate(dictlist_idxs.keys()):
            if idx != (len(dictlist_idxs) - 1):
                if dictlist_idxs[k] == (len(dictlist[k]) - 1):
                    dictlist_idxs[k] = 0
                else:
                    dictlist_idxs[k] += 1
                    break
            elif idx == (len(dictlist_idxs) - 1):
                if dictlist_idxs[k] == (len(dictlist[k]) - 1):
                    done = True
                else:
                    dictlist_idxs[k] += 1
                break
        list_dict.append(d)
        if len(dictlist_idxs) == 0:
            break
    return list_dict


def rawparse_args(rawoptions: str):
    matches = re.findall(r'(?:--?)([\w-]+)(.*?)(?= -|$)', rawoptions)
    result = {}
    for m in matches:
        val: str = m[1].strip()
        if val.isdigit() and float(val) == int(val):
            result[m[0]] = True if not m[1] else int(val)
        elif val.isdigit():
            result[m[0]] = True if not m[1] else float(val)
        else:
            result[m[0]] = True if not m[1] else val
    return result

def dictargs2str(dictargs: OrderedDict) -> str:
    cmd  = ""
    for argname, argval in dictargs.items():
        if type(argval) == bool:
            options = " --{argname}" if argval == True else ""
        elif type(argval) == list:
            options = f" --{argname} {','.join(argval)}"
        else:
            options = f" --{argname} {argval}"
        cmd += options
    return cmd

def append_basename(dirs: list[str], base: str):
  return [join(dir, base) for dir in dirs]


def prepend_dir(dirs: list[str], dirname: str):
  return [join(dirname, dir) for dir in dirs]

def get_subdirs(rootdir: str, filter=Optional[str], to_exclude = [], custom_filter=None):
    if filter == "folder":
        subdirs = [subdir for subdir in listdirs(rootdir) if (not subdir in to_exclude)]

    elif filter == "file":
        subdirs = [subdir for subdir in listfiles(rootdir) if (not subdir in to_exclude)]

    elif filter == "custom" and custom_filter:
        try:
            subdirs = [subdir for subdir in os.listdir(rootdir) if (not subdir in to_exclude) and custom_filter(subdir)]
        except FileNotFoundError:
            subdirs = []

    else:
        try:
            subdirs = [subdir for subdir in os.listdir(rootdir) if (not subdir in to_exclude)]
        except FileNotFoundError:
            subdirs = []

    subdirs.sort(key=lambda x: os.stat(join(rootdir, x)).st_ctime, reverse=True)
    return subdirs

def maplist(array: list, fun):
  return [fun(it) for it in array]

def runlist(array: list, fun):
    for item in array:
        fun(item)

def maplistindex(array: list, fun):
  return [fun(indx, item) for indx, item in enumerate(array)]

def get_valdicts(dicts: list[dict], key: str):
  return [d[key] for d in dicts]
