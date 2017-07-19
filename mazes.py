# Copyright (c) 2011 Brian Gordon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import png, random, heapq, argparse
rnd = random.SystemRandom()


class undirected_graph(dict):
	"""A dictionary of unordered pairs."""
	def __setitem__(self, key, value):
		super(undirected_graph, self).__setitem__(tuple(sorted(key)), value)

	def __getitem__(self, key):
		return super(undirected_graph, self).__getitem__(tuple(sorted(key)))

	def __has_key__(self, key):
		return super(undirected_graph, self).__has_key__(tuple(sorted(key)))

def grid_adjacent(vertex):
	"""Return all grid vertices adjacent to the given point."""
	x, y = vertex
	adj = []

	if x > 0:
		adj.append((x-1, y))
	if x < GRID_WIDTH-1:
		adj.append((x+1, y))
	if y > 0:
		adj.append((x, y-1))
	if y < GRID_HEIGHT-1:
		adj.append((x, y+1))

	return adj

def make_grid():
	weights = undirected_graph()
	for x in range(GRID_WIDTH):
		for y in range(GRID_HEIGHT):
			vertex = (x,y)
			for neighbor in grid_adjacent(vertex):
				weights[(vertex,neighbor)] = rnd.random()

	return weights

def MCST():
	spanning = undirected_graph()
	weights = make_grid()

	closed = set([(0,0)])
	heap = []
	for neighbor in grid_adjacent((0,0)):
		cost = weights[(0,0),neighbor]
		heapq.heappush(heap, (cost, (0,0), neighbor))

	while heap:
		cost, v1, v2 = heapq.heappop(heap)

		# v1 is the vertex already in the spanning tree
		# it's possible that we've already added v2 to the spanning tree
		if v2 in closed:
			continue

		# add v2 to the closed set
		closed.add(v2)

		# add v2's neighbors to the heap
		for neighbor in grid_adjacent(v2):
			if neighbor not in closed:
				cost = weights[v2, neighbor]
				heapq.heappush(heap, (cost, v2, neighbor))

		# update the spanning tree
		spanning[(v1,v2)] = True

	return draw_tree(spanning)

def RDM():
	spanning = undirected_graph()

	closed = set([(0,0)])
	neighbors = [((0,0), x) for x in grid_adjacent((0,0))]

	while neighbors:
		v1, v2 = neighbors.pop(rnd.randrange(len(neighbors)))

		# v1 is the vertex already in the spanning tree
		# it's possible that we've already added v2 to the spanning tree
		if v2 in closed:
			continue

		# add v2 to the closed set
		closed.add(v2)

		for neighbor in grid_adjacent(v2):
			if neighbor not in closed:
				neighbors.append((v2, neighbor))

		# update the spanning tree
		spanning[(v1,v2)] = True

	return draw_tree(spanning)

bl = 5

def draw_tree(spanning):
	# Create a big array of 0s and 1s for pypng

	pixels = []

	# Add a row of off pixels for the top
	[pixels.append([0]*bl + [1]*bl + ([0] * (img_width-2*bl))) for _ in range(bl)]

	for y in range(GRID_HEIGHT):
		# Row containing nodes
		row = [0] * bl # First column is off
		for x in range(GRID_WIDTH):
			[row.append(1) for _ in range(bl)]
			if x < GRID_WIDTH-1:
				[row.append( int(((x,y),(x+1,y)) in spanning) ) for _ in range(bl)]
		[row.append(0) for _ in range(bl)]
		[pixels.append(row) for _ in range(bl)]

		if y < GRID_HEIGHT-1:
			# Row containing vertical connections between nodes
			row = [0] * bl # First column is off
			for x in range(GRID_WIDTH):
				[row.append( int(((x,y),(x,y+1)) in spanning) ) for _ in range(bl)]
				[row.append(0) for _ in range(bl)]
			[row.append(0) for _ in range(bl)]
			[pixels.append(row) for _ in range(bl)]

	# Add a row of off pixels for the bottom
	[pixels.append(([0] * (img_width-2*bl)) + [1] * bl + [0] * bl) for _ in range(bl)]

	return pixels

# Handle arguments

parser = argparse.ArgumentParser(description='Generate a maze with one of two algorithms.')

group = parser.add_mutually_exclusive_group()
group.add_argument('--prims', action='store_true', help='Use Prim\'s algorithm')
group.add_argument('--random', action='store_true', help='Produce a random spanning tree')

parser.add_argument('-s', dest='size', required=True, type=int, nargs=2, action='store', metavar='size', help='The maze\'s size, width then height in cells')
parser.add_argument('-o', dest='filename', metavar='filename', nargs=1, default='maze.png')

args = parser.parse_args()

GRID_WIDTH, GRID_HEIGHT = tuple(args.size)

img_width = GRID_WIDTH * bl*2 + bl
img_height = GRID_HEIGHT * bl*2 + bl

if args.random:
	pix = RDM()
else:
	pix = MCST()

f = open(args.filename, 'wb')
w = png.Writer(img_width, img_height, greyscale=True, bitdepth=1)
w.write(f, pix)
f.close()
