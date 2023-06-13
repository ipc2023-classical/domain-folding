#!/usr/bin/env python3

import sys
import re
import random

pat_length = re.compile(r'^length\(([0-9]+)\)\.$')
pat_fold = re.compile(r'^fold\(([0-9]+),\s*([0-9]+),\s*([0-9]+)\)\.$')

def main(fn):
    asp = open(fn, 'r').read()
    asp = asp.split('\n')
    asp = [x.strip() for x in asp]
    asp = [x for x in asp if len(x) > 0]

    num_nodes = 0
    fold = []
    dim = 0
    for line in asp:
        m = pat_length.match(line)
        if m is not None:
            num_nodes = int(m.group(1))
            fold = [(None,None) for x in range(num_nodes + 1)]

    for line in asp:
        m = pat_fold.match(line)
        if m is not None:
            idx = int(m.group(1))
            fold[idx] = (int(m.group(2)), int(m.group(3)),)
    start_node_at = fold[1]


    directions = ['left', 'right', 'up', 'down']
    nodes = [f'n{i}' for i in range(1, num_nodes + 1)]
    coords = [f'c{i}' for i in range(1, num_nodes * 2 + 1)]

    coord_inc = ['(COORD-INC c{0} c{1})'.format(i, i+1) for i in range (1, num_nodes * 2)]
    connected = ['(CONNECTED n{0} n{1})'.format(i, i + 1) for i in range(1, num_nodes)]
    connected += [f'(END-NODE n{num_nodes})']

    heading = [f'(heading n{i} up)' for i in range(1, num_nodes)]

    init_pos = [start_node_at]
    at_init = ['(at n1 c{0} c{1})'.format(*start_node_at)]
    for i in range (2, num_nodes + 1):
        init_pos += [(start_node_at[0], start_node_at[1] + i - 1)]
        at_init += ['(at n{0} c{1} c{2})'.format(i, start_node_at[0], start_node_at[1] + i - 1)]
    init_pos = [(f'c{i}', f'c{j}') for (i, j) in init_pos]

    at_goal = []
    for i, (c1, c2) in enumerate(fold):
        if i > 0:
            at_goal += [f'(at n{i} c{c1} c{c2})']

    free = []
    for x in coords:
        for y in coords:
            if (x, y) not in init_pos:
                free += [f'(free {x} {y})']

    nodes = ' '.join(nodes)
    coords = ' '.join(coords)

    coord_inc = '\n    '.join(coord_inc)
    connected = '\n    '.join(connected)

    heading = '\n    '.join(heading)
    free = '\n    '.join(free)
    at_init = '\n    '.join(at_init)

    at_goal = '\n        '.join(at_goal)

    m = re.search(r'([^/.]+).asp', fn)
    fnheader = m.group(1)
    rand = int(1000000 * random.random())
    out = f'''(define (problem reverse-folding-asp-{fnheader}-{rand})
(:domain reverse-folding)

(:objects
    {nodes} - node
    {coords} - coord
)
(:init
    (NEXT-DIRECTION up clockwise right)
    (NEXT-DIRECTION up counterclockwise left)
    (NEXT-DIRECTION down clockwise left)
    (NEXT-DIRECTION down counterclockwise right)
    (NEXT-DIRECTION left clockwise up)
    (NEXT-DIRECTION left counterclockwise down)
    (NEXT-DIRECTION right clockwise down)
    (NEXT-DIRECTION right counterclockwise up)

    {coord_inc}

    {connected}

    {at_init}
    {heading}
    {free}

    (= (total-cost) 0)
    (= (rotate-cost) 1)
    (= (update-cost) 0)
)
(:goal
    (and
        {at_goal}
        (not (rotating))
    )
)
(:metric minimize (total-cost))
)
'''
    print(out)
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} prob.asp >prob.pddl', file = sys.stderr)
        print('''
This script translates the asp definition of the problem to the pddl
formulation.
''', file = sys.stderr)
        sys.exit(-1)
    sys.exit(main(sys.argv[1]))
