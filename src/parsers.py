#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Add new parsers at the end of this file.
#

import abc
import collections
import re
import xml.etree.ElementTree as et
import xml.dom.minidom


##############################
#   Authorship Information   #
##############################

__author__ = "Josep Pon Farreny"
__copyright__ = "Copyright 2016, Josep Pon Farreny"
__credits__ = ["Josep Pon Farreny"]


#########################
#   Exception Classes   #
#########################

class SerializationError(Exception):
    """Raised when (de)serializing incorrectly formatted data."""


####################
#   SolverResult   #
####################

SolverResult = collections.namedtuple(
    'SolverResult',
    ['conflicts', 'decisions', 'optimum',
     'propagations', 'restarts', 'solution']
)

SolverResult.fields = SolverResult._fields


_XML_INSTANCE_TAG = 'instance'
_XML_CONFLICTS_TAG = 'conflicts'
_XML_DECISIONS_TAG = 'decisions'
_XML_OPTIMUM_TAG = 'optimum'
_XML_PROPAGATIONS_TAG = 'propagations'
_XML_RESTARTS_TAG = 'restarts'
_XML_RESULTS_TAG = 'results'
_XML_RESULT_TAG = 'result'
_XML_SOLUTION_TAG = 'solution'
_XML_SOLVER_TAG = 'solver'
_XML_TIMESTAMP_TAG = 'timestamp'


def deserialize_results(serialized_str):
    """Deserializes the results from the given string.

    :param data: An XML formatted string with the serialized results.
    :return: A dictionary with the mapping, instnce_name -> SolverResult.
    """
    try:
        root = et.fromstring(serialized_str)
    except et.ParseError as e:
        raise SerializationError(str(e))

    if root.tag != _XML_RESULTS_TAG:
        raise SerializationError('Root tag must be %s' % _XML_RESULT_TAG)

    results = collections.OrderedDict()
    for r in root.findall(_XML_RESULT_TAG):
        instance, result = _deserilize_result(r)
        results[instance] = result
    return results


def serialize_results(results, solver="", timestamp="", prettify=False):
    """Serializes the results into an XML formatted string.

    :param results: A dictionary whose keys are instance paths and their
                    values SolverResult instances.
    :param prettify: Whether the resulting XML must be human readable.

    :return: An XML formatted string with the provided results.
    """
    root = et.Element(_XML_RESULTS_TAG)

    if solver:
        et.SubElement(root, _XML_SOLVER_TAG).text = solver
    if timestamp:
        et.SubElement(root, _XML_TIMESTAMP_TAG).text = timestamp

    for inst, r in results.items():
        result = et.SubElement(root, _XML_RESULT_TAG)

        et.SubElement(result, _XML_INSTANCE_TAG).text = inst
        et.SubElement(result, _XML_CONFLICTS_TAG).text = str(r.conflicts)
        et.SubElement(result, _XML_DECISIONS_TAG).text = str(r.decisions)
        et.SubElement(result, _XML_OPTIMUM_TAG).text = str(r.optimum)
        et.SubElement(result, _XML_PROPAGATIONS_TAG).text = str(r.propagations)
        et.SubElement(result, _XML_RESTARTS_TAG).text = str(r.restarts)
        et.SubElement(result, _XML_SOLUTION_TAG).text = str(r.solution)

    raw_str = et.tostring(root, 'utf-8')
    return raw_str if not prettify else \
           xml.dom.minidom.parseString(raw_str).toprettyxml(indent='    ')


def _deserilize_result(et_result):
    def raise_serialization_error(tag):
        raise SerializationError("There must be one and only one '%s' tag in "
                                 "each '%s' tag." % (tag, _XML_RESULT_TAG))

    instance = et_result.findall(_XML_INSTANCE_TAG)
    conflicts = et_result.findall(_XML_CONFLICTS_TAG)
    decisions = et_result.findall(_XML_DECISIONS_TAG)
    optimum = et_result.findall(_XML_OPTIMUM_TAG)
    propagations = et_result.findall(_XML_PROPAGATIONS_TAG)
    restarts = et_result.findall(_XML_RESTARTS_TAG)
    solution = et_result.findall(_XML_SOLUTION_TAG)

    if len(instance) != 1:
        raise_serialization_error(_XML_INSTANCE_TAG)
    if len(conflicts) != 1:
        raise_serialization_error(_XML_CONFLICTS_TAG)
    if len(decisions) != 1:
        raise_serialization_error(_XML_DECISIONS_TAG)
    if len(optimum) != 1:
        raise_serialization_error(_XML_OPTIMUM_TAG)
    if len(propagations) != 1:
        raise_serialization_error(_XML_PROPAGATIONS_TAG)
    if len(restarts) != 1:
        raise_serialization_error(_XML_RESTARTS_TAG)
    if len(solution) != 1:
        raise_serialization_error(_XML_SOLUTION_TAG)

    try:
        instance = instance[0].text.strip()
        conflicts = int(conflicts[0].text.strip())
        decisions = int(decisions[0].text.strip())
        optimum = int(optimum[0].text.strip())
        propagations = int(propagations[0].text.strip())
        restarts = int(restarts[0].text.strip())
        solution = solution[0].text.strip()

        return instance, \
               SolverResult(conflicts=conflicts, decisions=decisions,
                            optimum=optimum, propagations=propagations,
                            restarts=restarts, solution=solution)
    except ValueError:
        raise SerializationError("Tags '%s, %s, %s, %s and %s' must contain "
                                 "an integer value." %
                                 (_XML_CONFLICTS_TAG, _XML_DECISIONS_TAG,
                                  _XML_OPTIMUM_TAG, _XML_PROPAGATIONS_TAG,
                                  _XML_RESTARTS_TAG))


#################################
#   Parsers Factory Utilities   #
#################################

_parsers_registry = {}


def create_parser(name):
    return _parsers_registry[name]()


def get_parsers_names():
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
        """Parses the given solver output text.

        :return: The parsed result.
        """
        raise NotImplementedError("Abstract method.")

    def get_result(self):
        return SolverResult(
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
        self._solution = ""

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

        return self.get_result()


#
# Register MiniSat Parser Class
register_parser('minisat', MiniSatParser)
