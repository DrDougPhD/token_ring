from __future__ import absolute_import
from ..phone import Phone

def create_phones(cells, X_RES, Y_RES):
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
    phone_dict[l] = MobileHost(
      char=l.upper(),
      center=phone_locations[phone_labels.index(l)],
      cells=cells
    )
  return phone_dict


class MobileHost(Phone):
  def __init__(self, *args, **kwargs):
    Phone.__init__(self, *args, **kwargs)
    self.request_made_to_MSS = None


  def request_token(self):
    if self.request_made_to_MSS is None:
      print("Phone {0} is requesting the token".format(self.id))
      self.PCS_cell.request_token(self)
      self.request_made_to_MSS = self.PCS_cell

    else:
      print("Phone {0} already has a pending request!".format(self.id))


  def update_location(self):
    # Preserve a reference to the old MSS before updating.
    old_MSS = self.PCS_cell

    # Update the location of the phone by finding the new MSS in which it is
    #  located.
    Phone.update_location(self)

    # Join this MSS, passing in a reference to the old MSS.
    print("Mobile host {0} has moved from MSS {1} to MSS {2}".format(
      self.id,
      old_MSS.id,
      self.PCS_cell.id
    ))
    self.PCS_cell.join(self, self.request_made_to_MSS)


  def send_token(self):
    print("Phone {0} has received the token!".format(self.id))
    print("  "+"X"*20)
    print("    Phone {0} => CRITICAL SECTION".format(self.id))
    print("  "+"X"*20)
    self.request_made_to_MSS = None
