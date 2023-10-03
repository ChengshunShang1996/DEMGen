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

def move_mesh(mesh_data, offset_x):
    # Update the x-coordinates of the mesh vertices
    mesh_data.x += offset_x

# Example parameters
stl_file_path = 'original.stl'  # Path to the original STL file
scale_factor = 0.00005  # Scale factor
offset_x = 0.00001

# Scale the STL mesh
scaled_mesh = scale_stl_mesh(stl_file_path, scale_factor)
move_mesh(scaled_mesh, offset_x)

# Save the scaled STL mesh to a new file
scaled_file_path = 'scaled.stl'
scaled_mesh.save(scaled_file_path)