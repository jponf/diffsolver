::
:: Author: Josep Pon Farreny
::
:: Creates a bundled executable for windows using pyinstaller
::
@ECHO off

TITLE "Diffsolver Bundler"

SET pymain=../src/diffsolver.py
SET outname=diffsolver
SET specdir=installer
SET distdir=%specdir%/dist
SET workdir=%specdir%/build

pyinstaller --log-level=INFO ^
    --onefile ^
    --name %outname% ^
    --specpath=%specdir% ^
    --distpath=%distdir% ^
    --workpath=%workdir% ^
    %pymain%
exit
