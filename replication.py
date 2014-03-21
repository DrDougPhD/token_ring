class MobileHost(Phone):
  def __init__(self, *args, **kwargs):
    Phone.__init__(self, *args, **kwargs)
    self.h_count = 0
    self.tokenMH = False
 
 
  def request(self):
    self.h_count += 1     # Tracks the number of request made a phone
    self.PCS_cell.send_request(self)

 
  def update_location(self):
    # Preserve a reference to the old MSS before updating.
    #Calling PCS_cell to get the information of localMSS
    old_MSS = self.PCS_cell
 
    # Update the location of the phone by finding the new MSS in which it is
    #  located.
    Phone.update_location(self)
 
    # Join this MSS, passing in a reference to the old MSS.
    self.PCS_cell.join(self, old_MSS)
 
 
  def release(self):
	  self.tokenMH = False
    self.delete()
 
 
  def delete(self):	#where did you get mss from? Would it be PCS_cell or hexagon? or is the class name below?
	  for mss in self.cells:
		  mss.remove_from_Q(self)
		  mss.priorityNumber -= 1
		  mss.counterMSS -= 1
 
class Request:
  def __init__(self, phone_id, number, count, is_deliverable=False):
    self.phone_id = phone_id
    self.number = number
    self.count = count
    self.is_deliverable = is_deliverable


class MobileServiceStation(Hexagon):
  def grant(self):
    # Convert the request queue to the grant queue if the request queue is not empty and the grant queue is empty.
#################################################################################################
    self.counter -= 1
    request = self.Q.pop(0)
    if request.is_deliverable and request.phone_id == self:

    else:
			if((MobileHost.Flag == true) && (MobileHost.PCS_cell == this PCS_cell) && (MobileHost.counter == self.count[MHid])) #MH.id given as self. How to call from here?		
				MobileHost.tokenMH = true
				print("Token Received::Global resources accessed")
				MobileHost.release()

  def inform_of_new_request(self, request):
    self.remote_requests.append(request)
    self.priorityNumber += 1


  def send_request(self, phone):
    self.counter += 1
    self.priorityNumber += 1
    globally_maximum_request_number = self.priorityNumber
    for n in self.neighbor_MSSs:
      if n.priorityNumber + 1 > globally_maximum_request_number:
        globally_maximum_request_number = n.priorityNumber + 1

    # We have the globally maximum request number.
    request = Request(
      phone_id=phone,
      number=globally_maximum_request_number,
      count=phone.h_count,
      is_deliverable=True
    )
    self.Q.append(request)
    for n in self.neighbor_MSSs:
      n.inform_of_new_request(request)


  def __init__(self, *args, **kwargs):
    Hexagon.__init__(self, *args, **kwargs)
    self.tokenMSS = False
    self.count[] = {countMH1, countMH2, countMH3} # suppose we have three MH, each MSS will have this storage. Gotta update the respective MH at the time of a request 
    self.counter = 0
    self.priorityNumber = 0
    self.Q = []
    self.remote_requests = []

				

	
 
 
  def join(self, mobile_host, old_station):
    pass
 
 
  def remove_from_Q(self, mobile_host):
    pass
    
