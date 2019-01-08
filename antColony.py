import copy
import random
import math
import matplotlib.pyplot as plt
import cProfile
import pstats

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
	
	def calcScoreNumerator(self, road):
		return (self.pheromoneList[road.toHashKey()] ** self.ALPHA) * ((1/road.getLength()) ** self.BETA)
	
	def calcScore(self, currentRoad, notVisitedRoads):
		a = self.calcScoreNumerator(currentRoad)
		b = sum([self.calcScoreNumerator(road) for road in notVisitedRoads])
		return a / b
	
	def calcProbability(self):
		probability = {}
		notVisitedRoads = [Road(self.current, town) for town in self.notVisitedTowns]
		for town in self.notVisitedTowns:
			currentRoad = Road(self.current, town)
			a = self.calcScore(currentRoad, notVisitedRoads)
			b = sum([self.calcScore(road, notVisitedRoads) for road in notVisitedRoads])
			probability[town] = a / b
		return probability
	
	def walk(self):
		while len(self.notVisitedTowns) != 0:
			choice = random.random() #0~1
			prob = sorted(self.calcProbability().items(), key=lambda x: x[1])
			for p in prob:
				choice = choice - p[1]
				if(choice < 0):
					nextTown = p[0]
					break
			else:
				nextTown = prob[0][0]
			for road in self.roads:
				if Road(self.current, nextTown) == road:
					self.passedRoads.append(road)
			self.current = nextTown
			self.visitedTowns.append(nextTown)
			self.notVisitedTowns.remove(nextTown)
			#print(self.current.getName(), [town.getName() for town in self.visitedTowns], [town.getName() for town in self.notVisitedTowns])
		self.visitedTowns.append(self.visitedTowns[0])
		for road in self.roads:
			if Road(self.current, self.visitedTowns[0]) == road:
				self.passedRoads.append(road)
		self.visitedRoadLength = sum([self.visitedTowns[i].getRange(self.visitedTowns[i+1]) for i in range(len(self.visitedTowns)-1)])
	
	def calcDeltaPheromone(self):
		deltaPheromoneList = {}
		for road in self.roads:
			f = True
			for passedRoad in self.passedRoads:
				if road == passedRoad:
					deltaPheromoneList[road.toHashKey()] = self.Q / self.visitedRoadLength
					f = False
			if f:
				deltaPheromoneList[road.toHashKey()] = 0
		# print(*[f'({key[0]}, {key[1]}) :{self.pheromoneList[key]}	' for key in deltaPheromoneList.keys()])
		return deltaPheromoneList

class Town:
	def __init__(self, name, position):
		self.name = name
		self.position = position
	
	def getRange(self, jTown):
		return ((self.position[0] - jTown.position[0])**2 + (self.position[1] - jTown.position[1])**2)**(1/2)
	
	def getName(self):
		return self.name
	
	def __eq__(self, other):
		return (self.name == other.name) and (self.position == other.position)
	
	def __hash__(self):
		return hash(self.name)
	
	def __str__(self):
		return self.name

class Road:
	def __init__(self, iTown, jTown):
		self.iTown = iTown
		self.jTown = jTown
		self.hashKey = (iTown, jTown)
		self.length = iTown.getRange(jTown)
	
	def getLength(self):
		return self.length
	
	def toHashKey(self):
		return self.hashKey
		
	def __eq__(self, other):
		return ((self.iTown == other.iTown) and (self.jTown == other.jTown)) or ((self.iTown == other.jTown) and (self.jTown == other.iTown))

