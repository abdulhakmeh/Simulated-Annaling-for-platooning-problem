# -*- coding: utf-8 -*-
"""
@author: Abdul Hakmeh ahak15@tu-clausthal.de
"""
import random
import networkx as nx
import numpy as nump
from itertools import islice





##########################################
def append_value(dict_obj, key, value):

    if key in dict_obj:

        if not isinstance(dict_obj[key], list):

            dict_obj[key] = [dict_obj[key]]

        dict_obj[key].append(value)
    else:

        dict_obj[key] = value

def k_shortest_paths(G, source, target, k, weight=None):

    return list(
        
        islice(nx.shortest_simple_paths(G, source, int(target), weight='weight'), k)

    )
def convertToEdgePath(R):
   pathDict={}
   for p in range(len(R)):
       path=R[p]
       path_edge = []
       for i in range(len(path)-1):
            path_edge.append((path[i],path[i+1]))
       pathDict[p] = path_edge 
    
    
   return pathDict


def path_length(G, path):
    return sum([G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1)])


def calculateCost(G,T,platoon_length,fuelReductionFactor,R):
   R_=R[:]
   if R_ is None:
       return 0
        
        
        
   time_EdgeVector={}
   platoon_Dic={}

   pathDic=convertToEdgePath(R_)

   # none_e= (None,None)
   # for t in range(T):
   #    time_EdgeVector.update({t:none_e})
       

   for p in pathDic:  # build the time dic to investcate the platoon chances
       t=0       
       for e in pathDic[p]:

            weight=G.edges[e]['weight']
            for i in range(weight):
               
                if t in time_EdgeVector:
               
                    if e in time_EdgeVector[t]:
                        tp=e,t
                        if tp not in platoon_Dic:
                            platoon_Dic.update({tp:0})                       
                        platoon_Dic[e,t]+=1
                    
                    else: 
                        
                        append_value(time_EdgeVector, t, e)
                else:
                     time_EdgeVector.update({t:[e]})
                t+=1
                
                
                
   sum = 0                
   for t in  time_EdgeVector :
       for e in time_EdgeVector[t]:
               sum+= 1
       
   for e,t in platoon_Dic:
      sum+= platoon_Dic[e,t] - ( min(max(platoon_Dic[e,t], 1), platoon_length)  * fuelReductionFactor)
       
                       
                  
                   
   
   return sum


###########################################################


def GSS(G,Ea,Va,neighbours,time,missions,T,freePlatoonCost,platoon_length,fuelReductionFactor):
    R=[]

    for a in missions:
        #rand= random.randint(0, 2)
        #path = k_shortest_paths(G, missions[a][0], missions[a][1],3)[rand]
        path= nx.shortest_path(G, missions[a][0], missions[a][1], weight='weight')
  
        
        R.append(path)
       
        
#    R_cost = calculateCost(G,T,R)
        
    # if mode== 1: 
    #     if R_cost == freePlatoonCost: 
        
        
    #         for a_ in missions:
    #             a =random.randint(0, len(missions)-1)
    #             flag=False
    #             allpaths = k_shortest_paths(G, missions[a][0], missions[a][1], 2)
                
    #             for path in allpaths:
    #                 path_time=sum(time[(path[i],path[i+1])] for i in range(len(path)-1))
    #                 R_copy=copy.deepcopy(R)
    #                 R_copy[a]=path
    #                 if path_time > T:
    #                     T_=path_time
    #                 else: T_=T
    #                 cost_p=calculateCost(G,T_,R_copy)
                   
                        
    #                 if  cost_p < R_cost\
    #                     and path_length(G,path)<= missions[a][2]:
    #                     R[a]=path
    #                     print('one route has been optimizied, Route number: ',a,cost_p, R_cost)
    #                     flag= True
    #                     break
    #             if flag:
    #                 break
                
            
         
    R_cost= calculateCost(G,T,platoon_length,fuelReductionFactor,R)
    
    return R_cost, R








