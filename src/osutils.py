# -*- coding: utf-8 -*-

import os
import platform


# TODO check java and other kind of interpreters
OS_WINDOWS_NAMES = {'nt'}   # Cygwin reports posix (check)
OS_LINUX_NAMES = {'posix'}
OS_MAC_NAMES = {'posix'}

PLATFORM_WINDOWS_SYS = {'Windows'}
PLATFORM_LINUX_SYS = {'Linux'}
PLATFORM_MAC_SYS = {'Darwin'}


def is_windows():
    return os.name in OS_WINDOWS_NAMES and \
        platform.system() in PLATFORM_WINDOWS_SYS


def is_linux():
    return os.name in OS_LINUX_NAMES and \
        platform.system() in PLATFORM_LINUX_SYS


def is_mac():
    return os.name in OS_MAC_NAMES and \
        platform.system() in PLATFORM_MAC_SYS


def is_posix():  # TODO more exhaustive mechanism
    return os.name == 'posix' or is_linux() or is_mac()


if is_windows():

    # Check constants at:
    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms684880%28v=vs.85%29.aspx
    PROCESS_CREATE_PROCESS = 0x0080
    PROCESS_CREATE_THREAD = 0x0002
    PROCESS_DUP_HANDLE = 0x0040
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    PROCESS_SET_INFORMATION = 0x0200
    PROCESS_SET_QUOTA = 0x0100
    PROCESS_SUSPEND_RESUME = 0x0800
    PROCESS_TERMINATE = 0x0001
    PROCESS_VM_OPERATION = 0x0008
    PROCESS_VM_READ = 0x0010
    PROCESS_VM_WRITE = 0x0020

    DELETE = 0x00010000
    READ_CONTROL = 0x00020000
    SYNCHRONIZE = 0x00100000
    WRITE_DAC = 0x00040000
    WRITE_OWNER = 0x00080000
