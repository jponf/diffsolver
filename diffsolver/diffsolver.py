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

from parsers import create_parser, get_parsers_names, serialize_results, \
                    deserialize_results, SolverResult


##############################
#   Authorship Information   #
##############################

__author__ = "Josep Pon Farreny"
__copyright__ = "Copyright 2016, Josep Pon Farreny"
__credits__ = ["Josep Pon Farreny"]

__license__ = "GPL"
__version__ = "0.2"
__maintainer__ = "Josep Pon Farreny"
__email__ = ""
__status__ = "Development"


########################
#   Module Constants   #
########################

_EXIT_BINARY_ERR = 1
_EXIT_WORKDIR_ERR = 2
_EXIT_RESULTS_ERR = 3
_EXIT_RESULTS_INT = 4


###############################################
#   Test Solver Main and Commands Functions   #
###############################################

def main():
    """Test Solver entry function"""
    try:
        opts = parse_arguments(itertools.islice(sys.argv, 1, None))

        if not os.path.isdir(opts.workdir):
            print(opts.workdir, "is not a directory ... exiting")
            sys.exit(_EXIT_WORKDIR_ERR)

        find_and_fix_binary_path(opts)
        if not is_executable(opts.binary):
            print(opts.binary, "is not an executable file ... exiting")
            sys.exit(_EXIT_BINARY_ERR)

        instances = [x for x in get_instances(opts) if "blocks-blocks-36-0.130-NOTKNOWN.cnf" == x[0]]

        opts.func(opts, instances)
    except KeyboardInterrupt:
        print("Interrupted by user ... exiting")
        sys.exit(_EXIT_RESULTS_INT)


def run_gen(opts, instances):
    """Runs the gen sub-command"""
    print_options_summary(opts)

    results = collections.OrderedDict()  # Preserve loop's order
    for inst, path in instances:
        print("Generating:", inst)
        status, out, err = execute_solver(opts.binary, path)

        parser = parsers.create_parser(opts.parser)
        results[inst] = parser.parse(out)

    solver_name = os.path.basename(opts.binary)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S%z", time.localtime())

    serialized_result = serialize_results(
        results, solver=solver_name, timestamp=timestamp, prettify=True)

    results_file = os.path.join(opts.workdir, solver_name + ".results")
    with open(results_file, 'wt') as f:
        f.write(serialized_result)


def run_diff(opts, instances):
    """Runs the test sub-command"""
    find_and_fix_results_path(opts)
    print_options_summary(opts)

    num_different = 0
    results = load_results_file_or_exit(opts)

    for inst, path in instances:
        if inst not in results:
            print("++ Ignoring", inst, ". Not present in results")
        else:
            print("++ Executing", inst, end='', flush=True)
            status, out, err = execute_solver(opts.binary, path)

            parser = create_parser(opts.parser)
            result = parser.parse(out)
            expected = results[inst]

            differences = compute_results_differences(opts, expected, result)
            if differences:
                print(" -- DIFFERENT")
                num_different += 1
                print_results_comparison(differences)
            else:
                print(" -- EQUAL")
                print_results_comparison(
                    (attr, getattr(expected, attr), getattr(result, attr))
                    for attr in opts.show_fields)

    print("")
    print("***", num_different, "different results found. ***")


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
            return deserialize_results(f.read())
    except (FileNotFoundError, IOError) as e:
        print("Unable to read %s:" % opts.results, e)
        sys.exit(_EXIT_RESULTS_ERR)
    except parsers.SerializationError as e:
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
        if os.path.isfile(workdir_path):
            opts.results = workdir_path
        elif os.path.isfile(workdir_path_ext):
            opts.results = workdir_path_ext


def is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


def print_options_summary(opts):
    print("==== OPTIONS ====")
    print("= Work Directory:", opts.workdir)
    print("= Solver Binary:", opts.binary)
    print("= Instances Ext:", opts.ext)
    print("= Result Parser:", opts.parser)
    if hasattr(opts, 'comp_fields'):
        print("= Compare Fields:", opts.comp_fields)
    if hasattr(opts, 'show_fields'):
        print("= Show Fields:", opts.show_fields)
    if hasattr(opts, 'results'):
        print("= Results File:", opts.results)
    print("=================")
    print("")


def execute_solver(binary, instance):
    p = sp.Popen([binary, instance],
                 stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.PIPE,
                 universal_newlines=True)  # Use text pipes

    out, err = p.communicate()
    status = p.wait()
    return status, out, err


def compute_results_differences(opts, expected, result):
    differences = []
    for attr in opts.comp_fields:
        val_e = getattr(expected, attr)
        val_r = getattr(result, attr)
        if val_e != val_r:
            differences.append((attr, val_e, val_r))

    return differences


def print_results_comparison(attr_values):
    for attr, val_e, val_r in attr_values:
        print("**", attr)
        print("   -- Exp:", val_e)
        print("   -- Res:", val_r)


########################
#   Argument Parsing   #
########################

class MultipleChoicesAction(argparse.Action):

    def __init__(self, option_strings, choices, **kwargs):
        super().__init__(option_strings, choices=choices, **kwargs)
        if not self.choices:
            raise AttributeError("At least one choice is required")

    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            for value in values:
                if value not in self.choices:
                    choices_str = ", ".join((repr(a) for a in self.choices))
                    message = "invalid choice: {0} (choose from {1})"\
                              .format(value, choices_str)
                    raise argparse.ArgumentError(self, message)

            setattr(namespace, self.dest, values)


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

    base_subparser.add_argument('-p', '--parser', choices=get_parsers_names(),
                                required=True, help="Solver results parser.")

    # **** Subparser (sub-command) "GEN" ****
    subparsers = parser.add_subparsers(help='Possible options are:',
                                       metavar='command')
    subparsers.required = True

    parser_gen = subparsers.add_parser('gen', parents=[base_subparser],
                                       help='Generates a results file.')
    parser_gen.set_defaults(func=run_gen)

    # **** Subparser (sub-command) "DIFF" ****
    parser_diff = subparsers.add_parser('diff', parents=[base_subparser],
                                        help='Tests a solver.')

    parser_diff.add_argument('-cf', '--comp_fields', nargs='+',
                             action=MultipleChoicesAction,
                             choices=SolverResult.fields,
                             default=SolverResult.fields,
                             help="Result fields to compare. Valid Options "
                                  "are: {%s}" % ", ".join(SolverResult.fields),
                             metavar='fields')

    parser_diff.add_argument('-sf', '--show_fields', nargs='*',
                             action=MultipleChoicesAction,
                             choices=SolverResult.fields,
                             default=[],  # Otherwise it's None
                             help="Solver result fields shown when the compared"
                                  " fields are equal. Valid Options"
                                  " are: {%s}" % ", ".join(SolverResult.fields),
                             metavar='fields')

    parser_diff.add_argument('-r', '--results', type=str, action='store',
                             required=True, help="Results to compare.")
    parser_diff.set_defaults(func=run_diff)

    return parser.parse_args(args)


##########################
#   Script entry point   #
##########################

if __name__ == '__main__':
    main()
