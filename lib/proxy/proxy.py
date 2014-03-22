from __future__ import absolute_import
from ..hexagon import Hexagon
from ..hexagon import rotate_60
from ..hexagon import I_2
from .request import TokenRequest
import numpy
from .mss import MobileServiceStation
import pygame
from ..utils import transform_points_for_pygame

class Proxy(Hexagon):
  # When a mobile host underneath this proxy makes a request for the token,
  #  it requests the token from its local MSS. This MSS then forwards this
  #  request to its proxy.

  # If this Proxy is holding a request for a mobile host, and that mobile host
  #  has moved, then this proxy will receive an update of this move which
  #  contains the identify of the mobile host and its current proxy.

  # The Proxies form a token ring. When this proxy receives the token, the
  #  request queue is shifted into the grant queue. Until the grant queue is
  #  empty:
  #    1. Pop a request from the queue.
  #    2. If the mobile host of this request is within this proxy, then search
  #        each MSS under this proxy for that mobile host. Once the MSS is
  #        found, issue that MSS the token so that it can issue the token to
  #        the mobile host.
  #    3. If the mobile host of this request is not local, then deliver the
  #        token to the current proxy of the mobile host.
  #    4. The remote proxy will return the token once the mobile host releases
  #        it.
  #  Once the grant queue is empty, forward the token to the next proxy.
  def __init__(self, *args, **kwargs):
    Hexagon.__init__(self, *args, **kwargs)
    self.next = None
    self.local_MSSs = self.create_internal_MSSs()
    self.has_token = False
    self.requests = []
    self.grant_queue = []
    self.is_serving_requests = False


  def request_token(self, phone):
    print("Proxy {0} received a token request from phone {1}".format(
      self.id,
      phone.id
    ))
    self.requests.append(
      TokenRequest(mobile_host=phone, proxy=self)
    )


  def join(self, phone, old_proxy):
    # Test if the mobile phone has made a wide-area move. If the mobile phone
    #  is no longer under the proxy in which it made its request, then that
    #  proxy must be updated.
    print("Proxy {0} has received JOIN from phone {1}, who made a request on proxy {2}".format(
      self.id,
      phone.id,
      old_proxy.id
    ))
    old_proxy.update_request(phone, self)


  def update_request(self, phone, new_proxy):
    # A request has been made by the phone to this proxy. However, the phone
    #  has moved, and the request information must be updated.
    print("Updating request from phone {0} on proxy {1} to point to proxy {2}".format(
      phone.id,
      self.id,
      new_proxy.id
    ))
    for r in self.requests:
      if r.mobile_host == phone:
        r.proxy = new_proxy
        return


  def create_internal_MSSs(self):
    M = 2*rotate_60 + I_2
    new_north_direction = M.I*self.northeast_dir
    new_side_length = numpy.linalg.norm(new_north_direction)

    if (self.depth+1)%2 == 0:
      north_unit_vector = numpy.array([(0, 1)]).T

    else:
      north_unit_vector = new_north_direction/new_side_length

    internal_center_hexagon = MobileServiceStation(
      center=self.center,
      northern_most_unit_vector_direction=north_unit_vector,
      side_length=new_side_length,
      parent=self,
      depth=self.depth+1,
      color=self.color
    )
    for i in range(self.number_of_sides):
      center = internal_center_hexagon.get_center_point_of_neighbor(i)
      self.internal_hexagons[i] = MobileServiceStation(
        center=center,
        northern_most_unit_vector_direction=north_unit_vector,
        side_length=new_side_length,
        parent=self,
        depth=self.depth+1,
        color=self.color
      )

    # Set the center hexagon.
    self.internal_hexagons[-1] = internal_center_hexagon

    return self.internal_hexagons


  def send_token(self):
    self.has_token = True


  def pass_token(self):
    print("Sending token: Proxy {0} => Proxy {1}".format(
      self.id,
      self.next.id
    ))
    self.is_serving_requests = False
    self.next.send_token()
    self.has_token = False


  def progress(self):
    print("#"*80)
    if self.has_token:
      # If the Request Queue is not empty, then it must be served.
      if self.requests and len(self.grant_queue) == 0 and not self.is_serving_requests:
        print("Proxy {0} has {1} requests!"
              "Emptying the request queue into the grant queue.".format(
          self.id,
          len(self.requests)
        ))
        self.grant_queue = list(self.requests)
        self.requests = []

      # If the Grant Queue is not empty, serve the next grant.
      if self.grant_queue:
        self.is_serving_requests = True
        print("State of grant queue for proxy {0}:".format(self.id))
        print(self.grant_queue)
        request = self.grant_queue.pop(0)
        print("Proxy {0} is granting request of phone {1}".format(
          self.id,
          request.mobile_host.id
        ))
        request.proxy.serve_token(request.mobile_host)

      else:
        self.pass_token()


  def serve_token(self, phone):
    # The mobile host is under the calling proxy's jurisdiction.
    print("Proxy {0} will now grant the token to phone {1}".format(
      self.id,
      phone.id
    ))
    print("Searching for MSS of phone {0}".format(phone.id))
    for mss in self.internal_hexagons:
      if mss.has(phone):
        print("MSS {0} indicates that phone {1} is within its jurisdiction".format(
          mss.id,
          phone.id
        ))
        print("Proxy {0} is granting MSS {1} the token, to grant to phone {2}".format(
          self.id,
          mss.id,
          phone.id
        ))
        mss.serve_token(phone)
        print("Proxy {0} has received token back from MSS {1} / Phone {2}".format(
          self.id,
          mss.id,
          phone.id
        ))
        return


  def draw(self, color=None, width=0):
    Hexagon.draw(self, color, width)
    if self.has_token:
      x = int(float(self.center[0]))
      y = int(float(self.center[1]))
      circle_center = (x, y)
      pygame.draw.circle(
        pygame.display.get_surface(),
        (218,165,32), # goldenrod
        transform_points_for_pygame([circle_center])[0],
        70
      )
