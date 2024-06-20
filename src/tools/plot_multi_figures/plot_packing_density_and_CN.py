import numpy as np
import matplotlib.pyplot as plt
import os

#fig = plt.figure(1)
#ax = fig.add_subplot(111)
fig, axs = plt.subplots(1, 3)

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure',
                    'fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure', 
                    'radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

label_list = ['G-1', 'G-2', 'G-3', 'I-1', 'I-2', 'I-3', 'R-1', 'R-2', 'R-3']

i = 0
for aim_folder_name in folder_name_list:
    aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

    lambda_list = []
    packing_density_list = []
    with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
        for line in psd_error_data:
            values = [float(s) for s in line.split()]
            lambda_list.append(values[0])
            packing_density_list.append(values[1])

    i_label = label_list[i]
    if i < 3:
        lns3 = axs[0].plot(lambda_list, packing_density_list, 'o--', linewidth=1.5, label=i_label)
    elif i < 6:
        lns3 = axs[1].plot(lambda_list, packing_density_list, '^--', linewidth=1.5, label=i_label)
    elif i < 9:
        lns3 = axs[2].plot(lambda_list, packing_density_list, 's--', linewidth=1.5, label=i_label)

    '''
    if i == 0:
        lns3 = ax.plot(lambda_list, packing_density_list, 'o--', color = "darkblue", linewidth=2, label=i_label)
    elif i == 1:
        lns3 = ax.plot(lambda_list, packing_density_list, 'o--', color = "blue", linewidth=2, label=i_label)
    elif i == 2:
        lns3 = ax.plot(lambda_list, packing_density_list, 'o--', color = "cornflowerblue", linewidth=2, label=i_label)
    elif i == 3:
        lns3 = ax.plot(lambda_list, packing_density_list, '^--', color = "darkorange", linewidth=2, label=i_label)
    elif i == 4:
        lns3 = ax.plot(lambda_list, packing_density_list, '^--', color = "orange", linewidth=2, label=i_label)
    elif i == 5:
        lns3 = ax.plot(lambda_list, packing_density_list, '^--', color = "bisque", linewidth=2, label=i_label)
    elif i == 6:
        lns3 = ax.plot(lambda_list, packing_density_list, 's--', color = "darkgreen", linewidth=2, label=i_label)
    elif i == 7:
        lns3 = ax.plot(lambda_list, packing_density_list, 's--', color = "limegreen", linewidth=2, label=i_label)
    elif i == 8:
        lns3 = ax.plot(lambda_list, packing_density_list, 's--', color = "lightgreen", linewidth=2, label=i_label)
    '''
    i += 1

for ax in axs.flat:
    ax.set(xlabel='$\lambda$', ylabel='Packing density')
 
#ax2.set_ylim(0, 10)
#axs[0].set_xlim(0.0, 25)
#axs[0].set_ylim(0.55, 0.66)
#axs[1].set_xlim(0.0, 25)
#axs[1].set_ylim(0.55, 0.66)
#axs[2].set_xlim(0.0, 25)
#axs[2].set_ylim(0.55, 0.66)

for ax in axs.flat:
    ax.set_xlim(0.0, 25)
    ax.set_ylim(0.5, 0.7)
#plt.title(my_title)
for ax in axs.flat:
    ax.legend(fontsize=8, loc=4)
for ax in axs.flat:
    ax.grid(True, which='both')
for ax in axs.flat:
    ax.label_outer()
#ax.legend()
#ax2.legend()
plt.show()

#fig = plt.figure(2)
#ax = fig.add_subplot(111)
fig, axs = plt.subplots(1, 3)

lambda_list = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
measured_packing_density_mean = []
measured_packing_density_top = []
measured_packing_density_bot = []
measured_packing_density_max = []
measured_packing_density_min = []

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure']

for ii in range(1,12):
    i = 0
    packing_density_list = []
    for aim_folder_name in folder_name_list:
        aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        line_cnt = 0
        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            for line in psd_error_data:
                line_cnt += 1
                values = [float(s) for s in line.split()]
                if line_cnt == ii:
                    packing_density_list.append(values[1])

    sum_packing_density = 0.0
    for packing_density in packing_density_list:
        sum_packing_density += packing_density
    mean_packing_density = sum_packing_density / 3.0
    measured_packing_density_mean.append(mean_packing_density)
    measured_packing_density_top.append(max(packing_density_list) - mean_packing_density)
    measured_packing_density_bot.append(mean_packing_density - min(packing_density_list))
    measured_packing_density_max.append(max(packing_density_list))
    measured_packing_density_min.append(min(packing_density_list))

