Studying the interdomain routing system can be a difficult problem due to the size and complexity of the autonomous system (AS) topology. In Phillipa Gill's paper Modeling on Quicksand, the authors developed a fast algorithm called BGPSim that simulates the likely paths taken from a source AS to a destination AS. BGPSim creates a unique subgraph for every AS y, called a routing tree. Paths from any AS x to AS y can then be found using the routing tree for AS y. Unfortunately, the authors' implementation depends on deprecated software (DryadLinq), and ouput paths are unordered. We reimplement their algorithm in Python called BGPSimPy which is open-sourced and also provide routing trees for over 50,000 ASes online. As computing all routing trees was a computationally intensive task that took approximately 10 days over six servers, it is our hope that providing this resource freely online encourages future works that rely extensively on modeling and simulating the Internet's interdomain routing system. 

The process works like this:

1. Convert entire topology into a sparse matrix

You need a list of all AS relationships (p2p = peer to peer, p2c = provider to customer) in the following form:

28917	61316	p2p

25818	8513	p2c

...

So in this example, the ASes 28917 and 61316 have a peer to peer relationship.

We used the relationships on: https://raw.githubusercontent.com/sbunrg/Astoria/master/bgp_sim/Cyclops_caida_cons.txt

However, there are other sources of AS relationships available: http://irl.cs.ucla.edu/topology/ipv4/relationship/

From there you need to use fileToSparse("fileName.txt") in makeRoutingTree.py. This will convert that text file of AS relationships into a sparse matrix. 

2. Create a routing tree for your destination node

Say you would like the path from AS 1234 to AS 3388. This means you need a routing tree for AS 3388 (it is all based off of destination). Thus, you would run makeRoutingTree(3388) in makeRoutingTree.py which would create dcomplete3388.mtx

3. Find the path

Now that you have the appropriate routing tree, you can find the path from AS 1234 to AS 3388 by running find_all_paths(routingTree, 1234, 3388,0,[]). Note that routingTree is the result of loading dcomplete3388 via Scipy io mmread.


NOTE:

This implementation does not use cluster computing although that is highly recommended. In our paper that is currently being reviewed, we make use of GridEngine to compute routing trees and paths in parallel. In addition, we store statistics on the time and depths of routing trees on MongoDB. 

A great chunk of time will probably be spent on computing routing trees. Fortunately, we have provided over 50K routing trees for download at TBD

Please direct questions to cynthiaw2004@gmail.com



