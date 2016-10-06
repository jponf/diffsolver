# -*- coding: utf-8 -*-

from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from subprocess import Popen, TimeoutExpired, DEVNULL, PIPE


# Rename the appropriate classes and functions
##############################################################################

BrokenPoolException = BrokenProcessPool


# Runner result tuple
##############################################################################

RunnerResult = namedtuple(
    'RunnerResult',
    ['instance', 'exit_status', 'stdout', 'stderr', 'timeout']
)


# Runner class to ease the execution of multiple (solver, instance) pairs
##############################################################################

class Runner:

    def __init__(self, n_jobs, timeout):
        self._executor = ProcessPoolExecutor(max_workers=n_jobs)
        self._timeout = timeout
        self._done_callbacks = []
        self._id = 0

    def run(self, solver, instance):
        f = self._executor.submit(_execute_solver, solver, instance,
                                  self._timeout)
        f.id = self._next_id()
        for fn in self._done_callbacks:
            f.add_done_callback(fn)

        return f

    def add_done_callback(self, fn):
        self._done_callbacks.append(fn)

    def shutdown(self, wait=True):
        self._executor.shutdown(wait=wait)

    def _next_id(self):
        self._id += 1
        return self._id


def _execute_solver(binary, instance, timeout):
    p = Popen([binary, instance],
              stdin=DEVNULL, stdout=PIPE, stderr=PIPE,
              universal_newlines=True)  # Use text pipes
    try:
        out, err = p.communicate(timeout=timeout)
        status = p.wait()

        return RunnerResult(instance=instance, exit_status=status,
                            stdout=out, stderr=err, timeout=False)
    except TimeoutExpired:
        p.kill()
        return RunnerResult(instance=instance, exit_status=p.returncode,
                            stdout="", stderr="", timeout=True)
