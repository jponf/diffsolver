#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import abc
import re

import testdata


##############################
#   Authorship Information   #
##############################

__author__ = "Josep Pon Farreny"
__copyright__ = "Copyright 2016, Josep Pon Farreny"
__credits__ = ["Josep Pon Farreny"]


#########################
#   Factory Utilities   #
#########################

_parsers_registry = {}

def create(name):
    return _parsers_registry[name]()

def get_names():
    return list(_parsers_registry.keys())

def register_parser(name, parser_cls):
    _parsers_registry[name] = parser_cls


#######################
#   Abstract Parser   #
#######################

class AbstractSolverParser(metaclass=abc.ABCMeta):
    """All subclasses must provide an empty or default initialized __init__
    method.
    """

    @abc.abstractproperty
    def conflicts(self):
        raise NotImplementedError("Abstract property.")

    @abc.abstractproperty
    def decisions(self):
        raise NotImplementedError("Abstract property.")

    @abc.abstractproperty
    def optimum(self):
        raise NotImplementedError("Abstract property.")

    @abc.abstractproperty
    def propagations(self):
        raise NotImplementedError("Abstract property.")

    @abc.abstractproperty
    def restarts(self):
        raise NotImplementedError("Abstract property.")

    @abc.abstractproperty
    def solution(self):
        raise NotImplementedError("Abstract property.")

    @abc.abstractmethod
    def parse(self, text):
        raise NotImplementedError("Abstract method.")

    def get_result(self):
        return testdata.SolverResult(
            conflicts=self.conflicts, decisions=self.decisions,
            optimum=self.optimum, propagations=self.propagations,
            restarts=self.restarts, solution=self.solution
        )


######################
#   MiniSat Parser   #
######################

_MINISAT_CONF_RE = re.compile(r'conflicts\s*:\s*(\d+)[\s\S]*')
_MINISAT_DECS_RE = re.compile(r'decisions\s*:\s*(\d+)[\s\S]*')
_MINISAT_PROPS_RE = re.compile(r'propagations\s*:\s*(\d+)[\s\S]*')
_MINISAT_RESTARTS_RE = re.compile(r'restarts\s*:\s*(\d+)[\s\S]*')
_MINISAT_SOL_RE = re.compile(r'(INDETERMINATE|(?:UN)?SATISFIABLE)\s*')


class MiniSatParser(AbstractSolverParser):

    def __init__(self):
        self._conflicts = -1
        self._decisions = -1
        self._propagations = -1
        self._restarts = -1
        self._solution = "INDETERMINATE"

    @property
    def conflicts(self):
        return self._conflicts

    @property
    def decisions(self):
        return self._decisions

    @property
    def optimum(self):
        return -1

    @property
    def propagations(self):
        return self._propagations

    @property
    def restarts(self):
        return self._restarts

    @property
    def solution(self):
        return self._solution

    def parse(self, text):
        conf_match = _MINISAT_CONF_RE.search(text)
        decs_match = _MINISAT_DECS_RE.search(text)
        props_match = _MINISAT_PROPS_RE.search(text)
        restarts_match = _MINISAT_RESTARTS_RE.search(text)
        solution_match = _MINISAT_SOL_RE.search(text)

        if conf_match:
            self._conflicts = int(conf_match.group(1))
        if decs_match:
            self._decisions = int(decs_match.group(1))
        if props_match:
            self._propagations = int(props_match.group(1))
        if restarts_match:
            self._restarts = int(restarts_match.group(1))
        if solution_match:
            self._solution = solution_match.group(1)


#
# Register MiniSat Parser Class
register_parser('minisat', MiniSatParser)
