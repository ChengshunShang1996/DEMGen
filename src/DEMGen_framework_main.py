#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "0.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "June 20, 2024"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

import os
import json

from tkinter import Tk
from tkinter.filedialog import askopenfilename

from data_processing.pre_processing import *
from data_processing.post_processing import *
#from src.dynamic_methods import *

class DEMGenMainFramework():

    def __init__(self) -> None:
        
        print('-'*76 + '\n')

    ####################main processes#############################################
    def Initilization(self, aim_path):
        
        #read parameter.json file
        #file_path = self.choose_file()
        file_path = aim_path
        
        if file_path:
            self.set_working_directory(file_path)
            self.parameters = self.read_json(file_path)
        else:
            print("No file selected")
            exit(0)

        #

    def GenerationRun(self):
        
        #particle packing generation
        if self.parameters["generator_name"] == "gravitational_deposition_method":

            from dynamic_methods import gravitational_deposition_method
            MyDEM = gravitational_deposition_method.GravitationalDepositionMethod()
            MyDEM.Run(self.parameters, self.ini_path)

        elif self.parameters["generator_name"] == "isotropic_compression_method":
            
            pass

        elif self.parameters["generator_name"] == "radius_expansion_method":
            
            pass

        else:
            print("No generator name given")

        #what we get from above processes is a .mdpa file of DEM particles

    def CharacterizationRun(self):

        #particle packing characterization
        #this is not related to 
        if self.parameters["packing_charcterization_option"] is True:
            
            if self.parameters["regular_shape_option"] is True:

                pass

            else:

                pass
        else:
            print("No packing analysis has been done because [packing_charcterization_option] is set as [False]")


    def Finilization(self):
        
        print("Successfully finish!")

    ####################detail functions################################################
    def choose_file(self):

        print(f'Please select a ParametersDEMGen.json file for starting:')

        root = Tk()
        root.withdraw()
        
        file_path = askopenfilename(
            filetypes=[("JSON files", "*.json")], 
            title="Select ParametersDEMGen.json file"
        )

        print("Parameters file for DEMGen selected.")
        
        return file_path

    def set_working_directory(self, file_path):

        self.ini_path = os.getcwd()
        if self.ini_path.endswith('src'):
            self.ini_path = os.path.dirname(self.ini_path)

        directory = os.path.dirname(file_path)
        os.chdir(directory)
        print(f"Set current working directory: {os.getcwd()}")

    def read_json(self, file_path):

        with open(file_path, 'r') as file:
            parameters = json.load(file)
        return parameters


if __name__ == "__main__":
    
    TestDEM = DEMGenMainFramework()
    aim_path = 'C:\\Users\\cshang.PCCB201\\Desktop\\particle_packing_generator\example\\test_gravitational_deposition_method\\ParametersDEMGen.json'
    TestDEM.Initilization(aim_path)
    TestDEM.GenerationRun()
    TestDEM.CharacterizationRun()
    TestDEM.Finilization()
    