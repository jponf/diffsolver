#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import collections
import itertools
import os
import os.path
import subprocess as sp
import sys
import time

import parsers
import testdata


##############################
#   Authorship Information   #
##############################

__author__ = "Josep Pon Farreny"
__copyright__ = "Copyright 2016, Josep Pon Farreny"
__credits__ = ["Josep Pon Farreny"]

__license__ = "GPL"
__version__ = "0.1a"
__maintainer__ = "Josep Pon Farreny"
__email__ = ""
__status__ = "Development"


########################
#   Module Constants   #
########################

_EXIT_BINARY_ERR = 1
_EXIT_WORKDIR_ERR = 2
_EXIT_RESULTS_ERR = 3


###############################################
#   Test Solver Main and Commands Functions   #
###############################################

def main():
    """Test Solver entry function"""
    opts = parse_arguments(itertools.islice(sys.argv, 1, None))

    if not os.path.isdir(opts.workdir):
        print(opts.workdir, "is not a directory ... exiting")
        sys.exit(_EXIT_WORKDIR_ERR)

    find_and_fix_binary_path(opts)
    if not is_executable(opts.binary):
        print(opts.binary, "is not an executable file ... exiting")
        sys.exit(_EXIT_BINARY_ERR)

    instances = get_instances(opts)
    opts.func(opts, instances)


def run_gen(opts, instances):
    """Runs the gen sub-command"""
    print_options_summary(opts)

    results = collections.OrderedDict()  # Preserve loop's order
    for inst, path in instances:
        print("Generating:", inst)
        out, err = execute_solver(opts.binary, path)

        parser = parsers.create(opts.parser)
        results[inst] = parser.parse(out)

    solver_name = os.path.basename(opts.binary)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S%z", time.localtime())

    serialized_result = testdata.serialize_results(
        results, solver=solver_name, timestamp=timestamp, prettify=True)

    results_file = os.path.join(opts.workdir, solver_name + ".results")
    with open(results_file, 'wt') as f:
        f.write(serialized_result)


def run_test(opts, instances):
    """Runs the test sub-command"""
    find_and_fix_results_path(opts)
    print_options_summary(opts)

    results = load_results_file_or_exit(opts)
    for inst, path in instances:
        if inst not in results:
            print("Ignoring", inst, ". Not present in results")
        else:
            out, err = execute_solver(opts.binary, path)

            parser = parsers.create(opts.parser)
            r = parser.parse(out)

            if results[inst] == parser.get_result():
                print(inst, "- EQUAL")
            else:
                print(inst, "- DIFFERENT")


#######################
#   Utility methods   #
#######################

def get_instances(opts):
    """Gather all the instances from the working directory."""
    instances = []
    for root, dirs, files in os.walk(opts.workdir):
        instances.extend((f, os.path.join(root, f))
                         for f in files if f.endswith(opts.ext))
    return instances


def load_results_file_or_exit(opts):
    try:
        with open(opts.results, "rt") as f:
            return testdata.deserialize_results(f.read())
    except (FileNotFoundError, IOError) as e:
        print("Unable to read %s:" % opts.results, e)
        sys.exit(_EXIT_RESULTS_ERR)
    except testdata.SerializationError as e:
        print("Error loading results file:", e)
        sys.exit(_EXIT_RESULTS_ERR)


def find_and_fix_binary_path(opts):
    """Checks if the binary path is ok.

    If the path does not point to a valid executable file it looks for it
    in the user specified working directory.
    """
    if not is_executable(opts.binary):
        workdir_path = os.path.join(opts.workdir, opts.binary)
        if is_executable(workdir_path):
            opts.binary = workdir_path


def find_and_fix_results_path(opts):
    """Checks if the results path is ok.

    If the path does not point to a valid file it looks for it in the
    user specified working directory.
    """
    if not os.path.isfile(opts.results):
        workdir_path = os.path.join(opts.workdir, opts.results)
        workdir_path_ext = workdir_path + ".results"
        if os.path.is_file(workdir_path):
            opts.results = workdir_path
        elif os.path.is_file(workdir_path_ext):
            opts.results = workdir_path_ext


def is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


def print_options_summary(opts):
    print("==== OPTIONS ====")
    print("= Work Directory:", opts.workdir)
    print("= Solver Binary:", opts.binary)
    print("= Instances Ext:", opts.ext)
    print("= Result Parser:", opts.parser)
    if hasattr(opts, 'results'):
        print("= Results File:", opts.results)
    print("=================")
    print("")


def execute_solver(binary, instance):
    #progress_sequence = ['|', '/', '--', '\']
    #progress_index = 0

    p = sp.Popen([binary, instance],
                 stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.PIPE,
                 universal_newlines=True)  # Use text pipes

    #if sys.stdout.isatty():
    out, err = p.communicate()
    p.wait()
    return out, err


########################
#   Argument Parsing   #
########################

def parse_arguments(args):
    """Parses the given arguments.

    It creates several subparsers, one for each possible command and sets
    the 'func' attribute according to the selected command.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="",
        epilog="")

    parser.add_argument('--version', action='version',
                    version="Version: {0}".format(__version__))

    # **** Subparsers shared arguments ****
    base_subparser = argparse.ArgumentParser(add_help=False)

    base_subparser.add_argument('workdir', type=str, action='store',
                                help="Directory that contains the instances "
                                     " and result files.")

    base_subparser.add_argument('binary', type=str, action='store',
                                help="Path to the solver executable file.")

    base_subparser.add_argument('-e', '--ext', type=str, action='store',
                                default='cnf', help="Instance files extension.")

    #base_subparser.add_argument('-D', '--debug', action='store_true',
    #                            help="Enables debugging output")

    base_subparser.add_argument('-p', '--parser', choices=parsers.get_names(),
                                required=True, help="Solver results parser.")

    # **** Subparsers (sub-commands) ****
    subparsers = parser.add_subparsers(help='Possible options are:',
                                       metavar='command')
    subparsers.required = True

    parser_gen = subparsers.add_parser('gen', parents=[base_subparser],
                                       help='Generates a results file.')
    parser_gen.set_defaults(func=run_gen)

    parser_test = subparsers.add_parser('test', parents=[base_subparser],
                                        help='Tests a solver.')
    parser_test.add_argument('-r', '--results', type=str, action='store',
                             required=True, help="Results to compare.")
    parser_test.set_defaults(func=run_test)

    return parser.parse_args(args)


##########################
#   Script entry point   #
##########################

if __name__ == '__main__':
    main()
