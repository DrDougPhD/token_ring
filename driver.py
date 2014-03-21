# NOTE: Pygame has the origin of (x, y) = (0, 0) in the top-left corner, with
#  x increasing from left to right, and y increasing from up to down.
#  Thus, the northern-most vertex of a hexagon drawn in this manner will have
#  a y-value less than the center of the hexagon.
import numpy
import math
import random
import time
import pygame
random.seed(time.time())

from settings import X_RES
from settings import Y_RES
from hexagon import Hexagon
from phone import Phone

def create_all_hexagons(center, side_length, location_manager):
  center_point = numpy.array([(center)]).T
  # Create all hexagons within the viewing window.
  root_hexagon = location_manager(
    center=center_point,
    northern_most_unit_vector_direction=numpy.array([(0, 1)]).T,
    side_length=side_length,
    color=(127, 127, 127)
  )
  level_1_hexagons = root_hexagon.create_internal_hexagons()
  level_2_hexagons = []
  for h in level_1_hexagons:
    level_2_hexagons.extend(h.create_internal_hexagons())

  hexagons = [
    level_1_hexagons,
    level_2_hexagons
  ]
  return hexagons


def draw_all_hexagons(hexagons, phone):
  for h in hexagons:
    h.draw()

  for h in hexagons:
    if phone.PCS_cell != h:
      h.draw(color=(0,0,0), width=2)
    else:
      h.draw(color=(255,255,255), width=5)


def create_phones(cells):
  phone_labels = ['a', 'b', 'c', 'd', 'e']
  random_coord_within_screen = lambda coords: [
    random.randint(0, coords[i]) for i in range(2)
  ]
  phone_locations = [
    (X_RES/2., Y_RES/2.),
    (X_RES/2., Y_RES/3.),
    (X_RES/3., Y_RES*3/4.),
    (X_RES*9/11., Y_RES/4.),
    (X_RES/4., Y_RES*4/5.)
  ]

  phone_dict = {}
  for l in phone_labels:
    phone_dict[l] = Phone(
      char=l.upper(),
      center=phone_locations[phone_labels.index(l)],
      cells=PCS_cells
    )
  return phone_dict


class MobileHost(Phone):
  def __init__(self, *args, **kwargs):
    Phone.__init__(self, *args, **kwargs)


  def request(self):
    pass


  def has_moved_to_new_cell(self):
    # Only return True if the mobile host has moved to a new proxy region.
    pass


  def update_location(self):
    # Preserve a reference to the old MSS before updating.
    old_MSS = self.PCS_cell

    # Update the location of the phone by finding the new MSS in which it is
    #  located.
    Phone.update_location(self)

    # Join this MSS, passing in a reference to the old MSS.
    self.PCS_cell.join(self, old_MSS)


  def release(self):
    pass


  def delete(self):
    pass


# from hexagon import Hexagon
from hexagon import rotate_60
from hexagon import I_2
class MobileServiceStation(Hexagon):
  # MSS must know which proxy it is under. When a mobile host joins this MSS,
  #  the MSS must be able to compare the identify of the proxy in which the
  #  mobile host was previously in with this MSS's current proxy.
  #  If the mobile host has made a wide-area move, this MSS must inform the
  #  initial proxy of the new proxy.

  # Requests for the token from a local mobile host must be forwarded to the
  #  proxy of this MSS.

  def __init__(self, *args, **kwargs):
    Hexagon.__init__(self, *args, **kwargs)


  def join(self, mobile_host, old_station):
    pass


  def remove_from_Q(self, mobile_host):
    pass


class TokenRequest:
  def __init__(self, mobile_host, proxy):
    self.mobile_host = mobile_host
    self.proxy = proxy


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
    self.next_proxy = None
    self.local_MSSs = self.create_internal_MSSs()
    self.has_token = False
    self.requests = []
    self.grant_queue = []


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
    self.next_proxy.send_token()
    self.has_token = False


  def progress(self):
    if self.has_token:
      # If the Request Queue is not empty, then it must be served.
      if self.requests and len(self.grant_queue) == 0:
        self.grant_queue = list(self.requests)
        self.requests = []

      # If the Grant Queue is not empty, serve the next grant.
      if self.grant_queue:
        request = self.grant_queue.pop(0)

      else:
        self.pass_token()


  def draw(self, color=None, width=0):
    Hexagon.draw(self, color, width)
    if self.has_token:
      from utils import transform_points_for_pygame
      x = int(float(self.center[0]))
      y = int(float(self.center[1]))
      circle_center = (x, y)
      pygame.draw.circle(
        pygame.display.get_surface(),
        (218,165,32), # goldenrod
        transform_points_for_pygame([circle_center])[0],
        10
      )


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


