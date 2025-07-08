import gmsh
from geometry_def import (Circle, PlaneSurface, Rectangle, Point, add_refinement_zone_rect, apply_fields, custom_distance, Config, Params, RunMeshConfig, sigmoid_transition)

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
   gmsh.option.setNumber('General.Terminal', 0)
   gmsh.clear()

   # External domain
   total_length = params.length_upstream + params.length_downstream
   xc = total_length/2 - params.length_upstream
   ext_domain = Rectangle(xc, 0, total_length, params.height, mesh_size=params.global_mesh_size)

   # Cylinders and refinement around them
   circles = []
   total_length = params.length_refinement + params.length_refinement_downstream
   fields = []
   for pos in cylinders_pos:
      circles.append(Circle(pos[0], pos[1], params.diameter, params.n_points_cyl))
      xc = total_length/2 - params.length_refinement + pos[0]
      yc = pos[1]
      # The fields need to be applied later
      fields.append(add_refinement_zone_rect(xc, yc, total_length, params.length_refinement*2, params.refined_mesh_size, params.global_mesh_size, 40*params.diameter))
      # 1.02 to prevent mesh size from being lower to actual edges along the cylinder due to curvature, it would double the number of edges
      # fields.append(add_refinement_zone_cyl(pos[0], pos[1], 1.2*params.diameter, params.diameter/params.n_points_cyl*1.02, params.global_mesh_size))
      #fields.append(threshold(circles[-1].xc, circles[-1].yc, 0., params.diameter/2.*2., params.diameter/params.n_points_cyl*1.02, params.refined_mesh_size))
      const_dist = params.diameter/2.*1.1
      dist_total = params.diameter/2.*2.
      #fields.append(custom_distance(circles[-1].xc, circles[-1].yc, params.diameter/2, const_dist, params.diameter/params.n_points_cyl*1.02, params.diameter/params.n_points_cyl*1.05, params.global_mesh_size))
      # fields.append(sigmoid_transition(circles[-1].xc, circles[-1].yc, const_dist*0.99, dist_total, params.diameter/params.n_points_cyl*1.05, params.refined_mesh_size))
      #fields.append(custom_distance(circles[-1].xc, circles[-1].yc, const_dist*0.99, dist_total, params.diameter/params.n_points_cyl*1.05, params.refined_mesh_size, params.global_mesh_size))
      
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
      
   apply_fields(fields)

   # gmsh.option.setNumber("Mesh.Smoothing", 100)

   # Generate mesh
   gmsh.model.mesh.generate(2)

   gmsh.model.mesh

   # Output
   gmsh.write(out_path)

   # Open user interface of GMSH
   # gmsh.fltk.run()

   # Mesh file name and output
   gmsh.finalize()

def run(run_mesh_config: RunMeshConfig):
   for config_param in run_mesh_config:
      print("-> Starting to mesh: " + config_param[0].path)
      mesh(config_param[0].cyl_pos, config_param[0].path, config_param[1])
      print("-> Done meshing: " + config_param[0].path)

if __name__ == "__main__":
   import run_mesh_config
   run(run_mesh_config.to_run)