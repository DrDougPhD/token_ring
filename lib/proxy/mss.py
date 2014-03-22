from __future__ import absolute_import
from . import Hexagon # should be in __init__.py?

class MobileServiceStation(Hexagon):
  # MSS must know which proxy it is under. When a mobile host joins this MSS,
  #  the MSS must be able to compare the identity of the proxy in which the
  #  mobile host was previously in with this MSS's current proxy.
  #  If the mobile host has made a wide-area move, this MSS must inform the
  #  initial proxy of the new proxy.

  # Requests for the token from a local mobile host must be forwarded to the
  #  proxy of this MSS.

  def __init__(self, *args, **kwargs):
    Hexagon.__init__(self, *args, **kwargs)


  def join(self, mobile_host, old_station):
    print("MSS {0} received JOIN from phone {1}".format(
      self.id,
      mobile_host.id
    ))

    if old_station is not None and old_station.parent != self.parent:
      proxy_of_old_MSS = old_station.parent
      self.parent.join(mobile_host, proxy_of_old_MSS)

  def request_token(self, phone):
    print("MSS {0} received a token request from phone {1}".format(
      self.id,
      phone.id
    ))
    self.parent.request_token(phone)


  def has(self, phone):
    # Since the MSS is a derived Hexagon type, which is a derived Polygon,
    #  the function contains() will determine if the phone's location
    #  is contained within the hexagon.
    print("MSS {0} queried if it has phone {1}".format(self.id, phone.id))
    print("    {0}".format(self == phone.PCS_cell))
    return self == phone.PCS_cell


  def serve_token(self, phone):
    print("MSS {0} will grant the token to phone {1}".format(
      self.id,
      phone.id
    ))
    phone.send_token()
    print("Token returned from phone {0} to MSS {1}".format(
      phone.id,
      self.id
    ))

