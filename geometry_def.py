"""
This script contain the definition of geometrical objects needed to build the geometry.
"""

from operator import attrgetter
import gmsh
import numpy as np
import math


class Point:
    """
    A class to represent the point geometrical object of gmsh

    ...

    Attributes
    ----------
    x : float
        position in x
    y : float
        position in y
    z : float
        position in z
    mesh_size : float
        If mesh_size is > 0, add a meshing constraint
            at that point
    """

    def __init__(self, x, y, mesh_size):

        self.x = x
        self.y = y
        self.z = 0

        self.mesh_size = mesh_size
        self.dim = 0

        # create the gmsh object and store the tag of the geometric object
        self.tag = gmsh.model.occ.addPoint(self.x, self.y, self.z, self.mesh_size)

    def rotation(self, angle, origin, axis):
        """
        Methode to rotate the object Point
        ...

        Parameters
        ----------
        angle : float
            angle of rotation in rad
        origin : tuple
            tuple of point (x,y,z) which is the origin of the rotation
        axis : tuple
            tuple of point (x,y,z) which represent the axis of rotation
        """
        gmsh.model.occ.rotate(
            [(self.dim, self.tag)],
            *origin,
            *axis,
            angle,
        )

    def translation(self, vector):
        """
        Methode to translate the object Point
        ...

        Parameters
        ----------
        direction : tuple
            tuple of point (x,y,z) which represent the direction of the translation
        """
        gmsh.model.occ.translate([(self.dim, self.tag)], *vector)


class Line:
    """
    A class to represent the Line geometrical object of gmsh

    ...

    Attributes
    ----------
    start_point : Point
        first point of the line
    end_point : Point
        second point of the line
    """

    def __init__(self, start_point, end_point):
        self.start_point = start_point
        self.end_point = end_point

        self.dim = 1

        # create the gmsh object and store the tag of the geometric object
        self.tag = gmsh.model.occ.addLine(self.start_point.tag, self.end_point.tag)

    def rotation(self, angle, origin, axis):
        """
        Methode to rotate the object Line
        ...

        Parameters
        ----------
        angle : float
            angle of rotation in rad
        origin : tuple
            tuple of point (x,y,z) which is the origin of the rotation
        axis : tuple
            tuple of point (x,y,z) which represent the axis of rotation
        """
        gmsh.model.occ.rotate(
            [(self.dim, self.tag)],
            *origin,
            *axis,
            angle,
        )

    def translation(self, vector):
        """
        Methode to translate the object Line
        ...

        Parameters
        ----------
        direction : tuple
            tuple of point (x,y,z) which represent the direction of the translation
        """
        gmsh.model.occ.translate([(self.dim, self.tag)], *vector)

class CurveLoop:
    """
    A class to represent the CurveLoop geometrical object of gmsh
    Curveloop object are an addition entity of the existing line that forms it
    Curveloop must be created when the geometry is in its final layout

    ...

    Attributes
    ----------
    line_list : list(Line)
        List of Line object, in the order of the wanted CurveLoop and closed
    """

    def __init__(self, line_list):

        self.line_list = line_list
        self.dim = 1

        # generate the Lines tag list to folow
        self.tag_list = [line.tag for line in self.line_list]
        # create the gmsh object and store the tag of the geometric object
        self.tag = gmsh.model.occ.addCurveLoop(self.tag_list)


