from abc import ABC, abstractmethod
from collections import deque
import math
import graph
from graph import Graph


def dfs(graph: Graph, source: int, target: int) -> tuple[list[graph.Edge], list[int]]:
    parent = [None] * graph.number_of_nodes()
    stack = deque([source])

    visited = [False] * graph.number_of_nodes()
    visited[source] = True

    while stack:
        u = stack.popleft()

        for edge in graph.get_edges_by_node(u):
            if not visited[edge.end] and edge.residual_capacity() > 0:
                stack.appendleft(edge.end)
                visited[edge.end] = True
                parent[edge.end] = edge
                if edge.end == target:
                    return parent, list()


def bfs(graph: Graph, source: int, target: int) -> tuple[list[graph.Edge], list[int]]:
    parent = [None] * graph.number_of_nodes()
    level = [-1] * graph.number_of_nodes()
    level[source] = 0
    queue = deque([source])

    visited = [False] * graph.number_of_nodes()
    visited[source] = True

    while queue:
        u = queue.popleft()

        for edge in graph.get_edges_by_node(u):
            if not visited[edge.end] and edge.residual_capacity() > 0:
                queue.append(edge.end)
                visited[edge.end] = True
                parent[edge.end] = edge
                level[edge.end] = level[u] + 1
                if edge.end == target:
                    return parent, level


def bfs_capacity(graph: Graph, source: int, target: int, delta: int) -> tuple[list[graph.Edge], list[int]]:
    parent = [None] * graph.number_of_nodes()
    queue = deque([source])

    visited = [False] * graph.number_of_nodes()
    visited[source] = True

    while queue:
        u = queue.popleft()

        for edge in graph.get_edges_by_node(u):
            if not visited[edge.end] and edge.residual_capacity() >= delta:
                queue.append(edge.end)
                visited[edge.end] = True
                parent[edge.end] = edge
                if edge.end == target:
                    return parent, list()


class MaxFlow(ABC):

    def __init__(self, graph: Graph, source: int, target: int):
        self.graph = graph
        self.source = source
        self.target = target

    @abstractmethod
    def step(self):
        pass


class FordFulkerson(MaxFlow):

    def __init__(self, graph: Graph, source: int, target: int, path_algo=dfs):
        super().__init__(graph, source, target)
        self.path_algo = path_algo

    def step(self):
        if result := self.path_algo(self.graph, self.source, self.target):
            parent, *_ = result
            path_flow = math.inf

            tmp = self.target
            path = deque()
            while tmp != self.source:
                path_flow = min(path_flow, parent[tmp].residual_capacity())
                path.appendleft(parent[tmp])
                tmp = parent[tmp].start

            tmp = self.target
            while tmp != self.source:
                parent[tmp].adjust(path_flow)
                tmp = parent[tmp].start

            return list(path)


class EdmondsKarp(FordFulkerson):

    def __init__(self, graph: Graph, source: int, target: int):
        super().__init__(graph, source, target, bfs)


class CapacityScaling(MaxFlow):

    def __init__(self, graph: Graph, source: int, target: int):
        super().__init__(graph, source, target)
        max_capacity = max(e.capacity for e in graph.get_edges())
        self.delta = 2 ** math.floor(math.log(max_capacity, 2))

    def step(self):
        if result := bfs_capacity(self.graph, self.source, self.target, self.delta):
            parent, *_ = result
            path_flow = math.inf

            tmp = self.target
            path = deque()
            while tmp != self.source:
                path_flow = min(path_flow, parent[tmp].residual_capacity())
                path.appendleft(parent[tmp])
                tmp = parent[tmp].start

            tmp = self.target
            while tmp != self.source:
                parent[tmp].adjust(path_flow)
                tmp = parent[tmp].start

            return list(path)
        else:
            if self.delta > 1:
                self.delta /= 2
                return self.step()


class Dinic(MaxFlow):  # TODO

    def __init__(self, graph: Graph, source: int, target: int):
        super().__init__(graph, source, target)

    def step(self):
        if result := bfs(self.graph, self.source, self.target):
            _, level = result
            start = [0] * (self.graph.number_of_nodes() + 1)
            edges = []
            while flow := self.blocking_flow(self.source, math.inf, start, level, edges):
                pass
            return edges, level

    def blocking_flow(self, u: int, flow: int, start: list[int], level: list[int], edges: list):
        # dfs in acyclic layer graph

        if u == self.target:
            return flow

        while start[u] < self.graph.get_degree(u):
            edge = self.graph.get_edges_by_node(u)[start[u]]  # edge.start == u
            if level[edge.end] == level[edge.start] + 1 and edge.residual_capacity() > 0:
                curr_flow = min(flow, edge.residual_capacity())
                curr_flow = self.blocking_flow(edge.end, curr_flow, start, level, edges)
                edges.append(edge)

                if curr_flow and curr_flow > 0:
                    edge.adjust(curr_flow)
                    return curr_flow
            start[u] += 1


class GoldbergTarjan(MaxFlow):  # TODO
    pass
