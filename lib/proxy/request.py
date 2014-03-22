
class TokenRequest:
  def __init__(self, mobile_host, proxy):
    self.mobile_host = mobile_host
    self.proxy = proxy


  def __repr__(self):
    return "< Phone({0}), Proxy({1}) >".format(
      self.mobile_host.id,
      self.proxy.id
    )

