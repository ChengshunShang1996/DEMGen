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
        self.MeasureLocalPorosityWithDifferentRadius()
        #self.MeasureTotalPorosityOfFinalPacking()
        #self.MeasurePSD()

    def MeasureLocalPorosityOfFinalPacking(self):
        
        print("start measurement")
        radius = 0.001
        distance_between_two_measure_sphere = 0.0005
        center_x_ini = 0.0005
        center_y_ini = 0.002
        center_z_ini = 0.0005
        self.container_x_min = -0.0013499998999967166
        self.container_x_max = 0.0225
        self.container_y_min = 0.0
        self.container_y_max = 0.024
        self.container_z_min = -0.0013499998999967166
        self.container_z_max = 0.0225

        if center_x_ini - radius < self.container_x_min or center_x_ini + radius > self.container_x_max:
            print("The measure sphere is out of the boundary. Please redefine the initial center coordinate x.")
            exit(0)
        elif center_y_ini - radius < self.container_y_min or center_y_ini + radius > self.container_y_max:
            print("The measure sphere is out of the boundary. Please redefine the initial center coordinate y.")
            exit(0)
        elif center_z_ini - radius < self.container_z_min or center_z_ini + radius > self.container_z_max:
            print("The measure sphere is out of the boundary. Please redefine the initial center coordinate z.")
            exit(0)

        x_direction_continuue = y_direction_continuue = z_direction_continuue = True
        n_x = 0
        n_y = 0
        n_z = 0
        measure_x_list = []
        measure_y_list = []
        measured_porosity = []

        while z_direction_continuue:

            center_z = center_z_ini + n_z * distance_between_two_measure_sphere
            y_direction_continuue = True
            n_y = 0

            while y_direction_continuue:

                center_y = center_y_ini + n_y * distance_between_two_measure_sphere

                if center_y + radius > self.container_y_max:
                    
                        y_direction_continuue = False
                else:
                    x_direction_continuue = True
                    n_x = 0

                    while x_direction_continuue:

                        center_x = center_x_ini + n_x * distance_between_two_measure_sphere

                        if center_x + radius > self.container_x_max:
                            x_direction_continuue = False
                        else:
                            measure_x_list.append(center_x)
                            measure_y_list.append(center_y)
                            measured_porosity.append(self.MeasureSphereForGettingPackingProperties(radius, center_x, center_y, center_z, 'porosity'))
                        print(n_x)
                        n_x +=1
                print(n_y)
                n_y +=1

            print("break")
            break

        #ploting
        levels = 20
        plt.tricontourf(measure_x_list, measure_y_list, measured_porosity, levels=levels, cmap='coolwarm')
        #cs.clabel(inline=True, fmt='%d', fontsize = 'smaller', manual=true)

        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Measured porosity')

        plt.colorbar()
        plt.show()
        
        with open("porosity_r1mm.txt", "w") as f_w:
            for i in range(len(measure_x_list)):
                f_w.write(str(measure_x_list[i]) + ' '+ str(measure_y_list[i]) + ' '+ str(measured_porosity[i]) + '\n')

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
    
    def MeasurePSD(self):

        particle_sizes = [0.00015, 0.00018, 0.0002, 0.00022, 0.00025, 0.000275, 0.0003, 0.00035]
        frequencies = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        
        for node in self.spheres_model_part.Nodes:
            r = node.GetSolutionStepValue(RADIUS)
            for i in range(len(particle_sizes)):
                if 2.0* r <= particle_sizes[i]:
                    frequencies[i] += 1.0

        for i in range(len(frequencies)):
            frequencies[i] = (frequencies[i] / fre_sum) * 100.0

        with open("PSD.txt", "w") as f_w:
            for i in range(len(particle_sizes)):
                f_w.write(str(particle_sizes[i]) + ' '+ str(frequencies[i]) + '\n')

        exit(0)

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ParticlePackingGenerator(model, parameters).Run()
