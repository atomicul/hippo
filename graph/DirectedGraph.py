from typing import List, Set, Optional, Iterator, Dict, TextIO, TypeVar
import sys


class Node:
    _id: str
    _in: List["Node"]
    _out: List["Node"]
    _graph: "Graph"

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

    def __init__(self, id: str, graph: "Graph"):
        self._id = id
        self._graph = graph
        self._in = []
        self._out = []

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"Node({str(self)})"

    def link(self, node: "Node"):
        """
        @brief: Adds an edge to the given node
        @param node: The node to link to
        @throws ValueError: If the nodes have different parent graphs
        """
        if self._graph is not node._graph:
            raise ValueError("Cannot link nodes from different graphs")

        if self is node:
            return

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
        @warning: This leaves the node object in an invalid state.
                    You shall not call methods on any dangling reference to it.
        """
        for node in self._in:
            node._out = [n for n in node._out if n is not self]
        for node in self._out:
            node._in = [n for n in node._in if n is not self]

        del self._graph._nodes[self.id]

    def dfs(
        self, *, reverse=False, _visited: Optional[Set["Node"]] = None
    ) -> Iterator["Node"]:
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

        for node in self.out_nodes if not reverse else self.in_nodes:
            yield from node.dfs(_visited=_visited, reverse=reverse)
        yield self


class Graph:
    _nodes: Dict[str, Node]
    _node_type: type["Node"]

    T = TypeVar("T", bound="Graph")

    @classmethod
    def read_graph(
        cls: type[T],
        node: type["Node"] = Node,
        *,
        input_buffer: TextIO = sys.stdin,
        limit: Optional[int] = None,
        sep: Optional[str] = None,
    ) -> T:
        """
        @brief: Reads a graph from `input_buffer` (stdin by default)
        @note: The input is expected to be in the form of edges, one per line.
        @param node: The node class to be used in the graph
        @param input_buffer: The input stream to read from
            By default, sys.stdin
        @param limit: Maximum number of edges (lines) to read.
            If omitted, the function will attemtp to read until EOF.
        @param sep: The separator bethween the nodes of an edge.
            By default, any whitespace.
        @return: The graph object
        """
        out = cls(node)
        for _, line in zip(range(limit) if limit else _forever(), input_buffer):
            x, y = line.split(sep)
            for id in (x, y):
                if id not in out:
                    out.new(id)

            out[x].link(out[y])
        return out

    def __init__(self, node: type["Node"] = Node):
        """
        @param node: The node class to be used in the graph
        """
        self._nodes = {}
        self._node_type = node

    def new(self, id: str) -> "Node":
        """
        @brief: Creates a new node
        @param id: The id of the node
        @throws ValueError: If a node with the given id already exists
        @return: The new node object
        """

        if id in self._nodes:
            raise ValueError(f"ID({id}) already exists")

        node = self._node_type(id, self)
        self._nodes[id] = node
        return node

    def __len__(self) -> int:
        return len(self._nodes)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __iter__(self) -> Iterator["Node"]:
        return iter(self._nodes.values())

    def __getitem__(self, id: str):
        return self._nodes[id]

    def __contains__(self, id: "str | Node") -> bool:
        if isinstance(id, Node):
            return id in self._nodes.values()
        return id in self._nodes

    def __delitem__(self, id: str):
        self._nodes[id].remove()


def _forever() -> Iterator[None]:
    """An infinite iterator"""
    while True:
        yield None
