import numpy
from utils import RANDOM_COLOR
from utils import transform_points_for_pygame
from shapely.geometry import Polygon
import pygame
from colors import ColourGenerator
COLORS = ColourGenerator()

pi_d_3 = numpy.pi/3
sin_60_degrees = numpy.sin(pi_d_3)
cos_60_degrees = numpy.cos(pi_d_3)
rotate_60 = numpy.matrix([
      [cos_60_degrees, sin_60_degrees],
      [-sin_60_degrees, cos_60_degrees],
])

I_2 = numpy.matrix([
  [1, 0],
  [0, 1]
])
M = 2*rotate_60 + I_2

UNIQUE_ID = 1


class Hexagon(Polygon):
  number_of_sides = 6
  neighbor_order = ["NE", "E", "SE", "SW", "W", "NW"]
  vertex_order = ["N", "NE", "SE", "S", "SW", "NW"]
  neighbor_index = {"NE": 0, "E": 1, "SE": 2, "SW": 3, "W": 4, "NW": 5}
  vertex_order = {"N": 0, "NE": 1, "SE": 2, "S": 3, "SW": 4, "NW": 5}
  M_I = M.I

  def __init__(self, center=None, northern_most_unit_vector_direction=None,
               side_length=None, parent=None, depth=0, color=None):
    # The Hexagon class is a representation of a 2D planar hexagon,
    #  represented in Cartesian coordinates of the center and all vertices.
    #
    # center := an absolute point, as a 2D numpy column vector, representing
    #  the center of hexagon in a Cartesian coordinate system.
    #
    # northern_most_vertex_direction := a free unit vector, as a 2D numpy
    #  column vector, indicating the direction of the northern-most vertex.
    #
    # side_length := a scalar representing the length of any side of the
    #  resulting hexagon.
    if center is not None and\
       northern_most_unit_vector_direction is not None and\
       side_length is not None:
      self.set(center, northern_most_unit_vector_direction, side_length, parent, depth)
    else:
      self.initialized = False
      self.parent = parent
      self.depth = depth
      self.internal_hexagons = None

    self.color = color if color is not None else RANDOM_COLOR() #COLORS.get_next_RGB()
    # Keys are the phone IDs, values are pointers to the PCS cell or
    #  Registration Area.
    global UNIQUE_ID
    self.id = UNIQUE_ID
    UNIQUE_ID += 1


  def set(self, center, northern_most_unit_vector_direction, side_length, parent, depth=None):
    # The Hexagon class is a representation of a 2D planar hexagon,
    #  represented in Cartesian coordinates of the center and all vertices.
    #
    # center := an absolute point, as a 2D numpy column vector, representing
    #  the center of hexagon in a Cartesian coordinate system.
    #
    # northern_most_vertex_direction := a free unit vector, as a 2D numpy
    #  column vector, indicating the direction of the northern-most vertex.
    #
    # side_length := a scalar representing the length of any side of the
    #  resulting hexagon.
    self.initialized = True
    if depth is not None:
      self.depth = depth
    self.center = center.copy()
    self.north_unit_dir = northern_most_unit_vector_direction.copy()
    self.side_length = side_length
    scaled_north_dir = side_length * northern_most_unit_vector_direction
    north = scaled_north_dir + self.center

    # From the center point and the north vertex, we can compute the other
    #  vertices of the hexagon. Each vertex, relative to the center, is
    #  simply the previous vector rotated by 60 degrees (pi/3 radians).
    # Perform this rotation five times to calculate the direction of all
    #  six hexagon vertices.
    self.vertex_directions = [scaled_north_dir]
    self.vertices = [north]
    for i in range(5):
      prev_direction = self.vertex_directions[-1]
      rotated_direction = rotate_60 * prev_direction
      self.vertex_directions.append(rotated_direction)

      # Calculate Cartesian coordinates of vertex.
      vertex = rotated_direction + self.center
      self.vertices.append(vertex)

    self.north_dir,\
    self.northeast_dir,\
    self.southeast_dir,\
    self.south_dir,\
    self.southwest_dir,\
    self.northwest_dir = self.vertex_directions

    self.north_vertex,\
    self.northeast_vertex,\
    self.southeast_vertex,\
    self.south_vertex,\
    self.southwest_vertex,\
    self.northwest_vertex = self.vertices
    Polygon.__init__(self, self.vertices)

    # The following member variables correspond to points to neighboring
    #  hexagons related to the topological relationship between this hexagon
    #  and neighboring hexagons.
    self.neighboring_hexagons = [None for i in range(6)]
    self.internal_hexagons = [None for i in range(7)]
    self.parent = parent


  def draw(self, color=None, width=0):
    if self.initialized:
      if color is None:
        color = self.color
      pygame.draw.polygon(
        pygame.display.get_surface(),
        color,
        transform_points_for_pygame(self.vertices),
        width
      )

      # Label the hexagons according to their address id.
      label_font = pygame.font.SysFont("monospace", 12)
      label = label_font.render(
        str(self.id),
        True,
        [255-c for c in self.color]
      )
      x = float(self.northwest_vertex[0])
      y = float(self.northwest_vertex[1])
      p = (x+13, y-13)
      label_top_left_corner = transform_points_for_pygame([p])[0]
      pygame.display.get_surface().blit(
        label,
        label_top_left_corner
      )


  def draw_vertices(self, color=None):
    if self.initialized:
      if color is None:
        color = self.color
      map(
        lambda p: pygame.draw.circle(pygame.display.get_surface(), color, p, 4),
        transform_points_for_pygame(self.vertices)
      )


  def create_internal_hexagons(self):
    # Compute the north direction of the hexagons that will be under the root
    #  hexagon.
    new_north_direction = self.M_I*self.northeast_dir
    new_side_length = numpy.linalg.norm(new_north_direction)

    if (self.depth+1)%2 == 0:
      north_unit_vector = numpy.array([(0, 1)]).T

    else:
      north_unit_vector = new_north_direction/new_side_length

    internal_center_hexagon = self.__class__(
      center=self.center,
      northern_most_unit_vector_direction=north_unit_vector,
      side_length=new_side_length,
      parent=self,
      depth=self.depth+1
    )
    for i in range(self.number_of_sides):
      center = internal_center_hexagon.get_center_point_of_neighbor(i)
      self.internal_hexagons[i].set(
        center=center,
        northern_most_unit_vector_direction=north_unit_vector,
        side_length=new_side_length,
        parent=self,
        depth=self.depth+1
      )

    # Set the center hexagon.
    self.internal_hexagons[-1].set(
      center=self.center,
      northern_most_unit_vector_direction=north_unit_vector,
      side_length=new_side_length,
      parent=self
    )
    return self.internal_hexagons


  def create_neighbor(self, i):
    # Create the neighbor of this hexagon according to the neighbor index.
    center = self.get_center_point_of_neighbor(i)
    hexagon = self.__class__(
      center=center,
      northern_most_unit_vector_direction=self.north_unit_dir,
      side_length=self.side_length,
    )

    self.set_neighbor(hexagon, i)
    return hexagon


  def get_center_point_of_neighbor(self, i):
    return self.center + self.vertex_directions[i] +\
           self.vertex_directions[self.next_neighbor_index(i)]


  def previous_neighbor_index(self, i):
    return (i-1)%self.number_of_sides


  def next_neighbor_index(self, i):
    return (i+1)%self.number_of_sides


  def create_northeast_hexagon(self):
    return self.create_neighbor(0)


  def create_east_hexagon(self):
    return self.create_neighbor(1)


  def create_southeast_hexagon(self):
    return self.create_neighbor(2)


  def create_southwest_hexagon(self):
    return self.create_neighbor(3)


  def create_west_hexagon(self):
    return self.create_neighbor(4)


  def create_northwest_hexagon(self):
    return self.create_neighbor(5)


  def set_neighbor(self, neighbor, direction_index):
    self.neighboring_hexagons[direction_index] = neighbor
    neighbor.neighboring_hexagons[(direction_index+3)%6] = self


  def set_northeast_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 0)


  def set_east_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 1)


  def set_southeast_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 2)


  def set_southwest_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 3)


  def set_west_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 4)


  def set_northwest_neighbor(self, neighbor):
    self.set_neighbor(neighbor, 5)


