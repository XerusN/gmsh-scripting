import gmsh
from geometry_def import (Circle, PlaneSurface, Rectangle, Point, add_refinement_zone, apply_fields)

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
REFINEMENT_MESH_SIZE = DIAMETER/8



def mesh(cylinders_pos, out_path):
   """
   Method to create a mesh with multiple cylinders with a fixed diameter
   ...

   Parameters
   ----------
   cylinders_pos : [(x, y)]
      Array of 2D position tuple, it is recommanded that the first cylinder is (0, 0)
   out_path : str
      File name and path to the mesh output
   """

   # Generate Geometry
   gmsh.initialize()

   # External domain
   total_length = UPSTREAM_DIST + DOWNSTREAM_DIST
   xc = total_length/2 - UPSTREAM_DIST
   ext_domain = Rectangle(xc, 0, total_length, HEIGHT, mesh_size=GLOBAL_MESH_SIZE)

   # Cylinders and refinement around them
   circles = []
   total_length = REFINEMENT_DOWNSTREAM_SIZE + REFINEMENT_SIZE
   fields = []
   for pos in cylinders_pos:
      circles.append(Circle(pos[0], pos[1], DIAMETER, N_POINTS_CYL))
      xc = total_length/2 - REFINEMENT_SIZE + pos[0]
      yc = pos[1]
      # The fields need to be applied later
      fields.append(add_refinement_zone(xc, yc, total_length, REFINEMENT_SIZE*2, REFINEMENT_MESH_SIZE, GLOBAL_MESH_SIZE))
   apply_fields(fields)

   # Surface generation
   closed_loops = [ext_domain]
   for circle in circles:
      closed_loops.append(circle)
   surface_domain = PlaneSurface(closed_loops)
   gmsh.model.occ.synchronize()

   # BC definition
   ext_domain.define_bc()
   for i, circle in enumerate(circles):
      circle.define_bc('cyl'+str(i))
   surface_domain.define_bc()
   gmsh.model.occ.synchronize()

   # Generate mesh
   gmsh.model.mesh.generate(2)

   # Output
   gmsh.write(out_path)

   # Open user interface of GMSH
   gmsh.fltk.run()

   # Mesh file name and output
   gmsh.finalize()

def main():
   mesh([(0, 0), (DIAMETER, DIAMETER), (-2*DIAMETER, -2*DIAMETER)], 'meshes/cylinders.msh')

if __name__ == "__main__":
   main()