#!/usr/bin/env python3

import sys
import os
import random

TOPDIR = os.path.dirname(os.path.realpath(__file__))
GEN = os.path.join(TOPDIR, 'generate.py')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} num-tasks', file = sys.stderr)
        print('''
This script calls the generate.py script num-tasks times with random
parameters. The names of the resulting .pddl and .plan files are
p-{scenario}-{length-of-string}-{number-of-folds}.*
''', file = sys.stderr)
        sys.exit(-1)

    for _ in range(int(sys.argv[1])):
        length = random.randint(8, 64)
        folds = random.randint(1, length - 1)
        scenario = random.choice(['zigzag', 'spiral', 'bias-spiral'])
        print(f'SCENARIO {scenario} LENGHT {length} FOLDS {folds}')
        fn = 'p-{0}-{1:02d}-{2:02d}'.format(scenario, length, folds)
        if os.path.isfile(fn + '.pddl'):
            print(f'Already have {fn}.pddl')
            continue

        cmd = f'python3 {GEN} {scenario} {length} {folds} {fn}.pddl {fn}.plan'
        print(cmd)
        os.system(cmd)