def create_proxies_and_MSSs():
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


if __name__ == "__main__":
  import sys
  pygame.init()

  screen = pygame.display.set_mode((X_RES, Y_RES))
  BACKGROUND_COLOR = (127, 127, 127)
  screen.fill(BACKGROUND_COLOR)

  hexagons = create_proxies_and_MSSs()
  PCS_cells = hexagons[-1]
  current_depth = len(hexagons)-1

  # Give the first proxy the token.
  proxies = hexagons[0]
  token_holder = proxies[0]
  token_holder.send_token()

  phone_dict = create_phones(PCS_cells)
  phone_labels = [ord(k) for k in phone_dict.keys()]
  selected_phone = phone_dict['a']
  draw_all_hexagons(hexagons[current_depth], selected_phone)

  # Draw each phone on the screen.
  for k in phone_dict:
    p = phone_dict[k]
    screen.blit(p.image, p.rect)

  # Phones need to be added to a render group so that they're updated whenever
  #  they move.
  phones = pygame.sprite.RenderUpdates(phone_dict.values())

  pygame.display.update()

  while True:
    for event in pygame.event.get(): 
      if event.type == pygame.QUIT:
        sys.exit(0) 
      elif event.type == pygame.KEYDOWN:

        # Erase the entire screen for preparation of redrawing.
        screen.fill(BACKGROUND_COLOR)

        # If the Minus key is pressed, interpret this as the user wants to
        #  visualize the the depth that is above the currently displayed depth.
        #  In other words, if current depth = i, display depth i-1.
        if event.key == pygame.K_MINUS:
          if current_depth > 0:
            current_depth -= 1

        elif event.key == pygame.K_EQUALS:
          if current_depth < len(hexagons)-1:
            current_depth += 1

        # If the arrow keys are pressed, then we assume the user wants to move
        #  the currently selected phone in the direction of the key.
        elif event.key == pygame.K_UP:
          selected_phone.move_by((0, 1))

        elif event.key == pygame.K_DOWN:
          selected_phone.move_by((0, -1))

        elif event.key == pygame.K_RIGHT:
          selected_phone.move_by((1, 0))

        elif event.key == pygame.K_LEFT:
          selected_phone.move_by((-1, 0))

        # Test if one of the cell phone labels have been selected.
        elif event.key in phone_labels:
          # We now need to determine if the user is selecting a cell phone, or
          #  if they are calling a cell phone.
          key = chr(event.key)

          # Test if the Ctrl button is selected. This implies the user is
          #  calling another cell phone.
          if pygame.key.get_mods() & pygame.KMOD_CTRL:
            # One of the Ctrl keys is being pressed. This represents a call.
            # The phone initiating the call is the currently selected phone.
            # We must now make sure the callee is not the same as the caller.
            mobile_host = phone_dict[key]
            mobile_host.request()
            print("Phone #{0} is doing something!".format(mobile_host.id))

          else:
            # The user is pressing only one key, which is a label for another
            #  phone. Make this phone the currently selected phone.
            selected_phone = phone_dict[key]
            print("Phone #{0} is selected.".format(selected_phone.id))

        # Execute the next step of the Token Ring algorithm.
        elif event.key == pygame.K_SPACE:
          print("SPACE!!!")
          token_holder.progress()
          if not token_holder.has_token:
            token_holder = token_holder.next_proxy

        # Check to see if the phone is still in the previously set cell.
        if selected_phone.has_moved_to_new_cell():
          selected_phone.update_location()

        # Redraw the hexagons that are on the currently selected depth.
        draw_all_hexagons(hexagons[current_depth], selected_phone)

        # Draw all of the phones to the screen.
        phones.update()
        phones.draw(screen)
        pygame.display.update()

