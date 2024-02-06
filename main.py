#!/bin/env python3
from graph.DirectedGraph import Graph, Node
from graph.UndirectedGraph import UndirectedNode


def main():
    graph = Graph.read_graph(UndirectedNode)

    for node in graph:
        print(f"Node {node.id}:")
        print("Out:", node.out_nodes)
        print("In:", node.in_nodes)


if __name__ == "__main__":
    main()
