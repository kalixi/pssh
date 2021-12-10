# Copyright (c) 2018, Jeffrey Lund

import itertools
import os

NODE_NUM = int(os.environ.get('PSSH_NODENUM', '0'))
NUM_NODES = int(os.environ.get('PSSH_NUMNODES', '1'))


def pardo(xs):
    """
    Helper function for splitting up work using pssh. Assuming the
    environmental variables PSSH_NODENUM and PSSH_NUMNODES are set, will yield
    only the subset of xs which corespond to this node's work. If these
    variables are not set, then every value of xs will be yielded.
    """
    task_no = -1
    for i, x in enumerate(xs):
        task_no += 1
        if task_no % NUM_NODES != NODE_NUM:
            continue
        yield x


def prange(*args):
    """
    A shortcut for pardo(range(*args)).
    """
    yield from pardo(range(*args))


def penumerate(iterable, start=0):
    """
    A shortchut for pardo(enumerate(iterable, start=start)).
    """
    yield from pardo(enumerate(iterable, start=start))


def pproduct(*iterables, repeat=1):
    """
    A shortcut for pardo(itertools.product(*iterables, repeat=repeat)).
    """
    yield from pardo(itertools.product(*iterables, repeat=repeat))
