import copy
import random
import math
import matplotlib.pyplot as plt
import cProfile
import pstats
import numpy as np
# import eel


class Agent:
    def __init__(self, towns, startTown, roads, pheromoneList,
                 ALPHA=1, BETA=3, Q=1000):
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
        a = np.array([self.pheromoneList[Road(self.current, town)]
                      for town in self.notVisitedTowns])
        a = np.power(a, self.ALPHA)
        b = np.array([town.getRange(self.current)
                      for town in self.notVisitedTowns])
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

    def addDeltaPheromone(self, deltaPheromoneList):
        for road in self.passedRoads:
            deltaPheromoneList[road] += self.Q / \
                (self.visitedRoadLength * road.getLength())


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
                 drawBest=True, drawPheromone=False, drawCutoff=0.01):
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

        self.agents = [Agent(self.towns, self.startTown, self.roads,
                             self.pheromoneList, ALPHA=0, BETA=1, Q=1000)]
        self.agents[0].walk()
        self.calcPheromone()

        # eel.positions({
        #     'nodes': {town.name:
        #               town.position for town in self.towns},
        #     'edges': {str((road.iTown.name, road.jTown.name)):
        #               (road.iTown.name, road.jTown.name) for road in self.roads}
        # })

    def calcPheromone(self):
        for key in self.pheromoneList:
            self.pheromoneList[key] = self.RHO * self.pheromoneList[key]
        # best = min(self.agents, key=lambda agent: agent.visitedRoadLength)
        # ave = best.visitedRoadLength / len(self.roads)
        d = {road: 0 for road in self.roads}
        for agent in self.agents:
            agent.addDeltaPheromone(d)
        for key in self.pheromoneList:
            self.pheromoneList[key] += (1 - self.RHO) * d[key]

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
        bests = []
        for i in range(count):
            best = self.walkAgents()
            bests.append(best)
            # print('->'.join([town.getName() for town in best.visitedTowns]))
            print(i, best.visitedRoadLength)

            # eel.refresh({'best': [str((road.iTown.name, road.jTown.name))
            #                       for road in best.passedRoads],
            #              'pheromone': {str((road.iTown.name, road.jTown.name)):
            #                            self.pheromoneList[road]
            #                            for road in self.pheromoneList}
            #              })

            if self.drawBest or self.drawPheromone:
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
                            plt.plot([road.iTown.position[0],
                                      road.jTown.position[0]],
                                     [road.iTown.position[1],
                                      road.jTown.position[1]],
                                     c="Blue", alpha=t, linewidth=1)

                plt.pause(0.01)
                plt.savefig(f"aco/{i+1}.png")
        return min(bests, key=lambda agent: agent.visitedRoadLength)


def main():
    # eel.init("web")
    # web_app_options = {
    #     "mode": "chrome-app",
    #     "chromeFlags": ["--incognito", "--window-size=500,500"]
    # }
    # eel.start("main.html", options=web_app_options, block=False)
    # eel.sleep(3)

    c_profile = cProfile.Profile()
    c_profile.enable()

    names = []
    positions = []
    minRoadLength = 1
    # with open('xql662.tsp', 'r') as file:
    #     minRoadLength = int(file.readline())
    #     while True:
    #         cells = file.readline().split()
    #         if len(cells) == 0:
    #             break
    #         names.append(cells[0])
    #         positions.append((int(cells[1]), int(cells[2])))

    names = [str(i) for i in range(100)]
    mapRange = 500
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
    optimizeCount = 50
    RHO = 0.3

    print('answer: ', minRoadLength)

    antColony = AntColony(towns, startTown, agentCount,
                          ALPHA=1, BETA=2, RHO=RHO,
                          drawBest=False, drawPheromone=False)
    bestRecord = antColony.optimization(optimizeCount).visitedRoadLength
    print(f'aco: {bestRecord}, score: {bestRecord / minRoadLength}')

    # antColony = AntColony(towns, startTown, 1, 0, 1, 1, False, False)
    # kmeansRecord = antColony.optimization(1).visitedRoadLength
    # print(f'kmeans: {kmeansRecord}, score: {kmeansRecord / minRoadLength}')

    c_profile.disable()
    c_stats = pstats.Stats(c_profile)
    c_stats.sort_stats('tottime').print_stats(5)

    plt.show()


if __name__ == "__main__":
    main()
