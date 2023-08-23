#/////////////////////////////////////////////////
#// Main author: Chengshun Shang (CIMNE)
#// Email: chengshun.shang1996@gmail.com
#// Date: August 2023
#/////////////////////////////////////////////////

import os

class creat_fem_and_inlet_mesh_files():

    def __init__(self) -> None:  
        self.fem_points_list = []
        self.fem_elements_list = []

    def initialize(self, RVE_size):

        RVE_length_x = RVE_size[0]
        RVE_length_y = RVE_size[1]
        RVE_length_z = RVE_size[2]
        
        #we need creat a cuboid which has a height of two times of the RVE 
        #------------------for creating FEM boundary mesh (start)---------------------------
        for i in range(1, 9):

            fem_point_dict = {
                    "id" : 0,
                    "p_x" : 0.0,
                    "p_y" : 0.0,
                    "p_z" : 0.0
                    }
            
            if i == 1:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = -0.5 * RVE_length_x
                fem_point_dict["p_y"] = -0.5 * RVE_length_y
                fem_point_dict["p_z"] = 0.0
                self.fem_points_list.append(fem_point_dict)
            elif i == 2:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = 0.5 * RVE_length_x
                fem_point_dict["p_y"] = -0.5 * RVE_length_y
                fem_point_dict["p_z"] = 0.0
                self.fem_points_list.append(fem_point_dict)
            elif i == 3:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = 0.5 * RVE_length_x
                fem_point_dict["p_y"] = 0.5 * RVE_length_y
                fem_point_dict["p_z"] = 0.0
                self.fem_points_list.append(fem_point_dict)
            elif i == 4:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = -0.5 * RVE_length_x
                fem_point_dict["p_y"] = 0.5 * RVE_length_y
                fem_point_dict["p_z"] = 0.0
                self.fem_points_list.append(fem_point_dict)
            elif i == 5:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = -0.5 * RVE_length_x
                fem_point_dict["p_y"] = -0.5 * RVE_length_y
                fem_point_dict["p_z"] = RVE_length_z * 2
                self.fem_points_list.append(fem_point_dict)
            elif i == 6:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = 0.5 * RVE_length_x
                fem_point_dict["p_y"] = -0.5 * RVE_length_y
                fem_point_dict["p_z"] = RVE_length_z * 2
                self.fem_points_list.append(fem_point_dict)
            elif i == 7:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = 0.5 * RVE_length_x
                fem_point_dict["p_y"] = 0.5 * RVE_length_y
                fem_point_dict["p_z"] = RVE_length_z * 2
                self.fem_points_list.append(fem_point_dict)
            elif i == 8:
                fem_point_dict["id"] = i
                fem_point_dict["p_x"] = -0.5 * RVE_length_x
                fem_point_dict["p_y"] = 0.5 * RVE_length_y
                fem_point_dict["p_z"] = RVE_length_z * 2
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
        


        #---------------------for creating inlet mesh (end)-----------------------------
        

    def creatFemMeshFile(self, problem_name):
        
        aim_file_name = problem_name + 'DEM_FEM_boundary.mdpa'
        aim_path_and_name = os.path.join(os.getcwd(), aim_file_name)

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
                    f.write(str(fem_element_dict["id"]) + ' ' + str(fem_element_dict["p_1_id"]) + ' ' + str(fem_element_dict["p_2_id"]) + ' ' + str(fem_element_dict["p_3_id"]) + ' ' + str(fem_element_dict["p_4_id"]) + '\n')
                    break
            f.write("End Conditions \n \n")

            f.write("Begin Conditions RigidFace3D4N// GUI group identifier: BOTTOM \n")
            for fem_element_dict in self.fem_elements_list:
                if fem_element_dict["id"] == 1:
                    f.write(str(fem_element_dict["id"]) + ' ' + str(fem_element_dict["p_1_id"]) + ' ' + str(fem_element_dict["p_2_id"]) + ' ' + str(fem_element_dict["p_3_id"]) + ' ' + str(fem_element_dict["p_4_id"]) + '\n')
                    break
            f.write("End Conditions \n \n")

            f.write("Begin Conditions RigidFace3D4N// GUI group identifier: WALL \n")
            for fem_element_dict in self.fem_elements_list:
                if fem_element_dict["id"] != 1 and fem_element_dict["id"] != 2:
                    f.write(str(fem_element_dict["id"]) + ' ' + str(fem_element_dict["p_1_id"]) + ' ' + str(fem_element_dict["p_2_id"]) + ' ' + str(fem_element_dict["p_3_id"]) + ' ' + str(fem_element_dict["p_4_id"]) + '\n')
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

    def creatInletMeshFile(self, problem_name):
        pass

if __name__ == "__main__":

    TestDEM = creat_fem_and_inlet_mesh_files()
    problem_name = 'inletPG'
    RVE_length_x = 0.003
    RVE_length_y = 0.003
    RVE_length_z = 0.003
    RVE_size = [RVE_length_x, RVE_length_y, RVE_length_z]
    particle_radius_max = 0.001
    TestDEM.initialize(RVE_size)
    TestDEM.creatFemMeshFile(problem_name)