lns1 = axs[0].errorbar(lambda_list, measured_packing_density_mean, yerr=(measured_packing_density_bot, measured_packing_density_top),\
                    lw = 1.5, capsize = 2, capthick = 2, ecolor = "green", color = "blue", label = "Packing density - G")

#ax.set_xlabel("$\lambda$")
#ax.set_ylabel("Averaged packing density")

abs_error = []
for i in range(len(measured_packing_density_max)):
    abs_error.append(measured_packing_density_max[i] - measured_packing_density_min[i])

ax2 = axs[0].twinx()
lns2 = ax2.plot(lambda_list, abs_error, 'o--', color = "gray", linewidth=1.5, label="AE width - G")

measured_packing_density_mean = []
measured_packing_density_top = []
measured_packing_density_bot = []
measured_packing_density_max = []
measured_packing_density_min = []

folder_name_list = ['fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure']

for ii in range(1,12):
    i = 0
    packing_density_list = []
    for aim_folder_name in folder_name_list:
        aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        line_cnt = 0
        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            for line in psd_error_data:
                line_cnt += 1
                values = [float(s) for s in line.split()]
                if line_cnt == ii:
                    packing_density_list.append(values[1])

    sum_packing_density = 0.0
    for packing_density in packing_density_list:
        sum_packing_density += packing_density
    mean_packing_density = sum_packing_density / 3.0
    measured_packing_density_mean.append(mean_packing_density)
    measured_packing_density_top.append(max(packing_density_list) - mean_packing_density)
    measured_packing_density_bot.append(mean_packing_density - min(packing_density_list))
    measured_packing_density_max.append(max(packing_density_list))
    measured_packing_density_min.append(min(packing_density_list))

lns3 = axs[1].errorbar(lambda_list, measured_packing_density_mean, yerr=(measured_packing_density_bot, measured_packing_density_top),\
                    lw = 1.5, capsize = 2, capthick = 2, ecolor = "green", color = "blue", label = "Packing density - I")

abs_error = []
for i in range(len(measured_packing_density_max)):
    abs_error.append(measured_packing_density_max[i] - measured_packing_density_min[i])
ax3 = axs[1].twinx()
lns4 = ax3.plot(lambda_list, abs_error, 'o--', color = "gray", linewidth=1.5, label="AE width - I")

measured_packing_density_mean = []
measured_packing_density_top = []
measured_packing_density_bot = []
measured_packing_density_max = []
measured_packing_density_min = []

