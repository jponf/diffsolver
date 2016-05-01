#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import itertools
import os.path
import sys


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

    opts.func(opts)


def run_gen(opts):
    """Runs the gen sub-command"""
    print("Gen")


def run_test(opts):
    """Runs the test sub-command"""
    print("Test")


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

    base_subparser.add_argument('-p', '--parser', choices=['minisat'],
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
