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
    results = {}
    root = et.fromstring(serialized_str)

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


##################