class Circle:
    """
    A class to represent a Circle geometrical object, composed of many arcCircle object of gmsh

    ...

    Attributes
    ----------
    xc : float
        position of the center in x
    yc : float
        position of the center in y
    z : float
        position in z
    radius : float
        radius of the circle
    mesh_size : float
        determine the mesh resolution and how many segment the
        resulting circle will be composed of
    """

    def __init__(self, xc, yc, diameter, n_points):
        # Position of the disk center
        self.xc = xc
        self.yc = yc
        self.zc = 0

        self.radius = diameter/2
        self.mesh_size = diameter/n_points
        self.dim = 1

        # create a structured arcCricle to merge in one curveloop
        self.distribution = int(n_points*np.pi)
        self.arcCircle_list = [
            gmsh.model.occ.addCircle(
                self.xc,
                self.yc,
                self.zc,
                self.radius,
                angle1=2 * np.pi / self.distribution * i,
                angle2=2 * np.pi / self.distribution * (1 + i),
            )
            for i in range(0, self.distribution)
        ]
        # Remove the duplicated points generated by the arcCircle
        gmsh.model.occ.synchronize()
        gmsh.model.occ.removeAllDuplicates()

    def close_loop(self):
        """
        Method to form a close loop with the current geometrical object

        Returns
        -------
        _ : int
            return the tag of the CurveLoop object
        """
        return gmsh.model.occ.addCurveLoop(self.arcCircle_list)

    def define_bc(self, name):
        """
        Method that define the marker of the circle
        for the boundary condition
        -------
        """

        self.bc = gmsh.model.addPhysicalGroup(self.dim, self.arcCircle_list)
        self.physical_name = gmsh.model.setPhysicalName(self.dim, self.bc, name)

    def rotation(self, angle, origin, axis):
        """
        Methode to rotate the object Circle
        ...

        Parameters
        ----------
        angle : float
            angle of rotation in rad
        origin : tuple
            tuple of point (x,y,z) which is the origin of the rotation
        axis : tuple
            tuple of point (x,y,z) which represent the axis of rotation
        """
        [
            gmsh.model.occ.rotate(
                [(self.dim, arccircle)],
                *origin,
                *axis,
                angle,
            )
            for arccircle in self.arcCircle_list
        ]

    def translation(self, vector):
        """
        Methode to translate the object Circle
        ...

        Parameters
        ----------
        direction : tuple
            tuple of point (x,y,z) which represent the direction of the translation
        """
        [
            gmsh.model.occ.translate([(self.dim, arccircle)], *vector)
            for arccircle in self.arcCircle_list
        ]


class Rectangle:
    """
    A class to represent a rectangle geometrical object, composed of 4 Lines object of gmsh

    ...

    Attributes
    ----------
    xc : float
        position of the center in x
    yc : float
        position of the center in y
    z : float
        position in z
    dx: float
        length of the rectangle along the x direction
    dy: float
        length of the rectangle along the y direction
    mesh_size : float
        attribute given for the class Point
    """

    def __init__(self, xc, yc, dx, dy, mesh_size):

        self.xc = xc
        self.yc = yc
        self.z = 0

        self.dx = dx
        self.dy = dy

        self.mesh_size = mesh_size
        self.dim = 1

        # Generate the 4 corners of the rectangle
        self.points = [
            Point(self.xc - self.dx / 2, self.yc - self.dy / 2, self.mesh_size),
            Point(self.xc + self.dx / 2, self.yc - self.dy / 2, self.mesh_size),
            Point(self.xc + self.dx / 2, self.yc + self.dy / 2, self.mesh_size),
            Point(self.xc - self.dx / 2, self.yc + self.dy / 2, self.mesh_size),
        ]

        # Generate the 4 lines of the rectangle
        self.lines = [
            Line(self.points[0], self.points[1]),
            Line(self.points[1], self.points[2]),
            Line(self.points[2], self.points[3]),
            Line(self.points[3], self.points[0]),
        ]

    def close_loop(self):
        """
        Method to form a close loop with the current geometrical object

        Returns
        -------
        _ : int
            return the tag of the CurveLoop object
        """
        return CurveLoop(self.lines).tag

    def define_bc(self):
        """
        Method that define the different markers of the rectangle for the boundary condition
        self.lines[0] => wall_bot
        self.lines[1] => outlet
        self.lines[2] => wall_top
        self.lines[3] => inlet
        -------
        """

        self.bc_in = gmsh.model.addPhysicalGroup(self.dim, [self.lines[3].tag], tag=-1)
        gmsh.model.setPhysicalName(self.dim, self.bc_in, "inlet")

        self.bc_out = gmsh.model.addPhysicalGroup(self.dim, [self.lines[1].tag])
        gmsh.model.setPhysicalName(self.dim, self.bc_out, "outlet")

        self.bc_wall_top = gmsh.model.addPhysicalGroup(
            self.dim, [self.lines[2].tag]
        )
        gmsh.model.setPhysicalName(self.dim, self.bc_wall_top, "wall_top")

        self.bc_wall_bottom = gmsh.model.addPhysicalGroup(
            self.dim, [self.lines[0].tag]
        )
        gmsh.model.setPhysicalName(self.dim, self.bc_wall_bottom, "wall_bottom")

        self.bc = [self.bc_in, self.bc_out, self.bc_wall_top, self.bc_wall_bottom]

    def rotation(self, angle, origin, axis):
        """
        Methode to rotate the object Rectangle
        ...

        Parameters
        ----------
        angle : float
            angle of rotation in rad
        origin : tuple
            tuple of point (x,y,z) which is the origin of the rotation
        axis : tuple
            tuple of point (x,y,z) which represent the axis of rotation
        """
        [line.rotation(angle, origin, axis) for line in self.lines]

    def translation(self, vector):
        """
        Methode to translate the object Rectangle
        ...

        Parameters
        ----------
        direction : tuple
            tuple of point (x,y,z) which represent the direction of the translation
        """
        [line.translation(vector) for line in self.lines]

