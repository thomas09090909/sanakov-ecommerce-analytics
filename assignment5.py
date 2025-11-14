import open3d as o3d
import numpy as np

# Path to the OBJ file
file_path = r"C:\Users\user\Desktop\3rd year 1st trimester\Data Visualization\week 10\3D_models\Intergalactic_Spaceship-(Wavefront).obj"

# -----------------------
# 1. Load the 3D model
# -----------------------
mesh = o3d.io.read_triangle_mesh(file_path)

if mesh.is_empty():
    print("Mesh is empty! Check the path or file.")
else:
    # Visualize the original mesh
    o3d.visualization.draw_geometries([mesh], window_name="Original Model")

    # Print mesh statistics
    print("Mesh Statistics:")
    print("Number of vertices:", len(mesh.vertices))
    print("Number of triangles:", len(mesh.triangles))
    print("Has vertex normals:", mesh.has_vertex_normals())
    print("Has vertex colors:", mesh.has_vertex_colors())

    # -----------------------
    # 2. Convert mesh to a point cloud
    # -----------------------
    pcd = mesh.sample_points_uniformly(number_of_points=10000)  # Sample 10k points

    # Visualize the point cloud
    o3d.visualization.draw_geometries([pcd], window_name="Point Cloud")

    # Print point cloud statistics
    print("\nPoint Cloud Statistics:")
    print("Number of points:", len(pcd.points))
    print("Has colors:", pcd.has_colors())

    # -----------------------
    # 3. Surface reconstruction from point cloud using Poisson reconstruction
    # -----------------------
    poisson_mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)

    # Remove artifacts using the bounding box of the point cloud
    bbox = pcd.get_axis_aligned_bounding_box()
    poisson_mesh = poisson_mesh.crop(bbox)

    # Visualize the reconstructed mesh
    o3d.visualization.draw_geometries([poisson_mesh], window_name="Reconstructed Mesh")

    # Print statistics of the reconstructed mesh
    print("\nReconstructed Mesh Statistics:")
    print("Number of vertices:", len(poisson_mesh.vertices))
    print("Number of triangles:", len(poisson_mesh.triangles))
    print("Has vertex normals:", poisson_mesh.has_vertex_normals())
    print("Has vertex colors:", poisson_mesh.has_vertex_colors())

    # -----------------------
    # 4. Voxelization of the point cloud
    # -----------------------
    voxel_size = 0.05  # size of each voxel
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(pcd, voxel_size=voxel_size)

    # Visualize voxel grid
    o3d.visualization.draw_geometries([voxel_grid], window_name="Voxel Grid")

    # Print voxel grid statistics
    print("\nVoxel Grid Statistics:")
    print("Number of voxels:", len(voxel_grid.get_voxels()))
    print("Has colors:", voxel_grid.has_colors())

    # -----------------------
# 5. Create a plane at the center of the object
# -----------------------
bbox = mesh.get_axis_aligned_bounding_box()
center = bbox.get_center()

# Create a thin and wide plane
plane = o3d.geometry.TriangleMesh.create_box(width=0.01, height=3.0, depth=3.0)
plane.paint_uniform_color([0.8, 0.8, 0.8])  # Gray color

# Translate plane so its center matches the mesh center
plane_center = np.array([1.5, 0.005, 1.5])  # Default plane center (width/2, height/2, depth/2)
translation = center - plane_center
plane.translate(translation)

# Visualize mesh with centered plane
o3d.visualization.draw_geometries([mesh, plane], window_name="Mesh with Centered Plane")


# -----------------------
# 6. Clip the mesh using the plane
# -----------------------
plane_x = 2.0  # Plane at X = 2.0

vertices = np.asarray(mesh.vertices)
triangles = np.asarray(mesh.triangles)

# Keep vertices to the left of the plane
mask = vertices[:, 0] <= plane_x
new_vertices = vertices[mask]

# Map old indices to new indices for triangles
index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(np.where(mask)[0])}

# Keep only triangles with all vertices remaining
new_triangles = []
for tri in triangles:
    if all(v in index_map for v in tri):
        new_triangles.append([index_map[v] for v in tri])
new_triangles = np.array(new_triangles)

# Create new mesh after clipping
clipped_mesh = o3d.geometry.TriangleMesh()
clipped_mesh.vertices = o3d.utility.Vector3dVector(new_vertices)
clipped_mesh.triangles = o3d.utility.Vector3iVector(new_triangles)

# Copy colors and normals if present
if mesh.has_vertex_colors():
    colors = np.asarray(mesh.vertex_colors)
    clipped_mesh.vertex_colors = o3d.utility.Vector3dVector(colors[mask])
if mesh.has_vertex_normals():
    normals = np.asarray(mesh.vertex_normals)
    clipped_mesh.vertex_normals = o3d.utility.Vector3dVector(normals[mask])

# Visualize clipped mesh
o3d.visualization.draw_geometries([clipped_mesh], window_name="Clipped Mesh")

# Print clipped mesh statistics
print("\nClipped Mesh Statistics:")
print("Number of vertices:", len(clipped_mesh.vertices))
print("Number of triangles:", len(clipped_mesh.triangles))
print("Has vertex normals:", clipped_mesh.has_vertex_normals())
print("Has vertex colors:", clipped_mesh.has_vertex_colors())

# -----------------------
# 7. Work with colors and extreme points
# -----------------------
# Remove original colors
mesh.vertex_colors = o3d.utility.Vector3dVector(np.zeros((len(mesh.vertices), 3)))

vertices = np.asarray(mesh.vertices)

# Create a gradient based on Z-axis
z_min, z_max = vertices[:, 2].min(), vertices[:, 2].max()
colors = (vertices[:, 2] - z_min) / (z_max - z_min)  # Normalize to 0..1
colors = np.vstack([colors, np.zeros_like(colors), 1 - colors]).T  # Gradient from blue to red
mesh.vertex_colors = o3d.utility.Vector3dVector(colors)

# Find extreme points along Z-axis
min_idx = np.argmin(vertices[:, 2])
max_idx = np.argmax(vertices[:, 2])
min_point = vertices[min_idx]
max_point = vertices[max_idx]

print("\nExtreme Points Coordinates:")
print("Minimum Z point:", min_point)
print("Maximum Z point:", max_point)

# Visualize extreme points with spheres
min_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.05)
min_sphere.translate(min_point)
min_sphere.paint_uniform_color([1, 0, 0])  # Red sphere

max_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.05)
max_sphere.translate(max_point)
max_sphere.paint_uniform_color([0, 1, 0])  # Green sphere

# Visualize mesh with gradient and extreme points
o3d.visualization.draw_geometries([mesh, min_sphere, max_sphere], window_name="Mesh with Gradient and Extremes")
