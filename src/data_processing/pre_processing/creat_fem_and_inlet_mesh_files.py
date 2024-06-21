#/////////////////////////////////////////////////
#// Main author: Chengshun Shang (CIMNE)
#// Email: chengshun.shang1996@gmail.com
#// Date: August 2023
#/////////////////////////////////////////////////

import os
import shutil

class CreatFemAndInletMeshFiles():

    def __init__(self) -> None:  
        self.fem_points_list = []
        self.fem_elements_list = []
        self.inlet_points_list = []

    def Initialize(self, RVE_size, particle_radius_max, mesher_cnt, ini_path):

        RVE_length_x = RVE_size[0]
        RVE_length_y = RVE_size[1]
        RVE_length_z = RVE_size[2]
        self.mesher_cnt = mesher_cnt
        self.ini_path = ini_path
        
        #we need creat a cuboid which has a height of two times of the RVE 
        #------------------for creating FEM boundary mesh (start)---------------------------
        for i in range(1, 9):

            #here, Y direction is the default Gravity direction (Height direction)
            fem_point_dict = {
                    "id" : 0,
                    "p_x" : 0.0,
                    "p_y" : 0.0,
                    "p_z" : 0.0
                    }
            
            if i == 1:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = -0.5 * RVE_length_x
                fem_point_dict["p_y"] = 0.0
                fem_point_dict["p_z"] = -0.5 * RVE_length_z
                self.fem_points_list.append(fem_point_dict)
            elif i == 2:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = 0.5 * RVE_length_x
                fem_point_dict["p_y"] = 0.0
                fem_point_dict["p_z"] = -0.5 * RVE_length_z
                self.fem_points_list.append(fem_point_dict)
            elif i == 3:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = 0.5 * RVE_length_x
                fem_point_dict["p_y"] = 0.0
                fem_point_dict["p_z"] = 0.5 * RVE_length_z
                self.fem_points_list.append(fem_point_dict)
            elif i == 4:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = -0.5 * RVE_length_x
                fem_point_dict["p_y"] = 0.0
                fem_point_dict["p_z"] = 0.5 * RVE_length_z
                self.fem_points_list.append(fem_point_dict)
            elif i == 5:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = -0.5 * RVE_length_x
                fem_point_dict["p_y"] = RVE_length_y * 2
                fem_point_dict["p_z"] = -0.5 * RVE_length_z
                self.fem_points_list.append(fem_point_dict)
            elif i == 6:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = 0.5 * RVE_length_x
                fem_point_dict["p_y"] = RVE_length_y * 2
                fem_point_dict["p_z"] = -0.5 * RVE_length_z
                self.fem_points_list.append(fem_point_dict)
            elif i == 7:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = 0.5 * RVE_length_x
                fem_point_dict["p_y"] = RVE_length_y * 2
                fem_point_dict["p_z"] = 0.5 * RVE_length_z
                self.fem_points_list.append(fem_point_dict)
            elif i == 8:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = -0.5 * RVE_length_x
                fem_point_dict["p_y"] = RVE_length_y * 2
                fem_point_dict["p_z"] = 0.5 * RVE_length_z
                self.fem_points_list.append(fem_point_dict)
        
        for i in range(1,7):
            
            fem_element_dict = {
                    "id" : 0,
                    "p_1_id" : 0,
                    "p_2_id" : 0,
                    "p_3_id" : 0,
                    "p_4_id" : 0
                    }
            
            if i == 1:
                fem_element_dict["id"] = i
                fem_element_dict["p_1_id"] = 1
                fem_element_dict["p_2_id"] = 2
                fem_element_dict["p_3_id"] = 3
                fem_element_dict["p_4_id"] = 4
                self.fem_elements_list.append(fem_element_dict)
            elif i == 2:
                fem_element_dict["id"] = i
                fem_element_dict["p_1_id"] = 5
                fem_element_dict["p_2_id"] = 6
                fem_element_dict["p_3_id"] = 7
                fem_element_dict["p_4_id"] = 8
                self.fem_elements_list.append(fem_element_dict)
            elif i == 3:
                fem_element_dict["id"] = i
                fem_element_dict["p_1_id"] = 1
                fem_element_dict["p_2_id"] = 2
                fem_element_dict["p_3_id"] = 6
                fem_element_dict["p_4_id"] = 5
                self.fem_elements_list.append(fem_element_dict)
            elif i == 4:
                fem_element_dict["id"] = i
                fem_element_dict["p_1_id"] = 2
                fem_element_dict["p_2_id"] = 3
                fem_element_dict["p_3_id"] = 7
                fem_element_dict["p_4_id"] = 6
                self.fem_elements_list.append(fem_element_dict)
            elif i == 5:
                fem_element_dict["id"] = i
                fem_element_dict["p_1_id"] = 3
                fem_element_dict["p_2_id"] = 4
                fem_element_dict["p_3_id"] = 8
                fem_element_dict["p_4_id"] = 7
                self.fem_elements_list.append(fem_element_dict)
            elif i == 6:
                fem_element_dict["id"] = i
                fem_element_dict["p_1_id"] = 4
                fem_element_dict["p_2_id"] = 1
                fem_element_dict["p_3_id"] = 5
                fem_element_dict["p_4_id"] = 8
                self.fem_elements_list.append(fem_element_dict)
        #------------------for creating FEM boundary mesh (end)---------------------------

        #---------------------for creating inlet mesh (start)-----------------------------
        row_z_max = -0.5 * RVE_length_z + 2 * particle_radius_max
        row_end = False
        column_end = False
        id_max = 8

        while not (row_end is True and column_end is True):
             
            column_x_max = -0.5 * RVE_length_x + 2 * particle_radius_max
            column_end = False

            while not (column_end is True): # the end of one row is column_end

                inlet_point_dict = {
                    "id" : 0,
                    "p_x" : 0.0,
                    "p_y" : 0.0,
                    "p_z" : 0.0
                    }
                
                inlet_point_dict["id"] = id_max + 1
                inlet_point_dict["p_x"] = column_x_max 
                inlet_point_dict["p_y"] = 2 * RVE_length_y - 2 * particle_radius_max
                inlet_point_dict["p_z"] = row_z_max
                self.inlet_points_list.append(inlet_point_dict)
                id_max += 1

                if (column_x_max + 3 * particle_radius_max) > 0.5 * RVE_length_x:
                    column_end = True

                column_x_max += 2 * particle_radius_max
            
            if (row_z_max + 3 * particle_radius_max) > 0.5 * RVE_length_z:
                row_end = True
            
            row_z_max += 2 * particle_radius_max

        #---------------------for creating inlet mesh (end)-----------------------------

        self.clear_old_and_creat_new_mesher_cases_folder()
        self.copy_seed_files_to_aim_folders()
    
    def clear_old_and_creat_new_mesher_cases_folder(self):
        mesher_cases_folder_name = 'generated_mesher_cases'
        
        if os.path.exists(mesher_cases_folder_name):
            shutil.rmtree(mesher_cases_folder_name, ignore_errors=True)
            os.makedirs(mesher_cases_folder_name)
        else:
            os.makedirs(mesher_cases_folder_name)

        new_folder_name = "mesher_case_" + str(self.mesher_cnt)
        aim_path = os.path.join(os.getcwd(),'generated_mesher_cases', new_folder_name)
        os.makedirs(aim_path)
    
    def copy_seed_files_to_aim_folders(self):
        
        aim_folder_name = "mesher_case_" + str(self.mesher_cnt)
        aim_path = os.path.join(os.getcwd(), "generated_mesher_cases", aim_folder_name)

        seed_file_name_list = ['MaterialsDEM.json', 'ProjectParametersDEM.json']
        for seed_file_name in seed_file_name_list:
            seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities', 'seed_files_for_gravitational_method', seed_file_name)
            aim_file_path_and_name = os.path.join(aim_path, seed_file_name)
            shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

    def CreatFemMeshFile(self, problem_name):
        
        aim_folder_name = "mesher_case_" + str(self.mesher_cnt)
        aim_file_name = problem_name + 'DEM_FEM_boundary.mdpa'
        aim_path_and_name = os.path.join(os.getcwd(), "generated_mesher_cases", aim_folder_name, aim_file_name)

        # clean the exsisted file first
        if os.path.isfile(aim_path_and_name):
            os.remove(aim_path_and_name)
        
        with open(aim_path_and_name,'a') as f:
            # write the FEM information
            f.write("Begin ModelPartData \n //  VARIABLE_NAME value \nEnd ModelPartData \n \nBegin Properties 0 \nEnd Properties \n \n")
            
            f.write("Begin Nodes\n")
            for fem_point_dict in self.fem_points_list:
                f.write(str(fem_point_dict["id"]) + ' ' + str(fem_point_dict["p_x"]) + ' ' + str(fem_point_dict["p_y"]) + ' ' + str(fem_point_dict["p_z"]) + '\n')
            f.write("End Nodes \n \n")

            f.write("Begin Conditions RigidFace3D4N// GUI group identifier: TOP \n")
            for fem_element_dict in self.fem_elements_list:
                if fem_element_dict["id"] == 2:
                    f.write(str(fem_element_dict["id"]) + ' 0 ' + str(fem_element_dict["p_1_id"]) + ' ' + str(fem_element_dict["p_2_id"]) + ' ' + str(fem_element_dict["p_3_id"]) + ' ' + str(fem_element_dict["p_4_id"]) + '\n')
                    break
            f.write("End Conditions \n \n")

            f.write("Begin Conditions RigidFace3D4N// GUI group identifier: BOTTOM \n")
            for fem_element_dict in self.fem_elements_list:
                if fem_element_dict["id"] == 1:
                    f.write(str(fem_element_dict["id"]) + ' 0 ' + str(fem_element_dict["p_1_id"]) + ' ' + str(fem_element_dict["p_2_id"]) + ' ' + str(fem_element_dict["p_3_id"]) + ' ' + str(fem_element_dict["p_4_id"]) + '\n')
                    break
            f.write("End Conditions \n \n")

            f.write("Begin Conditions RigidFace3D4N// GUI group identifier: WALL \n")
            for fem_element_dict in self.fem_elements_list:
                if fem_element_dict["id"] != 1 and fem_element_dict["id"] != 2:
                    f.write(str(fem_element_dict["id"]) + ' 0 ' + str(fem_element_dict["p_1_id"]) + ' ' + str(fem_element_dict["p_2_id"]) + ' ' + str(fem_element_dict["p_3_id"]) + ' ' + str(fem_element_dict["p_4_id"]) + '\n')
            f.write("End Conditions \n \n")

            f.write("Begin SubModelPart DEM-FEM-Wall_TOP // DEM-FEM-Wall - group identifier: TOP \n \
                    Begin SubModelPartData // DEM-FEM-Wall. Group name: TOP \n \
                        LINEAR_VELOCITY [3] (0.0, 0.0, 0.0) \n \
                        VELOCITY_PERIOD 0.0 \n \
                        ANGULAR_VELOCITY [3] (0.0,0.0,0.0) \n \
                        ROTATION_CENTER [3] (0.0,0.0,0.0) \n \
                        ANGULAR_VELOCITY_PERIOD 0.0 \n \
                        VELOCITY_START_TIME 0.0 \n \
                        VELOCITY_STOP_TIME 100.0 \n \
                        ANGULAR_VELOCITY_START_TIME 0.0 \n \
                        ANGULAR_VELOCITY_STOP_TIME 100.0 \n \
                        FIXED_MESH_OPTION 0 \n \
                        RIGID_BODY_MOTION 1 \n \
                        FREE_BODY_MOTION 0 \n \
                        IS_GHOST 0 \n \
                        IDENTIFIER TOP \n \
                        FORCE_INTEGRATION_GROUP 0 \n \
                    End SubModelPartData \n ")
            
            f.write("Begin SubModelPartNodes \n")
            f.write(" 5 \n 6 \n 7 \n 8\n")
            f.write("End SubModelPartNodes \n")

            f.write("Begin SubModelPartConditions \n")
            f.write(" 2 \n")
            f.write("End SubModelPartConditions \n")
            f.write("End SubModelPart \n \n")

            f.write("Begin SubModelPart DEM-FEM-Wall_BOTTOM // DEM-FEM-Wall - group identifier: BOTTOM \n \
                    Begin SubModelPartData // DEM-FEM-Wall. Group name: BOTTOM \n \
                        LINEAR_VELOCITY [3] (0.0, 0.0, 0.0) \n \
                        VELOCITY_PERIOD 0.0 \n \
                        ANGULAR_VELOCITY [3] (0.0,0.0,0.0) \n \
                        ROTATION_CENTER [3] (0.0,0.0,0.0) \n \
                        ANGULAR_VELOCITY_PERIOD 0.0 \n \
                        VELOCITY_START_TIME 0.0 \n \
                        VELOCITY_STOP_TIME 100.0 \n \
                        ANGULAR_VELOCITY_START_TIME 0.0 \n \
                        ANGULAR_VELOCITY_STOP_TIME 100.0 \n \
                        FIXED_MESH_OPTION 0 \n \
                        RIGID_BODY_MOTION 1 \n \
                        FREE_BODY_MOTION 0 \n \
                        IS_GHOST 0 \n \
                        IDENTIFIER BOTTOM \n \
                        FORCE_INTEGRATION_GROUP 0 \n \
                    End SubModelPartData \n ")
            
            f.write("Begin SubModelPartNodes \n")
            f.write(" 1 \n 2 \n 3 \n 4\n")
            f.write("End SubModelPartNodes \n")

            f.write("Begin SubModelPartConditions \n")
            f.write(" 1 \n")
            f.write("End SubModelPartConditions \n")
            f.write("End SubModelPart \n \n")

            f.write("Begin SubModelPart DEM-FEM-Wall_WALL // DEM-FEM-Wall - group identifier: WALL \n \
                    Begin SubModelPartData // DEM-FEM-Wall. Group name: WALL \n \
                        LINEAR_VELOCITY [3] (0.0, 0.0, 0.0) \n \
                        VELOCITY_PERIOD 0.0 \n \
                        ANGULAR_VELOCITY [3] (0.0,0.0,0.0) \n \
                        ROTATION_CENTER [3] (0.0,0.0,0.0) \n \
                        ANGULAR_VELOCITY_PERIOD 0.0 \n \
                        VELOCITY_START_TIME 0.0 \n \
                        VELOCITY_STOP_TIME 100.0 \n \
                        ANGULAR_VELOCITY_START_TIME 0.0 \n \
                        ANGULAR_VELOCITY_STOP_TIME 100.0 \n \
                        FIXED_MESH_OPTION 0 \n \
                        RIGID_BODY_MOTION 1 \n \
                        FREE_BODY_MOTION 0 \n \
                        IS_GHOST 0 \n \
                        IDENTIFIER WALL \n \
                        FORCE_INTEGRATION_GROUP 0 \n \
                    End SubModelPartData \n ")
            
            f.write("Begin SubModelPartNodes \n")
            f.write(" 1 \n 2 \n 3 \n 4\n 5 \n 6 \n 7 \n 8\n")
            f.write("End SubModelPartNodes \n")

            f.write("Begin SubModelPartConditions \n")
            f.write(" 3 \n 4 \n 5 \n 6\n")
            f.write("End SubModelPartConditions \n")
            f.write("End SubModelPart \n")
        f.close()

    def CreatInletMeshFile(self, problem_name, inlet_properties):
        
        aim_folder_name = "mesher_case_" + str(self.mesher_cnt)
        aim_file_name = problem_name + 'DEM_Inlet.mdpa'
        aim_path_and_name = os.path.join(os.getcwd(), "generated_mesher_cases", aim_folder_name, aim_file_name)

        # clean the exsisted file first
        if os.path.isfile(aim_path_and_name):
            os.remove(aim_path_and_name)
        
        with open(aim_path_and_name,'a') as f:
            # write the inlet information
            f.write("Begin ModelPartData \n //  VARIABLE_NAME value \nEnd ModelPartData \n \nBegin Properties 0 \nEnd Properties \n \n")
            
            f.write("Begin Nodes\n")
            for inlet_point_dict in self.inlet_points_list:
                f.write(str(inlet_point_dict["id"]) + ' ' + str(inlet_point_dict["p_x"]) + ' ' + str(inlet_point_dict["p_y"]) + ' ' + str(inlet_point_dict["p_z"]) + '\n')
            f.write("End Nodes \n \n")

            f.write("Begin SubModelPart Inlet_INLET // Group INLET // Subtree Inlet\n")
            f.write("Begin SubModelPartData\n")
            f.write("RIGID_BODY_MOTION " + str(inlet_properties["RIGID_BODY_MOTION"]) + '\n')
            f.write("IDENTIFIER Inlet_INLET \n")
            f.write("INJECTOR_ELEMENT_TYPE " + str(inlet_properties["INJECTOR_ELEMENT_TYPE"]) + '\n')
            f.write("ELEMENT_TYPE " + str(inlet_properties["ELEMENT_TYPE"]) + '\n')
            f.write("CONTAINS_CLUSTERS " + str(inlet_properties["CONTAINS_CLUSTERS"]) + '\n')
            f.write("VELOCITY [3] " + str(inlet_properties["VELOCITY"]) + '\n')
            f.write("MAX_RAND_DEVIATION_ANGLE " + str(inlet_properties["MAX_RAND_DEVIATION_ANGLE"]) + '\n')
            f.write("INLET_NUMBER_OF_PARTICLES " + str(inlet_properties["INLET_NUMBER_OF_PARTICLES"]) + '\n')
            f.write("IMPOSED_MASS_FLOW_OPTION " + str(inlet_properties["IMPOSED_MASS_FLOW_OPTION"]) + '\n')
            f.write("INLET_START_TIME " + str(inlet_properties["INLET_START_TIME"]) + '\n')
            f.write("INLET_STOP_TIME " + str(inlet_properties["INLET_STOP_TIME"]) + '\n')
            f.write("RADIUS " + str(inlet_properties["RADIUS"]) + '\n')
            f.write("PROBABILITY_DISTRIBUTION " + str(inlet_properties["PROBABILITY_DISTRIBUTION"]) + '\n')
            f.write("STANDARD_DEVIATION " + str(inlet_properties["STANDARD_DEVIATION"]) + '\n')
            f.write("End SubModelPartData \n")
            f.write("Begin SubModelPartNodes\n")
            for inlet_point_dict in self.inlet_points_list:
                f.write(' ' + str(inlet_point_dict["id"])  + '\n')
            f.write("End SubModelPartNodes \n")
            f.write("End SubModelPart \n \n")
        f.close()

    def CreatDemMeshFile(self, problem_name):

        aim_folder_name = "mesher_case_" + str(self.mesher_cnt)
        aim_file_name = problem_name + 'DEM.mdpa'
        aim_path_and_name = os.path.join(os.getcwd(), "generated_mesher_cases", aim_folder_name, aim_file_name)

        # clean the exsisted file first
        if os.path.isfile(aim_path_and_name):
            os.remove(aim_path_and_name)
        
        with open(aim_path_and_name,'a') as f:
            # write the inlet information
            f.write("Begin ModelPartData \n //  VARIABLE_NAME value \nEnd ModelPartData \n \nBegin Properties 0 \nEnd Properties \n \n")
        f.close()

