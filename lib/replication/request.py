class TokenRequest:
  def __init__(self, mobile_host, request_no):
    self.mobile_host = mobile_host
    self.round_number = mobile_host.num_requests
    self.request_no = request_no


  def __repr__(self):
    return "< Phone({0}), Request #{1}, Round #{2} >".format(
      self.mobile_host.id,
      self.request_no,
      self.round_number
    )
