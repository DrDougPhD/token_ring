from __future__ import absolute_import
import numpy
from ..hexagon import Hexagon
from .mss import MobileServiceStation

def setup_coverage_areas(X_RES, Y_RES):
  root = InformCreator(
    center=numpy.array([(X_RES/2, Y_RES/2)]).T,
    northern_most_unit_vector_direction=numpy.array([(0, 1)]).T,
    side_length=Y_RES/2,
    color=(127, 127, 127)
  )

  return [
    root.service_stations
  ]


class InformCreator(Hexagon):
  def __init__(self, *args, **kwargs):
    Hexagon.__init__(self, *args, **kwargs)
    level_1_hexagons = Hexagon.create_internal_hexagons(self)

    # Create the MSS regions within each proxy.
    self.service_stations = []
    for p in level_1_hexagons:
      self.service_stations.extend(self.create_service_stations(p))

    self.create_ring()


  def create_service_stations(self, parent_hexagon):
    new_north_direction = self.M_I*parent_hexagon.northeast_dir
    new_side_length = numpy.linalg.norm(new_north_direction)

    if (self.depth+1)%2 == 0:
      north_unit_vector = numpy.array([(0, 1)]).T

    else:
      north_unit_vector = new_north_direction/new_side_length

    internal_center_hexagon = MobileServiceStation(
      center=parent_hexagon.center,
      northern_most_unit_vector_direction=north_unit_vector,
      side_length=new_side_length,
      parent=parent_hexagon,
      depth=parent_hexagon.depth+1,
      color=parent_hexagon.color
    )
    for i in range(self.number_of_sides):
      center = internal_center_hexagon.get_center_point_of_neighbor(i)
      parent_hexagon.internal_hexagons[i] = MobileServiceStation(
        center=center,
        northern_most_unit_vector_direction=north_unit_vector,
        side_length=new_side_length,
        parent=parent_hexagon,
        depth=parent_hexagon.depth+1,
        color=parent_hexagon.color
      )

    # Set the center hexagon.
    parent_hexagon.internal_hexagons[-1] = internal_center_hexagon
    return parent_hexagon.internal_hexagons


  def create_ring(self):
    for i in range(len(self.service_stations)):
      self.service_stations[i].next = self.service_stations[
        (i+1) % len(self.service_stations)
      ]

      # Since a ring is being formed, let's also rename the areas based on
      #  their order in the ring.
      self.service_stations[i].id = i
