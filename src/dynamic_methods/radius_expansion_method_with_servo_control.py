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

class RadiusExpansionMethodWithServoControl(DynamicMethod):

    def __init__(self) -> None:

        pass

    def CreatInitialCases(self):

        CreatIniCases = creat_particles_inside_of_a_domain.CreatParticlesInsideOfADomain()
        RVE_size = [self.parameters["domain_length_x"], self.parameters["domain_length_y"], self.parameters["domain_length_z"]]
        domain_scale_multiplier = self.parameters["random_particle_generation_parameters"]["domain_scale_multiplier"]
        aim_file_name = 'inletPGDEM_ini.mdpa'
        self.parameters["random_particle_generation_parameters"]["aim_packing_density"] = self.try_packing_desnity

        CreatIniCases.Initialize(RVE_size, domain_scale_multiplier, self.packing_cnt, self.ini_path)
        CreatIniCases.CreatParticles(RVE_size)
        aim_folder_name = "case_" + str(self.packing_cnt)
        CreatIniCases.WriteOutGIDData(aim_folder_name, aim_file_name)

    def RunDEM(self):

        current_path = os.getcwd()
        aim_folder_name = "case_" + str(self.packing_cnt)
        aim_path = os.path.join(current_path, "generated_cases", aim_folder_name)
        os.chdir(aim_path)
        if self.last_try:
            os.system("python radius_expansion_method_with_servo_control_run_final.py")
        else:
            os.system("python radius_expansion_method_with_servo_control_run.py")
        
        if os.path.isfile("success.txt"):
            os.chdir(current_path)
            return True
        else:
            return False

    def Run(self, parameters, ini_path):

        self.Initialization(parameters, ini_path)
        packing_num = self.parameters["packing_num"]
        aim_packing_density = self.parameters["random_particle_generation_parameters"]["aim_packing_density"]
        aim_packing_density_list = [aim_packing_density-0.002, aim_packing_density-0.005, aim_packing_density-0.01, aim_packing_density-0.02, aim_packing_density-0.05]
        self.packing_cnt = 1
        while self.packing_cnt <= packing_num:
            self.last_try = False
            for try_packing_desnity in aim_packing_density_list:
                self.try_packing_desnity = try_packing_desnity
                if try_packing_desnity == aim_packing_density_list[-1]:
                    self.last_try = True
                self.CreatInitialCases()
                success_marker = self.RunDEM()
                if success_marker:
                    break
            self.packing_cnt += 1