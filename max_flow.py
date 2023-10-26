from abc import ABC, abstractmethod
from collections import deque


def dfs(graph, source, target, parent):
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
                    return True
    return False


def bfs(graph, source, target, parent):
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
                if edge.end == target:
                    return True
    return False


class MaxFlow(ABC):

    def __init__(self, graph, source, target):
        self.graph = graph
        self.source = source
        self.target = target

    @abstractmethod
    def step(self):
        pass


class FordFulkerson(MaxFlow):

    def __init__(self, graph, source, target, path_algo=dfs):
        super().__init__(graph, source, target)
        self.path_algo = path_algo

    def step(self):
        parent = [None] * self.graph.number_of_nodes()

        while self.path_algo(self.graph, self.source, self.target, parent):
            path_flow = float("Inf")

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

    def __init__(self, residual_graph, source, target):
        super().__init__(residual_graph, source, target, bfs)


class Dinic(MaxFlow):  # TODO

    def __init__(self, graph, source, target):
        super().__init__(graph, source, target)

    def step(self):
        levels = [None] * self.graph.number_of_nodes()

        while bfs(self.graph, self.source, self.target, levels):

            start = [0 for i in range(self.graph.number_of_nodes() + 1)]
            while True:
                flow = self.send_flow(self.source, float("int"), self.target, start)
                if not flow:
                    break

    def send_flow(self, u, flow, t, start, levels):
        if u == t:
            return flow

        while start[u] < len(self.adj[u]):
            e = self.adj[u][start[u]]
            if levels[e.v] == levels[u] + 1 and e.flow < e.C:
                curr_flow = min(flow, e.C - e.flow)
                temp_flow = self.send_flow(e.v, curr_flow, t, start, levels)

                if temp_flow and temp_flow > 0:
                    e.flow += temp_flow

                    self.adj[e.v][e.rev].flow -= temp_flow
                    return temp_flow
            start[u] += 1


class GoldbergTarjan(MaxFlow):  # TODO
    pass
