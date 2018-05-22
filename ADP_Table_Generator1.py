# -*- coding: utf-8 -*-
"""
@author: schultz
"""
import numpy as np

"""
Inventory management problem

Time length: 14 days; 336 hours

Demand
arrival rate = Poisson(50/sensor/hour)*10 sensors = Poisson(500/hr)
+ for 6 random times over time length, Poisson(50) added

Service
serive rate = 51/hour/analyst * 10 analyst/hr = 510
Goal: keep total queue length < 50

if total queue length <50, green
if 50 <= total queue length <= 100, yellow
if total queue length > 100, red


States: (backlog, number additional resources left/time left)
actions: number of additional resource hours to use (0-7)

"""

#################################################################
# ADP Function
#################################################################

"""
Approximate Dynamic Programming algorithm 3
figure 4.7 pg.141 from Approx Dyn Prog book

no TPM and asyncronous updates; uses Post-decision states
V=(1-alpha)V + alpha*v
"""

def ADP3(states,actions,cost,PDS,alpha,num_ite,ee):
    #states=number of states for the problem
    #actions = number of actions for the problem
    #cost = cost matrix to do action j in state i
    #PDS = post decision state with pre-decision on left and action on top
    #alpha = alpha value -> should be around 0.9
    #num_ite = number of iterations that should be performed before stopping
    #ee = alpha decay value -> should be large
   
    Translator=[]
    for i in range(1,states[1]):
        temp= np.array(range(0,states[2]))/float(max(1,i))
        Translator=np.append(Translator,temp)
    Translator=np.unique(Translator)
    #Step 0: Initialize V_0 for all states and choose an initial state S
    V=np.zeros((states[0],len(Translator),1))
    Policy=np.ones((1,states[0],len(Translator)))*-1
    aph=0.2
    aphs=[]
    
    #[backlog at begin,[hr,#extra hrs left at begin]]
    for b in range(0,num_ite):
        print(b)
        Sx=[0,[states[1]-1,states[2]-1]]
        Act=0
        xSx=[0,[states[1],states[2]-1]]
        Snext=[0,[states[1]-1,states[2]-1]]
        for l in range(0,336):
            S=Snext
            k=b*336+l
            #alpha decay
            uz=(k)**2/float((ee+k))
            aph=aph/float((1+uz))
            aphs=np.append(aphs,aph)
            #Step 2: choose the best action and update
            tempv=np.zeros((1,actions))
            Demand=np.random.randint(400,580)
            for a in range(0,actions):
                Sx=PDS(S,a)
                index= np.where(Translator == Sx[1][1]/float(max(Sx[1][0],1)))
                tempv[0,a]=cost(S,a) + (alpha*V[Sx[0],index[0][0],0])
            Act=np.argmin(tempv)
            print("Action taken: %s for queue %s" % (Act,S[0]))
            v=tempv[0,Act]
            index= np.where(Translator == S[1][1]/float(max(S[1][0],1)))
            Policy[0,S[0],index[0][0]]=Act
            index= np.where(Translator == xSx[1][1]/float(max(xSx[1][0],1)))
            V[int(xSx[0]),index[0][0],0]=(1-aph)*V[xSx[0],index[0][0],0] + (aph*v)
            
            #Step 3: determine next random state
            newQ=max(S[0]+Demand-(51*(10+min(Act,S[1][1]))),0)
            xSx=[newQ,[S[1][0]-1,min(S[1][1],S[1][1]-Act)]]
            Snext=[xSx[0],[xSx[1][0],xSx[1][1]]]
        
    return Policy,aphs,Translator

#################################################################
# Demand, Cost, PDS functions related to problem
#################################################################

def C_function(state,action):
    #begin number of hour left - physical state
    i=state[1][0]
    #backlog @ begin of hour - knowledge state
    j=state[0]
    #res_left @ begin of hour-knowledge state
    k=state[1][1]
    #can't use more than we have
    act=min(action,k)
    #total new demand @ begin of hour
    #queue @ end of hour
    q=max(0,(j-(51*act)))
    #relevant queue @ end of hour
    rel_q=max((q-50),0)
    #resources left @ end of hour given action
    res_left=k-act
    cost=((rel_q/float(50)) - (res_left/float(max(1,i))))
    return cost

def PDS(state,action):
    #begin number of hour left - physical state
    i=state[1][0]
    #backlog @ begin of hour - knowledge state
    j=state[0]
    #res_left @ begin of hour-knowledge state
    k=state[1][1]
    act=min(action,k)
    #queue @ end of hour
    q=max((j-(51*act)),0)
    #resources left @ end of hour given action
    res_left=k-act
    return [int(q),[i,int(res_left)]]


#################################################################
# Build Table
#################################################################

trials=1

#ADP3(states,actions,cost,PDS,alpha,num_ite,ee)
#run multiple trials to get various instances of the table
for k in range(0,trials):
    policy,aphs,Translator=ADP3((900,336,8),8,C_function,PDS,0.9,5000,10000000)
    if k==0:
        it_policies3=policy[np.newaxis,:]
    else:
        it_policies3=np.append(it_policies3,policy[np.newaxis,:],axis=0)

#choose the most common policies for our final table
Final_policy=np.empty((np.shape(it_policies3)[2],np.shape(it_policies3)[3]))
for i in range(0,np.shape(it_policies3)[2]):
    for j in range(0,np.shape(it_policies3)[3]):
        values,counts=np.unique(it_policies3[:,0,i,j],return_counts=True)
        if (len(values)>1) & (values[0]==-1):
            values=values[1:]
            counts=counts[1:]
            Final_policy[i,j]=values[np.argmax(counts)]
        else:
            Final_policy[i,j]=values[np.argmax(counts)]

##save our table to be called at any time
with open("DP_Action_State_Table.dat",'w+') as outfile:
        for i in range(0,np.shape(Final_policy)[0]):
            temp=' '.join(map(str,Final_policy[i,:])) + "\n"
            outfile.write(temp)