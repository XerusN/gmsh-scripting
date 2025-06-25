from geometry_def import Config

# Cylinder
N_POINTS_CYL = 50
DIAMETER = 0.01

# Bounding box
HEIGHT = 52*DIAMETER
UPSTREAM_DIST = 10*DIAMETER
DOWNSTREAM_DIST = 46*DIAMETER
GLOBAL_MESH_SIZE = DIAMETER*2

# Refinement zone around the cylinder
REFINEMENT_SIZE = DIAMETER
REFINEMENT_DOWNSTREAM_SIZE = 4*DIAMETER
REFINEMENT_MESH_SIZE = DIAMETER/12

LINE_1 = Config([(0, 0)], "meshes/cyl_line_1.msh")

L = 2.5*DIAMETER
H = 2.5*DIAMETER
LINE_6 = Config([(i*L, 0) for i in range(6)], "meshes/cyl_line_6.msh")

L = 2*DIAMETER
H = 2*DIAMETER
V_SETUP_B = Config([(i*L, ((-1)**i)*i*H) for i in range(9)], "meshes/cyl_v_setup_b.msh")

L = 2*DIAMETER
H = 2*DIAMETER
cyl_pos = [(0, 0)]
for i in range(1, 5):
   cyl_pos.append((i*L, i*H))
   cyl_pos.append((i*L, -i*H))
V_SETUP_D = Config(cyl_pos, "meshes/cyl_v_setup_d.msh")

to_run = [LINE_1, LINE_6, V_SETUP_B, V_SETUP_D]