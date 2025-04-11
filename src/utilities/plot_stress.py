import os
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
plt.style.use(['science'])


# create the BTS_peak_points.dat

aim_path_and_name = os.path.join(os.getcwd(), 'stress_tensor_0.txt')
aim_path_and_name_granular_temperature = os.path.join(os.getcwd(), 'granular_temperature_0.txt')

f = plt.figure(1, figsize=(6,6))
plt.xlabel('Time / s')
plt.ylabel(r'$\bar{p}$ / MPa')

if os.path.isfile(aim_path_and_name):
    X12, Y12, Y13 = [], [], []
    with open(aim_path_and_name, 'r') as stress_strain_data:
        for line in stress_strain_data:
            values = [float(s) for s in line.split()]
            X12.append(values[0])
            Y12.append(values[1] / 1e6)
            Y13.append(values[2])

    plt.plot(X12, Y12, 'b-o', label='Measured mean stress', markersize=6, markerfacecolor='none')
plt.yscale('log')
plt.grid()
plt.legend(frameon= True,framealpha=0.8)

f.savefig('stress_state.pdf')

g = plt.figure(2, figsize=(6,6))
#plt.title('Hertz model')
plt.xlabel('Time / s')
plt.ylabel(r'T / $\text{m}^2/\text{s}^2$')

if os.path.isfile(aim_path_and_name_granular_temperature):
    X12, Y12, Y22 = [], [], []
    with open(aim_path_and_name_granular_temperature, 'r') as granular_temperature_data:
        for line in granular_temperature_data:
            values = [float(s) for s in line.split()]
            X12.append(values[0])
            Y12.append(values[1])
            Y22.append(values[2])
            #Y12.append(real_porosity)

    plt.plot(X12, Y12, 'b-o', label=r'T$_{\text{mean}}$', markersize=6, markerfacecolor='none', zorder = 10)
    plt.plot(X12, Y22, 'r-o', label=r'T$_{\infty}$', markersize=6, markerfacecolor='none', zorder = 10)

plt.yscale("log")
plt.grid()
plt.legend(frameon= True,framealpha=0.8)
g.savefig('granular_temperature.pdf')

h = plt.figure(4, figsize=(6,6))
plt.xlabel('Time / s')
plt.ylabel(r'Packing density')
#

if os.path.isfile(aim_path_and_name):

    plt.plot(X12, Y13, 'g->', label='Measured packing density', markersize=6, markerfacecolor='none')

plt.grid()
plt.legend(frameon= True,framealpha=0.8)
h.savefig('packing_density_evolution.pdf')