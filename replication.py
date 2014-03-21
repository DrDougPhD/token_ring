# Each MSS maintain a copy of the pending requests of any migrant MH.		//Storage
# Token can be delivered by Local MSS only.								//constraints
# request sent by MH is request for token
# need a way to identify local MSS
# Is there anything such as an array of queues?


N = Total Number of MSS
h = MH.id
h.counter = 0
h.Flag = false
h.tokenMH = false

H = MSS.id
H.tokenMSS = false
H.counter = 0
H.priorityNumber = 0


class MobileHost:
  def request(self):
    self.counter += 1 # NOT sure what we are doing with this
    self.localMSS.priorityNumber += 1
    self.priorityNumber = self.localMSS.priorityNumber
    # MSS local to the MH sending the message;not sure if syntax is correct
    self.localMSS.Q.append([self, self.counter, self.Flag, self.priorityNumber]) 


  def move(self):
	  # join(h, h.counter) to new MSS.		//trying to understand what is the use of doing this
	  # Add the information of this MH in say a storage called 'localMH'
    pass


  def release(self):
	  self.tokenMH = False
    self.delete()


  def delete(self):
	  for mss in self.all_MSS:
		  mss.Q.remove(h, h.counter, h.Flag, h.priorityNumber)
		  mss.priorityNumber -= 1
		  mss.counter -= 1


class MobileServiceStation:
  def grant(self, h):
	  if h.Flag and h in self.local_MHs and True: #counter value of MH is equal to MH))		//NOt sure about the last two criteria 
    	h.tokenMH = True
    	print("Token Received::Global resources accessed")
      h.release()


  def replicate(self):
    //Tag request() Flag as false
    //priorityNumber added to request() based on its position within the Q
    for(i=0;i<N;i++)		//send copy of request() to all other MSS
      //Performing the selection of highest priorityNumber here only;instead of sending it back and forth. If required can put this piece after entire append (**optional part**) of all MSS, Then N will
      N -1 for this parent for loop
      temporary = 0
      temporary = H[i].priorityNumber
      if(temporary > h.priorityNumber)
        h.priorityNumber = temporary
      h.Flag = true
      H[i].Q.append(h, h.counter, h.Flag, h.priorityNumber)		//make sure you do not append it again to the original MSS. N is the total number of MSS 
      Sort request Q by every MSS // An insertion sort on all the MSS based on new assigned h.priorityNumber - is there an efficient way to do it (N number of sort for N Qs)
    grant(Q)	//First request after the sort


MSS side==>

if(currentMSS is the one to receive the token)
	H.tokenMSS = true
	if(H.counter > 0)	A request is there in the request queue of the MSS having the token
		for each request in the request Q    //Syntax?
			dataReplicationProtocol()
		H.counter--
		
MSS()
//maintain queue of request.
//Each request has a flag: Deliverable (D); Undeliverable (uD)
//Structure of the queue thus becomes:
h.Flag = false
h.priorityNumber = 0 						//how to assign the priorityNumbers?
MSS.Q.append(request(h, counter), h.Flag, h.priorityNumber) 	//Want to keep this 3 things together for every request but still want to treat them separately		

"""
**Optional Part***Not revised - one time write: revise if you use this
	//Other MSS received the request()
	//They overwrite the priorityNumber of the request() with temporaryPriorityNumber based on the priorityNumber of that request() in their Q		
	//send back the temporaryPriorityNumber set by all other MSS back to the original MSS			
	//After receiving all the temporaryPriorityNumber sort it in descending order
	for(i=0;i<N - 1);i++) // Receiving the priorityNumber from all the other MSS by the parent MSS
		if(h.temporaryPriorityNumber > h.priorityNumber)	//Not sure how to differentiate between these two; Maybe use an MSS identifier
			h.priorityNumber = h.temporaryPriorityNumber 
		//Select the largest priorityNumber as the new priorityNumber of the request()
		for(i=0;i<N - 1);i++)
			h.Flag = true
			MSS[i].Q.append(request(h, counter), h.Flag, h.priorityNumber)
		 
//Once every MSS has the chosen priority number 
//Every MSS re-sorts delivery queue after the last for loop operation -- not sure what this means

//Request can be served by an MSS if:
grant()
"""
