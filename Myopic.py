# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:21:40 2018

@author: schultz
"""
import numpy as np

def Myopic_Method(demand,resource,time,service_rate,analysts):
    #Demand- the number of threats incoming at the beginning of an hour
    #Resource- Total number of extra hours that can be alloted
    #Time - Total hours of a single horizon
    
    a=np.ones(time)*resource
    #queue at beginning of each time period
    q=np.zeros(time)
    #number of extra hours used at the beginning of each time period
    x=np.zeros(time)
    
    for t in range(1,time):
        q[t] = np.max((q[t-1]+demand[t-1]-(service_rate*analysts),0))
        while (q[t]>50) and (a[t]>0):
            x[t]+=1
            a[t:]-=1
            q[t]=np.max((q[t]-service_rate,0))
    return q,x,a

def NeverUse_Method(demand,resource,time,service_rate,analysts):
    #Demand- the number of threats incoming at the beginning of an hour
    #Resource- Total number of extra hours that can be alloted
    #Time - Total hours of a single horizon
    
    a=np.ones(time)*resource
    #queue at beginning of each time period
    q=np.zeros(time)
    #number of extra hours used at the beginning of each time period
    x=np.zeros(time)
    
    for t in range(1,time):
        q[t] = np.max((q[t-1]+demand[t-1]-(service_rate*analysts),0))
    return q,x,a