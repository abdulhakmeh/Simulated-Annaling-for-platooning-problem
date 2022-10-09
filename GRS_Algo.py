# -*- coding: utf-8 -*-
"""
@author: Abdul Hakmeh ahak15@tu-clausthal.de
"""
import random
import networkx as nx
import numpy as nump
from itertools import islice
import copy

def check_path(G,source,target):
      try:
          nx.shortest_path(G, source, target, weight='weight')
          return True
      except:       
          return False


def optimizSearchArea(graph,missions,detour_factor,distance):
    Ea_new={}

    print('restricting the search area by eliminating far edges')
        
    for a in missions:
                tmp = []  
                source_=missions[a][0]
                target_=missions[a][1]
               
                paths = [p for p in nx.algorithms.all_shortest_paths(graph, source_, target_, weight='weight')]
               # paths=  k_shortest_paths(graph, source_, target_,4)
                for node in nump.setdiff1d(graph.nodes,nump.unique(paths)): 
                    path_new=distance[source_,node] + distance[node,target_]
                    path_limit= distance[source_, target_] + (distance[source_, target_]* detour_factor)
        
                
                    if path_new <= path_limit:
                        paths.append(nx.algorithms.shortest_path(graph,source_, node, weight='weight') +\
                                      nx.algorithms.shortest_path(graph, node,target_, weight='weight') [1:] )
                       
                for path in paths:
                  tmp = tmp + [(path[i], path[i+1]) for i in range(len(path)-1)]   
                  _,uniq_nds = nump.unique(tmp, axis=0, return_index=True)
                  Ea_new[a] = [tmp[i] for i in uniq_nds]


    return Ea_new





def k_shortest_paths(G, source, target, k, weight=None):

    return list(
        
        islice(nx.shortest_simple_paths(G, source, int(target), weight='weight'), k)

    )


def append_value(dict_obj, key, value):

    if key in dict_obj:

        if not isinstance(dict_obj[key], list):

            dict_obj[key] = [dict_obj[key]]

        dict_obj[key].append(value)
    else:

        dict_obj[key] = value
    

def convertToEdgePath(R):
   pathDict={}
   index=0

       
   for path in R:
       path_edge = []
   
       for i in range(len(path)-1):
             path_edge.append((path[i],path[i+1]))
       pathDict[index] = path_edge
       index+=1
    
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

def GRS(S,G,T,V,Ea,distance,missions,platoon_length,fuelReductionFactor):

    flag = True
    rand = random.SystemRandom().uniform(0, 1)
    
    
    if rand < 0.75:
        
        while flag: 
            pIndex=random.randint(0, len(S)-1)
           
            #p=convertToEdgePath([S[pIndex]])
            #eIndex= random.randint(0, len(p)-1)
            
            #Ea_=copy.deepcopy(Ea)
            #G_=copy.deepcopy(G)
            
            #e=p[eIndex]
            #del Ea_[pIndex][eIndex]
            
            # for edge in G_.edges:
            #     if edge not in Ea_[pIndex]:
            #         G_.edges[edge]['weight'] = math.inf
            
            paths_n= k_shortest_paths(G, missions[pIndex][0],missions[pIndex][1], 2)
            rand=random.randint(0, len(paths_n)-1)
            #print(rand)
            
            if paths_n[rand] != S[pIndex]:
           
                if path_length(G,paths_n[rand]) <= missions[pIndex][2]:
                    S[pIndex]= paths_n[rand]
                    flag =False
            
    
        
            
   
        
        #########################################################################
        
    else:
        
        while flag:
            pIndex=random.randint(0, len(S)-1)
               
            intersection_list=[]
            path=S[pIndex] 
            
            
        
            for i in range(len(path)-1):
                if len(G[path[i]]) >1:
                    intersection_list.append((path[i],path[i+1]))
                    
                    
            tmp=intersection_list[:]       
            for e_ in   intersection_list:
                 
                 G_=copy.deepcopy(G)
                 G_.remove_edge(*e_)
                 if not check_path(G_,missions[pIndex][0],missions[pIndex][1]):
                      tmp.remove(e_)
                 
                 elif  path_length(G_,nx.shortest_path(G_, missions[pIndex][0], \
                                                       missions[pIndex][1], weight='weight'))  > missions[pIndex][2]:
                     
                     tmp.remove(e_)
                     
                      
                          
            if  tmp:
                G_=copy.deepcopy(G)
                eIndex= random.randint(0, len(tmp)-1)
                e= tmp[eIndex]
                G_.remove_edge(*e)                        
                path_new=[nx.shortest_path(G_, missions[pIndex][0], missions[pIndex][1], weight='weight')]
                for e in convertToEdgePath(path_new):
                        if not e in Ea[pIndex]:
                            flag=False
                            
        
                if flag:
                    S[pIndex]= path_new
                    flag=False

    
        
        
        ###################################################################
        
        
    fS=calculateCost(G,T,platoon_length,fuelReductionFactor,S)
        
        
    return S,fS
    