# -*- coding: utf-8 -*-

from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor, wait
from concurrent.futures.process import BrokenProcessPool
from subprocess import Popen, DEVNULL, PIPE


# Rename the appropriate classes and functions
##############################################################################

BrokenPoolException = BrokenProcessPool
wait_futures = wait


# Runner result tuple
##############################################################################

RunnerResult = namedtuple(
    'RunnerResult',
    ['instance', 'exit_status', 'stdout', 'stderr']
)


# Runner class to ease the execution of multiple (solver, instance) pairs
##############################################################################


class Runner:

    def __init__(self, n_jobs):
        self._executor = ProcessPoolExecutor(max_workers=n_jobs)
        self._done_callbacks = []
        self._id = 0

    def run(self, solver, instance):
        f = self._executor.submit(_execute_solver, solver, instance)
        f.id = self._next_id()
        for fn in self._done_callbacks:
            f.add_done_callback(fn)

        return f

    def add_done_callback(self, fn):
        self._done_callbacks.append(fn)

    def _next_id(self):
        self._id += 1
        return self._id


def _execute_solver(binary, instance):
    p = Popen([binary, instance],
              stdin=DEVNULL, stdout=PIPE, stderr=PIPE,
              universal_newlines=True)  # Use text pipes

    out, err = p.communicate()
    status = p.wait()

    return RunnerResult(instance=instance, exit_status=status,
                        stdout=out, stderr=err)
