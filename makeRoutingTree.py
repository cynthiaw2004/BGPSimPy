"""Make Routing Trees."""
import numpy as np
from scipy import sparse
import scipy.io
import time
import itertools
from itertools import izip
import copy
import sys

numNodes = 393774
# if empSparseMatrix does not exist, you must run fileToSparse
fullgraph = scipy.io.mmread("empSparseMatrix").tocsr()

def fileToSparse(fileName):
    '''
    reads the full AS graph in as a text file of relationships,
    converts it to a sparse matrix (note that row x or column x is for AS x)
    saves the sparse matrix 
    loads the sparse matrix and times the loading
    usage: fileToSparse("Cyclops_caida_cons.txt")
    '''
    with open(fileName,'r') as f:
        content = f.readlines()
    empMatrix = sparse.csr_matrix((numNodes+1,numNodes+1), dtype=np.int8)
    i = 1
    total = len(content)
    for line in content:
        print i, " out of ", total
        i += 1
        splitLine = line.split("\t",2)
        node1 = int(splitLine[0])
        node2 = int(splitLine[1])
        relationship = splitLine[2][:3]
        if relationship == "p2p":
            empMatrix[node1,node2] = 1
            empMatrix[node2,node1] = 1
        if relationship == "p2c":
            empMatrix[node1,node2] = 2
            empMatrix[node2,node1] = 3
    scipy.io.mmwrite("empSparseMatrix",empMatrix)
    start = time.time()
    test = scipy.io.mmread("empSparseMatrix").tolil()  #5.4MB to save sparse matrix
    end = time.time()
    print end-start, " seconds to load" #2.3 seconds

def checkPreviousLevelsAlt(BFS,node,level):
    '''
    check if node is in BFS at given level or any previous level
    '''
    while level >= 0:
        if node in BFS[level][1]:
            return True
        level -= 1
    return False

def customerToProviderBFS(destinationNode,routingTree):
    '''
    input: 
        destinationNode (the root of routing tree)
        empty routing tree which is sparse also
    output:
        routing tree after step 1 of routing tree algorithm
        nodes added this step as a dictionary where key = level and value = list of nodes
    what it does:
        perform a bfs from destinationNode and only add relationship = 3 
    '''
    BFS = [(0,[destinationNode])]
    addedEdges = []
    for pair in BFS:
        level = pair[0]
        #print "---level---: ",level
        vertices = pair[1]
        for vertex in vertices:
            for node,relationship in izip(fullgraph[vertex].nonzero()[1],fullgraph[vertex].data):
                if (relationship == 3) and ([vertex,node] not in addedEdges) and (not ((checkPreviousLevelsAlt(BFS,node,level)) and (checkPreviousLevelsAlt(BFS,vertex,level)))): 
                    #print "edge: ",(vertex,node)
                    routingTree[node,vertex] = 1
                    addedEdges.append([vertex,node])
                    addedEdges.append([node,vertex])
                    if BFS[-1][0] == level:
                        BFS.append((level+1,[node]))
                    else:
                        BFS[-1][1].append(node)
    return routingTree,BFS

def peerToPeer(routingTree,BFS):
    '''
    input:
        routing tree which is sparse also
        nodes from step 1 of RT algorithm in bfs order
    output:
        routing tree after step 2 of routing tree algorithm
        nodes added from this step and previous step as a dictionary where key = level and value = list of nodes
    purpose:
        connect new nodes to nodes added in step 1 with relationship = 1
    '''
    oldNodes = []
    for pair in BFS:
        oldNodes.extend(pair[1])
    newBFS = copy.deepcopy(BFS)
    for pair in BFS:
        level = pair[0]
        #print "---level---: ",level
        vertices = pair[1]
        for vertex in vertices:
            for node,relationship in izip(fullgraph[vertex].nonzero()[1],fullgraph[vertex].data):
                if (relationship == 1) and (node not in oldNodes): 
                    #print "edge: ",(vertex,node)
                    routingTree[node,vertex] = 1
                    if newBFS[-1][0] == level:
                        newBFS.append((level+1,[node]))
                    else:
                        newBFS[-1][1].append(node)
    return routingTree,newBFS

def providerToCustomer(routingTree,BFS):
    '''
    input:
        routing tree which is sparse also
        nodes from step 1 and 2 of RT algorithm
    output:
        routing tree after step 3 of routing tree algorithm
        nodes added from this step and previous two steps as a dictionary where key = level and value = list of nodes
    purpose:
        breadth first search of tree, add nodes with relationship 2
    '''
    oldNodes = []
    for pair in BFS:
        oldNodes.extend(pair[1])
    addedEdges = []
    for pair in BFS:
        level = pair[0]
        print "level: ",level
        vertices = pair[1]
        for vertex in vertices:
            for node,relationship in izip(fullgraph[vertex].nonzero()[1],fullgraph[vertex].data):
                if (relationship == 2) and (node not in oldNodes) and ([vertex,node] not in addedEdges) and (not ((checkPreviousLevelsAlt(BFS,node,level)) and (checkPreviousLevelsAlt(BFS,vertex,level)))): 
                    #print "edge: ",(vertex,node)
                    routingTree[node,vertex] = 1
                    addedEdges.append([vertex,node])
                    addedEdges.append([node,vertex])
                    if BFS[-1][0] == level:
                        BFS.append((level+1,[node]))
                    else:
                        BFS[-1][1].append(node)
    return routingTree

def makeRoutingTree(destinationNode):
    '''
    input: 
        destination AS
    output:
        routing tree of destination AS in sparse matrix format
    '''
    routingTree = sparse.dok_matrix((numNodes+1,numNodes+1), dtype=np.int8)
    print "\nstep one"
    stepOneRT,stepOneNodes = customerToProviderBFS(destinationNode,routingTree)
    print "\nstep two"
    stepTwoRT,stepTwoNodes = peerToPeer(stepOneRT,stepOneNodes)
    print "\nstep three"
    stepThreeRT = providerToCustomer(stepTwoRT,stepTwoNodes)
    scipy.io.mmwrite("dcomplete"+str(destinationNode),stepThreeRT)
    return stepThreeRT

def main():

    destinationNode = 3388
    start = time.time()
    print "making routing tree for destination node: ",destinationNode
    routingTree = makeRoutingTree(destinationNode)
    end = time.time()
    print "time to make routing tree: ",end-start, "for destination node: ", destinationNode





main()