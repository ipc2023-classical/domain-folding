#!/usr/bin/env python3

import sys
import random
import copy

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

def subplan(state_pos, state_dir, node, rot, next_pos, next_dir):
    num_nodes = len(state_pos)
    plan = []
    plan += [f'(rotate n{node} {rot} {state_dir[node - 1]} {next_dir[node - 1]})']
    for n in range(node - 1, num_nodes - 1):
        n1 = n + 1
        n2 = n + 2
        (x, y) = state_pos[n2 - 1]
        if n2 - 1 < len(state_dir):
            d1 = state_dir[n2 - 1]
            d2 = next_dir[n2 - 1]
            a = f'(rotate-first-pass n{node} {rot} n{n1} n{n2} c{x} c{y} {d1} {d2})'
        else:
            a = f'(rotate-first-pass-end n{node} {rot} n{n1} n{n2} c{x} c{y})'
        plan += [a]

    for n in range(node - 1, num_nodes - 1):
        n1 = n + 1
        n2 = n + 2
        (x1, y1) = next_pos[n1 - 1]
        d1 = next_dir[n1 - 1]
        (x2, y2) = next_pos[n2 - 1]
        a = f'(rotate-second-pass n{n1} c{x1} c{y1} {d1} n{n2} c{x2} c{y2})'
        plan += [a]
    plan += [f'(rotate-second-pass-end n{num_nodes})']
    return plan

def rotate(state_dr, node, rot):
    dr = copy.deepcopy(state_dr)

    for idx in range(node - 1, len(state_dr)):
        dr[idx] = next_direction[(dr[idx], rot)]
    assert(len(state_dr) == len(dr))

    num_nodes = len(state_dr) + 1
    pos = [(num_nodes, num_nodes)]
    for n in range(1, num_nodes):
        direction = dr[n - 1]
        x = pos[-1][0]
        y = pos[-1][1]
        if direction == 'up':
            y += 1
        elif direction == 'down':
            y -= 1
        elif direction == 'left':
            x -= 1
        elif direction == 'right':
            x += 1
        if (x, y) in pos:
            return None, None
        pos += [(x, y)]

    return pos, dr

def _genGoal(num_folds, num_nodes, scenario = 'zigzag'):
    # Initial state
    state_pos = [(num_nodes, num_nodes)]
    state_dir = []
    for i in range(1, num_nodes):
        state_pos += [(num_nodes, state_pos[-1][1] + 1)]
        state_dir += ['up']

    # Select nodes that and the direction of rotation
    nodes = list(range(1, num_nodes))
    random.shuffle(nodes)
    nodes = nodes[:num_folds]
    folds = {}
    for n in nodes:
        if scenario == 'zigzag':
            f = random.choice(['clockwise', 'counterclockwise'])
        elif scenario == 'spiral':
            f = 'clockwise'
        elif scenario == 'bias-spiral':
            f = random.choice(['clockwise', 'clockwise', 'clockwise', 'counterclockwise'])
        else:
            print(f'Error: Unkown scenario {scenario}', file = sys.stderr)
            sys.exit(-1)
        folds[n] = f

    # Apply and generate the plan
    plan = []
    for n in nodes:
        next_pos, next_dir = rotate(state_dir, n, folds[n])
        if next_pos is None:
            return None, None, None
        plan += subplan(state_pos, state_dir, n, folds[n], next_pos, next_dir)
        state_pos = next_pos
        state_dir = next_dir

    img = [[' ' for _ in range(num_nodes * 4)] for __ in range(num_nodes * 4)]
    img[2 * num_nodes][2 * num_nodes] = 'x'
    for n in range(1, num_nodes):
        x = state_pos[n][0]
        y = state_pos[n][1]
        img[2 * y][2 * x] = '.'
    for n in range(0, num_nodes - 1):
        x = state_pos[n][0]
        y = state_pos[n][1]
        direction = state_dir[n]
        if direction == 'up':
            img[2 * y + 1][2 * x] = '|'
        elif direction == 'down':
            img[2 * y - 1][2 * x] = '|'
        elif direction == 'left':
            img[2 * y][2 * x - 1] = '-'
        elif direction == 'right':
            img[2 * y][2 * x + 1] = '-'

    img_out = ''
    img = img[::-1]
    img = [''.join(l).rstrip() for l in img]
    img = [l for l in img if len(l)]
    prefix_len = min([len(l) - len(l.lstrip()) for l in img])
    img = [l[prefix_len:] for l in img]
    img_out = ';; ' + '\n;; '.join(img)
    return state_pos, plan, img_out

def genGoal(num_folds, num_nodes, scenario, max_tries = 5000):
    for i in range(max_tries):
        #print(f'Try {i}...', file = sys.stderr)
        pos, plan, img = _genGoal(num_folds, num_nodes, scenario)
        if pos is not None:
            return pos, plan, img
    return None, None, None

def main(scenario, num_nodes, num_folds, fnpddl, fnplan):
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

    goal_pos, plan, goal_img = genGoal(num_folds, num_nodes, scenario)
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
(define (problem folding-{scenario}-{num_nodes}-{num_folds}-{rand})
(:domain folding)

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
        cost = len([a for a in plan if a.startswith('(rotate ')])
        print(f';; Optimal cost: {cost}', file = fout)
        for p in plan:
            print(p, file = fout)
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print(f'Usage: {sys.argv[0]} scenario length num-folds prob.pddl prob.plan',
              file = sys.stderr)
        print('  scenario: zigzag, spiral, bias-spiral', file = sys.stderr)
        print('''
This script generates a random task based on the given scenario.
The task is generated so that is has a string consisting of {length}
elements and it generates {num-folds} folds (rotations) over randomly
selected sequence of elements of the string. There is at most one rotation
per a string's element so the generated plan should be optimal, but I'm not
completely sure of it.

The scenarios change how the rotations are chosen:
    zigzag: Randomly from (clockwise, counterclockwise)
    spiral: Always choose clockise
    bias-spiral: Randomly from (clockwise, clockwise, clockwise, counterclockwise),
                 i.e., "it prefers spiral by allows some zigzag".
''', file = sys.stderr)
        sys.exit(-1)
    sys.exit(main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]))