class AntColony:
	def __init__(self, towns, startTown, agentCount, ax, bestLines, RHO=0.3):
		self.towns = towns
		self.startTown = startTown
		self.ax = ax
		self.bestLines = bestLines
		self.roads = []
		for i in range(len(self.towns)):
			for j in range(len(self.towns)):
				self.roads.append(Road(towns[i], towns[j]))
		self.pheromoneList = {}
		for road in self.roads:
			self.pheromoneList[road.toHashKey()] = random.random()
		self.agentCount = agentCount
		self.RHO = RHO
		
	def calcPheromone(self):
		for key in self.pheromoneList:
			self.pheromoneList[key] = self.RHO * self.pheromoneList[key]
		for agent in self.agents:
			d = agent.calcDeltaPheromone()
			for key in d.keys():
				t = (1 - self.RHO) * d[key] + self.pheromoneList[key]
				self.pheromoneList[key] = t
		
		# print(*[f'({key[0]}, {key[1]}) :{self.pheromoneList[key]:0.2}	' for key in self.pheromoneList.keys()])
		
	def walkAgents(self):
		self.agents = [Agent(self.towns, self.startTown, self.roads, self.pheromoneList, ALPHA=1, BETA=2, Q=1000) for i in range(self.agentCount)]
		for agent in self.agents:
			agent.walk()
		self.calcPheromone()
		# for i in range(self.agentCount):
			# self.ax.plot([t.position[0] for t in self.agents[i].visitedTowns], [t.position[1] for t in self.agents[i].visitedTowns], alpha=1.0/(10*50))
		best = min(self.agents, key=lambda agent: agent.visitedRoadLength).visitedTowns
		return best
	
	def optimization(self, count):
		for i in range(count):
			best = self.walkAgents()
			print('->'.join([town.getName() for town in best]), sum([best[i].getRange(best[i+1]) for i in range(len(best)-1)]))
			
			self.bestLines.set_data([town.position[0] for town in best], [town.position[1] for town in best])
			self.ax.set_title(str(i+1))
			plt.pause(0.001)
			plt.savefig("aco/" + str(i) + ".png")
		return best

def main():
	c_profile = cProfile.Profile()
	c_profile.enable()

	# names = [str(i) for i in range(15)]
	# mapRange = 1000
	# positions = [(random.randint(0, mapRange), random.randint(0, mapRange)) for name in names]
	# positions = [[0, 0] for i in range(len(names))]
	# positions[0][0] = 984
	# positions[0][1] = 98
	# positions[1][0] = 238
	# positions[1][1] = 919
	# positions[2][0] = 476
	# positions[2][1] = 14
	# positions[3][0] = 792
	# positions[3][1] = 782
	# positions[4][0] = 143
	# positions[4][1] = 188
	# positions[5][0] = 801
	# positions[5][1] = 550
	# positions[6][0] = 713
	# positions[6][1] = 617
	# positions[7][0] = 313
	# positions[7][1] = 108
	# positions[8][0] = 592
	# positions[8][1] = 918
	# positions[9][0] = 101
	# positions[9][1] = 173
	# positions[10][0] = 453
	# positions[10][1] = 492
	# positions[11][0] = 944
	# positions[11][1] = 594
	# positions[12][0] = 620
	# positions[12][1] = 675
	# positions[13][0] = 212
	# positions[13][1] = 22
	# positions[14][0] = 750
	# positions[14][1] = 219
	# for i in range(len(positions)):
		# for j in range(len(positions[i])):
			# print('positions[' + str(i) + '][' + str(j) + '] = ' + str(positions[i][j]) + ';')
	# towns = [Town(names[i], positions[i]) for i in range(len(names))]
	
	mapRange = 10
	townA = Town('A', (2, 1))
	townB = Town('B', (9, 2))
	townC = Town('C', (10, 4))
	townD = Town('D', (5, 9))
	townE = Town('E', (1, 5))
	towns = [townA, townB, townC, townD, townE]

	startTown = towns[random.randint(0, len(towns)-1)]
	agentCount = 20
	optimizeCount = 50
	
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	ax.set_xlim(0,mapRange)
	ax.set_ylim(0,mapRange)
	bestLines, = ax.plot([], c="Red", linewidth=2)
	RHO = 0.3
	
	antColony = AntColony(towns, startTown, agentCount, ax, bestLines, RHO)
	bestRecord = antColony.optimization(optimizeCount)
	print('->'.join([town.getName() for town in bestRecord]))
	
	c_profile.disable()
	c_stats = pstats.Stats(c_profile)
	c_stats.sort_stats('tottime').print_stats(10)
	
	bestLines.set_data([town.position[0] for town in bestRecord], [town.position[1] for town in bestRecord])
	plt.show()


if __name__ == "__main__":
	main()