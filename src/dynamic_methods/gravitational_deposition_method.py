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

from dynamic_methods.dynamic_method import DynamicMethod
from data_processing.pre_processing import create_fem_and_inlet_mesh_files

class GravitationalDepositionMethod(DynamicMethod):

    def __init__(self) -> None:

        pass

    def CreateInitialCases(self):

        CreateIniCases = create_fem_and_inlet_mesh_files.CreateFemAndInletMeshFiles()
        RVE_size = [self.parameters["domain_length_x"], self.parameters["domain_length_y"], self.parameters["domain_length_z"]]
        packing_num = self.parameters["packing_num"]
        problem_name = self.parameters["problem_name"]
        
        packing_cnt = 1
        while packing_cnt <= packing_num:
            CreateIniCases.Initialize(RVE_size, self.parameters["particle_radius_max"], packing_cnt, self.ini_path)
            CreateIniCases.CreateFemMeshFile(problem_name, self.parameters["periodic_boundary_option"])
            CreateIniCases.CreateInletMeshFile(problem_name, self.parameters["inlet_properties"])
            CreateIniCases.CreateDemMeshFile(problem_name)
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
                os.system("python gravitational_deposition_method_run.py")
            else: # for linux
                os.system("python3 gravitational_deposition_method_run.py")
            os.chdir(current_path)
            packing_cnt += 1

        '''
        file_num = 0
        time_count = 0
        while file_num != self.parameters["packing_num"]:
            aim_path_and_folder = os.path.join(current_path,'generated_cases')
            file_num = len(glob.glob1(aim_path_and_folder,"*.txt"))
            time.sleep(30)
            print('-----Waiting for DEM cases -----')
            time_count += 0.5
            print('-------Cost {} min(s)-------'.format(time_count)) 
        '''