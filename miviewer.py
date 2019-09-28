#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from functools import reduce
import matplotlib.pyplot as plt
from matplotlib import animation
from argparse import ArgumentParser
import time
import subprocess

GRAPH_TYPES = {
    "active": ["MemFree",
               "Active(file)",
               "Inactive(file)",
               "Unevictable",
               "Active(anon)",
               "Inactive(anon)",
               "SReclaimable",
               "SUnreclaim",
               "KernelStack",
               "PageTables",
               "VmallocUsed"],
    "buff-cache": ["MemFree",
                   "Buffers",
                   "Cached",
                   "AnonPages",
                   "SReclaimable",
                   "SUnreclaim",
                   "KernelStack",
                   "PageTables",
                   "VmallocUsed"],
    "available": ["MemAvailable", "@MemNotAvailable"],
    "user-kernel": ["MemFree", "@UserSpace", "@KernelSpace"]}

PERF=False

def get_meminfo(from_adb):
    if from_adb:
        mi_str = subprocess.check_output(["adb", "shell", "cat", "/proc/meminfo"]).decode()
    else:
        with open("/proc/meminfo", "r") as file:
            mi_str = file.read()
    return mi_str

def parse_meminfo_line(mi, line):
    lst = line.split()
    key = lst[0].replace(":", "")
    size = int(lst[1])
    mi[key] = size
    return mi

def check_mem_available(mi):
    avail1 = mi["MemAvailable"]
    avail2 = mi["MemFree"] + mi["Inactive(file)"] + mi["SReclaimable"]
    diff = avail1 - avail2
    print("MemAvailable diff: {} kB".format(diff))

def check_active(mi):
    active1 = mi["Active"]
    active2 = mi["Active(file)"] + mi["Active(anon)"]
    diff = active1 - active2
    print("Active diff: {} kB".format(diff))

def check_inactive(mi):
    inactive1 = mi["Inactive"]
    inactive2 = mi["Inactive(file)"] + mi["Inactive(anon)"]
    diff = inactive1 - inactive2
    print("Inactive diff: {} kB".format(diff))

def check_file_backed(mi):
    file_backed1 = mi["Buffers"] + mi["Cached"]
    file_backed2 = mi["Active(file)"] + mi["Inactive(file)"] + mi["Shmem"]
    diff = file_backed1 - file_backed2
    print("File Backed diff: {} kB".format(diff))

def check_anon(mi):
    anon1 = mi["Active(anon)"] + mi["Inactive(anon)"]
    anon2 = mi["Shmem"] + mi["AnonPages"]
    diff = anon1 - anon2
    print("Anonymous diff: {} kB".format(diff))

def check_user_space(mi):
    user1 = mi["AnonPages"] + mi["Buffers"] + mi["Cached"]
    user2 = mi["Active(file)"] + mi["Inactive(file)"] + mi["Unevictable"] \
            + mi["Active(anon)"] + mi["Inactive(anon)"]
    diff = user1 - user2
    print("User Space diff: {} kB".format(diff))

def check_slab(mi):
    slab1 = mi["Slab"]
    slab2 = mi["SReclaimable"] + mi["SUnreclaim"]
    diff = slab1 - slab2
    print("Slab diff: {} kB".format(diff))

def check_total(mi):
    total1 = mi["MemTotal"]
    total2 = mi["MemFree"] + mi["Active(file)"] \
             + mi["Inactive(file)"] + mi["Unevictable"] \
             + mi["Active(anon)"] + mi["Inactive(anon)"] \
             + mi["SReclaimable"] + mi["SUnreclaim"] \
             + mi["KernelStack"] + mi["PageTables"] \
             + mi["VmallocUsed"]
    diff = total1 - total2
    print("Total size diff: {} kB".format(diff))

def check_meminfo(mi):
    check_mem_available(mi)
    check_active(mi)
    check_inactive(mi)
    check_file_backed(mi)
    check_anon(mi)
    check_user_space(mi)
    check_slab(mi)
    check_total(mi)

def parse_meminfo(mi_str):
    mi_lines = mi_str.splitlines()
    mi = reduce(parse_meminfo_line, mi_lines, {})
    mi["@MemNotAvailable"] = mi["MemTotal"] - mi["MemAvailable"]
    mi["@UserSpace"] = mi["AnonPages"] + mi["Buffers"] + mi["Cached"]
    mi["@FileBacked"] = mi["Buffers"] + mi["Cached"]
    mi["@Anonymous"] = mi["Active(anon)"] + mi["Inactive(anon)"]
    mi["@KernelSpace"] = mi["MemTotal"] - mi["MemFree"] - mi["@UserSpace"]
    return mi

# XXX: frame 0 is passed twice. So using global counter.
update_count = 0
def update_graph(frame, axes, x, y, keys, window, interval_ms, from_adb):
    global update_count

    if PERF:
        time_start = time.perf_counter()

    plt.cla()
    plt.xlabel("[sec]")
    plt.ylabel("[GB]")

    mi = parse_meminfo(get_meminfo(from_adb))

    current_sec = update_count * interval_ms / 1000
    x.append(current_sec)
    for idx, key in enumerate(keys):
        y[idx].append(mi[key] / 1024 / 1024)

    if len(x) > window * 1000 / interval_ms + 1:
        x.pop(0)
        for yelem in y:
            yelem.pop(0)

    xstart = max([0, current_sec - window])
    plt.xlim(xstart, xstart + window)
    axes.stackplot(x, np.vstack(y), labels=keys)

    handles, labels = axes.get_legend_handles_labels()
    axes.legend(
        # Change the legend order to be same as the line order.
        handles[::-1], labels[::-1],
        # Locate the legend outside of graph.
        bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)

    plt.plot()

    update_count += 1

    if PERF:
        time_end = time.perf_counter()
        print("elapsed = {}".format(time_end - time_start))

def draw_graph(interval_ms, frames, window, graph_type, from_adb):
    fig, axes = plt.subplots()
    fig.suptitle("/proc/meminfo ({})".format(graph_type))
    keys = GRAPH_TYPES[graph_type]

    # Shrink x-axis for legend
    box = axes.get_position()
    axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    x = []
    y = [[] for i in keys]

    params = {
        "fig": fig,
        "func": update_graph,
        "fargs": (axes, x, y, keys, window, interval_ms, from_adb),
        "interval": interval_ms,
        "frames": frames,
        "repeat": False,
    }
    anime = animation.FuncAnimation(**params)

    plt.show()

def parse_option():
    ap = ArgumentParser()
    ap.add_argument("-a", "--adb", action="store_true",
                    help="Get meminfo via adb.")
    ap.add_argument("-i", "--interval", type=int,
                    default=200,
                    help="The delay between updates in milli-seconds. Default is 200.")
    ap.add_argument("-c", "--count", type=int,
                    default=None,
                    help="Number of updates.  Default is infinite.")
    ap.add_argument("--check", action="store_true",
                    help="Check some formulas.")
    ap.add_argument("-w", "--window", type=int,
                    default=60,
                    help="Shown period time in seconds.  Default is 60.")
    ap.add_argument("-t", "--type", choices=["active", "buff-cache", "available", "user-kernel"],
                    default="active",
                    help="Graph type. Default is active.")
    return ap.parse_args()

def main():
    args = parse_option()

    if args.check:
        mi = parse_meminfo(get_meminfo(args.adb))
        check_meminfo(mi)
        exit()

    draw_graph(args.interval,
               args.count,
               args.window,
               args.type,
               args.adb)

if __name__ == "__main__":
    main()
