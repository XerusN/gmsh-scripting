import sys
import numpy as np
from mesh import run
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
REFINED_MESH_SIZE = DIAMETER*np.pi/N_POINTS_CYL*5

def param_1_cyl(n: int):
   REFINED_MESH_SIZE = DIAMETER/n*5
   print(n, REFINED_MESH_SIZE)
   return Params(DIAMETER, n, HEIGHT, LENGTH_UPSTREAM, LENGTH_DOWNSTREAM, GLOBAL_MESH_SIZE, LENGTH_REFINEMENT, LENGTH_REFINEMENT_DOWNSTREAM, REFINED_MESH_SIZE)

LINE_1_5 = (Config([(0, 0)], "./meshes/cyl_line_1_5.msh"), param_1_cyl(5))
LINE_1_10 = (Config([(0, 0)], "./meshes/cyl_line_1_10.msh"), param_1_cyl(10))
LINE_1_15 = (Config([(0, 0)], "./meshes/cyl_line_1_15.msh"), param_1_cyl(15))
LINE_1_20 = (Config([(0, 0)], "./meshes/cyl_line_1_20.msh"), param_1_cyl(20))
LINE_1_30 = (Config([(0, 0)], "./meshes/cyl_line_1_30.msh"), param_1_cyl(30))
LINE_1_40 = (Config([(0, 0)], "./meshes/cyl_line_1_40.msh"), param_1_cyl(40))
LINE_1_60 = (Config([(0, 0)], "./meshes/cyl_line_1_60.msh"), param_1_cyl(60))
LINE_1_80 = (Config([(0, 0)], "./meshes/cyl_line_1_80.msh"), param_1_cyl(80))
LINE_1_100 = (Config([(0, 0)], "./meshes/cyl_line_1_100.msh"), param_1_cyl(100))
LINE_1_125 = (Config([(0, 0)], "./meshes/cyl_line_1_125.msh"), param_1_cyl(125))
LINE_1_150 = (Config([(0, 0)], "./meshes/cyl_line_1_150.msh"), param_1_cyl(150))

L = 2.5*DIAMETER
H = 2.5*DIAMETER
LINE_6 = (Config([(i*L, 0) for i in range(6)], "gmsh-scripting/meshes/cyl_line_6.msh"), param_1_cyl(30))

L = 2*DIAMETER
H = 2*DIAMETER
V_SETUP_B = (Config([(i*L, ((-1)**i)*i*H) for i in range(9)], "gmsh-scripting/meshes/cyl_v_setup_b.msh"), param_1_cyl(30))

L = 2*DIAMETER
H = 2*DIAMETER
cyl_pos = [(0, 0)]
for i in range(1, 5):
   cyl_pos.append((i*L, i*H))
   cyl_pos.append((i*L, -i*H))
V_SETUP_D = (Config(cyl_pos, "gmsh-scripting/meshes/cyl_v_setup_d.msh"), param_1_cyl(30))

to_run = [LINE_1_5, LINE_1_10, LINE_1_15, LINE_1_20, LINE_1_30, LINE_1_40, LINE_1_60, LINE_1_80, LINE_1_100, LINE_1_125, LINE_1_150, LINE_6, V_SETUP_B, V_SETUP_D]
# to_run = [LINE_1_100]
# to_run = []

if __name__ == "__main__":
   run(to_run)