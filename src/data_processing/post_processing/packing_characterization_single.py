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
import subprocess

from data_processing.post_processing.packing_characterization import PackingCharacterization

class PackingCharacterizationSingle(PackingCharacterization):

    def __init__(self) -> None:

        pass

    def CreateInitialCases(self):

        self.clear_old_cases_folder()
        self.copy_seed_files_to_aim_folders()

    def RunDEM(self):

        cases_folder_name = 'packing_characterization'

        if self.parameters["generator_type"] =="constructive":
            aim_path = os.path.join(os.getcwd(), cases_folder_name)
        elif self.parameters["generator_type"] =="dynamic":    
            aim_path = os.path.join(os.getcwd(), 'generated_cases', 'case_1', cases_folder_name)
        
        os.chdir(aim_path)
        if os.name == 'nt': # for windows
            #os.system("python packing_characterization_run.py")
            #subprocess.run(['python', 'packing_characterization_run.py'], check=True)
            try:
                result = subprocess.run(
                    ['python', 'packing_characterization_run.py'],
                    cwd=aim_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print("Script failed with return code:", e.returncode)
                print("Standard output:\n", e.stdout)
                print("Standard error:\n", e.stderr)
        else: # for linux
            os.system("python3 packing_characterization_run.py")

    def clear_old_cases_folder(self):

        cases_folder_name = 'packing_characterization'

        if self.parameters["generator_type"] =="constructive":
            cases_folder_path = cases_folder_name
        elif self.parameters["generator_type"] =="dynamic":    
            cases_folder_path = os.path.join(os.getcwd(), 'generated_cases', 'case_1', cases_folder_name)

        if os.path.exists(cases_folder_path):
            shutil.rmtree(cases_folder_path, ignore_errors=True)
            os.makedirs(cases_folder_path)
        else:
            os.makedirs(cases_folder_path)
    
    def copy_seed_files_to_aim_folders(self):

        aim_folder_name = 'packing_characterization'
        
        if self.parameters["generator_type"] =="constructive":
            aim_path = aim_folder_name
        elif self.parameters["generator_type"] =="dynamic":    
            aim_path = os.path.join(os.getcwd(), 'generated_cases', 'case_1', aim_folder_name)

        seed_file_name_list = ['MaterialsDEM.json', 'ProjectParametersDEM.json', 'inletPGDEM_FEM_boundary.mdpa']
        for seed_file_name in seed_file_name_list:
            seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities','rem_seed_files', seed_file_name)
            aim_file_path_and_name = os.path.join(aim_path, seed_file_name)
            if seed_file_name == 'ProjectParametersDEM.json':
                with open(seed_file_path_and_name, "r") as f_material:
                    with open(aim_file_path_and_name, "w") as f_material_w:
                        for line in f_material.readlines():
                            if "BoundingBoxMaxX" in line:
                                line = "    \"BoundingBoxMaxX\"                : " + str(self.parameters["domain_length_x"] / 2.0) + ', \n'
                            elif "\"BoundingBoxMaxY\"" in line:
                                line = "    \"BoundingBoxMaxY\"                : " + str(self.parameters["domain_length_y"] / 2.0) + ', \n'
                            elif "BoundingBoxMaxZ" in line:
                                line = "    \"BoundingBoxMaxZ\"                : " + str(self.parameters["domain_length_z"] / 2.0) + ', \n'
                            elif "BoundingBoxMinX" in line:
                                line = "    \"BoundingBoxMinX\"                : " + str(self.parameters["domain_length_x"] / -2.0) + ', \n'
                            elif "\"BoundingBoxMinY\"" in line:
                                line = "    \"BoundingBoxMinY\"                : " + str(self.parameters["domain_length_y"] / -2.0) + ', \n'
                            elif "BoundingBoxMinZ" in line:
                                line = "    \"BoundingBoxMinZ\"                : " + str(self.parameters["domain_length_z"] / -2.0) + ', \n'
                            elif "FinalTime" in line:
                                line = "    \"FinalTime\"                      : " + str(self.dt * 2) + ', \n'
                            elif "\"GraphExportFreq\"" in line:
                                line = "    \"GraphExportFreq\"                : " + str(self.dt) + ', \n'
                            elif "VelTrapGraphExportFreq" in line:
                                line = "    \"VelTrapGraphExportFreq\"         : " + str(self.dt) + ', \n'
                            elif "OutputTimeStep" in line:
                                line = "    \"OutputTimeStep\"                 : " + str(self.dt) + ', \n'
                            elif "NeighbourSearchFrequency" in line:
                                line = "    \"NeighbourSearchFrequency\"       : " + str(1) + ', \n'
                            elif "RadiusExpansionOption" in line:
                                line = "    \"RadiusExpansionOption\"          : " + "false" + ', \n'
                            elif "RadiusExpansionRateChangeOption" in line:
                                line = "    \"RadiusExpansionRateChangeOption\": " + "false" + ', \n'
                            f_material_w.write(line)
            else:
                if os.path.exists(seed_file_path_and_name):
                    shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

        seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'data_processing', 'post_processing', 'packing_characterization_run.py')
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

        seed_file_path_and_name = os.path.join(os.getcwd(), 'ParametersDEMGen.json')
        aim_file_path_and_name = os.path.join(aim_path, 'ParametersDEMGen.json')
        shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)