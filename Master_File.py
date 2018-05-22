# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:20:32 2018

@author: schultz
"""
import Myopic
import NonAnt
import ES_rolling2
import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt

######################################################
#Set-up and Variables
######################################################

def master_scenario(x_t,W):
    q=np.zeros(len(x_t))
    a_t=np.ones(len(x_t))*7
    for t in range(1,len(x_t)):
        #for each time period, solve for queue
        #queue of pending threats to be analyzed @ end t
        q[t]=max(q[t-1]+W[t-1] -(51*(10+x_t[t-1])),0)
        a_t[(t+1):]-=x_t[t-1]
    return q,a_t

#Total number of extra hours that can be alloted
Resource=int(7)
#Total hours of a single horizon
Time=int(336)
#Arrival rate per sensor
Arrival_rate=int(50)
# Service rate = rate per analyst
Service_rate=int(51)
#number sensors in the system
sensors=int(10)
#analysts available in system
analyst=int(10)

#Step 1: produce a demand scenario
peaks=[32,33,54,47,80,70,170,69,210,51,320,47] 
peaks=np.reshape(peaks,(6,2))

Demand=np.sum(np.random.poisson(lam=Arrival_rate,size=(sensors,Time)),axis=0)
#add in some extra demand for realism
for i in range(0,np.shape(peaks)[0]):
    Demand[peaks[i,0]]+=peaks[i,1]*2

######################################################
#Case 1: Never-Use Extra Resources
######################################################
[never_queue,never_use,never_avail]= Myopic.NeverUse_Method(Demand,Resource,Time,Service_rate,analyst)

######################################################
#Case 2: Myopic Use of Resources
######################################################
[myopic_queue,myopic_use,myopic_avail]= Myopic.Myopic_Method(Demand,Resource,Time,Service_rate,analyst)

######################################################
#Case 3: Evolutionary Strategy Use of Resources
######################################################
action_plan=[]
Demand_outcome=[]
for i in range(0,1):
    variables=7-len(action_plan)
    print("time",i)
    print("variables",variables)
    if variables>0:
        ES_iterations= ES_rolling2.Train_ES(4,10,1,60,variables,1000,10,action_plan,Demand_outcome)
        val=np.unique(ES_iterations[:,0])
        if val[0]>0:
            action_plan=np.append(action_plan,[np.ones(val[0])*i])
        Demand_outcome=np.append(Demand_outcome,Demand[i])
        print("arrived to policy", val[0])
        print("action plan up to now:",action_plan)
        print("our list of previous demands",Demand_outcome)

x_t=np.zeros(336)
for i in range(0,len(action_plan)):
    x_t[action_plan[i]]+=1
ES_queue,ES_avail=master_scenario(x_t,Demand)

######################################################
#Case 4: Stochastic with Non-Anticipativity Use of Resources
######################################################

history_x=[]
num_scenario=10
p=np.ones(num_scenario)/num_scenario
for i in range(0,336):
    history_W=Demand[0:i]
    
    num_res=Resource-np.sum(history_x)
    t=Time-i
    W=np.random.poisson(lam=51*10,size=(t,num_scenario))
    initial_q=NonAnt.calc_queue_history(history_x,history_W)
    fq,final_x,objval=NonAnt.solve_for_future(t,num_scenario,p,initial_q[-1],num_res,W)
 #since non-anticpatory constraints require the first decision to be the same among all scenarios,
#    we only need to pull the first x answer
    history_x=np.append(history_x,final_x[0,0])
    
MS_queue,MS_avail=master_scenario(history_x,Demand)
    
######################################################
#Case 5: Dynamic Programming Use of Resources
######################################################
    
##NOTE: The dynamic programming code is run seperate from this. 
#       This will read from a file that has the table from that stored

#read in the action-state and Translator files
states=[600,336,8]
Translator=[]
for i in range(1,states[1]):
    temp= np.array(range(0,states[2]))/float(max(1,i))
    Translator=np.append(Translator,temp)
Translator=np.unique(Translator)
SA_table=genfromtxt("DP_Action_State_Table.dat", delimiter=' ')

unvisited=0
#available resources for use at each time period
DP_a=np.ones(Time)*Resource
#queue at beginning of each time period
DP_q=np.zeros(Time)
#number of extra hours used at the beginning of each time period
DP_x=np.zeros(Time)
for t in range(0,336):
    if t>0:
        print(t,DP_q[t-1],Demand[t-1],DP_x[t-1])
        DP_q[t] = max((DP_q[t-1]+Demand[t-1]-(Service_rate*(10+DP_x[t-1]))),0)
    print("DP_Q(t)=",DP_q[t])
    index=np.where(Translator==(DP_a[t]/float(max(1,335-t))))
    print(index)
    print("res left",DP_a[t],"time",335-t)
    index=int(index[0])
    print("ration left",DP_a[t]/float(max(1,335-t)),DP_a[t],float(max(1,334-t)))
    if SA_table[int(DP_q[t]),int(index)] == -1:
        print("we never visited here")
        unvisited+=1
    else:
        print("we should use %s at time %s" % (SA_table[DP_q[t],index],t))
    valid_action=max(SA_table[DP_q[t],index],0)
    DP_x[t] = min(DP_a[t],valid_action)
    print(DP_a[t],valid_action)
    DP_a[t+1:]-=DP_x[t]
    print(DP_a[(t-1):(t+2)])

print(unvisited)
DP_queue,DP_avail=master_scenario(DP_x,Demand)


######################################################
#Plotting
######################################################

####################Never Use Strategy##########################
a1=plt.figure()
plt.plot(range(Time),never_queue, color='black')

plt.axhspan(0, 50, facecolor='g', alpha=0.5)
plt.axhspan(50, 100, facecolor='y', alpha=0.5)
plt.xlim(0,336)
plt.axhspan(100, np.max((150,np.max(never_queue))), facecolor='r', alpha=0.5)
plt.xlabel("Time (hrs)")
plt.ylabel("Queue (# of alerts)")
plt.title("Never use the extra resources")


####################Myopic Strategy##########################
a1=plt.figure()
plt.plot(range(Time),myopic_queue, color='black')
plt.plot(range(Time),never_queue, color='blue')

plt.axhspan(0, 50, facecolor='g', alpha=0.5)
plt.axhspan(50, 100, facecolor='y', alpha=0.5)
plt.xlim(0,336)
plt.axhspan(100, np.max((150,np.max(myopic_queue))), facecolor='r', alpha=0.5)
plt.xlabel("Time (hrs)")
plt.ylabel("Queue (# of alerts)")
plt.title("Myopic Strategy")


a2=plt.figure()
plt.plot(range(Time),myopic_avail, color='black')
plt.xlim(0,336)
plt.xlabel("Time (hrs)")
plt.ylabel("Available Additional Resources (# of hrs)")
plt.title("Myopic Strategy")


####################Evolutionary Strategy##########################
a3=plt.figure()
plt.plot(range(Time),never_queue, color='blue', label= "No Additional Resource Queue")
plt.plot(range(Time),myopic_queue, color='purple',label="Myopic Strategy Queue")
plt.plot(range(Time),ES_queue, color='black', label= "Evolutionary Strategy Queue")

plt.axhspan(0, 50, facecolor='g', alpha=0.5)
plt.axhspan(50, 100, facecolor='y', alpha=0.5)
plt.legend(bbox_to_anchor=(1.0,1.0))
plt.xlim(0,336)
plt.axhspan(100, np.max((150,np.max(never_queue))), facecolor='r', alpha=0.5)
plt.xlabel("Time (hrs)")
plt.ylabel("Queue (# of alerts)")
plt.title("ES Strategy")



a6=plt.figure()
plt.plot(range(Time),ES_avail, color='black',label="Evolutionary Strategy Resource Use")
plt.plot(range(Time),myopic_avail, color='purple',label="Myopic Strategy Resource Use")
plt.xlabel("Time (hrs)")
plt.legend(bbox_to_anchor=(1.0,1.0))
plt.ylabel("Available Additional Resources (# of hrs)")
plt.title("ES Strategy")



####################Stochastic Strategy##########################
a5=plt.figure()
plt.plot(range(Time),never_queue, color='blue', label= "No Additional Resource Queue")
plt.plot(range(Time),myopic_queue, color='purple',label="Myopic Strategy Queue")
plt.plot(range(Time),MS_queue, color='black',label="Multi-Stage Strategy Queue")


plt.axhspan(0, 50, facecolor='g', alpha=0.5)
plt.axhspan(50, 100, facecolor='y', alpha=0.5)
plt.xlim(0,336)
plt.legend(bbox_to_anchor=(1.0,1.0))
plt.axhspan(100, np.max((150,np.max(never_queue))), facecolor='r', alpha=0.5)
plt.xlabel("Time (hrs)")
plt.ylabel("Queue (# of alerts)")
plt.title("Stochastic Strategy")


a6=plt.figure()
plt.plot(range(Time),MS_avail, color='black',label="Multi-Stage Strategy Resource Use")
plt.plot(range(Time),myopic_avail, color='purple',label="Myopic Strategy Resource Use")
plt.xlabel("Time (hrs)")
plt.legend(bbox_to_anchor=(1.0,1.0))
plt.ylabel("Available Additional Resources (# of hrs)")
plt.title("Stochastic Strategy")


####################DP Strategy##########################
a6=plt.figure()
plt.plot(range(Time),never_queue, color='blue', label= "No Additional Resource Queue")
#plt.plot(range(Time),myopic_queue, color='purple',label= "Myopic Strategy Queue")
plt.plot(range(Time),DP_queue, color='black',label="DP Strategy Queue")

plt.axhspan(0, 50, facecolor='g', alpha=0.5)
plt.axhspan(50, 100, facecolor='y', alpha=0.5)
plt.xlim(0,336)
plt.axhspan(100, np.max((150,np.max(DP_q))), facecolor='r', alpha=0.5)
plt.legend(bbox_to_anchor=(1.0,1.0))
plt.xlabel("Time (hrs)")
plt.ylabel("Queue (# of alerts)")
plt.title("DP Strategy")


a6=plt.figure()
plt.plot(range(Time),DP_avail, color='black',label="DP Strategy Resource Use")
plt.plot(range(Time),myopic_avail, color='purple',label="Myopic Strategy Resource Use")
plt.legend(bbox_to_anchor=(1.0,1.0))
plt.xlim(0,336)
plt.xlabel("Time (hrs)")
plt.ylabel("Available Additional Resources (# of hrs)")
plt.title("DP Strategy")

#######################################33
###MISC
########################################


a6=plt.figure()
plt.plot(range(Time),myopic_avail, color='blue',label="Myopic Strategy Resource Use")
plt.plot(range(Time),never_avail, color='black',label="No Extra Resource Use")
plt.plot(range(Time),ES_avail, color='purple',label="ES Strategy Resource Use")
plt.plot(range(Time),MS_avail, color='green',label="Multi-Staged Non-Anticipative Strategy Resource Use")
plt.plot(range(Time),DP_avail, color='red',label="Dynamic Programming Strategy Resource Use")
plt.xlim(0,336)
plt.legend(bbox_to_anchor=(1.0,1.0))
plt.xlabel("Time (hrs)")
plt.ylabel("Available Additional Resources (# of hrs)")
plt.title("Compare Strategy")
