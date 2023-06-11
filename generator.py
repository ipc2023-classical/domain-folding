#!/usr/bin/env python3

import sys
import random

next_direction = {
        ('up', 'clockwise') : 'right',
        ('up', 'counterclockwise') : 'left',
        ('down', 'clockwise') : 'left',
        ('down', 'counterclockwise') : 'right',
        ('left', 'clockwise') : 'up',
        ('left', 'counterclockwise') : 'down',
        ('right', 'clockwise') : 'down',
        ('right', 'counterclockwise') : 'up',
}

def _genGoal(num_folds, num_nodes):
    nodes = list(range(1, num_nodes))
    random.shuffle(nodes)
    nodes = sorted(nodes[:num_folds])
    folds = {}
    for n in nodes:
        f = random.choice(['clockwise', 'counterclockwise'])
        folds[n] = f

    img = [[' ' for _ in range(num_nodes * 4)] for __ in range(num_nodes * 4)]
    plan = []
    direction = ['up' for _ in range(num_nodes)]
    direction = 'up'
    pos = [(num_nodes, num_nodes)]
    img[2 * num_nodes][2 * num_nodes] = 'x'
    for n in range(1, num_nodes):
        if n in folds:
            f = folds[n]
            next = next_direction[(direction, f)]
            plan += [f'(rotate n{n} {f} {direction} {next})']
            direction = next
        x = pos[-1][0]
        y = pos[-1][1]
        if direction == 'up':
            img[2 * y + 1][2 * x] = '|'
            y += 1
        elif direction == 'down':
            img[2 * y - 1][2 * x] = '|'
            y -= 1
        elif direction == 'left':
            img[2 * y][2 * x - 1] = '-'
            x -= 1
        elif direction == 'right':
            img[2 * y][2 * x + 1] = '-'
            x += 1
        next_pos = (x, y)
        if next_pos in pos:
            return None, None, None
        img[2 * y][2 * x] = '.'
        pos += [(x, y)]

    img_out = ''
    img = img[::-1]
    img = [''.join(l).rstrip() for l in img]
    img = [l for l in img if len(l)]
    prefix_len = min([len(l) - len(l.lstrip()) for l in img])
    img = [l[prefix_len:] for l in img]
    img_out = ';; ' + '\n;; '.join(img)
    return pos, plan, img_out

def genGoal(num_folds, num_nodes, max_tries = 50):
    for i in range(50):
        print(f'Try {i}...', file = sys.stderr)
        pos, plan, img = _genGoal(num_folds, num_nodes)
        if pos is not None:
            return pos, plan, img
    return None, None, None

def main(num_nodes, num_folds, fnpddl, fnplan):
    nodes = [f'n{i}' for i in range(1, num_nodes + 1)]
    coords = [f'c{i}' for i in range(1, num_nodes * 2)]

    coord_inc = ['(COORD-INC c{0} c{1})'.format(i, i+1) for i in range (1, num_nodes * 2 - 1)]
    connected = ['(CONNECTED n{0} n{1})'.format(i, i + 1) for i in range(1, num_nodes)]
    connected += [f'(END-NODE n{num_nodes})']

    heading = [f'(heading n{i} up)' for i in range(1, num_nodes)]

    start_node_at = (num_nodes, num_nodes)
    init_pos = [start_node_at]
    at_init = ['(at n1 c{0} c{1})'.format(*start_node_at)]
    for i in range (2, num_nodes + 1):
        init_pos += [(start_node_at[0], start_node_at[1] + i - 1)]
        at_init += ['(at n{0} c{1} c{2})'.format(i, start_node_at[0], start_node_at[1] + i - 1)]
    init_pos = [(f'c{i}', f'c{j}') for (i, j) in init_pos]

    free = []
    for x in coords:
        for y in coords:
            if (x, y) not in init_pos:
                free += [f'(free {x} {y})']

    goal_pos, plan, goal_img = genGoal(num_folds, num_nodes)
    if goal_pos is None:
        print('Error: Cannot find any random sequence!', file = sys.stderr)
        sys.exit(-1)

    at_goal = []
    for i, (x, y) in enumerate(goal_pos):
        at_goal += [f'(at n{i + 1} c{x} c{y})']

    nodes = ' '.join(nodes)
    coords = ' '.join(coords)

    coord_inc = '\n    '.join(coord_inc)
    connected = '\n    '.join(connected)

    heading = '\n    '.join(heading)
    free = '\n    '.join(free)
    at_init = '\n    '.join(at_init)

    at_goal = '\n        '.join(at_goal)

    rand = int(1000000 * random.random())
    out = f'''{goal_img}
(define (problem reverse-folding-asp-{num_nodes}-{num_folds}-{rand})
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

    with open(fnpddl, 'w') as fout:
        fout.write(out)
    with open(fnplan, 'w') as fout:
        print(f';; Optimal cost: {len(plan)}', file = fout)
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(f'Usage: {sys.argv[0]} length num-folds prob.pddl prob.plan')
        sys.exit(-1)
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]))
