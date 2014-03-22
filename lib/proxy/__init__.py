from __future__ import absolute_import
import numpy
from ..hexagon import Hexagon
from .proxy import Proxy

def setup_coverage_areas(X_RES, Y_RES):
  root = ProxyCreator(
    center=numpy.array([(X_RES/2, Y_RES/2)]).T,
    northern_most_unit_vector_direction=numpy.array([(0, 1)]).T,
    side_length=Y_RES/2,
    color=(127, 127, 127)
  )

  return [
    root.proxies,
    root.service_stations
  ]


class ProxyCreator(Hexagon):
  def __init__(self, *args, **kwargs):
    Hexagon.__init__(self, *args, **kwargs)
    self.proxies = self.create_proxies()
    self.ring_members = self.proxies

    # Create the MSS regions within each proxy.
    self.service_stations = []
    for p in self.proxies:
      self.service_stations.extend(p.local_MSSs)
    self.create_ring()


  def create_proxies(self):
    new_north_direction = self.M_I*self.northeast_dir
    new_side_length = numpy.linalg.norm(new_north_direction)

    if (self.depth+1)%2 == 0:
      north_unit_vector = numpy.array([(0, 1)]).T

    else:
      north_unit_vector = new_north_direction/new_side_length

    internal_center_hexagon = Proxy(
      center=self.center,
      northern_most_unit_vector_direction=north_unit_vector,
      side_length=new_side_length,
      parent=self,
      depth=self.depth+1
    )
    for i in range(self.number_of_sides):
      center = internal_center_hexagon.get_center_point_of_neighbor(i)
      self.internal_hexagons[i] = Proxy(
        center=center,
        northern_most_unit_vector_direction=north_unit_vector,
        side_length=new_side_length,
        parent=self,
        depth=self.depth+1
      )

    # Set the center hexagon.
    self.internal_hexagons[-1] = internal_center_hexagon

    return self.internal_hexagons


  def create_ring(self):
    for i in range(len(self.ring_members)):
      self.ring_members[i].next = self.ring_members[
        (i+1) % len(self.ring_members)
      ]
