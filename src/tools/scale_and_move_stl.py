from stl import mesh
import numpy as np

def scale_stl_mesh(stl_file_path, scale_factor):
    # Load STL mesh
    mesh_data = mesh.Mesh.from_file(stl_file_path)

    # Scale the vertices of the mesh
    scaled_vertices = mesh_data.points * scale_factor

    # Create a new STL mesh
    scaled_mesh = mesh.Mesh(np.zeros(mesh_data.points.shape[0], dtype=mesh.Mesh.dtype))
    scaled_mesh.points = scaled_vertices

    return scaled_mesh

def move_mesh(mesh_data, offset_x, offset_y, offset_z):
    # Update the x-coordinates of the mesh vertices
    mesh_data.x += offset_x
    mesh_data.y += offset_y
    mesh_data.z += offset_z

# Example parameters
stl_file_path = 'acueducto-de-segovia.stl'  # Path to the original STL file
scale_factor = 0.000625  # Scale factor
offset_x = 0.002
offset_y = 0.0
offset_z = 0.007

# Scale the STL mesh
scaled_mesh = scale_stl_mesh(stl_file_path, scale_factor)
move_mesh(scaled_mesh, offset_x, offset_y, offset_z)

# Define the rotation angle in radians (90 degrees)
angle = np.pi / 2

# Create a rotation matrix for the specified angle around the Z-axis
rotation_matrix = np.array([
    [np.cos(angle), -np.sin(angle), 0],
    [np.sin(angle), np.cos(angle), 0],
    [0, 0, 1]
])

# Apply the rotation to the mesh vertices
for i in range(len(scaled_mesh.v0)):
    scaled_mesh.v0[i] = np.dot(rotation_matrix, scaled_mesh.v0[i])
    scaled_mesh.v1[i] = np.dot(rotation_matrix, scaled_mesh.v1[i])
    scaled_mesh.v2[i] = np.dot(rotation_matrix, scaled_mesh.v2[i])

offset_x = 0.0
offset_y = 0.007
offset_z = 0.0
move_mesh(scaled_mesh, offset_x, offset_y, offset_z)

# Save the scaled STL mesh to a new file
scaled_file_path = 'scaled-acueducto-de-segovia.stl'
scaled_mesh.save(scaled_file_path)