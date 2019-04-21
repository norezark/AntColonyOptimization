import copy
import random
import math
import matplotlib.pyplot as plt
import cProfile
import pstats
import numpy as np
# import bokeh
# import bokeh.plotting as plt


class Agent:
    def __init__(self, towns, startTown, roads, pheromoneList, ALPHA=1, BETA=3, Q=1000):
        self.current = startTown
        self.roads = roads
        self.pheromoneList = pheromoneList
        self.notVisitedTowns = copy.deepcopy(towns)
        self.notVisitedTowns.remove(startTown)
        self.visitedTowns = [startTown]
        self.passedRoads = []
        self.ALPHA = ALPHA
        self.BETA = BETA
        self.Q = Q

    def calcProbability(self):
        notVisitedRoads = [Road(self.current, town)
                           for town in self.notVisitedTowns]
        a = np.array([self.pheromoneList[road] for road in notVisitedRoads])
        a = np.power(a, self.ALPHA)
        b = np.array([road.getLength() for road in notVisitedRoads])
        b = np.power(np.reciprocal(b), self.BETA)
        ab = a * b
        score = ab / np.sum(ab)
        score = score / np.sum(score)
        return score

    def walk(self):
        self.visitedRoadLength = 0
        while len(self.notVisitedTowns) != 0:
            nextTown = np.random.choice(self.notVisitedTowns,
                                        p=self.calcProbability())
            nextRoad = Road(self.current, nextTown)
            self.passedRoads.append(nextRoad)
            self.current = nextTown
            self.visitedTowns.append(nextTown)
            self.notVisitedTowns.remove(nextTown)
            self.visitedRoadLength += nextRoad.getLength()
        self.visitedTowns.append(self.visitedTowns[0])
        retRoad = Road(self.current, self.visitedTowns[0])
        self.passedRoads.append(retRoad)
        self.visitedRoadLength += retRoad.getLength()

    def calcDeltaPheromone(self):
        deltaPheromoneList = {road: 0 for road in self.roads}
        for road in self.passedRoads:
            deltaPheromoneList[road] = self.Q / self.visitedRoadLength
        return deltaPheromoneList


class Town:
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.hashKey = hash((self.name, self.position))

    def getRange(self, jTown):
        return ((self.position[0] - jTown.position[0])**2 +
                (self.position[1] - jTown.position[1])**2) ** (1/2)

    def getName(self):
        return self.name

    def __eq__(self, other):
        return (self.name == other.name) and (self.position == other.position)

    def __hash__(self):
        return self.hashKey

    def __str__(self):
        return self.name


class Road:
    def __init__(self, iTown, jTown):
        if iTown.name < jTown.name:
            self.iTown = iTown
            self.jTown = jTown
        else:
            self.iTown = jTown
            self.jTown = iTown
        self.hashKey = hash((self.iTown, self.jTown))
        self.length = iTown.getRange(jTown)

    def getLength(self):
        return self.length

    def __eq__(self, other):
        return self.hashKey == other.hashKey

    def __hash__(self):
        return self.hashKey


class AntColony:
    def __init__(self, towns, startTown, agentCount,
                 ALPHA=1, BETA=2, RHO=0.3,
                 drawBest=True, drawPheromone=False, drawCutoff=0.1):
        self.towns = towns
        self.startTown = startTown
        self.roads = []
        for i in range(len(self.towns)-1):
            for j in range(i+1, len(self.towns)):
                self.roads.append(Road(towns[i], towns[j]))
        self.pheromoneList = {road: 1 for road in self.roads}
        self.agentCount = agentCount
        self.ALPHA = ALPHA
        self.BETA = BETA
        self.RHO = RHO
        self.drawBest = drawBest
        self.drawPheromone = drawPheromone
        self.drawCutoff = drawCutoff
        # self.agents = [Agent(self.towns, self.startTown, self.roads,
        #                      self.pheromoneList, ALPHA=0, BETA=3, Q=1000)]
        # self.agents[0].walk()
        # self.calcPheromone()

    def calcPheromone(self):
        for key in self.pheromoneList:
            self.pheromoneList[key] = self.RHO * self.pheromoneList[key]
        # best = min(self.agents, key=lambda agent: agent.visitedRoadLength)
        # ave = best.visitedRoadLength / len(self.roads)
        for agent in self.agents:
            d = agent.calcDeltaPheromone()
            for key in d:
                self.pheromoneList[key] += (1 - self.RHO) * d[key]
        # print(self.pheromoneList.values())
        # self.pheromoneList[key] = t * \
        #     (best.visitedRoadLength / agent.visitedRoadLength)
        # self.pheromoneList[key] = t * \
        # math.log(agent.visitedRoadLength, best.visitedRoadLength)
        # agent = min(self.agents, key=lambda agent: agent.visitedRoadLength)
        # d = agent.calcDeltaPheromone()
        # for key in d:
        #     t = (1 - self.RHO) * d[key] + self.pheromoneList[key]
        #     self.pheromoneList[key] = t

        # print(self.pheromoneList.values())

    def walkAgents(self):
        self.agents = [Agent(self.towns, self.startTown, self.roads,
                             self.pheromoneList, Q=1000,
                             ALPHA=self.ALPHA, BETA=self.BETA)
                       for i in range(self.agentCount)]
        for agent in self.agents:
            agent.walk()
        self.calcPheromone()
        best = min(self.agents, key=lambda agent: agent.visitedRoadLength)
        return best

    def optimization(self, count):
        for i in range(count):
            best = self.walkAgents()
            print('->'.join([town.getName() for town in best.visitedTowns]),
                  best.visitedRoadLength)

            plt.cla()
            plt.title(str(i + 1))
            if self.drawBest:
                plt.plot([town.position[0] for town in best.visitedTowns],
                         [town.position[1] for town in best.visitedTowns],
                         c="Red", linewidth=2)

            if self.drawPheromone:
                maxPhe = max(self.pheromoneList.values())
                for road in self.pheromoneList:
                    t = self.pheromoneList[road] / maxPhe
                    if t > self.drawCutoff:
                        plt.plot([road.iTown.position[0], road.jTown.position[0]],
                                 [road.iTown.position[1], road.jTown.position[1]],
                                 c="Blue", alpha=t, linewidth=1)

            plt.pause(0.01)
            plt.savefig(f"aco/{i+1}.png")
        return best


def main():
    c_profile = cProfile.Profile()
    c_profile.enable()

    names = [str(i) for i in range(500)]
    mapRange = 1000
    positions = [(0, 0) for name in names]
    positions = [(random.randint(0, mapRange), random.randint(0, mapRange))
                 for name in names]

    for i in range(len(positions)):
        print(f'positions[{i}] = {positions[i]}')
    towns = [Town(names[i], positions[i]) for i in range(len(names))]

    # mapRange = 10
    # townA = Town('A', (2, 1))
    # townB = Town('B', (9, 2))
    # townC = Town('C', (10, 4))
    # townD = Town('D', (5, 9))
    # townE = Town('E', (1, 5))
    # towns = [townA, townB, townC, townD, townE]

    startTown = towns[0]
    agentCount = 20
    optimizeCount = 20
    RHO = 0.3

    antColony = AntColony(towns, startTown, agentCount,
                          ALPHA=1, BETA=2, RHO=RHO,
                          drawBest=True, drawPheromone=False)
    bestRecord = antColony.optimization(optimizeCount).visitedTowns
    print('->'.join([town.getName() for town in bestRecord]))

    c_profile.disable()
    c_stats = pstats.Stats(c_profile)
    c_stats.sort_stats('tottime').print_stats(5)

    plt.show()


if __name__ == "__main__":
    main()
