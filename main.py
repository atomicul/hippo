#!/bin/env python3
from hippo.shortcuts import UndirectedGraph


def main():
    graph = UndirectedGraph.read_graph()

    node = next(iter(graph))

    for layer in node.bfs():
        print(*layer)


if __name__ == "__main__":
    main()
