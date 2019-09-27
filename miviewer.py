#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce

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

def main():
    mi = parse_meminfo(get_meminfo())
    print(mi)

if __name__ == "__main__":
    main()
