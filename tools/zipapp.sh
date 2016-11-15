#!/usr/bin/env bash

# Python interpreter executable
PYTHON=python3

# Python version components
PYV_MAJOR=0
PYV_MINOR=1
PYV_MICRO=2

# Output file name
ZAPPNAME=diffsolver.pyz


# Get version
################################################################################

py_version_all=`$PYTHON 2>&1 -V`  # Python2 writes into stderr
if [ "$?" -ne 0 ]; then
    echo "Python not found ($PYTHON)"
    exit 1
fi

py_version=`sed -e 's/Python//' \
                -e 's/^[[:space:]]*//' \
                -e 's/[[:space:]]*$//' <<< "$py_version_all"`

OLD_IFS="$IFS"; IFS='.'
read -r -a py_version <<< "$py_version"
IFS="$OLD_IFS"

if [ "${#py_version[@]}" -ne 3 ]; then
    echo "Python version should have 3 components"
    exit 2
fi

echo ""
echo "++ Using $py_version_all"


# Remove byte-compiled files
################################################################################

echo "-- Deleting byte-compiled files and __pycache__ directories"
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "__pycache__" -delete


# Generate zipapp.sh
################################################################################

[ "${py_version[$PYV_MAJOR]}" -gt 3 ] || \
[[ "${py_version[$PYV_MAJOR]}" -eq 3 && "${py_version[$PYV_MINOR]}" -ge 5 ]]
has_zipapp=$?

if [ $has_zipapp == 0 ]; then  # It has zipapp.sh
    echo "-- Using zipapp module"
    $PYTHON -m zipapp ../src -m diffsolver:main -o $ZAPPNAME \
            -p "/usr/bin/env $PYTHON"
else
    # Add main function
    echo "-- Creating zipapp manually"
    echo "#!/usr/bin/env $PYTHON" > $ZAPPNAME

    echo "# -*- coding: utf-8 -*-"    > __main__.py
    echo "if __name__ == '__main__':" >> __main__.py
    echo "    import diffsolver"      >> __main__.py
    echo "    diffsolver.main()"      >> __main__.py

    zip -j -9 - `find . -name "*.py"` | cat >> $ZAPPNAME

    rm __main__.py
    chmod +x $ZAPPNAME
fi

echo ""
