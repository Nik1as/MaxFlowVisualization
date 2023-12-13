import random
import tkinter as tk
import math

import max_flow
from graph import Graph, Node


def euclidean_distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def absolute_position(node: Node, width, height):
    return round(node.x * width), round(node.y * height)


def get_source_and_target(graph: Graph):  # TODO min-cut
    for s in range(graph.number_of_nodes()):
        for t in range(graph.number_of_nodes()):
            if s != t:
                if max_flow.dfs(graph, s, t):
                    return s, t
    return random.sample(range(graph.number_of_nodes()), 2)


# https://stackoverflow.com/questions/27820178/how-to-add-placeholder-to-an-entry-in-tkinter
class EntryWithPlaceholder(tk.Entry):
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
