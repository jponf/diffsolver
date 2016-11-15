#!/usr/bin/env sh
#
# Author: Josep Pon Farreny
#
# Creates a bundled executable for linux/osx using pyinstaller
#

uname_str=`uname`
arch_str=`uname -m`

if [ $uname_str = "Linux" ]; then
    platform="linux"
elif [ "$uname_str" = "FreeBSD" ]; then
    platform="bsd"
elif [ "$uname_str" = "Darwin" ]; then
    platform="mac"
else
    platform="unknown"
fi

pymain=../src/diffsolver.py
outname=diffsolver-${platform}-${arch_str}
specdir=installer
distdir=${specdir}/dist
workdir=${specdir}/build


pyinstaller --log-level=INFO \
    --onefile \
    --name "${outname}"   \
    --specpath=${specdir} \
    --distpath=${distdir} \
    --workpath=${workdir} \
    ${pymain}
