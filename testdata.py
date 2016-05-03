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

_XML_SOLVER_RESULTS_TAG = 'sresults'
_XML_SOLVER_RESULT_TAG = 'sresult'
_XML_INSTANCE_TAG = 'instance'
_XML_CONFLICTS_TAG = 'conflicts'
_XML_DECISIONS_TAG = 'decisions'
_XML_OPTIMUM_TAG = 'optimum'
_XML_PROPAGATIONS_TAG = 'propagations'
_XML_RESTARTS_TAG = 'restarts'
_XML_SOLUTION_TAG = 'solution'
_XML_SOLVER_TAG = 'solver'
_XML_TIMESTAMP_TAG = 'timestamp'


def deserialize_results(data):
    raise NotImplementedError()


def serialize_results(results, solver="", timestamp="", prettify=False):
    """Serializes the results into an XML formatted string.

    :param results: A dictionary whose keys are instance paths and their
                    values SolverResult instances.
    :param prettify: Whether the resulting XML must be human readable.

    :return: An XML with the information of the provided results.
    """
    root = et.Element(_XML_SOLVER_RESULTS)
    root.append(et.Comment("# Results: " + str(len(results))))

    if solver:
        et.SubElement(root, _XML_SOLVER_TAG).text = solver
    if timestamp:
        et.SubElement(root, _XML_TIMESTAMP_TAG).text = timestamp

    for inst, r in results.items():
        result = et.SubElement(root, _XML_SOLVER_RESULT_TAG)
        instance = et.SubElement(result, _XML_INSTANCE_TAG)
        conflicts = et.SubElement(result, _XML_CONFLICTS_TAG)
        decisions = et.SubElement(result, _XML_DECISIONS_TAG)
        optimum = et.SubElement(result, _XML_OPTIMUM_TAG)
        propagations = et.SubElement(result, _XML_PROPAGATIONS_TAG)
        restarts = et.SubElement(result, _XML_RESTARTS_TAG)
        solution = et.SubElement(result, _XML_SOLUTION_TAG)

        instance.text = inst
        conflicts.text = str(r.conflicts)
        decisions.text = str(r.decisions)
        optimum.text = str(r.optimum)
        propagations.text = str(r.propagations)
        restarts.text = str(r.restarts)
        solution.text = str(r.solution)

    raw_str = et.tostring(root, 'utf-8')
    return raw_string if not prettify else \
           xml.dom.minidom.parseString(raw_str).toprettyxml(indent='    ')


##################
