#!/bin/env python3
from hippo.weighted_graph import WeightedNode, WeightedGraph


def main():
    graph = WeightedGraph()

    a = graph.new("A")
    b = graph.new("B")
    c = graph.new("C")
    a.link(b, 5)
    b.link(c, 3)
    a = graph["A"]

    for component in graph.strongly_connected_components():
        print(*component)


if __name__ == "__main__":
    main()
