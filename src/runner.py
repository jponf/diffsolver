# -*- coding: utf-8 -*-

from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from subprocess import Popen, DEVNULL, PIPE
from threading import Timer

import errno
import os

import osutils

if osutils.is_windows():
    import ctypes


# Rename the appropriate classes and functions
##############################################################################

BrokenPoolException = BrokenProcessPool


# Runner result tuple
##############################################################################

RunnerResult = namedtuple(
    'RunnerResult',
    ['instance', 'exit_status', 'output', 'timeout', 'cpu_time', 'sys_time']
)


# Runner class to ease the execution of multiple (solver, instance) pairs
##############################################################################

class Runner:

    def __init__(self, n_jobs, timeout):
        self._executor = ProcessPoolExecutor(max_workers=n_jobs)
        self._timeout = timeout
        self._done_callbacks = []
        self._id = 0

    def run(self, solver, instance, parameters=()):
        f = self._executor.submit(_execute_solver, solver, instance,
                                  parameters, self._timeout)
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
    old_cwd = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(binary)))

    p = Popen([binary, instance],
              stdin=DEVNULL, stdout=PIPE, stderr=STDOUT,
def _execute_solver(binary, instance, parameters, timeout):
    command = [binary]
    command.extend(parameters)
    command.append(instance)

    p = Popen(command, stdin=DEVNULL, stdout=PIPE, stderr=DEVNULL,
              universal_newlines=True) # Use text pipelines
    handle = _get_subprocess_handle(p)

    p.timeout = False
    output, cpu_time, sys_time = "", -1, -1

    t = Timer(timeout, _timeout_callback, [p])
    t.start()

    try:
        line = p.stdout.readline()
        while line:
            output += line
            line = p.stdout.readline()
    finally:
        t.cancel()
        t.join()

    if not p.timeout:
        cpu_time, sys_time = _wait_and_get_execution_time(handle)

    os.chdir(old_cwd)

    return RunnerResult(instance=instance, exit_status=p.returncode,
                        output=output, timeout=p.timeout,
                        cpu_time=cpu_time, sys_time=sys_time)


def _timeout_callback(process):
    if process.poll() is None:
        try:
            process.kill()
            process.timeout = True
        except OSError as e:
            if e.errno != errno.ESRCH:
                raise


##############################################################################
# OS Utility functions
##############################################################################

def _get_subprocess_handle(process):
    if osutils.is_posix():
        return process.pid
    elif osutils.is_windows():
        access_rights = osutils.PROCESS_QUERY_INFORMATION \
                      | osutils.SYNCHRONIZE

        return ctypes.windll.kernel32.OpenProcess(access_rights, 0,
                                                  process.pid)
    else:
        raise NotImplementedError("Your OS is not supported")


def _wait_and_get_execution_time(handle):
    if osutils.is_posix():
        return _posix_wait_and_get_execution_time(handle)
    elif osutils.is_windows():
        return _windows_wait_and_get_execution_time(handle)
    else:
        raise NotImplementedError("Your OS is not supported")


def _posix_wait_and_get_execution_time(handle):
    _, _, rusage = os.wait4(handle, 0)
    return rusage.ru_utime, rusage.ru_stime


def _windows_wait_and_get_execution_time(handle):
    file_time_t = ctypes.wintypes.FILETIME
    uf_time, sf_time, dummy = file_time_t(), file_time_t(), file_time_t()

    ctypes.windll.kernel32.WaitForSingleObject(handle, ctypes.c_int(-1))

    ctypes.windll.kernel32.GetProcessTimes(
        handle, ctypes.byref(dummy), ctypes.byref(dummy),
        ctypes.byref(sf_time), ctypes.byref(uf_time))

    # time is expressed in units of 100 nanoseconds
    utime = (uf_time.dwHighDateTime << 32 + uf_time.dwLowDateTime) / 10**7
    stime = (sf_time.dwHighDateTime << 32 + sf_time.dwLogDateTime) / 10**7

    ctypes.windll.kernel32.CloseHandle(handle)

    return utime, stime
