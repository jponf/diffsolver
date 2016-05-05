DiffSolver
===========

A simple and naive tool to test if the results of a solver have changed.

## Requirements ##

No special requirements.

## Zipapp ##

To create a Zipapp, run the following command

> python3 -m zipapp diffsolver -m diffsolver:main

Additionally, if you want to make the generated file "executable" in POSIX
environments, add the argument

> -p "/path/to/python_interpreter"

The complete command should look like this

> python3 -m zipapp diffsolver -m diffsolver:main -p "/usr/bin/env python3"

For more information, please see https://docs.python.org/3/library/zipapp.html
