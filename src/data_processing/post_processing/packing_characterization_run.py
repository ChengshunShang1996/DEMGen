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

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics.DEMApplication import DEM_procedures as DEM_procedures
import math
from sys import exit
import matplotlib.pyplot as plt
import time
import numpy as np

class ParticlePackingGenerator(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator() 
        #self.GetInitialDemSphereVolume()

    def InitializePackingGenerator(self):

        #define the aim porosity
        self.aim_final_packing_porosity = 0.5
        self.max_porosity_tolerance = 0.03
        self.aim_container_filling_ratio = 0.5 #this means the inlet will stop when the generated particel's volume occupies [aim_container_filling_ratio * container_volume]
        self.max_particle_velocity_in_phase_1_2 = 0.1
        
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

        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())
        
        self.container_shape = "cylinder"  #input: "cylinder" or "box"  

        if self.container_shape == "cylinder":
            self.container_radius = 0.025   #modify according to your case
            self.container_height = 0.1   #modify according to your case
            self.container_volume = math.pi * self.container_radius * self.container_radius * self.container_height

        if self.container_shape == "box":
            self.container_lenth  = 0.0   #modify according to your case
            self.container_width  = 0.0   #modify according to your case
            self.container_height = 0.0   #modify according to your cas�0�2e
            self.container_volume = self.container_lenth * self.container_width * self.container_height

        self.container_x_min = -0.0015
        self.container_x_max = 0.0225
        self.container_y_min = 0.0
        self.container_y_max = 0.024
        self.container_z_min = -0.0015
        self.container_z_max = 0.0225

        self.final_packing_shape = "cylinder"  #input: "cylinder" or "box" 

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
            self.final_packing_lenth  = 0.0   #modify according to your case
            self.final_packing_width  = 0.0   #modify according to your case
            self.final_packing_height = 0.0   #modify according to your case
            self.final_packing_volume = self.final_packing_lenth * self.final_packing_width * self.final_packing_height
            self.final_packing_bottom_center_point = KratosMultiphysics.Array3()
            self.final_packing_bottom_center_point[0] = self.final_packing_bottom_center_point[1] = self.final_packing_bottom_center_point[2] = 0.0
            self.final_packing_direction = KratosMultiphysics.Array3()
            self.final_packing_direction[0] = 0.0
            self.final_packing_direction[1] = 1.0
            self.final_packing_direction[2] = 0.0

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
        #self.MeasureLocalPorosityOfFinalPacking()
        #self.MeasureLocalPorosityWithDifferentRadius()
        self.MeasureLocalPorosityWithDifferentSideLength()
        exit(0)

    def MeasureLocalPorosityWithDifferentRadius(self):
        
        print("start measurement")
        radius = 0.0005
        radius_increasement = 0.0002
        center_x_ini = 0.012 - 0.5 * (0.003 - 2 * 0.001 * 0.11800010000236323)
        center_y_ini = 0.012
        center_z_ini = 0.012 - 0.5 * (0.003 - 2 * 0.001 * 0.11800010000236323)
        distance_between_two_measure_sphere = 0.0002
        self.container_x_min = -0.5 * (0.003 - 2 * 0.001 * 0.11800010000236323)
        self.container_x_max = 0.024 - 0.5 * (0.003 - 2 * 0.001 * 0.11800010000236323)
        self.container_y_min = 0.0
        self.container_y_max = 0.024
        self.container_z_min = -0.5 * (0.003 - 2 * 0.001 * 0.11800010000236323)
        self.container_z_max = 0.024 - 0.5 * (0.003 - 2 * 0.001 * 0.11800010000236323)

        inside_of_container = True
        n_R = 0
        measure_R_list = []
        measured_porosity_mean = []
        measured_porosity_max = []
        measured_porosity_min = []

        while inside_of_container:

            radius += n_R * radius_increasement
            measured_porosity = []
            for i in [-1,0,1]:
                center_x = center_x_ini + i * distance_between_two_measure_sphere
                center_y = center_y_ini
                center_z = center_z_ini

                if center_x - radius < self.container_x_min or center_x + radius > self.container_x_max:
                    print("The measure sphere is out of the boundary. Please redefine the initial center coordinate x.")
                    inside_of_container = False
                elif center_y - radius < self.container_y_min or center_y + radius > self.container_y_max:
                    print("The measure sphere is out of the boundary. Please redefine the initial center coordinate y.")
                    inside_of_container = False
                elif center_z - radius < self.container_z_min or center_z + radius > self.container_z_max:
                    print("The measure sphere is out of the boundary. Please redefine the initial center coordinate z.")
                    inside_of_container = False
                else:
                    measured_porosity.append(self.MeasureSphereForGettingPackingProperties(radius, center_x, center_y, center_z, 'porosity'))

            
            if inside_of_container:
                measure_R_list.append(radius)
                sum_poro = 0.0
                for poro in measured_porosity:
                    sum_poro += poro
                mean_poro = sum_poro / 3.0
                measured_porosity_mean.append(mean_poro)
                measured_porosity_max.append(max(measured_porosity) - mean_poro)
                measured_porosity_min.append(mean_poro - min(measured_porosity))
                n_R += 1
                print(n_R)

        plt.errorbar(measure_R_list, measured_porosity_mean, yerr=(measured_porosity_min, measured_porosity_max) )
        #plt.legend()
        plt.show()
        
        with open("porosity_diff_radius.txt", "w") as f_w:
            for i in range(len(measure_R_list)):
                f_w.write(str(measure_R_list[i]) + ' '+ str(measured_porosity_mean[i]) + ' '+ str(measured_porosity_max[i]) + ' '+ str(measured_porosity_min[i]) + '\n')

        exit(0)

    def MeasureLocalPorosityWithDifferentSideLength(self):
        
        print("start measurement")
        mean_diameter = 0.0002
        RVE_lambda = 4
        side_length = mean_diameter * RVE_lambda
        side_length_max = 0.005
        center_x = 0.0
        center_y = 0.0
        center_z = 0.0
        self.container_x_min = -0.0025
        self.container_x_max = 0.0025
        self.container_y_min = -0.0025
        self.container_y_max = 0.0025
        self.container_z_min = -0.0025
        self.container_z_max = 0.0025

        RVE_lambda_list = []
        measured_packing_density = []
        measured_averaged_coordination_number = []
        measured_eigenvalues = []
        measured_second_invariant_of_deviatoric_tensor = []
        while side_length <= side_length_max:

            RVE_lambda_list.append(RVE_lambda)
            #measured_packing_density.append(1 - self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'porosity'))
            measured_packing_density.append(1 - self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'porosity'))
            measured_averaged_coordination_number.append(self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'averaged_coordination_number'))
            eigenvalues, second_invariant_of_deviatoric_tensor = self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'fabric_tensor')
            measured_eigenvalues.append(eigenvalues)
            measured_second_invariant_of_deviatoric_tensor.append(second_invariant_of_deviatoric_tensor)
            self.MeasureSphereForGettingRadialDistributionFunction(side_length/2, center_x, center_y, center_z, mean_diameter/15, mean_diameter)
            self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'voronoi_input_data')

            RVE_lambda += 2
            side_length = mean_diameter * RVE_lambda
            side_length = round(side_length, 4)
        
        with open("packing_properties_1.1.txt", "w") as f_w:
            for i in range(len(RVE_lambda_list)):
                f_w.write(str(RVE_lambda_list[i]) + ' '+ str(measured_packing_density[i]) + ' '+ str(measured_averaged_coordination_number[i]) + ' '+\
                           str(measured_eigenvalues[i][0]) + ' '+ str(measured_eigenvalues[i][1]) + ' '+ str(measured_eigenvalues[i][2]) + ' ' +\
                            str(measured_second_invariant_of_deviatoric_tensor[i]) + '\n')

        print("Measurement finish")


if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ParticlePackingGenerator(model, parameters).Run()
