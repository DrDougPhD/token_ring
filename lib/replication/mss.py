from ..hexagon import Hexagon
from request import TokenRequest
import pygame
from ..utils import transform_points_for_pygame


class MobileServiceStation(Hexagon):
  def __init__(self, *args, **kwargs):
    Hexagon.__init__(self, *args, **kwargs)
    self.next = None
    self.has_token = False
    self.is_serving_requests = False
    self.token_rounds = 0
    self.requests = []
    self.local_mobile_hosts = []


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


  def progress(self):
    print("#"*80)
    if self.has_token:
      # If the Grant Queue is not empty, serve the next grant.
      if self.requests:
        self.is_serving_requests = True
        print("State of request queue for proxy {0}:".format(self.id))
        print(self.requests)
        request_to_serve = None
        for request in self.requests:
          if request.mobile_host in self.local_mobile_hosts and\
             request.round_number == self.token_rounds:
            request_to_serve = request
            break

        if request_to_serve is not None:
          self.requests.remove(request)
          self.serve_token(request.mobile_host)

          for mss in self.get_all_neighbors():
            mss.notify_of_served_request(request)

        else:
          self.pass_token()

      else:
        self.pass_token()


  def notify_of_served_request(self, req):
    print("  Removing {0} from MSS {1}".format(req, self.id))
    self.requests.remove(req)


  def send_token(self):
    self.has_token = True
    self.token_rounds += 1


  def pass_token(self):
    print("Sending token: Proxy {0} => Proxy {1}".format(
      self.id,
      self.next.id
    ))
    self.is_serving_requests = False
    self.next.send_token()
    self.has_token = False


  def join(self, phone):
    print("Phone {0} has joined MSS {1}".format(phone.id, self.id))
    h_count = phone.num_requests
    self.local_mobile_hosts.append(phone)


  def unjoin(self, phone):
    self.local_mobile_hosts.remove(phone)


  def request_token(self, phone):
    # With the local MSS receiving a request from phone, a two phase protocol
    # is executed.
    # Phase 1: Send request to all MSSs
    #  -> Each MSS finds the maximum local request number, as assigns that 
    #      number to this remove request.
    #  -> Each MSS then replies with this maximum request number.
    # Phase 2: Local MSS determines the maximum of all request numbers.
    #  -> Broadcast this request number to all other MSS.
    #  -> Each changes tag on request as deliverable.
    maximum_request_number = self.get_local_maximum_request_number() + 1
    neighbors = self.get_all_neighbors()
    for mss in neighbors:
      i = mss.get_local_maximum_request_number() + 1
      if i > maximum_request_number:
        print("Found larger request # from MSS {0}: {1}".format(
          mss.id,
          i
        ))
        maximum_request_number = i

    request = TokenRequest(phone, maximum_request_number)
    print("Phone {0} requested token from MSS {1}, {2}".format(phone.id, self.id, request))
    for mss in neighbors:
      mss.inform_of_new_request(request)
    self.requests.append(request)


  def get_local_maximum_request_number(self):
    if self.requests:
      return self.requests[-1].request_no

    else:
      return 0


  def inform_of_new_request(self, request):
    print("  MSS {0} notified of {1}".format(self.id, request))
    self.requests.append(request)


  def get_all_neighbors(self):
    neighbors = []
    for parent in self.parent.parent.internal_hexagons:
      neighbors.extend([
        mss for mss in parent.internal_hexagons if mss != self
      ])
    return neighbors

  def serve_token(self, phone):
    print("MSS {0} is serving Phone {1}".format(self.id, phone.id))
    phone.send_token()
    print("MSS {0} has received token back from Phone {1}".format(
      self.id,
      phone.id
    ))