class PlaneSurface:
    """
    A class to represent the PlaneSurface geometrical object of gmsh


    ...

    Attributes
    ----------
    geom_objects : list(geom_object)
        List of geometrical object able to form closedloop,
        First the object will be closed in ClosedLoop
        the first curve loop defines the exterior contour; additional curve loop
        define holes in the surface domaine

    """

    def __init__(self, geom_objects):

        self.geom_objects = geom_objects
        # close_loop() will form a close loop object and return its tag
        self.tag_list = [geom_object.close_loop() for geom_object in self.geom_objects]

        self.dim = 2

        # create the gmsh object and store the tag of the geometric object
        self.tag = gmsh.model.occ.addPlaneSurface(self.tag_list)

    def define_bc(self):
        """
        Method that define the domain marker of the surface
        -------
        """
        self.ps = gmsh.model.addPhysicalGroup(self.dim, [self.tag])
        gmsh.model.setPhysicalName(self.dim, self.ps, "fluid")

def add_refinement_zone_rect(xc, yc, length, height, mesh_size, mesh_size_out):
   field = gmsh.model.mesh.field.add("Box")
   gmsh.model.mesh.field.setNumber(field, "VIn", mesh_size)
   gmsh.model.mesh.field.setNumber(field, "VOut", mesh_size_out)
   gmsh.model.mesh.field.setNumber(field, "XMin", xc - length/2)
   gmsh.model.mesh.field.setNumber(field, "XMax", xc + length/2)
   gmsh.model.mesh.field.setNumber(field, "YMin", yc - height/2)
   gmsh.model.mesh.field.setNumber(field, "YMax", yc + height/2)
   gmsh.model.mesh.field.setNumber(field, "Thickness", 0.3)
   gmsh.model.occ.synchronize()
   return field

def add_refinement_zone_cyl(xc, yc, diameter, mesh_size, mesh_size_out):
   field = gmsh.model.mesh.field.add("Cylinder")
   gmsh.model.mesh.field.setNumber(field, "Radius",  diameter/2.)
   gmsh.model.mesh.field.setNumber(field, "VIn", mesh_size)
   gmsh.model.mesh.field.setNumber(field, "VOut", mesh_size_out)
   gmsh.model.mesh.field.setNumber(field, "XCenter", xc)
   gmsh.model.mesh.field.setNumber(field, "YCenter", yc)
   # gmsh.model.mesh.field.setNumber(field, "ZCenter", 2.5)
   gmsh.model.mesh.field.setNumber(field, "XAxis", 0)
   gmsh.model.mesh.field.setNumber(field, "YAxis", 0)
   # gmsh.model.mesh.field.setNumber(field, "ZAxis", 5)
   return field

def extend_from_circle(circle, dist, mesh_size_in, mesh_size_out):
   for curve in circle.arcCircle_list:
      gmsh.model.mesh.setSize(gmsh.model.getEntities(curve), mesh_size_in)
   field = gmsh.model.mesh.field.add("Extend")
   gmsh.model.mesh.field.setNumbers(field, "CurvesList", circle.arcCircle_list)
   gmsh.model.mesh.field.setNumber(field, "DistMax",  dist)
   gmsh.model.mesh.field.setNumber(field, "Power", 1)
   gmsh.model.mesh.field.setNumber(field, "SizeMax", mesh_size_out)
   return field

