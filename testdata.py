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

_XML_SOLVER_RESULTS = 'sresults'
_XML_SOLVER_RESULT = 'sresult'
_XML_SOLVER_RESULT_INSTANCE = 'instance'
_XML_SOLVER_RESULT_CONFLICTS = 'conflicts'
_XML_SOLVER_RESULT_DECISIONS = 'decisions'
_XML_SOLVER_RESULT_OPTIMUM = 'optimum'
_XML_SOLVER_RESULT_PROPAGATIONS = 'propagations'
_XML_SOLVER_RESULT_RESTARTS = 'restarts'
_XML_SOLVER_RESULT_SOLUTION = 'solution'


def serialize_results(results, prettify=False):
    """Serializes the results into an XML formatted string.

    :param results: A dictionary whose keys are instance paths and their
                    values SolverResult instances.
    :param prettify: Whether the resulting XML must be human readable.

    :return: An XML with the information of the provided results.
    """
    root = et.Element(_XML_SOLVER_RESULTS)
    root.append(et.Comment("Generated for testsolver"))

    for inst, r in results.items():
        result = et.SubElement(root, _XML_SOLVER_RESULT)
        instance = et.SubElement(result, _XML_SOLVER_RESULT_INSTANCE)
        conflicts = et.SubElement(result, _XML_SOLVER_RESULT_CONFLICTS)
        decisions = et.SubElement(result, _XML_SOLVER_RESULT_DECISIONS)
        optimum = et.SubElement(result, _XML_SOLVER_RESULT_OPTIMUM)
        propagations = et.SubElement(result, _XML_SOLVER_RESULT_PROPAGATIONS)
        restarts = et.SubElement(result, _XML_SOLVER_RESULT_RESTARTS)
        solution = et.SubElement(result, _XML_SOLVER_RESULT_SOLUTION)

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


def save_results(path,  results):
    """Saves the given results into the file specified by path.

    This function uses serialize_results before writing to the file, thereby
    the results must conform with the format expected by serialize_results.

    :param path: Path to the output file.
    :param results: A dictionary whose keys are instance paths and their
                    values SolverResult instances.
    """
    with open(path, 'wt') as f:
        print(serialize_results(results, True), file=f)


##################
