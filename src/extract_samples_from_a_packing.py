#/////////////////////////////////////////////////
#// Main author: Chengshun Shang (CIMNE)
#// Email: chengshun.shang1996@gmail.com
#// Date: March 2023
#/////////////////////////////////////////////////

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics.DEMApplication import DEM_procedures as DEM_procedures
import math
from sys import exit
import numpy as np
from stl import mesh

class ExtractSamplesFromAPacking(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator() 

    def InitializePackingGenerator(self):
        
        self.final_packing_shape = "rabbit"  #input: "cylinder" or "box" 

        if self.final_packing_shape == "cylinder":
            self.final_packing_radius = 0.0025   #modify according to your case
            self.final_packing_height = 0.01  #modify according to your case
            self.final_packing_volume = math.pi * self.final_packing_radius * self.final_packing_radius * self.final_packing_height
            self.final_packing_center_point = KratosMultiphysics.Array3()
            self.final_packing_center_point[0] = 0.0105
            self.final_packing_center_point[1] = 0.012
            self.final_packing_center_point[2] = 0.0105
            self.final_packing_direction_theta = 0.0  #Unit: degree

        if self.final_packing_shape == "box":
            self.final_packing_lenth  = 0.0   #modify according to your case
            self.final_packing_width  = 0.0   #modify according to your case
            self.final_packing_height = 0.0   #modify according to your case
            self.final_packing_volume = self.final_packing_lenth * self.final_packing_width * self.final_packing_height
            self.final_packing_bottom_center_point = KratosMultiphysics.Array3()
            self.final_packing_center_point[0] = 0.0
            self.final_packing_center_point[1] = 0.0
            self.final_packing_center_point[2] = 0.0
            self.final_packing_direction_theta = 0.0  #Unit: degree

        if self.final_packing_shape == "rabbit":
            self.mesh_data = []
            vertices = np.empty((3, 3))
            i = 0
            # Read the mesh file line by line
            with open('ball.stl', 'r') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("vertex"):
                        # Parse and split the vertex line
                        x, y, z = line.split()[1:]
                        vertices[i][0] = float(x)
                        vertices[i][1] = float(y)
                        vertices[i][2] = float(z)
                        i += 1
                    elif line.startswith("endloop"):
                        # End of a subarray, append it to the main list
                        self.mesh_data.append(vertices)
                        vertices = np.empty((3, 3))
                        i = 0

        print("********************Finish initialization*************************")

    def RunSolutionLoop(self):

        while self.KeepAdvancingSolutionLoop():
            self.time = self._GetSolver().AdvanceInTime(self.time)
            self.InitializeSolutionStep()
            self._GetSolver().Predict()
            self._GetSolver().SolveSolutionStep()
            self.FinalizeSolutionStep()
            self.OutputSolutionStep()

    def KeepAdvancingSolutionLoop(self):
        
        return self.time < self.end_time
    
    def FinalizeSolutionStep(self):
        super().FinalizeSolutionStep()

        '''
        for i in range(10):
            p_pram_list = []
            theta  = self.final_packing_direction_theta + i * 10
            p_pram_list = self.extract_sample_from_the_packing(theta)
            porosity_measured = self.MeasureTotalPorosityOfFinalPacking(p_pram_list)
            output_file_name = "DEM_" + str(theta) + '_'+ str(round(porosity_measured,2)) +".mdpa"
            self.WriteOutMdpaFileOfParticles(p_pram_list, output_file_name)
        '''
        p_pram_list = self.extract_sample_from_the_packing(0.0)
        self.WriteOutMdpaFileOfParticles(p_pram_list, "myrabbit.mdpa")          
        exit(0)

    def extract_sample_from_the_packing(self, theta):
        
        p_pram_list = []
        if self.final_packing_shape == "cylinder":
            
            temp_cnt = 1
            for node in self.spheres_model_part.Nodes:
                r = node.GetSolutionStepValue(RADIUS)
                x = node.X
                y = node.Y
                z = node.Z
                p_pram_dict = {
                    "id" : 0,
                    "p_x" : 0.0,
                    "p_y" : 0.0,
                    "p_z" : 0.0,
                    "radius" : 0.0,
                    "p_v_x" : 0.0,
                    "p_v_y" : 0.0,
                    "p_v_z" : 0.0,
                    "p_ele_id": 0,
                    "p_group_id": 0
                    }
                if self.is_sphere_inside_cylinder(theta, x, y, z, r):
                    p_pram_dict["id"] = temp_cnt
                    p_pram_dict["p_x"] = x
                    p_pram_dict["p_y"] = y
                    p_pram_dict["p_z"] = z
                    p_pram_dict["radius"] = r
                    p_pram_dict["p_ele_id"] = temp_cnt
                    p_pram_list.append(p_pram_dict)
                    temp_cnt += 1
            
            return p_pram_list
        
        elif self.final_packing_shape == "rabbit":
            temp_cnt = 1
            for node in self.spheres_model_part.Nodes:
                r = node.GetSolutionStepValue(RADIUS)
                x = node.X
                y = node.Y
                z = node.Z
                p_pram_dict = {
                    "id" : 0,
                    "p_x" : 0.0,
                    "p_y" : 0.0,
                    "p_z" : 0.0,
                    "radius" : 0.0,
                    "p_v_x" : 0.0,
                    "p_v_y" : 0.0,
                    "p_v_z" : 0.0,
                    "p_ele_id": 0,
                    "p_group_id": 0
                    }
                sphere_center = np.array([x, y, z])
                if self.is_sphere_inside_rabbit_stl(sphere_center, r):
                    p_pram_dict["id"] = temp_cnt
                    p_pram_dict["p_x"] = x
                    p_pram_dict["p_y"] = y
                    p_pram_dict["p_z"] = z
                    p_pram_dict["radius"] = r
                    p_pram_dict["p_ele_id"] = temp_cnt
                    p_pram_list.append(p_pram_dict)
                    print("add " + str(temp_cnt))
                    temp_cnt += 1
                #if temp_cnt > 1000:
                #    break
            return p_pram_list

    def MeasureTotalPorosityOfFinalPacking(self, p_pram_list):
        
        selected_element_volume = 0.0
        for p_pram_dict in p_pram_list:
            r = p_pram_dict["radius"]
            element_volume = 4/3 * math.pi * r * r * r
            selected_element_volume += element_volume

        final_packing_porosity = 1 - (selected_element_volume / self.final_packing_volume)

        return final_packing_porosity

    def is_sphere_inside_cylinder(self, theta, sx, sy, sz, sr):
        # Rotate the cylinder's coordinate system back to horizontal
        angle_rad = math.radians(theta)
        sx_rot = (sx - self.final_packing_center_point[0]) * math.cos(angle_rad) + (sy - self.final_packing_center_point[1]) * math.sin(angle_rad) + self.final_packing_center_point[0]
        sy_rot = (sy - self.final_packing_center_point[1]) * math.cos(angle_rad) - (sx - self.final_packing_center_point[0]) * math.sin(angle_rad) + self.final_packing_center_point[1]
        sz_rot = sz

        # Calculate the distance from the center of the sphere to the center of the cylinder in the horizontal plane
        distance = math.sqrt((sx_rot - self.final_packing_center_point[0]) ** 2 + (sz_rot - self.final_packing_center_point[2]) ** 2)

        # Determine if the ball is inside the cylinder
        if self.final_packing_center_point[1] - 0.5 * self.final_packing_height <= sy_rot <= self.final_packing_center_point[1] + 0.5 * self.final_packing_height and distance + sr <= self.final_packing_radius:
            return True
        else:
            return False
        
    def is_sphere_inside_rectangular_prism(self, theta, cx, cy, cz, l, w, h, sx, sy, sz, sr):
        # Rotate the cuboid's coordinate system back to horizontal
        angle_rad = math.radians(theta)
        sx_rot = (sx - cx) * math.cos(angle_rad) + (sy - cy) * math.sin(angle_rad) + cx
        sy_rot = (sy - cy) * math.cos(angle_rad) - (sx - cx) * math.sin(angle_rad) + cy
        sz_rot = sz

        # Calculate the distance from the center of the sphere to the boundary of the cuboid
        dx = max(abs(sx_rot - cx) - l / 2, 0)
        dy = max(abs(sy_rot - cy) - w / 2, 0)
        dz = max(abs(sz_rot - cz) - h / 2, 0)
        distance = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

        # Determine if the ball is inside the cuboid
        if distance + sr <= min(l, w, h) / 2:
            return True
        else:
            return False
        
    def ray_intersects_triangle(self, ray_origin, ray_direction, triangle):
        E1 = triangle[1] - triangle[0]
        E2 = triangle[2] - triangle[0]
        #print(triangle[0])
        #print(triangle[1])
        #print(triangle[2])
        #print(E1)
        #print(E2)
        p = np.cross(ray_direction, E2)
        det = np.dot(E1, p)
        epsilon = 1e-10

        # The ray intersects the triangle parallel or back
        if abs(det) < epsilon:
            return False

        inv_det = 1.0 / det
        t = ray_origin - triangle[0]

        u = np.dot(t, p) * inv_det
        if u < 0.0 or u > 1.0:
            return False

        q = np.cross(t, E1)
        v = np.dot(ray_direction, q) * inv_det
        if v < 0.0 or u + v > 1.0:
            return False

        t = np.dot(E2, q) * inv_det
        if t > epsilon:
            return True

        return False

    def is_sphere_inside_rabbit_stl(self, sphere_center, sphere_radius):
        # Load STL file
        #mesh_data = mesh.Mesh.from_file(stl_file_path)

        # Check if the sphere is completely contained within the STL mesh
        inter_cnt = 0
        surface_cnt = 0
        #for triangle in mesh_data.vectors:
        for triangle in self.mesh_data:
            #for i in range(3):
                #vertex = triangle[i]
            #triangle_center = np.mean(triangle, axis=0)
            ray_origin = sphere_center
            ray_direction = np.array([1.0, 0.0, 0.0])

            # Adjust ray direction and length to account for sphere radius
            ray_direction_normalized = ray_direction / np.linalg.norm(ray_direction)
            #ray_direction_scaled = ray_direction_normalized * (np.linalg.norm(ray_direction) + sphere_radius)

            if self.ray_intersects_triangle(ray_origin, ray_direction_normalized, triangle):
                inter_cnt += 1
                #print(ray_origin)
                #print(ray_direction_normalized)
                #print(triangle)
                #print(self.ray_intersects_triangle(ray_origin, ray_direction_normalized, triangle))
            surface_cnt += 1    
        if inter_cnt % 2 == 0:  
            return False
        else:
            return True

    def WriteOutMdpaFileOfParticles(self, p_pram_list, output_file_name):

        aim_path_and_name = os.path.join(os.getcwd(), output_file_name)

        # clean the exsisted file first
        if os.path.isfile(aim_path_and_name):
            os.remove(aim_path_and_name)
        
        with open(aim_path_and_name,'a') as f:
            # write the particle information
            f.write("Begin ModelPartData \n //  VARIABLE_NAME value \n End ModelPartData \n \n Begin Properties 0 \n End Properties \n \n")
            f.write("Begin Nodes\n")
            for p_pram_dict in p_pram_list:
                f.write(str(p_pram_dict["id"]) + ' ' + str(p_pram_dict["p_x"]) + ' ' + str(p_pram_dict["p_y"]) + ' ' + str(p_pram_dict["p_z"]) + '\n')
            f.write("End Nodes \n \n")

            f.write("Begin Elements SphericContinuumParticle3D// GUI group identifier: Body \n")
            for p_pram_dict in p_pram_list:
                f.write(str(p_pram_dict["p_ele_id"]) + ' ' + ' 0 ' + str(p_pram_dict["id"]) + '\n')
            f.write("End Elements \n \n")

            f.write("Begin NodalData RADIUS // GUI group identifier: Body \n")
            for p_pram_dict in p_pram_list:
                f.write(str(p_pram_dict["id"]) + ' ' + ' 0 ' + str(p_pram_dict["radius"]) + '\n')
            f.write("End NodalData \n \n")

            ''' only works for continuum DEM calculation
            f.write("Begin NodalData COHESIVE_GROUP // GUI group identifier: Body \n")
            for p_pram_dict in p_pram_list:
                f.write(str(p_pram_dict["id"]) + ' ' + ' 0 ' + " 1 " + '\n')
            f.write("End NodalData \n \n")

            f.write("Begin NodalData SKIN_SPHERE \n End NodalData \n \n")
            '''

            f.write("Begin SubModelPart DEMParts_Body // Group Body // Subtree DEMParts \n Begin SubModelPartNodes \n")
            for p_pram_dict in p_pram_list:
                if p_pram_dict["p_group_id"] == 0:
                    f.write(str(p_pram_dict["id"]) + '\n')
            f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
            for p_pram_dict in p_pram_list:
                if p_pram_dict["p_group_id"] == 0:
                    f.write(str(p_pram_dict["p_ele_id"]) + '\n')
            f.write("End SubModelPartElements \n")
            f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n \n")

            #write out joint group
            joint_exist = False
            for p_pram_dict in p_pram_list:
                if p_pram_dict["p_group_id"] == 1:
                    joint_exist = True

            if joint_exist:
                f.write("Begin SubModelPart DEMParts_Joint // Group Joint // Subtree DEMParts \n Begin SubModelPartNodes \n")
                for p_pram_dict in p_pram_list:
                    if p_pram_dict["p_group_id"] == 1:
                        f.write(str(p_pram_dict["id"]) + '\n')
                f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
                for p_pram_dict in p_pram_list:
                    if p_pram_dict["p_group_id"] == 1:
                        f.write(str(p_pram_dict["p_ele_id"]) + '\n')
                f.write("End SubModelPartElements \n")
                f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n")

            f.close()

        print("Successfully write out GID DEM.mdpa file!")

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ExtractSamplesFromAPacking(model, parameters).Run()

    '''
    TestFun = ExtractSamplesFromAPacking(model, parameters)
    TestFun.InitializePackingGenerator()
    ray_origin = np.array([-1.0, 0.0, 0.0])
    ray_direction = np.array([1.0, 0.0, 0.0])

    triangle = np.array([[ 0.00173205081, -0.001,  0.0],
                        [ 0.002, -1.2246468e-19,  0.0],
                        [ 0.00164024054, -0.00031979321, -0.00109879173]])
    print(ray_origin)
    print(ray_direction)
    print(triangle)
    Checker = TestFun.ray_intersects_triangle(ray_origin, ray_direction, triangle)
    print(Checker)
    print('--------------------------------')
    
    r = 1e-5
    sphere_center = np.array([-1.0, 0.0, 0.0])
    Checker2 = TestFun.is_sphere_inside_rabbit_stl(sphere_center, r)
    print(Checker2)
    '''

