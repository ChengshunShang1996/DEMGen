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

from src.data_processing.pre_processing import *
from src.data_processing.post_processing import *
#from src.dynamic_methods import *
#from src.utilities import *

class DEMGenMainFramework():

    def __init__(self) -> None:
        
        print('-'*76 + '\n')

        file_path = self.choose_file()
        
        if file_path:
            self.set_working_directory(file_path)
            self.parameters = self.read_json(file_path)
        else:
            print("No file selected")
            exit(0)

    def Initilization(self):
        pass
    
    def choose_file(self):

        print(f'Please select a Parameter.json file for starting:\n')

        root = Tk()
        root.withdraw()
        
        file_path = askopenfilename(
            filetypes=[("JSON files", "*.json")], 
            title="Select Parameters.json file"
        )
        
        return file_path

    def set_working_directory(self, file_path):

        directory = os.path.dirname(file_path)
        os.chdir(directory)
        print(f"Current working directory: {os.getcwd()}")

    def read_json(self, file_path):

        with open(file_path, 'r') as file:
            parameters = json.load(file)
        return parameters

    def Run(self):
        pass

    def Finilization(self):
        pass


if __name__ == "__main__":
    
    TestDEM = DEMGenMainFramework()
    