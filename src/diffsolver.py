#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import itertools
import os
import os.path
import sys
import threading
import time

from parsers import create_parser, get_parsers_names, serialize_results, \
                    deserialize_results, build_complete_result, \
                    SerializationError, CompleteSolverResult
from runner import BrokenPoolException, Runner


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
_EXIT_INSTDIR_ERR = 3
_EXIT_RESULTS_ERR = 4
_EXIT_RESULTS_INT = 5


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

        opts.func(opts)
    except KeyboardInterrupt:
        print("Interrupted by user ... exiting")
        sys.exit(_EXIT_RESULTS_INT)


# Gen sub-command
##############################################################################

def run_gen(opts):
    """Runs the gen sub-command"""
    print_options_summary(opts)

    if not is_executable(opts.solver):
        print("'%s'" % opts.solver, "is not an executable file ... exiting")
        sys.exit(_EXIT_BINARY_ERR)

    if not opts.instdir or not os.path.isdir(opts.instdir):
        print(opts.instdir, "is not a directory ... exiting")
        sys.exit(_EXIT_INSTDIR_ERR)

    instances = get_instances(opts.instdir, opts.extension)
    results = evaluate_all_instances(opts.solver, instances, opts.parser,
                                     opts.num_jobs, opts.solver_parameters,
                                     opts.timeout)

    if results is not None:
        print("Serializing", len(results), "results")
        solver_name = os.path.basename(opts.solver)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S%z", time.localtime())
        serialized_result = serialize_results(
            results, solver=solver_name, timestamp=timestamp, prettify=True)

        results_file = os.path.join(opts.workdir, solver_name + ".results")
        with open(results_file, 'wt') as f:
            f.write(serialized_result)

    print("Done!")


def evaluate_all_instances(solver, instances, parser, num_jobs,
                           parameters, timeout):
    futures, results = [], {}
    runner = Runner(num_jobs, timeout)
    callback = generate_execution_finished_callback(
        results, parser, get_common_path(instances))

    print("Setting runner task 'has finished' callback")
    runner.add_done_callback(callback)

    try:
        print("Enqueuing and waiting {0} evaluations".format(len(instances)))
        for path in instances:
            futures.append(runner.run(solver, path, parameters))
        runner.shutdown(wait=True)

        print("")
        return results
    except KeyboardInterrupt:
        for f in futures:
            f.cancel()
    finally:
        runner.shutdown(wait=True)

    return None


def generate_execution_finished_callback(results, parser_name, common_path):
    lock = threading.Lock()

    def execution_finished_callback(future):
        try:
            if future.cancelled():
                print("Cancelled {0}".format(future.id))
            else:
                r = future.result()  # concurrent.futures.Future
                parser = create_parser(parser_name)
                if r.timeout:
                    print("Timeout {0}:".format(future.id), r.instance)
                else:
                    print("Success {0}:".format(future.id), r.instance)
                    with lock:
                        name = r.instance.replace(common_path, '', 1)
                        results[name] = build_complete_result(
                            parser.parse(r.output), r.cpu_time)

        except (KeyboardInterrupt, BrokenPoolException):
            print("Execution aborted:", future.id)

    return execution_finished_callback


# Diff sub-command
##############################################################################

def run_diff(opts):
    """Runs the test sub-command"""
    print_options_summary(opts)

    results1 = load_results_file_or_exit(opts.results1)
    results2 = load_results_file_or_exit(opts.results2)
    num_different, num_equal, cpu_time1, cpu_time2 = 0, 0, 0.0, 0.0

    all_instances = list(results1.keys() | results2.keys())
    for instance in all_instances:
        if instance in results1.keys() and instance in results2.keys():
            r1, r2 = results1[instance], results2[instance]

            diff = compute_results_differences(r1, r2, opts.comp_fields)
            if diff:
                num_different += 1
                print("-- DIFFERENT:", instance)
                print_results_comparison(diff)
            else:
                num_equal += 1
                cpu_time1 += r1.cpu_time
                cpu_time2 += r2.cpu_time
                print("++ EQUAL:", instance)
                to_show = list(zip(opts.show_fields,
                                   r1.extract_fields(opts.show_fields),
                                   r2.extract_fields(opts.show_fields)))
                print_results_comparison(to_show)
        elif instance in results1.keys():
            print(":: Only in results 1:", instance)
        elif instance in results2.keys():
            print(":: Only in results 2:", instance)
        else:
            print("WTF:", instance)

    print("")
    print("*** # Results on 1:", len(results1), "***")
    print("*** # Results on 2:", len(results2), "***")
    print("*** # Equal results:", num_equal, "***")
    print("*** # Different results:", num_different, "***")
    print("*** Avg time for equal results (1):",
          cpu_time1 / num_equal if num_equal > 0 else "--", "***")
    print("*** Avg time for equal resutls (2):",
          cpu_time2 / num_equal if num_equal > 0 else "--", "***")


