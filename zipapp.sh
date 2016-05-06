#!/usr/bin/env sh

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

# Generate zipapp
################################################################################

[ "${py_version[$PYV_MAJOR]}" -gt 3 ] || [[ "${py_version[$PYV_MAJOR]}" -eq 3 && "${py_version[$PYV_MINOR]}" -ge 5 ]]
has_zipapp=$?

if [ $has_zipapp == 0 ]; then  # It has zipapp
    echo "-- Using zipapp module"
    $PYTHON -m zipapp diffsolver -m diffsolver:main -p "/usr/bin/env $PYTHON"
else
    # Add main function
    echo "-- Creating zipapp manually"
    echo "#/usr/bin/env $PYTHON" > $ZAPPNAME
    for f in `find . -name "*.py"`; do
        zip - $f >> $ZAPPNAME
    done
fi

echo ""
