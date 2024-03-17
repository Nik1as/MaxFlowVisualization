import itertools
import math
import random
import tkinter as tk

import max_flow
from graph import Graph, Node, Edge


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y


def euclidean_distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def absolute_position(node: Node, width, height):
    return round(node.x * width), round(node.y * height)


def edge_positions(node1, node2, radius):
    dx, dy = node2.x - node1.x, node2.y - node1.y
    length = (dx ** 2 + dy ** 2) ** 0.5

    dx_norm = dx / length
    dy_norm = dy / length

    x1, y1 = node1.x + dx_norm * radius, node1.y + dy_norm * radius
    x2, y2 = node2.x - dx_norm * radius, node2.y - dy_norm * radius

    return x1, y1, x2, y2


def rotate(origin, point, angle):
    x = origin.x + math.cos(angle) * (point.x - origin.x) - math.sin(angle) * (point.y - origin.y)
    y = origin.y + math.sin(angle) * (point.x - origin.x) + math.cos(angle) * (point.y - origin.y)
    return x, y


def text_position(p1, p2, offset):
    dx, dy = p2.x - p1.x, p2.y - p1.y
    length = (dx ** 2 + dy ** 2) ** 0.5

    dx_norm = dx / length
    dy_norm = dy / length

    mid_x = p1.x + 0.5 * dx
    mid_y = p1.y + 0.5 * dy

    orthogonal_x, orthogonal_y = -dy_norm * offset, dx_norm * offset

    mid_x += orthogonal_x
    mid_y += orthogonal_y

    return mid_x, mid_y


def edge_text(edge: Edge):
    if edge.residual_capacity() == edge.prev_flow:
        return f"{edge.residual_capacity()}"
    else:
        return f"{edge.residual_capacity()} ({edge.prev_flow})"


def get_source_and_target(graph: Graph):
    combinations = list(itertools.combinations(range(graph.number_of_nodes()), 2))
    random.shuffle(combinations)

    best_pair = None
    max_length = -1

    for s, t in combinations:
        result = max_flow.dfs(graph, s, t)
        if result is not None:
            parent, level = result

            length = 0
            current = t
            while current != s:
                current = parent[current].start
                length += 1

            if length >= 3:
                return s, t

            if length > max_length:
                max_length = length
                best_pair = (s, t)

    return best_pair


class EntryWithPlaceholder(tk.Entry):
    # https://stackoverflow.com/questions/27820178/how-to-add-placeholder-to-an-entry-in-tkinter
    def __init__(self, master=None, placeholder="PLACEHOLDER", color="grey", width=15):
        super().__init__(master, width=width)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self["fg"]

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self["fg"] = self.placeholder_color

    def foc_in(self, *args):
        if self["fg"] == self.placeholder_color:
            self.delete("0", "end")
            self["fg"] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
