# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 23:40:35 2018

@author: schultz
"""
import numpy as np
#assumes rho is 1
#assumes mutation is the normal pertubation + 1/5 sucess rule

def calc_past_queue(past_act,past_dem):
    time=len(past_dem)+1
    q=np.zeros(time)
    x_t=np.zeros(time)
    for i in range(0,len(past_act)):
        x_t[past_act[i]]+=1
    for t in range(1,time):
        #for each time period, solve for queue
        #queue of pending threats to be analyzed @ end t
        q[t]=max((q[t-1]+past_dem[t-1] -(51*(10+x_t[t-1]))),0)
    return q

def generate_parent(variables,past_q,time):
    x_k = np.random.randint(0,(336-time),size=variables)
    #resource used if between 0-335, 336 = never use it
    [fitness,queue,avail_res]= calc_fitness(x_k,past_q,variables,time)
    return [x_k,fitness]

def calc_fitness(x_k,past_queue,resources,time):
    #determine which of the 336 hours every resource is to be used in if used
    # if any time
    y=0
    x_t=np.zeros(336-time)
    q=np.zeros(336-time)
    a_t=np.ones(336-time)*resources
    W=generate_demand(10,51)
    for i in range(0,np.shape(x_k)[0]):
        if x_k[i]<(336-time):
            x_t[x_k[i]]+=1
            a_t[x_k[i]:]-=1
    for t in range(0,(336-time)):
        #for each time period, solve for cost
        #determine queue at beginning of t
        if t==0:
            q[t]=past_queue
        else:
            q[t]=max(q[t-1]+W[t-1] -(51*(10+x_t[t-1])),0)
        y+=(max(q[t]-50,0)/50)-(a_t[t]/(336-(t-1)))
    return y,q,a_t
    

def generate_demand(sensors,arr_rate):
    #normal demand for 336 hours
    W=np.random.poisson(lam=arr_rate,size=336)*sensors
    #add in 6 peak events randomly
    for i in range(0,6):
        W[np.random.randint(0,336)]+= np.random.poisson(arr_rate)
    return W
    
def mutate_parent(parent_x,sigma_l,time,past_q,resource):
    child_x=[]
    for p in range(0,np.shape(parent_x)[0]):
        temp=parent_x[p] + int(round(np.random.normal(0,sigma_l[p]),0))
        child_x.append(min(max(0,temp),336-time))
    child_x=np.asarray(child_x)
    #print("child is",child_x)
    [fitness,queue,avail_res]= calc_fitness(child_x,past_q,resource,time)
    #print("child's fitness is",fitness)
    return [child_x,fitness]
        


#individual ES: [x_values,fitness]
#generation l: [sigma,i_l = improvement count, u_l = # generations since last update ]


def PLUS_ES(mu,rho,lamb,variables,max_gen,update_rate,past_act,past_dem):
    # mu = number of parents per generation
    # rho = number of parents involved in mutation
    # lamb = number of offspring to produce per generation
    # max_gen = stopping criteria will be when the max generation is finished
    #update_rate = number iterations between sigma updates
    #Step 1: generate the initial set of parents
    if len(past_dem)==0:
        past_q=[0]
    else:
        past_q=calc_past_queue(past_act,past_dem)
    time=len(past_dem)
    parent=[]
    for i in range(0,mu):
        parent.append(generate_parent(variables,past_q[-1],time))
    parent=sorted(parent,key= lambda s_entry: s_entry[:][1])
    #print("parent",parent)
    
    #Step 2: Set up the generational data
    init_sigma=np.random.normal(30,5,size=variables)
    generation=[]
    generation.append([init_sigma,0,0])
    
    for l in range(0,max_gen):
        #Step 3a: create lamb mutated children times
        offspring=[]
        seeders=np.random.randint(0,mu,size=lamb)
        #print("seeder values",seeders)
        for j in seeders:
            #print("parent %s is making a baby" % (parent[j][0]))
            offspring.append(mutate_parent(parent[j][0],generation[l][0],time,past_q[-1],variables))

        #Step 3b: compare parents and children
        #generation is 'improved' if at least 20% are more fit then their parent
        tot_imp=0
        for g in range(0,lamb):
            if offspring[g][1]<parent[seeders[g]][1]:
                tot_imp+=1
        improv=generation[l][1]
        if tot_imp>=(.2*lamb):
            improv+=1
        #if the last time we updated sigma was update_rate ago, update
        if generation[l][2]<update_rate:
            up=generation[l][2]+1
            sigma=generation[l][0]
        else:
            up=0
            sigma=generation[l][0]
            if improv >= 10*update_rate:
                sigma=sigma*(1/0.85)
            else:
                sigma=sigma*0.85
        
        generation.append([sigma,improv,up])
        
        #Step 3c: rank the parents and offsprings and choose top mu
        survivors=parent
        for z in range(0,len(offspring)):
            survivors.append(offspring[z])
        survivors=sorted(survivors,key= lambda s_entry: s_entry[:][1])
        #sorted from lowest to highest, since min take the top mu
        survivors=survivors[0:mu]

        parent=survivors
        
    return survivors[0][0]

def Train_ES(num_iterations,mu,rho,lamb,resource,max_gen,update_rate,past_act,past_dem):
    time=336-np.shape(past_dem)[0]
    policy_iterations=[]
    for i in range(0,num_iterations):
        policy=PLUS_ES(mu,rho,lamb,resource,max_gen,update_rate,past_act,past_dem)
        x_t=np.zeros(time)
        for j in range(0,resource):
            if policy[j]<time:
                x_t[policy[j]]+=1
        if i==0:
            policy_iterations=x_t[np.newaxis,:]
        else:
            policy_iterations=np.append(policy_iterations,x_t[np.newaxis,:],axis=0)
    return policy_iterations

