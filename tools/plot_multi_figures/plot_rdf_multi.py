import numpy as np
import matplotlib.pyplot as plt
import os

fig, axs = plt.subplots(3, 3)

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure',
                    'fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure', 
                    'radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

label_list = ['G-1', 'G-2', 'G-3', 'I-1', 'I-2', 'I-3', 'R-1', 'R-2', 'R-3']

i = 0
for aim_folder_name in folder_name_list:
    aim_file_name   = "rdf_data_of_size_0.0048.txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, 'inletPG3_Graphs', aim_file_name)

    r_d_mean = []
    frequencies = []
    with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
        for line in psd_error_data:
            values = [float(s) for s in line.split()]
            r_d_mean.append(values[0])
            frequencies.append(values[1])

    #i_label = label_list[i]
    if i < 3:
        axs[0,i].plot(r_d_mean, frequencies, 'b-', linewidth=1)
    elif i < 6:
        axs[1,i-3].plot(r_d_mean, frequencies, 'b-', linewidth=1)
    elif i < 9:
        axs[2,i-6].plot(r_d_mean, frequencies, 'b-', linewidth=1)
    i += 1

for ax in axs.flat:
    ax.set(xlabel='$r/d_{mean}$', ylabel='RDF $g(r)$')
    ax.set_xlim(0.0, 12)
    ax.set_ylim(0.0, 4)
    #ax.legend(fontsize=8, loc=4)
    ax.grid(True, which='both')
    ax.label_outer()

ii = 0
for ax in axs.flat:
    ax.set_title(label_list[ii])
    ii += 1

plt.show()