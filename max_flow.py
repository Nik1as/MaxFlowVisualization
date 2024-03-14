import math
from collections import deque

from graph import Graph, Edge


def dfs(graph: Graph, source: int, target: int) -> tuple[list[Edge], list[int]]:
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


def bfs_capacity(graph: Graph, source: int, target: int, delta: int) -> tuple[list[Edge], list[int]]:
    parent = [None] * graph.number_of_nodes()
    level = [-1] * graph.number_of_nodes()
    level[source] = 0
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
                level[edge.end] = level[u] + 1
                if edge.end == target:
                    return parent, level


def bfs(graph: Graph, source: int, target: int) -> tuple[list[Edge], list[int]]:
    return bfs_capacity(graph, source, target, 1)


def ford_fulkerson(graph: Graph, source: int, target: int, path_algo=dfs):
    while result := path_algo(graph, source, target):
        parent, *_ = result
        path_flow = math.inf

        tmp = target
        path = deque()
        while tmp != source:
            path_flow = min(path_flow, parent[tmp].residual_capacity())
            path.appendleft(parent[tmp])
            tmp = parent[tmp].start

        tmp = target
        while tmp != source:
            parent[tmp].adjust(path_flow)
            tmp = parent[tmp].start

        yield list(path)


def edmonds_karp(graph: Graph, source: int, target: int):
    yield from ford_fulkerson(graph, source, target, bfs)


def capacity_scaling(graph: Graph, source: int, target: int):
    max_capacity = max(e.capacity for e in graph.get_edges())
    delta = 2 ** math.floor(math.log(max_capacity, 2))

    while delta >= 1:
        while result := bfs_capacity(graph, source, target, delta):
            parent, *_ = result
            path_flow = math.inf

            tmp = target
            path = deque()
            while tmp != source:
                path_flow = min(path_flow, parent[tmp].residual_capacity())
                path.appendleft(parent[tmp])
                tmp = parent[tmp].start

            tmp = target
            while tmp != source:
                parent[tmp].adjust(path_flow)
                tmp = parent[tmp].start

            yield list(path)

        delta /= 2


def dinic(graph: Graph, source: int, target: int):
    def blocking_flow(u: int, flow: int, start: list[int], level: list[int], edges: list):
        # dfs in acyclic layer graph

        if u == target:
            return flow

        while start[u] < graph.get_degree(u):
            edge = graph.get_edges_by_node(u)[start[u]]  # edge.start == u
            if level[edge.end] == level[edge.start] + 1 and edge.residual_capacity() > 0:
                curr_flow = min(flow, edge.residual_capacity())
                curr_flow = blocking_flow(edge.end, curr_flow, start, level, edges)

                if curr_flow and curr_flow > 0:
                    edge.adjust(curr_flow)
                    edges.append(edge)
                    return curr_flow
            start[u] += 1

    while result := bfs(graph, source, target):
        _, level = result
        start = [0] * (graph.number_of_nodes() + 1)
        edges = []
        while _ := blocking_flow(source, math.inf, start, level, edges):
            pass
        yield edges, level


def goldberg_tarjan(graph: Graph, source: int, target: int):
    excess = [0] * graph.number_of_nodes()
    label = [0] * graph.number_of_nodes()
    active = deque()
    in_queue = [False] * graph.number_of_nodes()

    def preflow():
        edges = []
        label[source] = graph.number_of_nodes()
        for edge in graph.get_edges_by_node(source):
            if not edge.reverse:
                edge.flow = edge.capacity
                excess[edge.end] += edge.flow

                active.append(edge.end)
                in_queue[edge.end] = True

                edges.append(edge)
        return edges, excess, label, source

    def push(node: int):
        edges = []
        for edge in graph.get_edges_by_node(node):
            if edge.residual_capacity() == 0:
                continue

            if label[edge.start] == label[edge.end] + 1:
                flow = min(edge.residual_capacity(), excess[node])

                if flow > 0:
                    excess[edge.start] -= flow
                    excess[edge.end] += flow
                    edge.adjust(flow)
                    edges.append(edge)

                    if edge.end not in (source, target) and excess[edge.end] > 0 and not in_queue[edge.end]:
                        active.append(edge.end)
                        in_queue[edge.end] = True

        return edges, excess, label, node

    def relabel(node: int):
        label[node] = 1 + min(label[edge.end]
                              for edge in graph.get_edges_by_node(node)
                              if edge.residual_capacity() > 0)

    yield preflow()

    while active:
        u = active.popleft()
        in_queue[u] = False

        if any(label[edge.start] == label[edge.end] + 1 and
               edge.residual_capacity() > 0
               for edge in graph.get_edges_by_node(u)):
            yield push(u)
        else:
            relabel(u)

        if u not in (source, target) and excess[u] > 0:
            active.append(u)
            in_queue[u] = True


"""
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


class Dinic(MaxFlow):

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

                if curr_flow and curr_flow > 0:
                    edge.adjust(curr_flow)
                    edges.append(edge)
                    return curr_flow
            start[u] += 1


class GoldbergTarjan(MaxFlow):  # TODO

    def __init__(self, graph: Graph, source: int, target: int):
        super().__init__(graph, source, target)
        self.excess = [0] * graph.number_of_nodes()
        self.label = [0] * graph.number_of_nodes()
        self.active = deque()
        self.preflow_executed = False

    def preflow(self):
        self.preflow_executed = True
        self.label[self.source] = self.graph.number_of_nodes()
        for edge in self.graph.get_edges_by_node(self.source):
            if not edge.reverse_edge:
                edge.flow = edge.capacity
                self.excess[edge.end] += edge.flow
                self.active.append(edge.end)

    def push(self, u):
        for edge in self.graph.get_edges_by_node(u):
            if edge.reverse_edge:
                continue
            if edge.flow == edge.capacity:
                continue

            v = edge.end
            if self.label[u] > self.label[v]:
                flow = min(edge.residual_capacity(), self.excess[u])
                self.excess[u] -= flow
                self.excess[v] += flow
                edge.adjust(flow)

    def relabel(self, u):
        self.label[u] = 1 + min(self.label[edge.v]
                                for edge in self.graph.get_edges_by_node(u)
                                if edge.residual_capacity() > 0)

    def step(self):
        if not self.preflow_executed:
            return self.preflow()

        if self.active:
            u = self.active.popleft()
            if any(self.excess[edge.end] > 0 for edge in self.graph.get_edges_by_node(u)):
                return self.push(u)
            else:
                return self.relabel(u)

            if u not in (s, t) and self.excess[u] > 0:
                self.active.append(u)
"""
