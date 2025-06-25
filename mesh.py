import gmsh
from geometry_def import (Circle, PlaneSurface, Rectangle, Point, add_refinement_zone, apply_fields, Config)

def mesh(cylinders_pos, out_path, params):
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
   gmsh.clear()

   # External domain
   total_length = params.UPSTREAM_DIST + params.DOWNSTREAM_DIST
   xc = total_length/2 - params.UPSTREAM_DIST
   ext_domain = Rectangle(xc, 0, total_length, params.HEIGHT, mesh_size=params.GLOBAL_MESH_SIZE)

   # Cylinders and refinement around them
   circles = []
   total_length = params.REFINEMENT_DOWNSTREAM_SIZE + params.REFINEMENT_SIZE
   fields = []
   for pos in cylinders_pos:
      circles.append(Circle(pos[0], pos[1], params.DIAMETER, params.N_POINTS_CYL))
      xc = total_length/2 - params.REFINEMENT_SIZE + pos[0]
      yc = pos[1]
      # The fields need to be applied later
      fields.append(add_refinement_zone(xc, yc, total_length, params.REFINEMENT_SIZE*2, params.REFINEMENT_MESH_SIZE, params.GLOBAL_MESH_SIZE))
   apply_fields(fields)
   gmsh.model.occ.synchronize()

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
   # gmsh.fltk.run()

   # Mesh file name and output
   gmsh.finalize()

def run(params):

   for config in params.to_run:
      mesh(config.cyl_pos, config.path, params)

if __name__ == "__main__":
   import params
   run(params)