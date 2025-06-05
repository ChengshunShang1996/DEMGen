#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "1.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "June 05, 2025"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

import os
import subprocess

from dynamic_methods.radius_expansion_with_servo_control_method import RadiusExpansionWithServoControlMethod

class ImprovedRadiusExpansionWithServoControlMethod(RadiusExpansionWithServoControlMethod):
    def __init__(self) -> None:
        super().__init__()

    def RunDEM(self):

        current_path = os.getcwd()
        aim_folder_name = "case_" + str(self.packing_cnt)
        aim_path = os.path.join(current_path, "generated_cases", aim_folder_name)
        os.chdir(aim_path)
        if self.last_try:
            if os.name == 'nt': # for windows
                subprocess.run(['python', 'improved_radius_expansion_with_servo_control_method_run_final.py'], check=True)
            else: # for linux
                subprocess.run(['python3', 'improved_radius_expansion_with_servo_control_method_run_final.py'], check=True)
        else:
            if os.name == 'nt': # for windows
                subprocess.run(['python', 'improved_radius_expansion_with_servo_control_method_run.py'], check=True)
            else: # for linux
                subprocess.run(['python3', 'improved_radius_expansion_with_servo_control_method_run.py'], check=True)

        if os.path.isfile("success.txt"):
            os.chdir(current_path)
            return True
        else:
            os.chdir(current_path)
            return False