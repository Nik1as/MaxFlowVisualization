import random


class Node:

    def __init__(self, node_id: int, x: float, y: float):
        self.node_id = node_id
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"id={self.node_id}, x={self.x}, y={self.y}"


class Edge:

    def __init__(self, start: int, end: int, capacity: int = 0, reverse: bool = False):
        self.start = start
        self.end = end
        self.capacity = capacity
        self.reverse = reverse
        self.reverse_edge = None
        self.flow = 0

    def residual_capacity(self):
        if self.reverse:
            return self.reverse_edge.flow
        else:
            return self.capacity - self.flow

    def adjust(self, delta):
        if self.reverse:
            self.reverse_edge.flow -= delta
        else:
            self.flow += delta


class Graph:

    def __init__(self, n: int):
        self.nodes = [Node(i, random.random(), random.random()) for i in range(n)]
        self.edges = [[] for _ in range(n)]
        self.n = n

    def add_edge(self, start: int, end: int, capacity: int):
        edge = Edge(start, end, capacity)
        rev_edge = Edge(end, start, reverse=True)

        edge.reverse_edge = rev_edge
        rev_edge.reverse_edge = edge

        self.edges[start].append(edge)
        self.edges[end].append(rev_edge)

    def get_edges_by_node(self, node: int):
        return self.edges[node]

    def get_degree(self, node: int):
        return len(self.edges[node])

    def get_edges(self):
        for i in range(self.n):
            for edge in self.get_edges_by_node(i):
                yield edge

    def has_edge(self, source, target):
        for edge in self.get_edges_by_node(source):
            if edge.start == source and edge.end == target:
                return True
        return False

    def get_nodes(self):
        return self.nodes

    def number_of_nodes(self):
        return self.n

    def copy(self):
        new_graph = Graph(self.number_of_nodes())
        for edge in self.get_edges():
            new_graph.add_edge(edge.start, edge.end, edge.capacity)
        return new_graph
