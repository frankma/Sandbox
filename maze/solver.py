from maze.maze import Maze


class Node(object):
    def __init__(self, rdx, cdx):
        self.rdx = rdx
        self.cdx = cdx

    def __str__(self):
        return f'({self.rdx}, {self.cdx})'


class Edge(object):
    def __init__(self, node_a: Node, node_b: Node):
        self.node_a = node_a
        self.node_b = node_b
        self.distance = abs(node_a.rdx - node_b.rdx) + abs(node_a.cdx - node_b.cdx)


class Graph(object):
    def __init__(self):
        pass


class MazeSolver(object):
    def __init__(self, maze: Maze):
        self.problem = maze

    def scan_maze(self):
        start_node = Node(*self.problem.start_coordinate)

    def generate_graph(self):
        pass
