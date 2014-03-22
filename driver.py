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

def draw_all_hexagons(hexagons, phone):
  for h in hexagons:
    h.draw()

  for h in hexagons:
    if phone.PCS_cell != h:
      h.draw(color=(0,0,0), width=2)
    else:
      h.draw(color=(255,255,255), width=5)


if __name__ == "__main__":
  import sys
  pygame.init()

  screen = pygame.display.set_mode((X_RES, Y_RES))
  BACKGROUND_COLOR = (127, 127, 127)
  screen.fill(BACKGROUND_COLOR)

  from lib.proxy import setup_coverage_areas
  #from lib.replication import setup_coverage_areas
  hexagons = setup_coverage_areas(X_RES, Y_RES)
  PCS_cells = hexagons[-1]
  current_depth = len(hexagons)-1

  # Give the first proxy the token.
  proxies = hexagons[0]
  token_holder = proxies[0]
  token_holder.send_token()

  from lib.proxy.mh import create_phones
  phone_dict = create_phones(PCS_cells, X_RES, Y_RES)
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
            mobile_host.request_token()

          else:
            # The user is pressing only one key, which is a label for another
            #  phone. Make this phone the currently selected phone.
            print("Changing focus from phone {0} to phone {1}".format(
              selected_phone.id,
              phone_dict[key].id
            ))
            selected_phone = phone_dict[key]

        # Execute the next step of the Token Ring algorithm.
        elif event.key == pygame.K_SPACE:
          token_holder.progress()
          if not token_holder.has_token:
            token_holder = token_holder.next

        # Check to see if the phone is still in the previously set cell.
        if selected_phone.has_moved_to_new_cell():
          selected_phone.update_location()

        # Redraw the hexagons that are on the currently selected depth.
        draw_all_hexagons(hexagons[current_depth], selected_phone)

        # Draw all of the phones to the screen.
        phones.update()
        phones.draw(screen)
        pygame.display.update()

