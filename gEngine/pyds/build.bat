@ echo off
del cy_light_mask.c
cd gEingine
cd pyds
del cy_light_mask.pyd
cd ..
cd ..
python setup.py build_ext --inplace
cd gEngine
cd pyds
ren cy_light_mask.
pause