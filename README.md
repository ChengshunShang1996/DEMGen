# DEMGen: A Standard Particle Packing Generator for Discrete Element Method

<p align=center><img height="80.0%" width="80.0%" src="docs/images/LOGO1.png"></p>

![Release][release-image] 
![License][license-image]
![Contributing][contributing-image]

[release-image]: https://img.shields.io/badge/release-0.0.1-green.svg?style=flat 

[license-image]: https://img.shields.io/badge/license-BSD-green.svg?style=flat

[contributing-image]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg



This code aims to achieve a standard particle packing generation framework for granular materials. This code not only allows users to generate a series of random packings that fulfill their requirements (such as particle size distribution, porosity, and stress) but also provides a series of tools for particle packing characterization of internally or externally generated packings.


## Table of Contents
- [Main Features](#main-features)
- [DEMGen Dependencies](#demgen-dependencies)
- [Instructions](#instructions)
    - [Input and Output Files](#input-and-output-files)
    - [Running Simulations](#running-simulations)
        - [Packing Generation](#packing-generation)
        - [Packing Characterization](#packing-characterization)
    - [Checking Results](#checking-results)
- [Examples](#examples)
- [Documentation](#documentation)
- [How to Contribute](#how-to-contribute)
- [How to Cite](#how-to-cite)
- [Authorship](#authorship)
- [License](#license)

## Main Features

This program deals with the classical **soft-sphere approach** of the DEM.
The main characteristics of this method are:

- It is assumed that the contact between the particles occurs through a small overlap between them.
- Each contact is evaluated through several time steps in an explicit integration scheme.
- Contact models relate the amount of overlap between neighboring particles to the forces between them.
- Other physical interactions (e.g. thermal) may also be related to the overlap between particles.
- The shape of the particles is kept unchanged during and after contact. 

## DEMGen Dependencies

DEMGen is fully written in the Pythonpython_website programming language and adopts the Object Oriented Programming (OOP) paradigm to offer modularity and extensibility.

Please make sure you have installed Python3.X.X on your PC. Currently, [Python3.10.0][python310_website] is recommended, as other versions haven't been tested.

For the dynamic generation methods, DEM calculations are required. The [DEM Application][demapp_link] of the [Kratos Multiphysics][kratos_link] framework is adopted here. By including the [external_libraries][web] to your 

## Instructions

### Input and Output Files

There are three types of files that may be used as input for the program:

* **Parameters (_.json_)**: 

This [JSON][json_link] file is necessary for running a simulation and must always be

* **Results (_.txt_)**: 

This binary file stores the results of a simulation.

### Running Simulations

To run a simulation, launch MATLAB and execute the script file [*main.m*][main_file_link] located inside the folder [*src*][src_folder_link].

#### Packing Generation

steps

#### Packing Characterization

In progress...

### Checking Results

To load and show the results from previously run simulations, launch MATLAB and execute the script file [*main.m*][main_file_link] located inside the folder [*src*][src_folder_link].

## Examples

Sample models are available inside the folder [*examples*][examples_link].

They are separated into different sub-folders according to their analysis type,
and each example has its _Project_ _Parameters_ and _Model_ _Parts_ files, as well as some results in the output sub-folders.

## Documentation

In progress...

## How to Contribute

Please check the [contribution guidelines][contribute_link].

## How to Cite

To cite this repository, you can use the metadata from [this file][citation_link].

## Authorship

- **Chengshun Shang** <sup>1,2</sup> (<cshang@cimne.upc.edu>)

<sup>1</sup> International Center for Numerical Methods in Engineering ([CIMNE][cimne_website])

<sup>2</sup> Universitat Politècnica de Catalunya ([UPC BarcelonaTech][upc_website])

<p float="left">
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="./docs/images/cimne_logo.png" height="100"/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="./docs/images/upc_logo.png" height="120"/> 
</p>


## License

DEMGen is licensed under the [BSD license][bsd_license_link],
which allows the program to be freely used by anyone for modification, private use, commercial use, and distribution, only requiring the preservation of copyright and license notices.
No liability and warranty are provided.

[demapp_link]:          https://github.com/KratosMultiphysics/Kratos/tree/master/applications/DEMApplication
[kratos_link]:          https://github.com/KratosMultiphysics/Kratos
[json_link]:            https://www.json.org/
[contribute_link]:      https://github.com/ChengshunShang1996/DEMGen/blob/main/CONTRIBUTING.md
[citation_link]:        https://github.com/ChengshunShang1996/DEMGen/blob/main/CITATION.cff
[cimne_website]:        https://www.cimne.com/
[upc_website]:          https://camins.upc.edu/
[bsd_license_link]:     https://choosealicense.com/licenses/bsd-2-clause/
[python_website]:       https://www.python.org/
[python310_website]:    https://www.python.org/downloads/release/python-3100/
