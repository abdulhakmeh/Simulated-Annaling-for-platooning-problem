# -*- coding: utf-8 -*-
"""
@author: Abdul Hakmeh ahak15@tu-clausthal.de
"""

import random
import networkx as nx
import numpy as nump
import os.path
from itertools import islice
import pickle



def cal_average(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + t           

    avg = sum_num / len(num)
    return avg

def k_shortest_paths(G, source, target, k, weight=None):

    return list(
        
        islice(nx.shortest_simple_paths(G, source, int(target), weight='weight'), k)

    )

def path_length(G, path):
    return sum([G[path[i]][path[i+1]]['weight'] for i in range(len(path)-1)])   

######################################################################################################


def generateGraphData(numberOfCites,numberOfVeichel,A,detour_factor,mode):
    
    
    if mode==0:
    
    
    
        if os.path.isfile('../Graph_Data/Graph_.adjlist'):   
            graph =nx.read_adjlist('../Graph_Data/Graph_.adjlist',nodetype = int)
            graph=nx.read_edgelist( '../Graph_Data/Graph_.edgeslist',nodetype = int)
        
        
        else:
            graph= nx.erdos_renyi_graph(numberOfCites, 0.3, seed=123, directed=False)
        #    b=nx.gnm_random_graph(numberOfCites,numberOfroads)
            for (u, v) in graph.edges():
                graph.edges[u,v]['weight'] = random.randint(2,20)
            nx.write_adjlist(graph, '../Graph_Data/Graph_.adjlist')
            nx.write_edgelist(graph, '../Graph_Data/Graph_.edgeslist')
        
    
        
        
        
        # generate randomly a mission for each truck contains source,target  and deadline
        index=0
        T=0
        missions = {} 
        Av = {}
        Va={}
        neighbours = {}
        shortestPathDict = {}
        freePlatoonCost=0
        Ea = {}
        E=[]
        V=[]
        
        for i in range(numberOfCites):
            V.append(i)
        
        
        
        while len(missions) < numberOfVeichel :
                source_=random.randint(0, numberOfCites-1)
           
                target_=random.randint(0, numberOfCites-1)
                if len(k_shortest_paths(graph, source_, target_, 1)[0]) > 2:
                    paths = [p for p in\
                             nx.algorithms.all_shortest_paths(graph, source_, target_, weight='weight')]
                    tmax=0
                    for path in paths:
                        if (path_length(graph,path) > tmax):
                            tmax=int(path_length(graph,path)+ path_length(graph,path)*detour_factor)
                    missions[index]=[source_,target_, tmax]
                    index+=1
                    if tmax > T:
                        T=tmax

        distance = nx.algorithms.shortest_paths.floyd_warshall_numpy(graph, weight='weight') #calculate distance matrix
        
        
        time={(i,j):
              graph.edges[i,j]['weight']
              for i, nbrs in graph.adj.items()
                  for j, eattr in nbrs.items()}  
        #calculate the available nodes for every truck (for small peoblems not very important)   
        
        for a in A:
            tmp = []  
            source_=missions[a][0]
            target_=missions[a][1]
            #paths=  k_shortest_paths(graph, source_, target_,2)
            paths = [p for p in nx.algorithms.all_shortest_paths(graph, source_, target_, weight='weight')]
            for node in nump.setdiff1d(graph.nodes,nump.unique(paths)): 
                 path_new=distance[source_,node] + distance[node,target_]
                 path_limit= distance[source_, target_] + (distance[source_, target_]* detour_factor)
    
            
                 if path_new <= path_limit:
                     paths.append(nx.algorithms.shortest_path(graph,source_, node, weight='weight') +\
                                  nx.algorithms.shortest_path(graph, node,target_, weight='weight') [1:] )
                   
            for path in paths:
              tmp = tmp + [(path[i], path[i+1]) for i in range(len(path)-1)]   
              _,uniq_nds = nump.unique(tmp, axis=0, return_index=True)
              Ea[a] = [tmp[i] for i in uniq_nds]
              
              
              
              
              
              
        
        #list of all nodes wich every truck will drive  N[a]= [node1,node2...] 
        
        for a in A:
            Av[a] = nump.unique(Ea[a])        
        #list of all trucks wich will drive e edge V[e]= [truck1,truck2...] 
        
        for i in Ea:
                for e in Ea[i]:
                    if  e in Va : 
                        Va[e].append(i) 
                    else:
                        Va[e] = [i]
                        
    
                
        
        #calculate the shortest path for comparation    
        for a in A:
            path = nx.shortest_path(graph, missions[a][0], missions[a][1], weight='weight')
            shortestPathDict[a] = path
            freePlatoonCost += sum(time[(path[i],path[i+1])] for i in range(len(path)-1))
        
    
        for a in A:
            for i in Av[a]:
                neighbour_r,neighbour_l = [],[]
                for n in graph[i]:
                    if  (n,i) in Ea[a] and n in Av[a] : neighbour_r.append(n)
                    if  (i,n) in Ea[a] and n in Av[a] :  neighbour_l.append(n)
                neighbours[a,i] = (neighbour_r,neighbour_l)
                    
    
    elif mode==1:
        data=nump.loadtxt(open('../Graph_Data/DistMatrix.csv', "rb"), delimiter=";")
        #coord=nump.loadtxt(open('../Graph_Data/coordinations.csv', "rb"), delimiter=";")
        
        mat =[]
        for i in range(len(data)):
            for k in range(len(data)):
                if data[i,k] > 0:
                    dist=data[i,k]
                    mat.append([i,k,int(dist/2)])
                    
      
                    
        
        graph = nx.Graph()  
        graph.add_weighted_edges_from(mat)
        distance = nx.algorithms.shortest_paths.floyd_warshall_numpy(graph, weight='weight') #create smaller copy of Dist. matrix
        
        
        
        # generate randomly a mission for each truck contains source,target  and deadline
        index=0
        T=0
        missions = {} 
        Av = {}
        Va={}
        neighbours = {}
        shortestPathDict = {}
        freePlatoonCost=0
        Ea = {}
        E=[]
        V=[*range(len(graph.nodes()))]
        
        avg=cal_average(distance.flatten())

        
        
        
        ####################################
        while len(missions) < numberOfVeichel :
                source= random.randint(0, len(distance)-1)
                target=random.randint(0, len(distance)-1)
                
                
                 
                if distance[source][target] >= avg*0.9:
                    path_k=nx.shortest_path(graph, source, target, weight='weight')
                    path_l=path_length(graph,path_k)
                    tmax= int (path_l +( path_l * detour_factor))
                    missions[index]=[source,target, tmax]
                    index+=1
                    if tmax > T:
                        T=tmax

                
      
        
        
        time={(i,j):
              graph.edges[i,j]['weight']
              for i, nbrs in graph.adj.items()
                  for j, eattr in nbrs.items()}  

        
        for a in A:
            tmp = []  
            source_=missions[a][0]
            target_=missions[a][1]

            paths = [p for p in nx.algorithms.all_shortest_paths(graph, source_, target_, weight='weight')]
            for node in nump.setdiff1d(graph.nodes,nump.unique(paths)): 
                path_new=distance[source_,node] + distance[node,target_]
                path_limit= distance[source_, target_] + (distance[source_, target_]* detour_factor)
    
            
                if path_new <= path_limit:
                    paths.append(nx.algorithms.shortest_path(graph,source_, node, weight='weight') +\
                                  nx.algorithms.shortest_path(graph, node,target_, weight='weight') [1:] )
                   
            for path in paths:
              tmp = tmp + [(path[i], path[i+1]) for i in range(len(path)-1)]   
              _,uniq_nds = nump.unique(tmp, axis=0, return_index=True)
              Ea[a] = [tmp[i] for i in uniq_nds]
              
        

        
        for a in A:
            Av[a] = nump.unique(Ea[a])        

        
        for i in Ea:
                for e in Ea[i]:
                    if  e in Va : 
                        Va[e].append(i) 
                    else:
                        Va[e] = [i]
                        
    
                
        
        #calculate the shortest path for comparation    
        for a in A:
            path = nx.shortest_path(graph, missions[a][0], missions[a][1], weight='weight')
            shortestPathDict[a] = path
            freePlatoonCost += sum(time[(path[i],path[i+1])] for i in range(len(path)-1))
        
    
        for a in A:
            for i in Av[a]:
                neighbour_r,neighbour_l = [],[]
                for n in graph[i]:
                    if  (n,i) in Ea[a] and n in Av[a] : neighbour_r.append(n)
                    if  (i,n) in Ea[a] and n in Av[a] :  neighbour_l.append(n)
                neighbours[a,i] = (neighbour_r,neighbour_l)
                     
           

               

        
    return graph,V,Ea,E,Va,neighbours,time,missions,Av,freePlatoonCost,shortestPathDict,distance,T