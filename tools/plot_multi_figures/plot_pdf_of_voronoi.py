import matplotlib.pyplot as plt
import numpy as np
import os

fig = plt.figure(1)
ax = fig.add_subplot(111)

for i in range(1,7):
    aim_folder_name = "mesher_case_" + str(i) + "_measure"
    aim_file_name   = "voronoi_info_face_number_surface_area_volume.txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, 'inletPG_Graphs', aim_file_name)

    face_number_per_cell_list = []
    with open(os.path.join(aim_path_for_file), 'r') as voronoi_data:
        for line in voronoi_data:
            values = [float(s) for s in line.split()]
            face_number_per_cell_list.append(values[0])
    
    hist, bins = np.histogram(face_number_per_cell_list, bins=np.arange(1, 35, 1), density=True)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    i_label = "Random packing " + str(i)
    lns3 = ax.plot(bin_centers, hist, 'o-', linewidth=2, label=i_label)

ax.set_xlabel("Face numbers per polyhedron, $f$")
ax.set_ylabel("Probability density function")
#ax2.set_ylim(0, 10)
#ax.set_ylim(0.15, 0.6)
#plt.title(my_title)
#plt.xticks(np.arange(0, 101, step=10)) 
ax.legend()
ax.grid(True, which='both')
#ax.legend()
#ax2.legend()
plt.show()

fig = plt.figure(2)
ax = fig.add_subplot(111)

for i in range(1,7):
    aim_folder_name = "mesher_case_" + str(i) + "_measure"
    aim_file_name   = "voronoi_info_face_number_surface_area_volume.txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, 'inletPG_Graphs', aim_file_name)

    surface_area_per_cell_list = []
    with open(os.path.join(aim_path_for_file), 'r') as voronoi_data:
        for line in voronoi_data:
            values = [float(s) for s in line.split()]
            surface_area_per_cell_list.append(values[1])
    
    hist, bins = np.histogram(surface_area_per_cell_list, bins=np.arange(0, 7e-7, 5e-8), density=True)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    i_label = "Random packing " + str(i)
    lns3 = ax.plot(bin_centers, hist, 'o-', linewidth=2, label=i_label)

ax.set_xlabel("Surface area per polyhedron, $S$")
ax.set_ylabel("Probability density function")
#ax2.set_ylim(0, 10)
#ax.set_ylim(0.15, 0.6)
#plt.title(my_title)
#plt.xticks(np.arange(0, 101, step=10)) 
ax.legend()
ax.grid(True, which='both')
#ax.legend()
#ax2.legend()
plt.show()

fig = plt.figure(3)
ax = fig.add_subplot(111)

for i in range(1,7):
    aim_folder_name = "mesher_case_" + str(i) + "_measure"
    aim_file_name   = "voronoi_info_face_number_surface_area_volume.txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, 'inletPG_Graphs', aim_file_name)

    volume_per_cell_list = []
    with open(os.path.join(aim_path_for_file), 'r') as voronoi_data:
        for line in voronoi_data:
            values = [float(s) for s in line.split()]
            volume_per_cell_list.append(values[2])
    
    hist, bins = np.histogram(volume_per_cell_list, bins=np.arange(0, 4e-11, 3e-12), density=True)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    i_label = "Random packing " + str(i)
    lns3 = ax.plot(bin_centers, hist, 'o-', linewidth=2, label=i_label)

ax.set_xlabel("Volume per polyhedron, $V$")
ax.set_ylabel("Probability density function")
#ax2.set_ylim(0, 10)
#ax.set_ylim(0.15, 0.6)
#plt.title(my_title)
#plt.xticks(np.arange(0, 101, step=10)) 
ax.legend()
ax.grid(True, which='both')
#ax.legend()
#ax2.legend()
plt.show()


fig = plt.figure(4)
ax = fig.add_subplot(111)

for i in range(1,7):
    aim_folder_name = "mesher_case_" + str(i) + "_measure"
    aim_file_name   = "voronoi_info_perimeter_per_face.txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, 'inletPG_Graphs', aim_file_name)

    perimeter_per_face_list = []
    with open(os.path.join(aim_path_for_file), 'r') as voronoi_data:
        for line in voronoi_data:
            values = [float(s) for s in line.split()]
            for value in values:
                perimeter_per_face_list.append(value)
    
    hist, bins = np.histogram(perimeter_per_face_list, bins=np.arange(0, 0.0012, 4e-5), density=True)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    i_label = "Random packing " + str(i)
    lns3 = ax.plot(bin_centers, hist, 'o-', linewidth=2, label=i_label)

ax.set_xlabel("Perimeter per face, $L$")
ax.set_ylabel("Probability density function")
#ax2.set_ylim(0, 10)
#ax.set_ylim(0.15, 0.6)
#plt.title(my_title)
#plt.xticks(np.arange(0, 101, step=10)) 
ax.legend()
ax.grid(True, which='both')
#ax.legend()
#ax2.legend()
plt.show()

fig = plt.figure(5)
ax = fig.add_subplot(111)

for i in range(1,7):
    aim_folder_name = "mesher_case_" + str(i) + "_measure"
    aim_file_name   = "voronoi_info_area_per_face.txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, 'inletPG_Graphs', aim_file_name)

    area_per_face_list = []
    with open(os.path.join(aim_path_for_file), 'r') as voronoi_data:
        for line in voronoi_data:
            values = [float(s) for s in line.split()]
            for value in values:
                area_per_face_list.append(value)
    
    hist, bins = np.histogram(area_per_face_list, bins=np.arange(0, 6e-8, 2e-9), density=True)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    i_label = "Random packing " + str(i)
    lns3 = ax.plot(bin_centers, hist, 'o-', linewidth=2, label=i_label)

ax.set_xlabel("Area per face, $L$")
ax.set_ylabel("Probability density function")
#ax2.set_ylim(0, 10)
#ax.set_ylim(0.15, 0.6)
#plt.title(my_title)
#plt.xticks(np.arange(0, 101, step=10)) 
ax.legend()
ax.grid(True, which='both')
#ax.legend()
#ax2.legend()
plt.show()

