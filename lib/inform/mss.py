from __future__ import absolute_import
from ..hexagon import Hexagon
from .request import TokenRequest
import pygame
from ..utils import transform_points_for_pygame

class MobileServiceStation(Hexagon):
  def __init__(self, *args, **kwargs):
    Hexagon.__init__(self, *args, **kwargs)
    self.next = None
    self.has_token = False
    self.requests = []
    self.grant_queue = []
    self.is_serving_requests = False


  def request_token(self, phone):
    print("MSS {0} received a token request from phone {1}".format(
      self.id,
      phone.id
    ))
    self.requests.append(
      TokenRequest(mobile_host=phone, mss=self)
    )


  def join(self, phone):
      print("MSS {0} has received JOIN from phone {1}".format(
        self.id,
        phone.id
      ))
      # The phone might have made a request to a previous MSS. Check this.
      if phone.request_made_to_MSS is not None:
        phone.request_made_to_MSS.update_request(phone, self)


  def unjoin(self, phone):
    pass


  def update_request(self, phone, new_mss):
    print("Updating request from phone {0} on MSS {1} to point to MSS {2}".format(
      phone.id,
      self.id,
      new_mss.id
    ))
    for r in self.requests:
      if r.mobile_host == phone:
        r.mss = new_mss
        return


  def send_token(self):
    self.has_token = True


  def pass_token(self):
    print("Sending token: MSS {0} => MSS {1}".format(
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
        print("MSS {0} has {1} requests!"
              "Emptying the request queue into the grant queue.".format(
          self.id,
          len(self.requests)
        ))
        self.grant_queue = list(self.requests)
        self.requests = []

      # If the Grant Queue is not empty, serve the next grant.
      if self.grant_queue:
        self.is_serving_requests = True
        print("State of grant queue for MSS {0}:".format(self.id))
        print(self.grant_queue)
        request = self.grant_queue.pop(0)
        print("MSS {0} is granting request of phone {1}".format(
          self.id,
          request.mobile_host.id
        ))
        request.mss.serve_token(request.mobile_host)
        if request.mss != self:
          print("MSS {0} has received the token back from MSS {1}".format(
            self.id,
            request.mss.id
          ))

      else:
        self.pass_token()


  def serve_token(self, phone):
    # The mobile host is under the calling proxy's jurisdiction.
    print("MSS {0} will now grant the token to phone {1}".format(
      self.id,
      phone.id
    ))
    phone.send_token()
    print("MSS {0} has received token back from Phone {1}".format(
      self.id,
      phone.id
    ))


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
        int(self.side_length/2.0)
      )
