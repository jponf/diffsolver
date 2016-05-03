#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import itertools
import os
import os.path
import subprocess as sp
import sys

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
#   Module Functions   #
########################

def main():
    """Test Solver entry function"""
    opts = parse_arguments(itertools.islice(sys.argv, 1, None))

    if not os.path.isfile(opts.binary) or not os.access(opts.binary, os.X_OK):
        print(opts.binary, "is not an executable file ... exiting")
        sys.exit(1)

    if not os.path.isdir(opts.workdir):
        print(opts.workdir, "is not a directory ... exiting")
        sys.exit(1)

    instances = get_instances(opts)
    opts.func(opts, instances)


def run_gen(opts, instances):
    """Runs the gen sub-command"""

    results = {}
    for inst, path in instances:
        print("Generating:", inst)
        p = sp.Popen([opts.binary, path],
                     stdin=sp.DEVNULL, stdout=sp.PIPE, stderr=sp.PIPE,
                     universal_newlines=True)  # Use text pipes

        out, err = p.communicate()
        p.wait()

        parser = parsers.create(opts.parser)
        parser.parse(out)
        results[inst] = parser.get_result()

    serialized_result = testdata.serialize_results(
        results, solver=os.path.basename(opts.binary),
        timestamp=str(datetime.datetime.now()),
        prettify=True
    )
    results_file = os.path.join(opts.workdir,
                                os.path.basename(opts.binary) + ".results")

    with open(results_file, 'wt') as f:
        f.write(serialized_result)


def run_test(opts, instances):
    """Runs the test sub-command"""
    print("Running test ...")
    print(instances)


def get_instances(opts):
    """Gather all the instances from the working directory."""
    instances = []
    for root, dirs, files in os.walk(opts.workdir):
        instances.extend((f, os.path.join(root, f))
                         for f in files if f.endswith(opts.ext))
    return instances


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

    base_subparser.add_argument('binary', type=str, action='store',
                                help="Path to the solver executable file.")

    base_subparser.add_argument('workdir', type=str, action='store',
                                help="Directory that contains the instances "
                                     " and result files.")

    base_subparser.add_argument('-e', '--ext', type=str, action='store',
                                default='cnf', help="Instance files extension.")

    base_subparser.add_argument('-d', '--debug', action='store_true',
                                help="Enables debugging output")

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
    parser_test.set_defaults(func=run_test)

    return parser.parse_args(args)


##########################
#   Script entry point   #
##########################

if __name__ == '__main__':
    main()
