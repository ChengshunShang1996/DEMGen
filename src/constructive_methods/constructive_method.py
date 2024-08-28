#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "0.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "August 21, 2024"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

class ConstructiveMethod():

    def __init__(self) -> None:

        pass

    def Initialization(self, parameters, ini_path):

        self.parameters = parameters
        self.ini_path = ini_path

    def CreatInitialPackings(self):

        try:
            int("string") 
        except ValueError:
            raise ValueError("This function should only be accessed in the derived class.")
    
    def Run(self, parameters, ini_path):

        self.Initialization(parameters, ini_path)
        self.CreatInitialPackings()