#######################
#   Utility methods   #
#######################

def get_instances(directory, extension):
    """Gather all the instances from the working directory."""
    instances = []
    dot_ext = "." + extension

    for root, dirs, files in os.walk(directory):
        instances.extend(os.path.join(root, f)
                         for f in files if f.endswith(dot_ext))
    return instances


def load_results_file_or_exit(file_path):
    try:
        with open(file_path, "rt") as f:
            return deserialize_results(f.read())
    except FileNotFoundError:
        print("File not found: %s" % file_path)
        sys.exit(_EXIT_RESULTS_ERR)
    except IOError as e:
        print("Error reading %s:" % file_path, e)
    except SerializationError as e:
        print("Error loading %s:" % file_path, e)
        sys.exit(_EXIT_RESULTS_ERR)


def is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


def get_common_path(paths):  # os.path.commonpath requires 3.5+
    common_prefix = os.path.commonprefix(paths)
    return os.path.join(os.path.dirname(common_prefix), '')


def print_options_summary(opts):
    opts_nv = [(n, v) for n, v in opts.__dict__.items() if n != "func"]

    req_len = max(len(n) for n, v in opts_nv)
    fmt_str = '- {0:>' + str(req_len) + '}:'

    print("==== OPTIONS ====")
    for name, value in opts_nv:
        print(fmt_str.format(name), value)
    print("=================")
    print("")


def compute_results_differences(results1, results2, comp_fields):
    differences = []
    for attr in comp_fields:
        val_1 = getattr(results1, attr)
        val_2 = getattr(results2, attr)
        if val_1 != val_2:
            differences.append((attr, val_1, val_2))

    return differences


def print_results_comparison(attr_values):
    for attr, val_1, val_2 in attr_values:
        print("***", attr)
        print("   -- 1:", val_1)
        print("   -- 2:", val_2)


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

    subparsers = parser.add_subparsers(help='Possible options are:',
                                       dest='command')
    subparsers.required = True

    # **** Subparsers shared arguments ****
    base_subparser = argparse.ArgumentParser(add_help=False)

    base_subparser.add_argument('-w', '--workdir', type=str,
                                default=os.getcwd(),
                                help="Directory where to write output files.")

    # **** Subparser (sub-command) "GEN" ****
    parser_gen = subparsers.add_parser('gen', parents=[base_subparser],
                                       help='Generates a results file.')
    parser_gen.add_argument('solver', type=str, action='store',
                            help="Path to the solver executable file.")

    parser_gen.add_argument('-sp', '--solver_parameters', nargs='*',
                            default=[],
                            help='Parameters to be passed to the solver')

    parser_gen.add_argument('-e', '--extension', type=str, action='store',
                            default='cnf', help="Instance files extension.")

    parser_gen.add_argument('-i', '--instdir', type=str, action='store',
                            help="Directory that contains the instances.")

    parser_gen.add_argument('-j', '--num_jobs', type=int,
                            default=1, help="Number of parallel executions.")

    parser_gen.add_argument('-p', '--parser', required=True,
                            choices=get_parsers_names(),
                            help="Solver results parser.")

    parser_gen.add_argument('-t', '--timeout', type=int, default=30,
                            help="Evaluations timeout in seconds.")

    parser_gen.set_defaults(func=run_gen)

    # **** Subparser (sub-command) "DIFF" ****
    parser_diff = subparsers.add_parser('diff', parents=[base_subparser],
                                        help='Tests a solver.')

    parser_diff.add_argument('results1', action='store',
                             help="First results to compare.")

    parser_diff.add_argument('results2', action='store',
                             help="Second results to compare.")

    parser_diff.add_argument('-cf', '--comp_fields', nargs='+',
                             action=MultipleChoicesAction,
                             choices=CompleteSolverResult.fields,
                             default=CompleteSolverResult.fields,
                             help="Result fields to compare. Valid Options "
                                  "are: {%s}" % ", "
                                  .join(CompleteSolverResult.fields),
                             metavar='fields')

    parser_diff.add_argument('-sf', '--show_fields', nargs='*',
                             action=MultipleChoicesAction,
                             choices=CompleteSolverResult.fields,
                             default=[],  # Otherwise it's None
                             help="Solver result fields shown when the compared"
                                  " fields are equal. Valid Options"
                                  " are: {%s}" % ", "
                                  .join(CompleteSolverResult.fields),
                             metavar='fields')

    parser_diff.set_defaults(func=run_diff)

    return parser.parse_args(args)


##########################
#   Script entry point   #
##########################

if __name__ == '__main__':
    main()
