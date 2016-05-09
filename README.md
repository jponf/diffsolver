DiffSolver
===========

A simple and naive tool to test if the results of a solver have changed.

## Requirements ##

No special requirements.

## Zipapp ##

In the root directory there is a shell script, _zipapp.sh_, that automatically
creates a Python Zipapp regardless of the Python version. If the Python
version is 3.5 or later, it uses the zipapp module, otherwise, it uses basic
UNIX commands to create a Python executable ZIP file.

\* _If you cannot execute the shell script, the commands to create it
    using the zipapp module are listed below._

## Zipapp (Python 3.5) ##

To create a Zipapp, run the following command

> python3 -m zipapp diffsolver -m diffsolver:main

Additionally, if you want to make the generated file "executable" in POSIX
environments, add the argument

> -p "/path/to/python_interpreter"

The complete command should look like this

> python3 -m zipapp diffsolver -m diffsolver:main -p "/usr/bin/env python3"

For more information, please see https://docs.python.org/3/library/zipapp.html