def threshold(xc, yc, dist_min, dist_max, mesh_size_in, mesh_size_out):
   distance = field = gmsh.model.mesh.field.add("Distance")
   center = gmsh.model.occ.addPoint(xc, yc, 0, mesh_size_in)
   gmsh.model.mesh.field.setNumbers(distance, "PointsList", [center])
   field = gmsh.model.mesh.field.add("Threshold")
   gmsh.model.mesh.field.setNumber(field, "DistMin",  dist_max)
   gmsh.model.mesh.field.setNumber(field, "DistMax", dist_max)
   gmsh.model.mesh.field.setNumber(field, "StopAtDistMax", dist_max*1.1)
   gmsh.model.mesh.field.setNumber(field, "SizeMin", mesh_size_in)
   gmsh.model.mesh.field.setNumber(field, "SizeMax", mesh_size_out)
   gmsh.model.mesh.field.setNumber(field, "InField", distance)
   return field

def custom_distance(xc, yc, dist_min, dist_max, mesh_size_in, mesh_size_out, global_mesh_size):
   expr_field = gmsh.model.mesh.field.add("MathEval")
   if xc >= 0 and yc >= 0:
      expr = "((sqrt((x - {})^2 + (y - {})^2) - {})/{})*({}) + {}".format(xc, yc, dist_min, dist_max - dist_min, mesh_size_out - mesh_size_in, mesh_size_in)
   elif xc < 0 and yc >= 0:
      expr = "(sqrt((x + {})^2 + (y - {})^2) - {})/{}*({}) + {}".format(-xc, yc, dist_min, dist_max - dist_min, mesh_size_out - mesh_size_in, mesh_size_in)
   elif xc < 0 and yc < 0:
      expr = "(sqrt((x + {})^2 + (y + {})^2) - {})/{}*({}) + {}".format(-xc, -yc, dist_min, dist_max - dist_min, mesh_size_out - mesh_size_in, mesh_size_in)
   elif xc >= 0 and yc < 0:
      expr = "(sqrt((x - {})^2 + (y + {})^2) - {})/{}*({}) + {}".format(xc, -yc, dist_min, dist_max - dist_min, mesh_size_out - mesh_size_in, mesh_size_in)
   # print(expr)
   gmsh.model.mesh.field.setString(expr_field, "F",  expr)
   field = gmsh.model.mesh.field.add("Threshold")
   gmsh.model.mesh.field.setNumber(field, "DistMin",  mesh_size_out*0.998)
   gmsh.model.mesh.field.setNumber(field, "DistMax", mesh_size_out*0.999)
   gmsh.model.mesh.field.setNumber(field, "SizeMin", 0.)
   gmsh.model.mesh.field.setNumber(field, "SizeMax", global_mesh_size)
   gmsh.model.mesh.field.setNumber(field, "InField", expr_field)
   field_max = gmsh.model.mesh.field.add("Max")
   gmsh.model.mesh.field.setNumbers(field_max, "FieldsList", [expr_field, field])
   gmsh.model.mesh.field.setAsBackgroundMesh(field_max)
   return field_max

def apply_fields(fields):
   field = gmsh.model.mesh.field.add("Min")
   gmsh.model.mesh.field.setNumbers(field, "FieldsList", fields)
   gmsh.model.mesh.field.setAsBackgroundMesh(field)

class Config:
   """
   A class to represent the config for multiple cylinders
   ...

   Attributes
   ----------
   cyl_pos : [(x, y)]
      positions of the cylinders, the first one should be in (0, 0), you should not exceed 20*D for x (no negative x is recommanded) and 20*D for abs(y)
   path : str
      file for the export of the mesh
   """
   def __init__(self, cyl_pos, path):
      self.cyl_pos = cyl_pos
      self.path = path

class Params:
   """
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
   """
   def __init__(self, diameter, n_points_cyl, height, length_upstream, length_downstream, global_mesh_size, length_refinement, length_refinement_downstream, refined_mesh_size):
      self.diameter = diameter
      self.n_points_cyl = n_points_cyl
      self.height = height
      self.length_upstream = length_upstream
      self.length_downstream = length_downstream
      self.global_mesh_size = global_mesh_size
      self.length_refinement = length_refinement
      self.length_refinement_downstream = length_refinement_downstream
      self.refined_mesh_size = refined_mesh_size

class RunMeshConfig:
   """
   configs_params_array: array of tuple: [(Config, Params)]
   """
   def __init__(configs_params_array):
      self.configs_params_array = configs_params_array