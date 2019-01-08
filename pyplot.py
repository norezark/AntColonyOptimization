import copy
import random
import math
import matplotlib.pyplot as plt
import cProfile
import pstats
import csv

def main():
	mapRange = 100
	positions = [[0, 0] for i in range(10)]
	positions[0][0] = 26
	positions[0][1] = 95
	positions[1][0] = 58
	positions[1][1] = 31
	positions[2][0] = 4
	positions[2][1] = 81
	positions[3][0] = 85
	positions[3][1] = 77
	positions[4][0] = 46
	positions[4][1] = 57
	positions[5][0] = 90
	positions[5][1] = 56
	positions[6][0] = 83
	positions[6][1] = 87
	positions[7][0] = 32
	positions[7][1] = 35
	positions[8][0] = 23
	positions[8][1] = 93
	positions[9][0] = 86
	positions[9][1] = 21


	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	ax.set_xlim(0,mapRange)
	ax.set_ylim(0,mapRange)
	bestLines, = ax.plot([], c="Red", linewidth=2)
	
	with open("sukita.csv") as file:
		reader = csv.reader(file)
		ln = 1
		for line in reader:
			print(line[0])
			# ax.plot([t.position[0] for t in self.agents[i].visitedTowns], [t.position[1] for t in self.agents[i].visitedTowns])
			bestLines.set_data([positions[int(town)][0] for town in line[1].split()], [positions[int(town)][1] for town in line[1].split()])
			ax.set_title(str(ln))
			plt.pause(0.1)
			plt.savefig("ga/" + str(ln) + ".png")
			ln += 1
	
	plt.show()


if __name__ == "__main__":
	main()