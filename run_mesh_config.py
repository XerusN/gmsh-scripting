from geometry_def import (Config, RunMeshConfig, Params)

# Cylinder
DIAMETER = 0.01
N_POINTS_CYL = 50

# Bounding box
HEIGHT = 52*DIAMETER
LENGTH_UPSTREAM = 10*DIAMETER
LENGTH_DOWNSTREAM = 46*DIAMETER
GLOBAL_MESH_SIZE = DIAMETER*2

# Refinement zone around the cylinder
LENGTH_REFINEMENT = DIAMETER
LENGTH_REFINEMENT_DOWNSTREAM = 4*DIAMETER
REFINED_MESH_SIZE = DIAMETER/12

default_params = Params(DIAMETER, N_POINTS_CYL, HEIGHT, LENGTH_UPSTREAM, LENGTH_DOWNSTREAM, GLOBAL_MESH_SIZE, LENGTH_REFINEMENT, LENGTH_REFINEMENT_DOWNSTREAM, REFINED_MESH_SIZE)

LINE_1 = (Config([(0, 0)], "meshes/cyl_line_1.msh"), default_params)

L = 2.5*DIAMETER
H = 2.5*DIAMETER
LINE_6 = (Config([(i*L, 0) for i in range(6)], "meshes/cyl_line_6.msh"), default_params)

L = 2*DIAMETER
H = 2*DIAMETER
V_SETUP_B = (Config([(i*L, ((-1)**i)*i*H) for i in range(9)], "meshes/cyl_v_setup_b.msh"), default_params)

L = 2*DIAMETER
H = 2*DIAMETER
cyl_pos = [(0, 0)]
for i in range(1, 5):
   cyl_pos.append((i*L, i*H))
   cyl_pos.append((i*L, -i*H))
V_SETUP_D = (Config(cyl_pos, "meshes/cyl_v_setup_d.msh"), default_params)

to_run = [LINE_1, LINE_6, V_SETUP_B, V_SETUP_D]