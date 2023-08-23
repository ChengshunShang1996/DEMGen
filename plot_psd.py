import numpy as np
import matplotlib.pyplot as plt

# Particle size data and corresponding frequencies (example data)
particle_sizes = [0.15, 0.18, 0.2, 0.22, 0.25, 0.275, 0.3, 0.35]
frequencies = [0.20754, 0.20754+0.15525, 0.20754+0.15525+0.13346, 0.20754+0.15525+0.13346+0.13821, 0.20754+0.15525+0.13346+0.13821+0.1751, 0.20754+0.15525+0.13346+0.13821+0.1751+0.09922, 
               0.20754+0.15525+0.13346+0.13821+0.1751+0.09922+0.05418, 0.20754+0.15525+0.13346+0.13821+0.1751+0.09922+0.05418+0.03704]

#particle_sizes = [0.0001, 0.00013, 0.00016]
#frequencies = [0.25, 0.75, 1.0]


frequencies100 = []
for i in range(len(frequencies)):
    frequencies100.append(frequencies[i] * 100)

frequencies100_sim = []
with open("PSD.txt", 'r') as psd_data:
    for line in psd_data:
        values = [float(s) for s in line.split()]
        frequencies100_sim.append(values[1])

frequencies100_sim_accu = frequencies100_sim

# Plot the PSD curve with log scale on x-axis
'''
plt.figure(figsize=(8, 4))
plt.semilogx(particle_sizes, frequencies100, 'bo-', linewidth=2,label="Input")
plt.semilogx(particle_sizes, frequencies100_sim_accu, 'ro-', linewidth=2, label="Simulated")
plt.xlabel('Particle diameter / mm')
plt.ylabel('Cumulative size distribution / %')
#plt.title('Particle Size Distribution')
plt.grid(True, which='both')
#plt.xlim(0.01, 1)
#plt.ylim(0, 110)
plt.legend()
plt.show()
'''

fig = plt.figure(1)
ax = fig.add_subplot(111)
lns1 = ax.semilogx(particle_sizes, frequencies100, 'bo-', linewidth=2,label="Input")
lns2 = ax.semilogx(particle_sizes, frequencies100_sim_accu, 'ro-', linewidth=2, label="Simulated")
ax.set_xlabel("Particle diameter / mm")
ax.set_ylabel("Cumulative size distribution / %")
ax.set_ylim(10, 110)

abs_error = []
for i in range(len(frequencies)):
    abs_error.append(abs(frequencies100_sim_accu[i] - frequencies100[i]))

ax2 = ax.twinx()
#lns3 = ax2.bar(particle_sizes, abs_error, color = "lightgray", width = 0.7, label='AE')
lns3 = ax2.semilogx(particle_sizes, abs_error, 'bo--', color = "lightgray", linewidth=2, label="AE")
ax2.set_ylabel("Absolute error (AE) / %")
ax2.set_ylim(0, 10)
#ax.set_ylim(-0.9e8, 4e8)
#plt.title(my_title)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, loc=2)
ax.grid(True, which='both')
#ax.legend()
#ax2.legend()
plt.show()
