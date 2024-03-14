import itertools
import math
import random

from graph import Graph
from utils import euclidean_distance, get_source_and_target


def line_intersect(p1, q1, p2, q2):
    def ccw(p, q, r):
        return (q.y - p.y) * (r.x - p.x) - (r.y - p.y) * (q.x - p.x)

    return ccw(p1, q1, p2) * ccw(p1, q1, q2) < 0 and ccw(p2, q2, p1) * ccw(p2, q2, q1) < 0


def generate(n: int, max_capacity: int) -> tuple[int, int, Graph]:
    graph = Graph(n)

    all_edges = list(itertools.permutations(graph.get_nodes(), 2))
    random.shuffle(all_edges)
    all_edges.sort(key=lambda edge: euclidean_distance(*edge))

    edges = []
    rows = math.ceil(math.sqrt(n))
    for n1, n2 in all_edges:
        if (not any(line_intersect(n1, n2, n3, n4) for (n3, n4) in edges)
                and abs(n1.node_id % rows - n2.node_id % rows) <= 1
                and abs(n1.node_id // rows - n2.node_id // rows) <= 1):
            edges.append((n1, n2))

    for n1, n2 in edges:
        if not graph.has_edge(n1.node_id, n2.node_id):
            graph.add_edge(n1.node_id, n2.node_id, random.randint(1, max_capacity))

    source, target = get_source_and_target(graph)

    degree_source = graph.get_degree(source) // 2
    for edge in graph.get_edges_by_node(source):
        if not edge.reverse:
            edge.capacity = (degree_source + 1) * max_capacity

    degree_target = graph.get_degree(target) // 2
    for edge in graph.get_edges():
        if edge.end == target and not edge.reverse:
            edge.capacity = (degree_target + 1) * max_capacity

    # TODO
    """
    while True:
        parent, dist = max_flow.bfs(graph, source, target)
        if dist[target] <= 3:
            pass  # add nodes between source and target
        else:
            break
    """

    return source, target, graph
