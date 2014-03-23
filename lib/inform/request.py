
class TokenRequest:
  def __init__(self, mobile_host, mss):
    self.mobile_host = mobile_host
    self.mss = mss


  def __repr__(self):
    return "< Phone({0}), MSS({1}) >".format(
      self.mobile_host.id,
      self.mss.id
    )

