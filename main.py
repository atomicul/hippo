#!/bin/env python3
import graph.UndirectedGraph
from graph.DirectedGraph import Graph


@graph.UndirectedGraph.UndirectedGraph
class UndirectedGraph(Graph):
    pass


def main():
    graph = Graph.read_graph()

    for component in graph.strongly_connected_components():
        print(*component)


if __name__ == "__main__":
    main()
