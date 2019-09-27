#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
from matplotlib import animation


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

def update_graph(frame, x, y, keys, axes):
    plt.cla()

    mi = parse_meminfo(get_meminfo())

    x.append(frame)
    for idx, key in enumerate(keys):
        y[idx].append(mi[key])

    axes.stackplot(x, np.vstack(y), labels=keys)
    axes.legend(loc="upper left")

    plt.plot()

def draw_graph(interval, frames, keys):
    fig, axes = plt.subplots()

    x = []
    y = [[] for i in keys]

    params = {
        "fig": fig,
        "func": update_graph,
        "fargs": (x, y, keys, axes),
        "interval": interval * 1000,
        "frames": frames,
        "repeat": False,
    }
    anime = animation.FuncAnimation(**params)

    plt.show()

def main():
    draw_graph(1, 10, ["MemFree", "Buffers", "Cached"])

if __name__ == "__main__":
    main()
