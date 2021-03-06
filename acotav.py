# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 09:42:08 2018
Updated on Tue Jan 7 20:30:01 2020
@author: ofersh@telhai.ac.il
Based on code by <github/Akavall>
"""
import numpy as np
"""
A class for defining an Ant Colony Optimizer for TSP-solving.
The c'tor receives the following arguments:
    Graph: TSP graph 
    Nant: Colony size
    Niter: maximal number of iterations to be run
    rho: evaporation constant
    alpha: pheromones' exponential weight in the nextMove calculation
    beta: heuristic information's (\eta) exponential weight in the nextMove calculation
    seed: random number generator's seed
"""


class AntforTSP(object):
    def __init__(self, n, Nant, Niter, rho, alpha=1, beta=1, seed=None):
        self.n = n #husein graph N**2 col N rows
        self.Graph = np.array([np.full((n**2), n) for i in range(n - 1)])
        self.Nant = Nant
        #self.ants = [Ant(n) for _ in range (Nant)]
        self.Niter = Niter
        self.rho = rho
        self.alpha = alpha
        self.beta = beta
        self.pheromone = np.ones(self.Graph.shape) / len(self.Graph)
        self.local_state = np.random.RandomState(seed)
        self.threat_cnt = np.array([np.zeros(n ** 2 , dtype='int64') for _ in range (self.Nant)])
        #each ant is a solution so has a N*N threat matrix
        """
        This method invokes the ACO search over the N queen graph.
        It returns the best tour located during the search.
        'all_paths' is a list of pairs, each contains a path and its associated length.
         every individual 'path' is a list of positions, each represented as node.
        """

    def run(self):
        """TODO"""
        # Book-keeping: best tour ever
        shortest_path = None
        best_path = ("TBD", np.inf)
        for i in range(self.Niter):
            all_paths = self.constructColonyPaths()
            self.depositPheronomes(all_paths)
            shortest_path = min(all_paths, key=lambda x: x[1])
            print(i + 1, ": ", shortest_path[1])
            print(shortest_path[0]) #not minimizing
            with open("ans.txt", "a") as ansf:
    # Writing data to a file
                intg = i+1
                ansf.write(str(intg))
                ansf.write(": ")
                ansf.write(str(shortest_path[1]))
                ansf.write(str(shortest_path[0]))
                ansf.write('\n')
  
            if shortest_path[1] < best_path[1]:
                best_path = shortest_path
                if shortest_path[1] == 0 :
                    return shortest_path
            self.pheromone *= self.rho  # evaporation

        return best_path

        """
        This method deposits pheromones on the edges.
        Importantly, unlike the lecture's version, this ACO selects only 1/4 of the top tours - and updates only their edges, 
        in a slightly different manner than presented in the lecture.
        """

    def depositPheronomes(self, all_paths):
        """
        TODO
        :param all_paths:
        :return:
        """
        sorted_paths = sorted(all_paths, key=lambda x: x[1])
        Nsel = int(self.Nant / 4)  # Proportion of updated paths
        for path, cost in sorted_paths[:Nsel]:
            for i in range (len(path)-1):
                self.pheromone[i,path[i]] += 1.0 / self.Graph[i,path[i]]  # dist
        #ERRRROR
        """
        This method generates paths for the entire colony for a concrete iteration.
        The input, 'path', is a list of edges, each represented by a pair of nodes.
        Therefore, each 'arc' is a pair of nodes, and thus Graph[arc] is well-defined as the edges' length.
        """

    def evalTour(self, path, iAnt):
        #cost of path is sum of all threats where queens placed
        return np.sum(self.threat_cnt[iAnt][path])

    def constructColonyPaths(self):
        # TODO find heuristic for starting node not 0 default
        self.threat_cnt.fill(0)  # zero all threats
        paths = []  # all Nant paths of graph size
        for i in range(self.Nant):  # run all ants
            # row = self.pheromone ** self.alpha * ((1.0 / self.Graph) ** self.beta)
            # norm_row = row / row.sum()
            # node = self.local_state.choice(range(self.n ** 2), 1, p=norm_row)[0]
            sol = self.constructSolution(self.local_state.randint(0,self.n**2), i)
            paths.append((sol, self.evalTour(sol, i)))  # paths is tuple of sol X and f(x) fitnes
        return paths
        """"""


    def constructSolution(self, start, iAnt):
        path = []  #to consturct solution we need a place for n queens
        visited = set()
        prev = start
        path.append(prev)
        self.threat_cnt_update(prev, iAnt) #to eval solution we need to consider threats
        visited.add(start)
        for i in range(self.n - 1):
            next_v = self.nextMove(self.pheromone[i][:], self.Graph[i][:], visited)
            visited.add(next_v)
            self.threat_cnt_update(next_v, iAnt)
            path.append(next_v)

        #print(self.threat_cnt[iAnt]) #each ant is a solution so has a N*N threat matrix flatted to N**2 list
        return path
        """
        This method generates 'Nant' paths, for the entire colony, representing a single iteration.
        """


    def threat_cnt_update(self, num, iAnt):
        n = self.n
        row = num % n
        col = num // n
        threats = np.zeros((n,n), dtype='int64')

        for j in range(1, row + 1):
            threats[col][row-j]+= 1 #update col
        for j in range(1, n - row):
            threats[col][row + j] += 1
        for j in range(1, n - col):
            threats[col + j][row] += 1  # update row fron
            if row + j < n:  # update upper diagonal
                threats[col + j][row + j] += 1
            if row - j > 0:  # update lower diagonal
                threats[col + j][row - j] += 1
        for j in range(1, col + 1):
            threats[col - j][row] += 1  # update row back
            if row + j < n:  # update lower diagonal
                threats[col - j][row + j] += 1
            if row - j > 0 :  # update upper diagonal
                threats[col - j][row - j] += 1

        threats = np.ravel(threats)
        self.threat_cnt[iAnt] = self.threat_cnt[iAnt] + threats

    def nextMove(self, pheromone, dist, visited):
        pheromone = np.copy(pheromone)  # Careful

        pheromone[list(visited)] = 0
        row = pheromone ** self.alpha * ((1.0 / dist) ** self.beta)
        norm_row = row / row.sum()
        node = self.local_state.choice(range(self.n ** 2), 1, p=norm_row)[0]
        return node

if __name__ == "__main__" :
    Niter = 10**4
    Nant = 200
    n = 16
    ant_colony = AntforTSP(n, Nant, Niter, rho=0.95, alpha=1.5, beta=1.5)
    shortest_path = ant_colony.run()
    print(shortest_path)