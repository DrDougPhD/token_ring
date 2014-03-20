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
    side_length=side_length
  )
  level_1_hexagons = root_hexagon.create_internal_hexagons()
  level_2_hexagons = []
  for h in level_1_hexagons:
    level_2_hexagons.extend(h.create_internal_hexagons())

  hexagons = [
    [root_hexagon],
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


if __name__ == "__main__":
  import sys
  pygame.init()

  screen = pygame.display.set_mode((X_RES, Y_RES))
  BACKGROUND_COLOR = (127, 127, 127)
  screen.fill(BACKGROUND_COLOR)

  # Create every hexagon on each level.
  hexagons = create_all_hexagons(
    center=(X_RES/2, Y_RES/2),
    side_length=Y_RES/2,
    location_manager=Hexagon
  )
  PCS_cells = hexagons[-1]
  current_depth = len(hexagons)-1

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
            print("Phone #{0} is doing something!".format(mobile_host.id))

          else:
            # The user is pressing only one key, which is a label for another
            #  phone. Make this phone the currently selected phone.
            selected_phone = phone_dict[key]
            print("Phone #{0} is selected.".format(selected_phone.id))

        # Check to see if the phone is still in the previously set cell.
        if selected_phone.has_moved_to_new_cell():
          selected_phone.update_location()

        # Redraw the hexagons that are on the currently selected depth.
        draw_all_hexagons(hexagons[current_depth], selected_phone)

        # Draw all of the phones to the screen.
        phones.update()
        phones.draw(screen)
        pygame.display.update()

