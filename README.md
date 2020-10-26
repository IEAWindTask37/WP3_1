# WP3_1
Repository for the wind turbine design optimization cases

## Aerodynamic-only optimization case

The aerodynamic-only optimization case is led by [Helena Canet](mailto:helena.canet@tum.de) at the Technical University of Munich, Germany.  

### Installation of the Python-based framework

Installation with [Anaconda](https://www.anaconda.com) is the recommended approach because of the ability to create self-contained environments suitable for testing and analysis.  WISDEM&reg; requires [Anaconda 64-bit](https://www.anaconda.com/distribution/).

The installation instructions below use the environment name, "wisdem-env," but any name is acceptable.

1.  Setup and activate the Anaconda environment from a prompt (Anaconda3 Power Shell on Windows or Terminal.app on Mac)

        conda config --add channels conda-forge
        conda create -y --name wisdem-env python=3.8
        conda activate wisdem-env

2.  Navigate to your desired directory (cd) and clone the repository 

        git clone https://github.com/IEAWindTask37/WP3_1

3.  Use conda to install the build dependencies, but then install WISDEM from source.  Note the differences between Windows and Mac/Linux build systems

        conda install -y wisdem git
        conda remove --force wisdem
        conda install compilers     # (Mac / Linux only)
        conda install m2w64-toolchain libpython       # (Windows only)
        git clone https://github.com/WISDEM/WISDEM.git
        cd WISDEM
        git checkout develop
        python setup.py develop
        cd ..

4.  Navigate to the script, run it, and check the output files that are generated

        cd WP3_1/Case_Aero
        python runCCBlade.py

5.  Build the optimization setup

The Python-based framework is maintained by [Pietro Bortolotti](mailto:pietro.bortolotti@nrel.gov). Contact him if you have any question.

### Installation of the Matlab-based framework


## Structural-only optimization case
This case has not been defined yet

## Aerostructural optimization case
This case has not been defined yet
