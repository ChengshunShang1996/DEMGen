#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "0.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "June 21, 2024"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

import os
from data_processing.post_processing.packing_characterization import PackingCharacterization

class PackingCharacterizationMulti(PackingCharacterization):

    def __init__(self) -> None:

        pass

    def Initialization(self, parameters, ini_path):

        self.parameters = parameters
        self.ini_path = ini_path

    def CreateInitialCases(self):

        pass

    def RunDEM(self):

        packing_num = self.parameters["packing_num"]
        packing_cnt = 1
        current_path = os.getcwd()
        while packing_cnt <= packing_num:
            aim_folder_name = "case_" + str(packing_cnt)
            aim_path = os.path.join(current_path, "generated_cases", aim_folder_name)
            os.chdir(aim_path)
            if os.name == 'nt': # for windows
                os.system("python isotropic_compression_method_run.py")
            else: # for linux
                os.system("python3 isotropic_compression_method_run.py")
            packing_cnt += 1
