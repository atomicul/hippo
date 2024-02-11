#!/bin/env python3
import sys
import graph.UndirectedGraph
from graph.DirectedGraph import Graph
from itertools import groupby


@graph.UndirectedGraph.UndirectedGraph
class UndirectedGraph(Graph):
    pass


def main():
    tree = Graph.read_graph()

    root = tree.tree_root()
    if root is None:
        sys.exit(1)
    for _, level in groupby(root.bfs(), key=lambda x: x[0]):
        level = (x[1] for x in level)
        print(*level)


if __name__ == "__main__":
    main()
