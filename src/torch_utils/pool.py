from re import sub
import subprocess

from os.path import exists, dirname
from shutil import copyfile, copytree
import time
import sys
import os

from ._utils import *






def prepare_training(cfg_file):
    cfg = read_yaml(cfg_file)
    listdict_args = dictList2ListDict(cfg['args'])
    rlistdict_args = []
    for d in listdict_args:
        for i in range(cfg['repeat']):
            rlistdict_args.append(d.copy())
    print(rlistdict_args)
    subdirs = makenumberedsubdirs(rootdir=cfg['rootdir'], t=len(rlistdict_args))
    print(subdirs)

    if not exists(cfg['rootdir']):
        os.makedirs(cfg['rootdir'])

    runlist(subdirs, os.makedirs)

    for idx, sub in enumerate(subdirs):
        os.makedirs(join(sub, "cfgs"))
        write_yaml(rlistdict_args[idx], join(sub, "cfgs", cfg['cfgname']))
        for sfile in cfg['files2move']:
            dfile = join(sub, sfile)
            if not exists(dirname(dfile)):
                os.makedirs(dirname(dfile))
            copyfile(sfile, dfile)

        for sdir in cfg['dirs2move']:
            ddir = join(sub, sdir)
            if not exists(dirname(ddir)):
                os.makedirs(dirname(ddir))
            copytree(sdir, ddir)
    return subdirs, cfg, rlistdict_args

def pooltrain(subdirs: list[str], cfg):
    procs, ins, outs, errs  = [], [], [], []
    execs = 0
    while execs < len(subdirs) or len(procs) > 0:
        if len(procs) < cfg['workers'] and execs < len(subdirs):
            for wd in subdirs:
                outs.append(open(join(wd, ".shell/stdout"), "w"))
                errs.append(open(join(wd, ".shell/stderr"), "w"))
                ins.append(open(join(wd, ".shell/stdin"), "x+"))
                proc = subprocess.Popen(
                    ["python", cfg['filename']],
                    cwd=wd,
                    stdin=ins[-1],
                    stdout=outs[-1],
                    stderr=errs[-1],
                    shell=True
                )
                yield proc
                procs.append(proc)
                execs += 1

        for proc in procs:
            if proc.poll() != None:
                proc.wait()
                id = procs.index(proc)
                outs[id].close()
                errs[id].close()
                ins[id].close()
                outs.pop(id)
                errs.pop(id)
                ins.pop(id)
                procs.pop(id)
        time.sleep(5)



def train_jobspoll(config_yaml: str="config.yaml"):
    subdirs, cfg, _ = prepare_training(config_yaml)
    pool, procs = pooltrain(subdirs, cfg), []

    for proc in pool:
        procs.append(proc)

    while True:
        all_terminated = True
        for i in range(len(procs)):
            if procs[i].poll() == None:
                all_terminated = False

        if all_terminated:
            break
        time.sleep(5)
