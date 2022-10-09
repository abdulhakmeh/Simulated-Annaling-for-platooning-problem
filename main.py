
# -*- coding: utf-8 -*-



#the code will generate a graphe based on the veriables and store the graph file-in
# case not exsist- in the folder Graph-date. To change the veraibles (number of
# nodes) you need to delete the saved files first
#the model i solved using groubi 9.1.
#this code is not sutabile for production. it may accure an error when run it 
#with changing the veraibles 
import sys
sys.modules[__name__].__dict__.clear()
import random
import networkx as nx

import numpy as nump
import gurobipy as gp
from gurobipy import GRB


import time as CPUTime
import generateGraphData as ex
import GSS_Algo as ges
import GRS_Algo as ger
import matplotlib.pyplot as plt

import copy
nump.warnings.filterwarnings('ignore', category=nump.VisibleDeprecationWarning)


######################## Parameters #####################################


#number of LKW
numberOfVeichel= 20
A=[*range(numberOfVeichel)]

#number of locations or cities(Nodes)
numberOfCities= 50




platoon_length=4
fuelReductionFactor=0.10
detour_factor=0.3
generateGraph_mode=0  #1: means generate graph from distance matrix 0:randolmy generated 
#startSolution_mode=0 # 1: means starting from optimizied soulation 0:starting from shortest path
plot_function= 0  # in case of generate a random graph plotting the graph is possible

#######################  SA paramterts ########################################

Temp_= 20
maxIter= 200
alpha=0.5
e = 2.718281828

#############################functions#########################################

def GetResultPath(x_val,A,Ea,missions):
    pathDict = {} 
    
    for a in A:

        path = []
        set_ = set()
        for e in Ea[a]:
            if x_val[a,e] > 0.5:                       
                set_.add(e)
        while set_ != set():
          for e in set_:
              if e[0] == missions[a][0]:
                  path = [e[0],e[1]]
                  set_.remove(e)
                  break
              if path != [] and e[0] == path[-1]:
                  path.append(e[1])
                  set_.remove(e)
                  break   
        path_ = []
        for node in range(len(path)):
            path_.append(path[node])
        pathDict[a] = path_
             
    return pathDict

###########################Groubi Model######################################## 
def base_Algo(G,Ea,E,Va,neighbours,time,missions,Na,T):
    #create Durobi Modell
    model= gp.Model("FEP")
    
    
    # create variables
    x={}
    c={}
    delta={}
    gama={}
    p={}
  
    
    # define the missions with deadlines
    trucks_,sources_,targets_,t_max =gp.multidict(missions)
    
    for a in A :
      for e in Ea[a]:    
            x[a,e]=model.addVar(vtype=GRB.BINARY,name='x%s,%s' %(e,a))
    
    for a in A:
        for e in Ea[a]:
            delta[e]=model.addVar(vtype=GRB.BINARY)
            c[e]=model.addVar(name="c(%s.%s)" %(e))
            p[e]=model.addVar(ub=platoon_length,vtype=GRB.INTEGER)
    
            
    
    #objective function Equation 1
    model.setObjective(gp.quicksum(c[e]* time[e] for e in Va.keys())  , GRB.MINIMIZE)
    #equation 2 & 3
    
    for a in A:
        for i in Na[a]:
            gama=0
            if i== sources_[a]:gama=1
            if i==targets_[a]:gama=-1
            node_r,node_l=neighbours[a,i][0],neighbours[a,i][1]           
            model.addConstr(sum(x[a,(i,k)]for k in node_l) - sum(x[a,(j,i)]for j in node_r ) ==gama)
    
    #equation 4
    
    for a in A:
             model.addConstr(gp.quicksum(x[a,e]* time[e] for e in Ea[a] )  <= t_max[a],name="time_Palancing")
       
  
  
    #equation 5 & 6 
    
    for e in Va.keys():
        
        for a in Va[e]:
            model.addConstr(x[a,e]  <= delta[e]  ,name="Node_status") # if any truck drives on edge e
        model.addConstr( sum(x[a,e] for a in Va[e])>=delta[e] )
        model.addConstr(p[e] <= sum(x[a,e] for a in Va[e]  ), name="platoonlength_restriction" )
        
    
    #equation 7
    for e in Va.keys():
         model.addConstr(c[e]== gp.quicksum(x[a,e] for a in Va[e] ) - (delta[e]* fuelReductionFactor * (p[e]-1))  )
    
   # model.write('../optimization_model/FEP_modell.lp')
    #model.LazyConstraints = 1
    model.setParam('TimeLimit', 1800) # maximum solution time = 3600
    model.Params.LogToConsole=0
    model.Params.OutputFlag=0
    est_time = CPUTime.time()
    model.optimize()
    est_time = CPUTime.time() - est_time
    obj = model.objVal
    model_val = {}
    for a in A:
        for e in Ea[a]:
            model_val[a,e] = x[a,e].X
    
    
    platoon_paths=GetResultPath(model_val, A, Ea,missions)
    percent= 100- ( (obj*100) /freePlatoonCost) 
    
    for i in shortestPathDict:
        if  shortestPathDict[i] != platoon_paths[i]:
            print( 'path ',i)

    
    results = f"""
    {'-'*40}
    #  platooning problem - Groubi model- Base Algo. 
    # free driving cost: {freePlatoonCost}
    # platoning driving cost: {obj}
    # number of Veichel: {numberOfVeichel}
    #number of Nodes:   {len(G.nodes())}
    #stimated Time: {est_time} Seconds
    #the route plan of free driving "shortestpath" {shortestPathDict}
    #the route plan of platooning {platoon_paths}
    # the percent of saving is {percent}
    {'-'*40}
    """
    
  #  print (results)

    return obj, est_time, platoon_paths,percent

