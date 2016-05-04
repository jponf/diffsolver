#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import xml.etree.ElementTree as et
import xml.dom.minidom


##############################
#   Authorship Information   #
##############################

__author__ = "Josep Pon Farreny"
__copyright__ = "Copyright 2016, Josep Pon Farreny"
__credits__ = ["Josep Pon Farreny"]


################################
#   Useful Exception Classes   #
################################

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
    """Deserializes the results from the given data.

    :param data: An XML formatted string with the serialized results.
    :return:
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
    return raw_string if not prettify else \
           xml.dom.minidom.parseString(raw_str).toprettyxml(indent='    ')


#######################
#   Utility methods   #
#######################

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
