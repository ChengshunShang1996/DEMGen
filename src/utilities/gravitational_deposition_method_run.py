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

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics.DEMApplication import DEM_procedures as DEM_procedures
import math
from sys import exit
import shutil
import re

class GravationalDepositionMethodRun(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator() 
        self.GetInitialDemSphereVolume()

    def InitializePackingGenerator(self):

        #define the aim porosity
        self.aim_final_packing_porosity = 0.3
        self.max_porosity_tolerance = 0.03
        self.aim_container_filling_ratio = 0.4 #this means the inlet will stop when the generated particel's volume occupies [aim_container_filling_ratio * container_volume]
        self.max_particle_velocity_in_phase_1_2 = 0.01
        
        self.container_filling_ratio = 0.0
        self.initial_sphere_volume = 0.0
        self.final_packing_porosity = 0.0
        self.generator_process_marker_phase_1 = True  # Phase 1: Generate initial particle packing
        self.generator_process_marker_phase_2 = False # Phase 2: Operate on initial particle packing for getting a desired porosity
        self.generator_process_marker_phase_3 = False # Phase 3: Get the final particle packing
        self.is_operations_running = False
        self.is_compressing = False
        self.is_running_more_time = False
        self.input_aim_time = 0.0
        self.is_after_delete_outside_particles = False
        self.final_check_counter = 0
        self.is_last_operations = False

        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())
        
        self.container_shape = "box"  #input: "cylinder" or "box", 'box' in default

        if self.container_shape == "cylinder":
            self.container_radius = 0.025   #modify according to your case
            self.container_height = 0.1   #modify according to your case
            self.container_volume = math.pi * self.container_radius * self.container_radius * self.container_height

        if self.container_shape == "box":
            self.container_lenth  = self.parameters["BoundingBoxMaxX"].GetDouble() - self.parameters["BoundingBoxMinX"].GetDouble()
            self.container_width  = self.parameters["BoundingBoxMaxZ"].GetDouble() - self.parameters["BoundingBoxMinZ"].GetDouble()
            self.container_height = self.parameters["BoundingBoxMaxY"].GetDouble() - self.parameters["BoundingBoxMinY"].GetDouble()
            self.container_volume = self.container_lenth * self.container_width * self.container_height

        #not so important now
        '''
        self.final_packing_shape = "box"  #input: "cylinder" or "box" 

        if self.final_packing_shape == "cylinder":
            self.final_packing_radius = 0.0125   #modify according to your case
            self.final_packing_height = 0.05  #modify according to your case
            self.final_packing_volume = math.pi * self.final_packing_radius * self.final_packing_radius * self.final_packing_height
            self.final_packing_bottom_center_point = KratosMultiphysics.Array3()
            self.final_packing_bottom_center_point[0] = self.final_packing_bottom_center_point[1] = self.final_packing_bottom_center_point[2] = 0.0
            self.final_packing_direction = KratosMultiphysics.Array3()
            self.final_packing_direction[0] = 0.0
            self.final_packing_direction[1] = 1.0
            self.final_packing_direction[2] = 0.0

        if self.final_packing_shape == "box":
            self.final_packing_lenth  = 0.003   #modify according to your case
            self.final_packing_width  = 0.003   #modify according to your case
            self.final_packing_height = 0.003   #modify according to your case
            self.final_packing_volume = self.final_packing_lenth * self.final_packing_width * self.final_packing_height
            self.final_packing_bottom_center_point = KratosMultiphysics.Array3()
            self.final_packing_bottom_center_point[0] = self.final_packing_bottom_center_point[1] = self.final_packing_bottom_center_point[2] = 0.0
            self.final_packing_direction = KratosMultiphysics.Array3()
            self.final_packing_direction[0] = 0.0
            self.final_packing_direction[1] = 1.0
            self.final_packing_direction[2] = 0.0

        print("********************Phase 1*************************")
        '''

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

        if self.final_check_counter == self.final_check_frequency:

            self.final_check_counter = 0

            if self.generator_process_marker_phase_1:
                self.CalculateFillingRatioAndSetInletStop()

            #waitting until partciles calm down
            if (self.generator_process_marker_phase_1 is False) and (self.generator_process_marker_phase_2 is False) and (self.generator_process_marker_phase_3 is False):
                self.CheckVelocityAndChangeOperationMarker()

            #not so important now
            '''
            if self.generator_process_marker_phase_2:
                self.MeasureLocalPorosityOfFinalPacking()
                self.MeasureTotalPorosityOfFinalPacking()
                if self.final_packing_porosity > (1 - self.max_porosity_tolerance) * self.aim_final_packing_porosity and self.final_packing_porosity < (1 + self.max_porosity_tolerance) * self.aim_final_packing_porosity:
                    self.generator_process_marker_phase_2 = False
                    self.generator_process_marker_phase_3 = True
                    self.WriteOutMdpaFileOfParticles('G-TriaxialDEM_2.mdpa')
                    print("********************Phase 3*************************")
                else:
                    if not self.is_operations_running:
                        self.OperationsOnParticlePacking()
                    elif self.is_compressing:
                        #self.CheckVelocityAndChangeOperationMarker()
                        pass
                    elif self.is_running_more_time:
                        self.CheckWhetherRunningTimeIsLongEnough(self.input_aim_time)
                        if self.is_running_time_long_enough:
                            self.CheckVelocityAndChangeOperationMarker()
                    else:
                        predicted_particle_falling_time = (2 * self.container_height / 9.81)**0.5
                        self.CheckWhetherRunningTimeIsLongEnough(predicted_particle_falling_time)
                        if self.is_running_time_long_enough:
                            self.CheckVelocityAndChangeOperationMarker()

            if self.generator_process_marker_phase_3:
                if not self.is_after_delete_outside_particles:
                    self.DeleteOutsideParticles()
                else:
                    self.WriteOutMdpaFileOfParticles('G-TriaxialDEM_3.mdpa')
                    self.PrintResultsForGid(self.time)
                    exit(0)
            '''
        self.final_check_counter += 1

        if self.is_last_operations:
            
            self.CheckWhetherRunningTimeIsLongEnough(self.parameters["NeighbourSearchFrequency"].GetInt() * self.dt)

            if self.is_running_time_long_enough:
                self.WriteOutMdpaFileOfParticles('inletPGDEM.mdpa')
                self.copy_files_and_run_show_results()
                exit(0)

    def GetInitialDemSphereVolume(self):

        for element in self.spheres_model_part.Elements:
            r = element.GetNode(0).GetSolutionStepValue(RADIUS)
            element_volume = 4/3 * math.pi * r * r * r
            self.initial_sphere_volume += element_volume

    def CalculateFillingRatioAndSetInletStop(self):
        
        #calculte container filling ratio
        total_element_volume = 0.0
        for element in self.spheres_model_part.Elements:
            r = element.GetNode(0).GetSolutionStepValue(RADIUS)
            element_volume = 4/3 * math.pi * r * r * r
            total_element_volume += element_volume

        generated_element_volume = total_element_volume - self.initial_sphere_volume
        self.container_filling_ratio = generated_element_volume / self.container_volume

        print("***********Current generated_element_volume is {} and self.container_volume is {}.".format(generated_element_volume, self.container_volume))
        print("***********Current container_filling_ratio is {}. \n".format(self.container_filling_ratio))

        #set Inlet stop time
        if self.container_filling_ratio > self.aim_container_filling_ratio:

            for submp in self.dem_inlet_model_part.SubModelParts:
                if submp.Has(INLET_STOP_TIME):
                    submp[INLET_STOP_TIME] = self.time + self.dt

            self.generator_process_marker_phase_1 = False

    def MeasureLocalPorosityOfFinalPacking(self):
        pass

    def MeasureTotalPorosityOfFinalPacking(self):
        
        selected_element_volume = 0.0
        for node in self.spheres_model_part.Nodes:
            r = node.GetSolutionStepValue(RADIUS)
            x = node.X
            y = node.Y
            z = node.Z
            is_inside_the_final_packing = self.CheckInsideFinalPackingOrNot(x,y,z)
            if is_inside_the_final_packing:
                element_volume = 4/3 * math.pi * r * r * r
                selected_element_volume += element_volume

        self.final_packing_porosity = 1 - (selected_element_volume / self.final_packing_volume)

        print("Aim porosity is {} and currently porosity is {}".format(self.aim_final_packing_porosity, self.final_packing_porosity))

        return self.final_packing_porosity

    def CheckInsideFinalPackingOrNot(self, x, y, z):

        #TODO: final_packing_direction should be included
        
        if self.final_packing_shape == "cylinder":

            if y >= self.final_packing_bottom_center_point[1] and y <= self.final_packing_bottom_center_point[1] + self.final_packing_height:
                if (self.final_packing_bottom_center_point[0] - x)**2 + (self.final_packing_bottom_center_point[2] - z)**2 < self.final_packing_radius * self.final_packing_radius:
                    return True
            else:
                return False

        if self.final_packing_shape == "box":

            if x > self.final_packing_bottom_center_point[0] - 0.5 * self.final_packing_lenth and x < self.final_packing_bottom_center_point[0] + 0.5 * self.final_packing_lenth:
                if y >= self.final_packing_bottom_center_point[1] and y <= self.final_packing_bottom_center_point[1] + self.final_packing_height:
                    if z > self.final_packing_bottom_center_point[2] - 0.5 * self.final_packing_width and z < self.final_packing_bottom_center_point[2] + 0.5 * self.final_packing_width:
                        return True
            else:
                return False
    
    def OperationsOnParticlePacking(self):
        
        print("*******Packing Operations*********")
        
        if self.final_packing_porosity > (1 + self.max_porosity_tolerance) * self.aim_final_packing_porosity:

            #set the plate v = 0.0
            for smp in self.rigid_face_model_part.SubModelParts:
                if smp[IDENTIFIER] == 'TOP':
                    smp[LINEAR_VELOCITY_Y] = 0.0
                if smp[IDENTIFIER] == 'BOTTOM':
                    smp[LINEAR_VELOCITY_Y] = 0.0

            print("You can input a number to achieve:")
            print("1. inverte")
            print("2. compressing")
            print("3. continue")
            print("4. run more time")

            selected_operation = input("Please input the number of the operation: ")

            #inverte operation
            if selected_operation == "1":
                
                self.spheres_model_part.ProcessInfo[GRAVITY] *= -1
                self.is_operations_running = True
                self.operation_starting_time = self.time
                self.is_running_time_long_enough = False

            #compressing operation
            if selected_operation == "2":
                
                for smp in self.rigid_face_model_part.SubModelParts:
                    if smp[IDENTIFIER] == 'TOP':
                        smp[LINEAR_VELOCITY_Y] = -0.05
                    if smp[IDENTIFIER] == 'BOTTOM':
                        smp[LINEAR_VELOCITY_Y] = 0.05

                self.is_operations_running = True
                self.is_compressing = True

            if selected_operation == "3":
                self.generator_process_marker_phase_2 = False
                self.generator_process_marker_phase_3 = True
                self.WriteOutMdpaFileOfParticles('G-TriaxialDEM_2.mdpa')
                print("********************Phase 3*************************")

            if selected_operation == "4":
                self.is_operations_running = True
                self.operation_starting_time = self.time
                self.is_running_time_long_enough = False
                self.is_running_more_time = True
                self.input_aim_time = input("Please input the time you would like to run (s): ")
                

        if self.final_packing_porosity < (1 - self.max_porosity_tolerance) * self.aim_final_packing_porosity:
            
            print("Porosity is lower than aim value.")
            print("Some particles will be deleted!")
                
            delete_particle_count = 0
            while self.final_packing_porosity < (1 - self.max_porosity_tolerance) * self.aim_final_packing_porosity:

                self.RandomDeleteAParticle()
                delete_particle_count += 1
                self.MeasureTotalPorosityOfFinalPacking()
            print("{} particles have been deleted.".format(delete_particle_count))
            self.generator_process_marker_phase_2 = False
            self.generator_process_marker_phase_3 = True
            self.WriteOutMdpaFileOfParticles('G-TriaxialDEM_2.mdpa')
            print("********************Phase 3*************************")

    def RandomDeleteAParticle(self):
        pass

    def CheckVelocityAndChangeOperationMarker(self):
        max_particle_velocity = 0.0
        for node in self.spheres_model_part.Nodes:
            velocity_x = node.GetSolutionStepValue(VELOCITY_X)
            velocity_y = node.GetSolutionStepValue(VELOCITY_Y)
            velocity_z = node.GetSolutionStepValue(VELOCITY_Z)
            velocity_magnitude = (velocity_x * velocity_x + velocity_y * velocity_y + velocity_z * velocity_z)**0.5
            if velocity_magnitude > max_particle_velocity:
                max_particle_velocity = velocity_magnitude
        if max_particle_velocity < self.max_particle_velocity_in_phase_1_2:
            self.is_operations_running = False
            if (self.generator_process_marker_phase_1 is False) and (self.generator_process_marker_phase_2 is False) and (self.generator_process_marker_phase_3 is False):
                self.generator_process_marker_phase_2 = True
                self.DeleteOutsideParticles()
                self.operation_starting_time = self.time
                self.is_last_operations = True
                self.is_running_time_long_enough = False
                #TODO: only Phase One is active here
                #print("********************Phase 2*************************")

    def CheckWhetherRunningTimeIsLongEnough(self, aim_time):
        running_time = self.time - self.operation_starting_time
        if running_time > aim_time:
            self.is_running_time_long_enough = True

    def DeleteOutsideParticles(self):

        '''
        if self.final_packing_shape == "cylinder":
            max_radius = self.final_packing_radius
            center = self.final_packing_bottom_center_point
            tolerance = 0.001 * self.final_packing_radius
            self.PreUtilities.MarkToEraseParticlesOutsideRadiusForGettingCylinder(self.spheres_model_part, max_radius, center, tolerance)
        
        if self.final_packing_shape == "cylinder":
            #for a cylinder, only y direction is important, so x and z are set as very big/small 
            min_x = -1e10
            max_x = 1e10
            min_y = self.final_packing_bottom_center_point[1]
            max_y = self.final_packing_bottom_center_point[1] + self.final_packing_height
            min_z = -1e10
            max_z = 1e10
            tolerance = 0.001 * self.final_packing_height

        if self.final_packing_shape == "box":
            min_x = self.final_packing_bottom_center_point[0] - 0.5 * self.final_packing_lenth
            max_x = self.final_packing_bottom_center_point[0] + 0.5 * self.final_packing_lenth
            min_y = self.final_packing_bottom_center_point[1]
            max_y = self.final_packing_bottom_center_point[1] + self.final_packing_height
            min_z = self.final_packing_bottom_center_point[2] - 0.5 * self.final_packing_width
            max_z = self.final_packing_bottom_center_point[2] + 0.5 * self.final_packing_width
            tolerance = 0.001 * self.final_packing_height
        
        self.PreUtilities.MarkToEraseParticlesOutsideBoundary(self.spheres_model_part, min_x, max_x, min_y, max_y, min_z, max_z, tolerance)

        self.is_after_delete_outside_particles = True
        '''
        min_x = self.parameters["BoundingBoxMinX"].GetDouble() * 1.2
        max_x = self.parameters["BoundingBoxMaxX"].GetDouble() * 1.2
        min_y = self.parameters["BoundingBoxMinY"].GetDouble() * 1.2
        max_y = self.parameters["BoundingBoxMaxY"].GetDouble() / 3.0
        min_z = self.parameters["BoundingBoxMinZ"].GetDouble() * 1.2
        max_z = self.parameters["BoundingBoxMaxZ"].GetDouble() * 1.2
        tolerance = 0.001 * (max_y - min_y)

        self.PreUtilities.MarkToEraseParticlesOutsideBoundary(self.spheres_model_part, min_x, max_x, min_y, max_y, min_z, max_z, tolerance)

    def WriteOutMdpaFileOfParticles(self, output_file_name):

        self.clear_old_and_create_new_show_packing_case_folder()
        aim_path_and_name = os.path.join(os.getcwd(), 'show_packing', output_file_name)

        # clean the exsisted file first
        if os.path.isfile(aim_path_and_name):
            os.remove(aim_path_and_name)
        
        with open(aim_path_and_name,'a') as f:
            # write the particle information
            f.write("Begin ModelPartData \n //  VARIABLE_NAME value \n End ModelPartData \n \n Begin Properties 0 \n End Properties \n \n")
            f.write("Begin Nodes\n")
            for node in self.spheres_model_part.Nodes:
                f.write(str(node.Id) + ' ' + str(node.X) + ' ' + str(node.Y) + ' ' + str(node.Z) + '\n')
            f.write("End Nodes \n \n")

            f.write("Begin Elements SphericParticle3D// GUI group identifier: Body \n")
            for element in self.spheres_model_part.Elements:
                f.write(str(element.Id) + ' ' + ' 0 ' + str(element.GetNode(0).Id) + '\n')
            f.write("End Elements \n \n")

            f.write("Begin NodalData RADIUS // GUI group identifier: Body \n")
            for node in self.spheres_model_part.Nodes:
                f.write(str(node.Id) + ' ' + ' 0 ' + str(node.GetSolutionStepValue(RADIUS)) + '\n')
            f.write("End NodalData \n \n")

            if self.is_after_delete_outside_particles:

                f.write("Begin NodalData COHESIVE_GROUP // GUI group identifier: Body \n")
                for node in self.spheres_model_part.Nodes:
                    f.write(str(node.Id) + ' ' + ' 0 ' + " 1 " + '\n')
                f.write("End NodalData \n \n")

                f.write("Begin NodalData SKIN_SPHERE \n End NodalData \n \n")

            f.write("Begin SubModelPart DEMParts_Body // Group Body // Subtree DEMParts \n Begin SubModelPartNodes \n")
            for node in self.spheres_model_part.Nodes:
                f.write(str(node.Id) + '\n')
            f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
            for element in self.spheres_model_part.Elements:
                f.write(str(element.Id) + '\n')
            f.write("End SubModelPartElements \n")
            f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n \n")

            f.close()

        print("Successfully write out GID DEM.mdpa file!")

    def copy_files_and_run_show_results(self):

        self.copy_seed_files_to_aim_folders()

        aim_path = os.path.join(os.getcwd(),'show_packing')
        os.chdir(aim_path)
        if os.name == 'nt': # for windows
            os.system("python show_packing.py")
        else: # for linux
            os.system("python3 show_packing.py")

    def clear_old_and_create_new_show_packing_case_folder(self):

        aim_path = os.path.join(os.getcwd(),'show_packing')

        if os.path.exists(aim_path):
            shutil.rmtree(aim_path, ignore_errors=True)
            os.makedirs(aim_path)
        else:
            os.makedirs(aim_path)
    
    def copy_seed_files_to_aim_folders(self):
        
        aim_path = os.path.join(os.getcwd(), 'show_packing')

        seed_file_name_list = ['MaterialsDEM.json', 'ProjectParametersDEM.json', 'inletPGDEM_FEM_boundary.mdpa', 'show_packing.py']
        for seed_file_name in seed_file_name_list:
            seed_file_path_and_name = os.path.join(os.getcwd(), seed_file_name)
            aim_file_path_and_name = os.path.join(aim_path, seed_file_name)

            if seed_file_name == 'ProjectParametersDEM.json':
                with open(seed_file_path_and_name, "r") as f_material:
                    with open(aim_file_path_and_name, "w") as f_material_w:
                        for line in f_material.readlines():
                            if "dem_inlet_option" in line:
                                line = line.replace("true", 'false')
                            elif "FinalTime" in line:
                                line = "    \"FinalTime\"                      : " + str(self.dt * 2) + ', \n'
                            elif "\"GraphExportFreq\"" in line:
                                line = "    \"GraphExportFreq\"                : " + str(self.dt) + ', \n'
                            elif "VelTrapGraphExportFreq" in line:
                                line = "    \"VelTrapGraphExportFreq\"         : " + str(self.dt) + ', \n'
                            elif "OutputTimeStep" in line:
                                line = "    \"OutputTimeStep\"                 : " + str(self.dt) + ', \n'
                            f_material_w.write(line)
            
            elif seed_file_name == 'MaterialsDEM.json':
                with open(seed_file_path_and_name, "r") as f_material:
                    with open(aim_file_path_and_name, "w") as f_material_w:
                        for line in f_material.readlines():
                            if "material_assignation_table" in line:
                                line = '\"material_assignation_table\" : [[\"RigidFacePart\",\"DEM-DefaultMaterial\"],[\"SpheresPart\",\"DEM-DefaultMaterial\"]] \n'
                            f_material_w.write(line)
            else:
                shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    GravationalDepositionMethodRun(model, parameters).Run()
