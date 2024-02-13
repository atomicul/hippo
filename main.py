#!/bin/env python3
import graph.UndirectedGraph
from graph.DirectedGraph import Graph


@graph.UndirectedGraph.UndirectedGraph
class UndrectedGraph(Graph):
    pass


def main():
    graph = Graph.read_graph()

    node = next(iter(graph))

    for layer in node.bfs():
        print(*layer)


if __name__ == "__main__":
    main()
