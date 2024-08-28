#/////////////////////////////////////////////////
#// Main author: Chengshun Shang (CIMNE)
#// Email: chengshun.shang1996@gmail.com
#// Date: March 2023
#/////////////////////////////////////////////////

import math

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics.DEMApplication import DEM_procedures as DEM_procedures


class GenerateInitialPacking(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator() 
        self.GetInitialDemSphereVolume()

    def InitializePackingGenerator(self):

        #define the aim porosity
        self.aim_final_packing_porosity = 0.5
        self.max_porosity_tolerance = 0.03
        self.aim_container_filling_ratio = 0.5 #this means the inlet will stop when the generated particel's volume occupies [aim_container_filling_ratio * container_volume]
        self.max_particle_velocity_in_phase_1_2 = 0.1
        
        self.container_filling_ratio = 0.0
        self.initial_sphere_volume = 0.0

        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())
        
        self.container_lenth  = 0.0   #modify according to your case
        self.container_width  = 0.0   #modify according to your case
        self.container_height = 0.0   #modify according to your case
        self.container_volume = self.container_lenth * self.container_width * self.container_height

        print("********************Initialization finish*************************")

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

        self.final_check_counter += 1

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
                self.WriteOutMdpaFileOfParticles('G-TriaxialDEM_1.mdpa')
                print("********************Phase 2*************************")

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

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    GenerateInitialPacking(model, parameters).Run()
