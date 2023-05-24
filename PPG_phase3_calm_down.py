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

class ParticlePackingGenerator(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator() 

    def InitializePackingGenerator(self):

        #define the aim porosity
        self.aim_final_packing_porosity = 0.5
        self.max_porosity_tolerance = 0.03
        self.aim_container_filling_ratio = 0.5 #this means the inlet will stop when the generated particel's volume occupies [aim_container_filling_ratio * container_volume]
        self.max_particle_velocity_in_phase_1_2 = 0.1
        
        self.generator_process_marker_phase_1 = True  # Phase 1: Generate initial particle packing
        self.generator_process_marker_phase_2 = False # Phase 2: Operate on initial particle packing for getting a desired porosity
        self.generator_process_marker_phase_3 = False # Phase 3: Get the final particle packing
        self.final_check_counter = 0
        self.is_running_time_long_enough = False
        self.operation_starting_time = self.time

        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())

        print("********************Phase 1*************************")

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

            #waitting until partciles calm down
            if (self.generator_process_marker_phase_1 is True) and (self.generator_process_marker_phase_2 is False) and (self.generator_process_marker_phase_3 is False):
                aim_time = 0.003
                self.CheckWhetherRunningTimeIsLongEnough(aim_time)
                if self.is_running_time_long_enough:
                    self.CheckVelocityAndChangeOperationMarker()

            if self.generator_process_marker_phase_2:
                aim_time = 0.0001
                self.CheckWhetherRunningTimeIsLongEnough(aim_time)
                if self.is_running_time_long_enough:
                    self.PrintResultsForGid(self.time)
                    exit(0)

        self.final_check_counter += 1

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
            self.generator_process_marker_phase_1 = False
            self.generator_process_marker_phase_2 = True
            self.WriteOutMdpaFileOfParticles('G-TriaxialDEM_1.mdpa')
            print("********************Phase 2*************************")
            self.operation_starting_time = self.time
            self.is_running_time_long_enough = False

    def CheckWhetherRunningTimeIsLongEnough(self, aim_time):
        running_time = self.time - self.operation_starting_time
        if running_time > aim_time:
            self.is_running_time_long_enough = True

    def WriteOutMdpaFileOfParticles(self, output_file_name):

        aim_path_and_name = os.path.join(os.getcwd(), output_file_name)

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

            f.write("Begin Elements SphericContinuumParticle3D// GUI group identifier: Body \n")
            for element in self.spheres_model_part.Elements:
                f.write(str(element.Id) + ' ' + ' 0 ' + str(element.GetNode(0).Id) + '\n')
            f.write("End Elements \n \n")

            f.write("Begin NodalData RADIUS // GUI group identifier: Body \n")
            for node in self.spheres_model_part.Nodes:
                f.write(str(node.Id) + ' ' + ' 0 ' + str(node.GetSolutionStepValue(RADIUS)) + '\n')
            f.write("End NodalData \n \n")

            '''
            if self.is_after_delete_outside_particles:

                f.write("Begin NodalData COHESIVE_GROUP // GUI group identifier: Body \n")
                for node in self.spheres_model_part.Nodes:
                    f.write(str(node.Id) + ' ' + ' 0 ' + " 1 " + '\n')
                f.write("End NodalData \n \n")

                f.write("Begin NodalData SKIN_SPHERE \n End NodalData \n \n")
            '''

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

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ParticlePackingGenerator(model, parameters).Run()
