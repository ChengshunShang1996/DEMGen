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
import shutil

from packing_characterization import PackingCharacterization

class PackingCharacterizationSingle(PackingCharacterization):

    def __init__(self) -> None:

        self.clear_old_cases_folder()

    def CreatInitialCases(self):

        self.creat_new_cases_folder()
        self.copy_seed_files_to_aim_folders()

    def RunDEM(self):

        aim_path = os.path.join(os.getcwd(), "packing_characterization")
        os.chdir(aim_path)
        os.system("python packing_characterization_run.py")

    def clear_old_cases_folder(self):

        cases_folder_name = 'packing_characterization'
        
        if os.path.exists(cases_folder_name):
            shutil.rmtree(cases_folder_name, ignore_errors=True)
            os.makedirs(cases_folder_name)
        else:
            os.makedirs(cases_folder_name)

    def creat_new_cases_folder(self):

        new_folder_name = "packing_characterization"
        aim_path = os.path.join(os.getcwd(), new_folder_name)
        os.makedirs(aim_path)
    
    def copy_seed_files_to_aim_folders(self):
        
        aim_folder_name = "packing_characterization"
        aim_path = os.path.join(os.getcwd(), aim_folder_name)

        seed_file_name_list = ['MaterialsDEM.json', 'ProjectParametersDEM.json', 'inletPGDEM_FEM_boundary.mdpa']
        for seed_file_name in seed_file_name_list:
            seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities','rem_seed_files', seed_file_name)
            aim_file_path_and_name = os.path.join(aim_path, seed_file_name)
            shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

        seed_file_path_and_name = os.path.join(self.ini_path, 'data_processing', 'post_processing', 'packing_characterization_run.py')
        aim_file_path_and_name = os.path.join(aim_path, 'packing_characterization_run.py')
        shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

        if self.parameters["generator_type"] =="constructive":
            seed_file_path_and_name = os.path.join(os.getcwd(), 'show_packing', 'inletPGDEM.mdpa')
            aim_file_path_and_name = os.path.join(aim_path, 'inletPGDEM.mdpa')
            shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)
        elif self.parameters["generator_type"] =="dynamic":
            seed_file_path_and_name = os.path.join(os.getcwd(), 'generated_cases', 'case_1', 'show_packing', 'inletPGDEM.mdpa')
            aim_file_path_and_name = os.path.join(aim_path, 'inletPGDEM.mdpa')
            shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)