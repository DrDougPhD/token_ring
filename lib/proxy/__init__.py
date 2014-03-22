from __future__ import absolute_import
import numpy
from ..hexagon import Hexagon
from ..hexagon import rotate_60
from ..hexagon import I_2
from .proxy import Proxy

def create_proxies_and_MSSs(X_RES, Y_RES):
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

    # Create the MSS regions within each proxy.
    self.service_stations = []
    for p in self.proxies:
      self.service_stations.extend(p.local_MSSs)


  def create_proxies(self):
    M = 2*rotate_60 + I_2
    new_north_direction = M.I*self.northeast_dir
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

    self.create_proxy_ring()
    return self.internal_hexagons


  def create_proxy_ring(self):
    for i in range(len(self.internal_hexagons)):
      self.internal_hexagons[i].next_proxy = self.internal_hexagons[
        (i+1) % len(self.internal_hexagons)
      ]
