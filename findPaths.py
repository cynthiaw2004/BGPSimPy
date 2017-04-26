"""Find Paths."""
import scipy.io
import time
from itertools import izip


def find_all_paths(subgraph, start, end, prevRelationship, path=[]): 
    # input: 
    # sparse matrix representation of subgraph,
    # starting node,
    # ending node,
    # previous relationship (initialize with 0),
    # path (defaults to empty),
    # output:
    # all paths between start and end
    path = path + [start]
    if start == end:
        return [path]
    if subgraph[start].nnz == 0:
        return []
    paths = []
    for node, relationship in izip(subgraph[start].nonzero()[1], subgraph[start].data):
        if node not in path:
            newpaths = find_all_paths(subgraph, node, end, relationship, path)
            paths.extend(newpaths)
    return paths

def main():
    # example: we want path(s) from AS 1234 to AS 3388
    sourceNode = 1234
    destinationNode = 3388
    # the destination node is 3388 so we load dcomplete 3388
    routingTree = scipy.io.mmread("dcomplete3388.mtx").tocsr()
    start = time.time()
    paths = find_all_paths(routingTree, sourceNode, destinationNode,0,[])
    end = time.time()
    print "time to find path: ", end - start
    print "all paths: ", paths
    print "shortest path: ", min(paths, key=len)

main()