#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
from matplotlib import animation
from argparse import ArgumentParser


def get_meminfo():
    with open("/proc/meminfo", "r") as file:
        mi_str = file.read()
    return mi_str

def parse_meminfo_line(mi, line):
    lst = line.split()
    key = lst[0].replace(":", "")
    size = int(lst[1])
    mi[key] = size
    return mi

def parse_meminfo(mi_str):
    mi_lines = mi_str.splitlines()
    mi = reduce(parse_meminfo_line, mi_lines, {})
    return mi

def update_graph(frame, axes, x, y, keys, window):
    plt.cla()

    mi = parse_meminfo(get_meminfo())

    x.append(frame)
    for idx, key in enumerate(keys):
        y[idx].append(mi[key])

    if len(x) > window:
        x.pop(0)
        for yelem in y:
            yelem.pop(0)

    axes.stackplot(x, np.vstack(y), labels=keys)
    axes.legend(loc="upper left")

    plt.plot()

def draw_graph(interval, frames, window, keys):
    fig, axes = plt.subplots()

    x = []
    y = [[] for i in keys]

    params = {
        "fig": fig,
        "func": update_graph,
        "fargs": (axes, x, y, keys, window),
        "interval": interval * 1000,
        "frames": frames,
        "repeat": False,
    }
    anime = animation.FuncAnimation(**params)

    plt.show()

def parse_option():
    ap = ArgumentParser()
    ap.add_argument('-i', '--interval', type=int,
                           default=1,
                           help='The delay between updates in seconds. Default is 1.')
    ap.add_argument('-c', '--count', type=int,
                           default=None,
                           help='Number of updates.  Default is infinite.')
    ap.add_argument('-w', '--window', type=int,
                           default=120,
                           help='Number of shown.  Default is 120.')
    return ap.parse_args()

def main():
    args = parse_option()
    draw_graph(args.interval,
               args.count,
               args.window,
               ["MemFree",
                "Active(file)",
                "Inactive(file)",
                "Unevictable",
                "Active(anon)",
                "Inactive(anon)",
                "SReclaimable",
                "SUnreclaim",
                "Slab",
                "KernelStack",
                "PageTables",
                "VmallocUsed"])

if __name__ == "__main__":
    main()
