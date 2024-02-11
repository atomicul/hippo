#!/bin/env python3
import sys
import graph.UndirectedGraph
from graph.DirectedGraph import Graph


@graph.UndirectedGraph.UndirectedGraph
class UndirectedGraph(Graph):
    pass


def main():
    graph = UndirectedGraph.read_graph()

    a = graph.new("a")
    b = graph.new("b")
    c = graph.new("c")
    a.link(b)
    b.link(c)

    for component in graph.connected_components():
        print(*component)


if __name__ == "__main__":
    main()
