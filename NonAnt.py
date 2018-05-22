# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 10:25:23 2018

@author: schultz
"""

from gurobipy import *
import numpy as np

def calc_queue_history(history_x,history_W):
    q=np.zeros(1)
    for t in range(0,len(history_W)):
        q=np.append(q,(np.max((q[t]+history_W[t] -(51*(10+history_x[t])),0))))
    return q

def solve_for_future(horizon,num_scen,p,initial_q,num_resource,W):
    m=Model("NonAnt")
    m.Params.timeLimit= 5*60
    print(horizon,type(horizon))
    print(num_scen)
    #create a variable for x,q, and c (and d for making linear)
    varsx = m.addVars(horizon,num_scen, lb=0, vtype=GRB.INTEGER, name='X')
    varsq = m.addVars(horizon,num_scen, lb=0, vtype=GRB.CONTINUOUS, name='Q')
    varsc = m.addVars(horizon,num_scen, lb=0, vtype=GRB.CONTINUOUS, name='C')
    m.update()
    
    
    #Add objective
    m.setObjective(quicksum(p[s]*quicksum((varsc[t,s]*(1/float(50))-((7-quicksum(varsx[k,s] for k in range(0,t)))/float(7))) for t in range(0,horizon)) for s in range(0,num_scen)),GRB.MINIMIZE)
#    m.setObjective(quicksum(p[s]*quicksum((varsc[t,s]/float(50))-((7-quicksum(varsx[k,s] for k in range(0,t)))/float((335-t))) for t in range(0,horizon)) for s in range(0,num_scen)),GRB.MINIMIZE)
   
    
    m.update()

    
    #Add Constraints for AX<=B
    ##q[0,s]=initial_q for every s
    m.addConstrs((varsq[0,s] == initial_q
                  for s in range(0,num_scen)),name='Ci')
    
    
    ##can't have more resources used then what is available
    m.addConstrs((quicksum(varsx[t,s] for t in range(0,horizon)) <= num_resource
                  for s in range(0,num_scen)),name='Cx')
    
    m.addConstrs((varsq[t,s] >= varsq[t-1,s] + W[t-1,s] - (51*(10+varsx[t-1,s]))  
                  for t in range(1,horizon)
                  for s in range(0,num_scen)), name='Cqm')
    m.addConstrs((varsq[t,s] >= 0
                  for t in range(1,horizon)
                  for s in range(0,num_scen)), name='Cqu')
        
        ##cost relationship is max(q-50,0)
    m.addConstrs((varsc[t,s] >= varsq[t,s]-50
                  for t in range(0,horizon)
                  for s in range(0,num_scen)), name='Cc')
    m.addConstrs((varsc[t,s] >= 0
                  for t in range(1,horizon)
                  for s in range(0,num_scen)), name='Cc')
    
    ##\[x_{t,s} = x_{t,s'} \forall t,s,s': (W_{1,s},...W_{t-1,s}) = (W_{1,s'},...W_{t-1,s'})\]
    for t in range(0,np.shape(W)[0]):
        for s in range(0,np.shape(W)[1]):
            for d in range(s+1,np.shape(W)[1]):
                if np.array_equal(W[0:t,s],W[0:t,d]):
                    m.addConstr(varsx[t,s]==varsx[t,d])
    m.update()
    
    m.write('master.lp')
    #solve for constraints
    m.optimize()
    
    final_q=np.zeros((horizon,num_scen))
    for t in range(0,horizon):
        for s in range(0,num_scen):
            final_q[t,s]=varsq[t,s].x
    
    final_x=np.zeros((horizon,num_scen))
    for t in range(0,horizon):
        for s in range(0,num_scen):
            final_x[t,s]=varsx[t,s].x
            
    return final_q,final_x,m.objVal

""" 

#Total number of extra hours that can be alloted
Resource=7
#Total hours of a single horizon
Time=336
#Arrival rate per sensor
Arrival_rate=50
# Service rate = rate per analyst
Service_rate=51
#number sensors in the system
sensors=10
#analysts available in system
analyst=10

#Step 1: produce a demand scenario
#peaks=[32,33,54,47,80,70,170,69,210,51,320,47] 
#peaks=np.reshape(peaks,(6,2))

Demand=[600,800,500,510,400]
#Demand=np.sum(np.random.poisson(lam=Arrival_rate,size=(sensors,Time)),axis=0)
#add in some extra demand for realism
#for i in range(0,np.shape(peaks)[0]):
#    Demand[peaks[i,0]]+=peaks[i,1]*2


history_x=[]
num_scenario=3
p=np.ones(num_scenario)/num_scenario
ex_W=[]
obj_val=[]
for i in range(0,5):
    history_W=Demand[0:i]
    num_res=Resource-np.sum(history_x)
    t=Time-i
    W=np.random.poisson(lam=51*10,size=(t,num_scenario))
    ex_W=np.append(ex_W,W)
    initial_q=calc_queue_history(history_x,history_W)
    print("initial_q",initial_q[-1])
    fq,final_x,obj=solve_for_future(t,num_scenario,p,initial_q[-1],num_res,W)
    obj_val=np.append(obj_val,obj)
 #   value,count=np.unique(final_x[0,:],return_counts=True)
 #since non-anticpatory constraints require the first decision to be the same among all scenarios,
#    we only need to pull the first x answer
    history_x=np.append(history_x,final_x[0,0])
"""