#######################generate  the Graph#############################
[G,V,Ea,E,Va,neighbours,time,missions,Na,freePlatoonCost,shortestPathDict,distance,T]=\
    ex.generateGraphData(numberOfCities,numberOfVeichel,A,detour_factor,generateGraph_mode)

if plot_function== 1    :
    
    pos=nx.spring_layout(G) 
    nx.draw_networkx(G,pos)
    labels = nx.get_edge_attributes(G,'weight')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)

######################solving the problem by Gurobi##########################

obj, est_time_exact, platoon_paths_excat,percent_ = base_Algo(G,Ea,E,Va,neighbours,time,missions,Na,T)

##########################Generate initial Start Solution #######################
fS,S = ges.GSS(G,Ea,Va,neighbours,time,missions,T,freePlatoonCost,platoon_length,fuelReductionFactor)

#print('first Sulation',fS)


###################### Simulated Annealing#####################################

#Ea_new= ger.optimizSearchArea(G,missions,detour_factor,distance)



S_opt = S[:]
fS_opt=copy.deepcopy(fS)
est_time = CPUTime.time()

while Temp_ > 0.01 :
    for i in range(maxIter):
        S_new,fS_new= ger.GRS(S,G,T,V,Ea,distance,missions,platoon_length,fuelReductionFactor)
        
        #print(fS_new)

        if fS_new < fS :
            fS=copy.deepcopy(fS_new)
            S=S_new[:]
            
            
            if fS_new < fS_opt :
              S_opt = copy.deepcopy(S_new) 
              fS_opt=copy.deepcopy(fS_new) 
                
       
        elif fS_new > fS:
            esum = pow(e,  ( fS - fS_new) / Temp_)
            rand = random.SystemRandom().uniform(0, 1)
            if esum > rand:
                fS= copy.deepcopy(fS_new)
                S=copy.deepcopy(S_new)
                print('bad solution accepted')
 
    Temp_= Temp_*alpha           
    print('temp changed')
    

est_time = CPUTime.time() - est_time
percent=100- ( (fS_opt / freePlatoonCost)  *100) 
R_=[]
for i in platoon_paths_excat:
  R_.append(platoon_paths_excat[i])
real_cost=ger.calculateCost(G,T,platoon_length,fuelReductionFactor,R_)

  

results = f"""
{'-'*40}
# ################## platooning problem - Simulated Annealing-############### . 
# free driving cost(no platoon): {freePlatoonCost}
# Driving with platoon (Optimal Objective function SA) cost,saving percent: {fS_opt,percent} 
# number of Veichel: {numberOfVeichel}
#number of Nodes:   {len(G.nodes())}
#stimated Time: {est_time} Seconds
# Gurobi objective function: (cost, saving percent) {obj, percent_}
#the cost of the optimal solution  from Gurobi calculated by external function:{real_cost} 
{'-'*40}
"""

print(results)
 
fresult = '../Results/' + str(numberOfVeichel)+ '_results.txt'
          

fout = open(fresult,'w')
fout.write('%f      %f      %f       %f      %f    %f      %f   \n' \
           %(freePlatoonCost,fS_opt,est_time,Temp_,maxIter,obj, est_time_exact))

fout.close()



  
