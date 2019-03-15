

"""
Author:
file:
"""
import operator
import random
from Individual import *
import sys
import math
import collections

class BasicTSP:
    def __init__(self, _fName, _popSize, _mutationRate, _maxIterations):
        """
        Parameters and general variables
        """

        self.population     = []
        self.matingPool     = []
        self.best           = None
        self.popSize        = _popSize
        self.genSize        = None
        self.mutationRate   = _mutationRate
        self.maxIterations  = _maxIterations
        self.iteration      = 0
        self.fName          = _fName
        self.data           = {}

        self.readInstance()
        self.initPopulation()


    def readInstance(self):
        """
        Reading an instance from fName
        """
        file = open(self.fName, 'r')
        self.genSize = int(file.readline())
        self.data = {}
        for line in file:
            (id, x, y) = line.split()
            self.data[int(id)] = (int(x), int(y))
        file.close()

    def initPopulation(self):
        """
        Creating random individuals in the population
        """
        for i in range(0, self.popSize):
            individual = Individual(self.genSize, self.data)
            individual.computeFitness()
            self.population.append(individual)

        self.best = self.population[0].copy()
        for ind_i in self.population:
            if self.best.getFitness() > ind_i.getFitness():
                self.best = ind_i.copy()
        print ("Best initial sol: ",self.best.getFitness())

    def updateBest(self, candidate):
        if self.best == None or candidate.getFitness() < self.best.getFitness():
            self.best = candidate.copy()
            print ("iteration: ",self.iteration, "best: ",self.best.getFitness())

    def randomSelection(self):
        """
        Random (uniform) selection of two individuals
        """
        indA = self.matingPool[ random.randint(0, self.popSize-1) ]
        indB = self.matingPool[ random.randint(0, self.popSize-1) ]

        while indA == indB:
            indB = self.matingPool[random.randint(0, self.popSize - 1)]

        return [indA, indB]

    # Function to select Best and Second best candidates
    def bestSelection(self):
        sorted_individuals = sorted(self.matingPool, key=operator.attrgetter('fitness'))
        return sorted_individuals[:2]


    #Implementation of Roulette Wheel selection
    def rouletteWheel(self):
        """
        Your Roulette Wheel Selection Implementation

        """
        sum_of_fitness = sum(individual.getFitness() for individual in self.matingPool)
        max = 0

        for individual in self.matingPool:
            if individual.getFitness() > max :
                max = individual.getFitness()

        #print(max1)
        #print(sum_of_fitness)

        rand_num_1 = random.uniform(0, 1)
        #print("rand_num_1",rand_num_1)
        #rand_num_2 = random.uniform(0, 1)
        #print("rand_num_2",rand_num_2)

        track_total_fitness = 0
        #tmp = None
        #tmp2 = None
        for ind1 in self.matingPool:
            #tmp1= ind1
            prob = ind1.getFitness() / sum_of_fitness

            #normalizing the value
            #step 1
            temp=(max+1)-prob
            #step 2
            norm=temp/sum_of_fitness
            #step 3
            track_total_fitness=track_total_fitness+norm

            if track_total_fitness>=rand_num_1:
                return ind1

    # Implementation of Uniform Crossover
    def uniformCrossover(self, indA, indB):

        child = [0]* indA.genSize
        # how many indexes to pick
        index_selec = random.randint(1, indA.genSize - 1)
        #print("No. of indexes:", index_selec)
        #print(num_no)
        # we initialize this variable to make sure everytime it will generate a unique random number
        unique = [-1]
        num = -1

        # this for loop will select indexes and copy those index values to the child lists
        for i in range(0, index_selec):

            while num in unique:
                num = random.randint(0, indA.genSize - 1)
            unique.append(num)
            #print("index no.", i + 1, "is:", num)
            child[i] = indA.genes[num]
            #childB[num] = indB.genes[num]

        #print(child)
        for i in range(0, indB.genSize):
            d = 1
            if indB.genes[i] not in child:
                d = 0

            if d == 0:
                for n in range(0, len(child)):
                    if child[n] == 0:
                        child[n] = indB.genes[i]
                        break

        #print("child A is:", childA)
        #print(child)
        individual = Individual(self.genSize, self.data)
        individual.genes = child
        return individual

    def cycleCrossover(self, indA, indB):
        """
        Your Cycle Crossover Implementation
        """

        cycle = 1
        flag = True
        child = [0] * indA.genSize
        while flag == True:
            if cycle == 1:
                fixedPoint = indA.genes[0]
                j = 0
                while indA.genes[0] != indB.genes[j]:
                    child[j] = indB.genes[j]
                    toSearch = indB.genes[j]
                    for x in range(0, indA.genSize, 1):
                        if toSearch == indA.genes[x]:
                            j = x
                            break
                child[j] = indB.genes[j]

            else:
                x = 0
                for x in range(0, len(child), 1):
                    if child[x] == 0:
                        j = x
                        break
                while indA.genes[x] != indB.genes[j]:
                    child[j] = indA.genes[j]
                    toSearch = indB.genes[j]
                    for m in range(0, indA.genSize, 1):
                        if toSearch == indA.genes[m]:
                            j = m
                            break
                child[j] = indA.genes[j]

            flag = False
            for i in range(0, len(child), 1):
                if child[i] == 0:
                    flag = True
                    break
            cycle = cycle + 1

        individual = Individual(self.genSize, self.data)
        individual.genes = child
        return individual

    def reciprocalExchangeMutation(self, ind):
        """
        Your Reciprocal Exchange Mutation implementation
        """

        if random.random() > self.mutationRate:
            return
        indexA = random.randint(0, self.genSize-1)
        indexB = random.randint(0, self.genSize-1)

        tmp = ind.genes[indexA]
        ind.genes[indexA] = ind.genes[indexB]
        ind.genes[indexB] = tmp

        ind.computeFitness()
        self.updateBest(ind)

    def scrambleMutation(self, ind):
        """
        Your Scramble Mutation implementation
        """
        #select index range for shuffling the values
        indexA = random.randint(0, ind.genSize - 2)
        indexB = random.randint(indexA+1, ind.genSize - 1)

        #storing the values of selected range in the list
        selected_elements = ind.genes[indexA:indexB+1]
        #print(selected_elements)

        #performing shuffle operation on those elements
        random.shuffle(selected_elements)
        #print(selected_elements)

        #combining the shuffles values back in the individual list
        ind.genes[indexA:indexB + 1] = selected_elements
        #print(ind)


        ind.computeFitness()
        self.updateBest(ind)


    def crossover(self, indA, indB):
        """
        Executes a 1 order crossover and returns a new individual
        """
        child = []
        tmp = {}

        indexA = random.randint(0, self.genSize-1)
        indexB = random.randint(0, self.genSize-1)

        for i in range(0, self.genSize):
            if i >= min(indexA, indexB) and i <= max(indexA, indexB):
                tmp[indA.genes[i]] = False
            else:
                tmp[indA.genes[i]] = True
        aux = []
        for i in range(0, self.genSize):
            if not tmp[indB.genes[i]]:
                child.append(indB.genes[i])
            else:
                aux.append(indB.genes[i])
        child += aux
        return child

    def mutation(self, ind):
        """
        Mutate an individual by swaping two cities with certain probability (i.e., mutation rate)
        """
        if random.random() > self.mutationRate:
            return
        indexA = random.randint(0, self.genSize-1)
        indexB = random.randint(0, self.genSize-1)

        tmp = ind.genes[indexA]
        ind.genes[indexA] = ind.genes[indexB]
        ind.genes[indexB] = tmp

        ind.computeFitness()
        self.updateBest(ind)

    def updateMatingPool(self):
        """
        Updating the mating pool before creating a new generation
        """
        self.matingPool = []
        for ind_i in self.population:
            self.matingPool.append( ind_i.copy() )

    def newGeneration(self):
        """
        Creating a new generation
        1. Selection
        2. Crossover
        3. Mutation
        """
        for i in range(0, len(self.population)):
            #[ind1, ind2] = self.randomSelection()
            [ind1, ind2] = self.bestSelection()
            #ind2 = self.rouletteWheel()
            #ind1 = self.rouletteWheel()
            child = self.uniformCrossover(ind1, ind2)
            #child = self.cycleCrossover(ind1, ind2)
            self.scrambleMutation(child)
            #self.reciprocalExchangeMutation(child)
            self.population[i] = child


    def GAStep(self):
        """
        One step in the GA main algorithm
        1. Updating mating pool with current population
        2. Creating a new Generation
        """

        self.updateMatingPool()
        self.newGeneration()

    def search(self):
        """
        General search template.
        Iterates for a given number of steps
        """
        self.iteration = 0
        while self.iteration < self.maxIterations:
            self.GAStep()
            self.iteration += 1

        print ("Total iterations: ",self.iteration)
        print ("Best Solution: ", self.best.getFitness())

if len(sys.argv) < 2:
    #print ("Error - Incorrect input")
    #print ("Expecting python BasicTSP.py [instance] ")
    file_name="dataset/inst-0.tsp"
    ga = BasicTSP(file_name, 200, 1.0, 300)
    #ga = BasicTSP(sys.argv[], 300, 0.1, 500)
    ga.search()
    sys.exit(0)

problem_file = sys.argv[1]

