#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "0.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "June 26, 2024"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

import os

from dynamic_methods.dynamic_method import DynamicMethod
from data_processing.pre_processing import creat_particles_inside_of_a_domain

class RadiusExpansionMethod(DynamicMethod):

    def __init__(self) -> None:

        pass

    def CreatInitialCases(self):

        CreatIniCases = creat_particles_inside_of_a_domain.CreatParticlesInsideOfADomain()
        RVE_size = [self.parameters["domain_length_x"], self.parameters["domain_length_y"], self.parameters["domain_length_z"]]
        packing_num = self.parameters["packing_num"]
        domain_scale_multiplier = self.parameters["random_particle_generation_parameters"]["domain_scale_multiplier"]
        aim_file_name = 'inletPGDEM_ini.mdpa'

        packing_cnt = 1
        while packing_cnt <= packing_num:
            CreatIniCases.Initialize(RVE_size, domain_scale_multiplier, packing_cnt, self.ini_path)
            CreatIniCases.CreatParticles(RVE_size)
            aim_folder_name = "case_" + str(packing_cnt)
            CreatIniCases.WriteOutGIDData(aim_folder_name, aim_file_name)
            packing_cnt += 1

    def RunDEM(self):

        packing_num = self.parameters["packing_num"]
        packing_cnt = 1
        current_path = os.getcwd()
        while packing_cnt <= packing_num:
            aim_folder_name = "case_" + str(packing_cnt)
            aim_path = os.path.join(current_path, "generated_cases", aim_folder_name)
            os.chdir(aim_path)
            if os.name == 'nt': # for windows
                os.system("python radius_expansion_method_run_v1.4.py")
            else: # for linux
                os.system("python3 radius_expansion_method_run_v1.4.py")
            os.chdir(current_path)
            packing_cnt += 1