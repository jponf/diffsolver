#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import itertools
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
    print(opts)


def run_gen(opts):
    """Runs the gen sub-command"""
    print("Gen")

def run_test(opts):
    """Runs the test sub-command"""
    print("Test")


def parse_arguments(args):  # TODO Fix this
    """Parses the given arguments"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="---- DESCRIPTION HERE ----",
        epilog="---- EPILOG HERE ----")

    subparsers = parser.add_subparsers(help='sub-command --help')

    parser_gen = subparsers.add_parser('gen',
                                       help='Generates a results file.')
    parser_gen.set_defaults(func=run_gen)

    parser_test = subparsers.add_parser('test',
                                        help='Tests the results of the solver.')
    parser_test.set_defaults(func=run_test)


    parser.add_argument('binary', type=str, action='store',
                        help="Path to the solver executable file.")
    parser.add_argument('workdir', type=str, action='store',
                        help="Directory that contains the instances/results.")
    parser.add_argument('-e', '--ext', type=str, action='store', default='cnf',
                        help="Instance files extension.")
    parser.add_argument('-p', '--parser', choices=['minisat'], required=True,
                        help="Solver results parser-")

    parser.add_argument('--version', action='version',
                        version="Version: {0}".format(__version__))

    return parser.parse_args(args)


##########################
#   Script entry point   #
##########################

if __name__ == '__main__':
    main()
