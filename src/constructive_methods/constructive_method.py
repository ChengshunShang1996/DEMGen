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

import os
import shutil
class ConstructiveMethod():

    def __init__(self) -> None:

        pass

    def Initialization(self, parameters, ini_path):

        self.parameters = parameters
        self.ini_path = ini_path
        self.particle_list = []
        self.dt = self.parameters['max_time_step']

    def CreatInitialPackings(self):

        try:
            int("string") 
        except ValueError:
            raise ValueError("This function should only be accessed in the derived class.")
    
    def WriteOutMdpaFileOfParticles(self, output_file_name):

        self.ClearOldAndCreatNewShowPackingCaseFolder()
        aim_path_and_name = os.path.join(os.getcwd(), 'show_packing', output_file_name)

        # clean the exsisted file first
        if os.path.isfile(aim_path_and_name):
            os.remove(aim_path_and_name)
        
        with open(aim_path_and_name,'a') as f:
            # write the particle information
            f.write("Begin ModelPartData \n //  VARIABLE_NAME value \n End ModelPartData \n \n Begin Properties 0 \n End Properties \n \n")
            f.write("Begin Nodes\n")
            for p_parameter_dict in self.particle_list:
                f.write(str(p_parameter_dict["id"]) + ' ' + str(p_parameter_dict["p_x"]) + ' ' + str(p_parameter_dict["p_y"]) + ' ' + str(p_parameter_dict["p_z"]) + '\n')
            f.write("End Nodes \n \n")

            f.write("Begin Elements SphericParticle3D// GUI group identifier: Body \n")
            for p_parameter_dict in self.particle_list:
                f.write(str(p_parameter_dict["p_ele_id"]) + ' ' + ' 0 ' + str(p_parameter_dict["id"]) + '\n')
            f.write("End Elements \n \n")

            f.write("Begin NodalData RADIUS // GUI group identifier: Body \n")
            for p_parameter_dict in self.particle_list:
                f.write(str(p_parameter_dict["id"]) + ' ' + ' 0 ' + str(p_parameter_dict["radius"]) + '\n')
            f.write("End NodalData \n \n")

            #uncomment this if it is for continuum simulation
            '''
            f.write("Begin NodalData COHESIVE_GROUP // GUI group identifier: Body \n")
            for p_parameter_dict in self.particle_list:
                f.write(str(p_parameter_dict["id"]) + ' ' + ' 0 ' + " 1 " + '\n')
            f.write("End NodalData \n \n")

            f.write("Begin NodalData SKIN_SPHERE \n End NodalData \n \n")
            '''

            f.write("Begin SubModelPart DEMParts_Body // Group Body // Subtree DEMParts \n Begin SubModelPartNodes \n")
            for p_parameter_dict in self.particle_list:
                if p_parameter_dict["p_group_id"] == 0:
                    f.write(str(p_parameter_dict["id"]) + '\n')
            f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
            for p_parameter_dict in self.particle_list:
                if p_parameter_dict["p_group_id"] == 0:
                    f.write(str(p_parameter_dict["p_ele_id"]) + '\n')
            f.write("End SubModelPartElements \n")
            f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n \n")

            #write out joint group
            joint_exist = False
            for p_parameter_dict in self.particle_list:
                if p_parameter_dict["p_group_id"] == 1:
                    joint_exist = True

            if joint_exist:
                f.write("Begin SubModelPart DEMParts_Joint // Group Joint // Subtree DEMParts \n Begin SubModelPartNodes \n")
                for p_parameter_dict in self.particle_list:
                    if p_parameter_dict["p_group_id"] == 1:
                        f.write(str(p_parameter_dict["id"]) + '\n')
                f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
                for p_parameter_dict in self.particle_list:
                    if p_parameter_dict["p_group_id"] == 1:
                        f.write(str(p_parameter_dict["p_ele_id"]) + '\n')
                f.write("End SubModelPartElements \n")
                f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n")

            f.close()

        print("Successfully write out GID DEM.mdpa file!")

    def CopyFilesAndRunShowResults(self):

        self.CopySeedFilesToAimFolders()

        aim_path = os.path.join(os.getcwd(),'show_packing')
        os.chdir(aim_path)
        os.system("python show_packing.py")

    def ClearOldAndCreatNewShowPackingCaseFolder(self):

        aim_path = os.path.join(os.getcwd(),'show_packing')

        if os.path.exists(aim_path):
            shutil.rmtree(aim_path, ignore_errors=True)
            os.makedirs(aim_path)
        else:
            os.makedirs(aim_path)
    
    def CopySeedFilesToAimFolders(self):
        
        aim_path = os.path.join(os.getcwd(), 'show_packing')

        seed_file_name_list = ['MaterialsDEM.json', 'ProjectParametersDEM.json', 'inletPGDEM_FEM_boundary.mdpa']
        for seed_file_name in seed_file_name_list:
            seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities', 'rem_seed_files', seed_file_name)
            aim_file_path_and_name = os.path.join(aim_path, seed_file_name)

            if seed_file_name == 'ProjectParametersDEM.json':
                with open(seed_file_path_and_name, "r") as f_material:
                    with open(aim_file_path_and_name, "w") as f_material_w:
                        for line in f_material.readlines():
                            if "PeriodicDomainOption" in line:
                                line = line.replace("true", 'false')
                            elif "RadiusExpansionOption" in line:
                                line = line.replace("true", 'false')
                            elif "RadiusExpansionRateChangeOption" in line:
                                line = line.replace("true", 'false')
                            elif "BoundingBoxMaxX" in line:
                                line = "    \"BoundingBoxMaxX\"                : " + str(0.5 * self.parameters["domain_length_x"]) + ', \n'
                            elif "BoundingBoxMaxY" in line:
                                line = "    \"BoundingBoxMaxY\"                : " + str(0.5 * self.parameters["domain_length_y"]) + ', \n'
                            elif "BoundingBoxMaxZ" in line:
                                line = "    \"BoundingBoxMaxZ\"                : " + str(0.5 * self.parameters["domain_length_z"]) + ', \n'
                            elif "BoundingBoxMinX" in line:
                                line = "    \"BoundingBoxMinX\"                : " + str(-0.5 * self.parameters["domain_length_x"]) + ', \n'
                            elif "BoundingBoxMinY" in line:
                                line = "    \"BoundingBoxMinY\"                : " + str(-0.5 * self.parameters["domain_length_y"]) + ', \n'
                            elif "BoundingBoxMinZ" in line:
                                line = "    \"BoundingBoxMinZ\"                : " + str(-0.5 * self.parameters["domain_length_z"]) + ', \n'
                            elif "FinalTime" in line:
                                line = "    \"FinalTime\"                      : " + str(self.dt * 2) + ', \n'
                            elif "\"GraphExportFreq\"" in line:
                                line = "    \"GraphExportFreq\"                : " + str(self.dt) + ', \n'
                            elif "VelTrapGraphExportFreq" in line:
                                line = "    \"VelTrapGraphExportFreq\"         : " + str(self.dt) + ', \n'
                            elif "OutputTimeStep" in line:
                                line = "    \"OutputTimeStep\"                 : " + str(self.dt) + ', \n'
                            f_material_w.write(line)
            else:
                shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

        seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities', 'show_packing.py')
        aim_file_path_and_name = os.path.join(aim_path, 'show_packing.py')
        shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

    def Run(self, parameters, ini_path):

        self.Initialization(parameters, ini_path)
        self.CreatInitialPackings()
        self.WriteOutMdpaFileOfParticles("inletPGDEM.mdpa")
        self.CopyFilesAndRunShowResults()