folder_name_list = ['radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

for ii in range(1,12):
    i = 0
    packing_density_list = []
    for aim_folder_name in folder_name_list:
        aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        line_cnt = 0
        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            for line in psd_error_data:
                line_cnt += 1
                values = [float(s) for s in line.split()]
                if line_cnt == ii:
                    packing_density_list.append(values[1])

    sum_packing_density = 0.0
    for packing_density in packing_density_list:
        sum_packing_density += packing_density
    mean_packing_density = sum_packing_density / 3.0
    measured_packing_density_mean.append(mean_packing_density)
    measured_packing_density_top.append(max(packing_density_list) - mean_packing_density)
    measured_packing_density_bot.append(mean_packing_density - min(packing_density_list))
    measured_packing_density_max.append(max(packing_density_list))
    measured_packing_density_min.append(min(packing_density_list))

lns5 = axs[2].errorbar(lambda_list, measured_packing_density_mean, yerr=(measured_packing_density_bot, measured_packing_density_top),\
                    lw = 1.5, capsize = 2, capthick = 2, ecolor = "green", color = "blue", label = "Packing density - R")

abs_error = []
for i in range(len(measured_packing_density_max)):
    abs_error.append(measured_packing_density_max[i] - measured_packing_density_min[i])
ax4 = axs[2].twinx()
lns6 = ax4.plot(lambda_list, abs_error, 'o--', color = "gray", linewidth=1.5, label="AE width - R")
ax4.set_ylabel("Absolute error (AE) width ")

for ax in axs.flat:
    ax.set(xlabel='$\lambda$', ylabel='Averaged packing density')
#ax2.set_ylim(0, 0.05)
#ax.set_ylim(0.60, 0.68)
#plt.title(my_title)
h1, l1 = axs[0].get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
axs[0].legend(h1+h2, l1+l2, loc=1, fontsize=8)

h1, l1 = axs[1].get_legend_handles_labels()
h2, l2 = ax3.get_legend_handles_labels()
axs[1].legend(h1+h2, l1+l2, loc=1, fontsize=8)

h1, l1 = axs[2].get_legend_handles_labels()
h2, l2 = ax4.get_legend_handles_labels()
axs[2].legend(h1+h2, l1+l2, loc=1, fontsize=8)
#ax2.set_ylim(0, 10)
#ax.set_ylim(-0.9e8, 4e8)
#plt.title(my_title)
#ax.grid(True, which='both')
#ax.legend()
#ax2.legend()
ax2.set_ylim(0, 0.05)
ax3.set_ylim(0, 0.05)
ax2.set_yticks([])
ax3.set_yticks([])
ax4.set_ylim(0, 0.05)

for ax in axs.flat:
    ax.set_xlim(0.0, 25)
    ax.set_ylim(0.5, 0.7)
#plt.title(my_title)
#for ax in axs.flat:
#    ax.legend(fontsize=8)
for ax in axs.flat:
    ax.grid(True, which='both')
for ax in axs.flat:
    ax.label_outer()
plt.show()

################################################################################
################################################################################

fig, axs = plt.subplots(1, 3)

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure',
                    'fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure', 
                    'radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

label_list = ['G-1', 'G-2', 'G-3', 'I-1', 'I-2', 'I-3', 'R-1', 'R-2', 'R-3']

i = 0
for aim_folder_name in folder_name_list:
    aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

    lambda_list = []
    CN_list = []
    with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
        for line in psd_error_data:
            values = [float(s) for s in line.split()]
            lambda_list.append(values[0])
            CN_list.append(values[2])

    i_label = label_list[i]
    if i < 3:
        lns3 = axs[0].plot(lambda_list, CN_list, 'o--', linewidth=1.5, label=i_label)
    elif i < 6:
        lns3 = axs[1].plot(lambda_list, CN_list, '^--', linewidth=1.5, label=i_label)
    elif i < 9:
        lns3 = axs[2].plot(lambda_list, CN_list, 's--', linewidth=1.5, label=i_label)
    i += 1

for ax in axs.flat:
    ax.set(xlabel='$\lambda$', ylabel='MCN')
 

for ax in axs.flat:
    ax.set_xlim(0.0, 25)
    ax.set_ylim(3, 7)
for ax in axs.flat:
    ax.legend(fontsize=8, loc=4)
for ax in axs.flat:
    ax.grid(True, which='both')
for ax in axs.flat:
    ax.label_outer()
plt.show()

##############################################################
##############################################################

fig, axs = plt.subplots(1, 3)

lambda_list = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
measured_mcn_mean = []
measured_mcn_top = []
measured_mcn_bot = []
measured_mcn_max = []
measured_mcn_min = []

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure']

for ii in range(1,12):
    i = 0
    mcn_list = []
    for aim_folder_name in folder_name_list:
        aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        line_cnt = 0
        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            for line in psd_error_data:
                line_cnt += 1
                values = [float(s) for s in line.split()]
                if line_cnt == ii:
                    mcn_list.append(values[2])

    sum_mcn = 0.0
    for mcn in mcn_list:
        sum_mcn += mcn
    mean_mcn = sum_mcn / 3.0
    measured_mcn_mean.append(mean_mcn)
    measured_mcn_top.append(max(mcn_list) - mean_mcn)
    measured_mcn_bot.append(mean_mcn - min(mcn_list))
    measured_mcn_max.append(max(mcn_list))
    measured_mcn_min.append(min(mcn_list))

lns1 = axs[0].errorbar(lambda_list, measured_mcn_mean, yerr=(measured_mcn_bot, measured_mcn_top),\
                    lw = 1.5, capsize = 2, capthick = 2, ecolor = "green", color = "blue", label = "MCN - G")

#ax.set_xlabel("$\lambda$")
#ax.set_ylabel("Averaged packing density")

abs_error = []
for i in range(len(measured_mcn_max)):
    abs_error.append(measured_mcn_max[i] - measured_mcn_min[i])

ax2 = axs[0].twinx()
lns2 = ax2.plot(lambda_list, abs_error, 'o--', color = "gray", linewidth=1.5, label="AE width - G")

measured_mcn_mean = []
measured_mcn_top = []
measured_mcn_bot = []
measured_mcn_max = []
measured_mcn_min = []

folder_name_list = ['fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure']

for ii in range(1,12):
    i = 0
    mcn_list = []
    for aim_folder_name in folder_name_list:
        aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        line_cnt = 0
        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            for line in psd_error_data:
                line_cnt += 1
                values = [float(s) for s in line.split()]
                if line_cnt == ii:
                    mcn_list.append(values[2])

    sum_mcn = 0.0
    for mcn in mcn_list:
        sum_mcn += mcn
    mean_mcn = sum_mcn / 3.0
    measured_mcn_mean.append(mean_mcn)
    measured_mcn_top.append(max(mcn_list) - mean_mcn)
    measured_mcn_bot.append(mean_mcn - min(mcn_list))
    measured_mcn_max.append(max(mcn_list))
    measured_mcn_min.append(min(mcn_list))

lns3 = axs[1].errorbar(lambda_list, measured_mcn_mean, yerr=(measured_mcn_bot, measured_mcn_top),\
                    lw = 1.5, capsize = 2, capthick = 2, ecolor = "green", color = "blue", label = "MCN - I")

abs_error = []
for i in range(len(measured_mcn_max)):
    abs_error.append(measured_mcn_max[i] - measured_mcn_min[i])
ax3 = axs[1].twinx()
lns4 = ax3.plot(lambda_list, abs_error, 'o--', color = "gray", linewidth=1.5, label="AE width - I")

measured_mcn_mean = []
measured_mcn_top = []
measured_mcn_bot = []
measured_mcn_max = []
measured_mcn_min = []

folder_name_list = ['radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

for ii in range(1,12):
    i = 0
    mcn_list = []
    for aim_folder_name in folder_name_list:
        aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        line_cnt = 0
        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            for line in psd_error_data:
                line_cnt += 1
                values = [float(s) for s in line.split()]
                if line_cnt == ii:
                    mcn_list.append(values[2])

    sum_mcn = 0.0
    for mcn in mcn_list:
        sum_mcn += mcn
    mean_mcn = sum_mcn / 3.0
    measured_mcn_mean.append(mean_mcn)
    measured_mcn_top.append(max(mcn_list) - mean_mcn)
    measured_mcn_bot.append(mean_mcn - min(mcn_list))
    measured_mcn_max.append(max(mcn_list))
    measured_mcn_min.append(min(mcn_list))

lns5 = axs[2].errorbar(lambda_list, measured_mcn_mean, yerr=(measured_mcn_bot, measured_mcn_top),\
                    lw = 1.5, capsize = 2, capthick = 2, ecolor = "green", color = "blue", label = "MCN - R")

abs_error = []
for i in range(len(measured_mcn_max)):
    abs_error.append(measured_mcn_max[i] - measured_mcn_min[i])
ax4 = axs[2].twinx()
lns6 = ax4.plot(lambda_list, abs_error, 'o--', color = "gray", linewidth=1.5, label="AE width - R")
ax4.set_ylabel("Absolute error (AE) width ")

for ax in axs.flat:
    ax.set(xlabel='$\lambda$', ylabel='MCN')
#ax2.set_ylim(0, 0.05)
#ax.set_ylim(0.60, 0.68)
#plt.title(my_title)
h1, l1 = axs[0].get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
axs[0].legend(h1+h2, l1+l2, loc=1, fontsize=8)

h1, l1 = axs[1].get_legend_handles_labels()
h2, l2 = ax3.get_legend_handles_labels()
axs[1].legend(h1+h2, l1+l2, loc=1, fontsize=8)

h1, l1 = axs[2].get_legend_handles_labels()
h2, l2 = ax4.get_legend_handles_labels()
axs[2].legend(h1+h2, l1+l2, loc=1, fontsize=8)
#ax2.set_ylim(0, 10)
#ax.set_ylim(-0.9e8, 4e8)
#plt.title(my_title)
#ax.grid(True, which='both')
#ax.legend()
#ax2.legend()
ax2.set_ylim(0, 2)
ax3.set_ylim(0, 2)
ax2.set_yticks([])
ax3.set_yticks([])
ax4.set_ylim(0, 2)

for ax in axs.flat:
    ax.set_xlim(0.0, 25)
    ax.set_ylim(3, 7)
#plt.title(my_title)
#for ax in axs.flat:
#    ax.legend(fontsize=8)
for ax in axs.flat:
    ax.grid(True, which='both')
for ax in axs.flat:
    ax.label_outer()
plt.show()