#!/bin/env python3
from typing import List, Set, Optional, Iterable, Dict


def main():
    pass


class Graph:
    _nodes: Dict[str, "Node"]

    @staticmethod
    def read_graph(
        *, limit: Optional[int] = None, sep: Optional[str] = None
    ) -> "Graph":
        """
        @brief: Reads a graph from stdin
        @note: The input is expected to be in the form of edges, one per line.
        @param limit: Maximum number of edges (lines) to read.
            If omitted, the function will attemtp to read until EOF.
        @param sep: The separator bethween the nodes of an edge.
            By default, any whitespace.
        @return: The graph object
        """
        out = Graph()
        try:
            while True:
                x, y = input().split(sep)
                for id in (x, y):
                    if id not in out:
                        out.new(id)

                out[x].link(out[y])
        except EOFError:
            return out

    def __init__(self):
        self._dict = {}

    def new(self, id: str) -> "Node":
        """
        @brief: Creates a new node
        @param id: The id of the node
        @throws ValueError: If a node with the given id already exists
        @return: The new node object
        """

        if id in self._nodes:
            raise ValueError(f"ID({id}) already exists")

        node = Node(id, self)
        self._nodes[id] = node
        return node

    def loosely_connected_compontents(self) -> Iterable[Iterable["Node"]]:
        """
        @brief: Finds the loosely connected components of the graph
        @return: An iterator over the components as `Iterable[Node]`
        """
        raise NotImplementedError()

        visited = set()
        for node in self:
            iter = node.dfs(_visited=visited)
            if iter:
                yield iter

    def __len__(self) -> int:
        return len(self._nodes)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __iter__(self) -> Iterable["Node"]:
        return self._nodes.values()

    def __getitem__(self, id: str):
        return self._nodes[id]

    def __contains__(self, id: "str | Node") -> bool:
        if isinstance(id, Node):
            return id in self._nodes.values()
        return id in self._nodes

    def __delitem__(self, id: str):
        self._nodes[id].remove()


class Node:
    _id: str
    _in: List["Node"] = []
    _out: List["Node"] = []
    _graph: Graph

    @property
    def id(self):
        """A name for the node"""
        return self._id

    @property
    def in_nodes(self):
        """A tuple of the ingoing nodes"""
        return tuple(self._in)

    @property
    def out_nodes(self):
        """A tuple of the outgoing nodes"""
        return tuple(self._out)

    def __init__(self, id: str, graph: Graph):
        self._id = id
        self._graph = graph

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"Node({str(self)}"

    def link(self, node: "Node"):
        """
        @brief: Adds an edge to the given node
        @param node: The node to link to
        @throws ValueError: If the nodes have different parent graphs
        """
        if self._graph is not node._graph:
            raise ValueError("Cannot link nodes from different graphs")

        if node not in self._out:
            self._out.append(node)
        if self not in node._in:
            node._in.append(self)

    def unlink(self, node: "Node"):
        """Removes the edge to the given node if there is one"""
        self._out = [n for n in self._out if n is not node]
        node._in = [n for n in node._in if n is not self]

    def remove(self):
        """
        @brief: Removes the node from the graph, including its edges.
        @warning: This leaves the node in an invalid state.
        """
        for node in self._in:
            node._out = [n for n in node._out if n is not self]
        for node in self._out:
            node._in = [n for n in node._in if n is not self]

        del self._graph._nodes[self.id]

    def dfs(
        self, *, reverse=False, _visited: Optional[Set["Node"]] = None
    ) -> Iterable["Node"]:
        """
        @brief: Depth-first search iterator
        @param reverse: If True, the search will be done in the inverse graph
            i.e. following the ingoing edges.
        @return: An iterator over the reachable nodes in dfs order
        """
        if _visited is None:
            _visited = set()

        if self in _visited:
            return
        _visited.add(self)

        for node in self._out if not reverse else self._in:
            yield from node.dfs(_visited=_visited, reverse=reverse)
        yield self


if __name__ == "__main__":
    main()
