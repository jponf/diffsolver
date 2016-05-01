#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import xml.etree.ElementTree as et
import xml.dom


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
    ['instance', 'conflicts', 'decisions', 'optimum',
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
    root = et.Element(_XML_SOLVER_RESULTS)
    root.append(et.Comment("Generated for testsolver"))

    for r in results:
        result = et.SubElement(root, _XML_SOLVER_RESULT)
        instance = et.SubElement(result, _XML_SOLVER_RESULT_INSTANCE)
        conflicts = et.SubElement(result, _XML_SOLVER_RESULT_CONFLICTS)
        decisions = et.SubElement(result, _XML_SOLVER_RESULT_DECISIONS)
        optimum = et.SubElement(result, _XML_SOLVER_RESULT_OPTIMUM)
        propagations = et.SubElement(result, _XML_SOLVER_RESULT_PROPAGATIONS)
        restarts = et.SubElement(result, _XML_SOLVER_RESULT_RESTARTS)
        solution = et.SubElement(result, _XML_SOLVER_RESULT_SOLUTION)

        instance.text = str(r.instance)
        conflicts.text = str(r.conflicts)
        decisions.text = str(r.decisions)
        optimum.text = str(r.optimum)
        propagations.text = str(r.propagations)
        restarts.text = str(r.restarts)
        solution.text = str(r.solution)

    raw_str = et.tostring(root, 'utf-8')
    return xml.dom.parseString(raw_str).toprettyxml(indent='    ') if prettify \
           else raw_string


def save_results(path, results):
    with open(path, 'wt') as f:
        print(serialize_results(results, True), file=f)


##################