if __name__ == "__main__":

    TestDEM = CreatFemAndInletMeshFiles()
    problem_name = 'inletPG'
    RVE_length_x = 0.015
    RVE_length_y = 0.015
    RVE_length_z = 0.007
    RVE_size = [RVE_length_x, RVE_length_y, RVE_length_z]
    particle_radius_max = 0.000175
    inlet_properties = {}
    inlet_properties["RIGID_BODY_MOTION"] = 0
    inlet_properties["INJECTOR_ELEMENT_TYPE"] = "SphericParticle3D"
    inlet_properties["ELEMENT_TYPE"] = "SphericParticle3D"
    inlet_properties["CONTAINS_CLUSTERS"] = 0
    inlet_properties["VELOCITY"] = (0.0, -0.55, 0.0)
    inlet_properties["MAX_RAND_DEVIATION_ANGLE"] = 0.01
    inlet_properties["INLET_NUMBER_OF_PARTICLES"] = 50000000
    inlet_properties["IMPOSED_MASS_FLOW_OPTION"] = 0
    inlet_properties["INLET_START_TIME"] = 0.0
    inlet_properties["INLET_STOP_TIME"] = 100.0
    inlet_properties["RADIUS"] = 0.0004
    #inlet_properties["PROBABILITY_DISTRIBUTION"] = "discrete"
    inlet_properties["PROBABILITY_DISTRIBUTION"] = "piecewise_linear"
    inlet_properties["STANDARD_DEVIATION"] = 0.0
    mesher_cnt = 1
    TestDEM.Initialize(RVE_size, particle_radius_max, mesher_cnt)
    TestDEM.CreatFemMeshFile(problem_name)
    TestDEM.CreatInletMeshFile(problem_name, inlet_properties)
    TestDEM.CreatDemMeshFile(problem_name)
