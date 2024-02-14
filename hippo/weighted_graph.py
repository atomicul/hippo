from typing import List, Tuple, Iterator, Optional
from .graph import Graph, Node


class WeightedNode(Node):
    _in: List[Tuple[float, "WeightedNode"]]
    _out: List[Tuple[float, "WeightedNode"]]

    @property
    def in_nodes(self):
        return tuple(node for _, node in self._in)

    @property
    def out_nodes(self):
        return tuple(node for _, node in self._out)

    @property
    def in_edges(self):
        """A tuple of ingoing edges in form of (weight, node) tuples"""
        return tuple(self._in)

    @property
    def out_edges(self):
        """A tuple of outgoing edges in form of (weight, node) tuples"""
        return tuple(self._out)

    def __init__(
        self,
        id: str,
        graph: "WeightedGraph",
    ):
        super().__init__(id, graph)

    def link(self, node: Node, weight: float = 1):
        """
        @brief: Adds an edge to the given node
        @param node: The node to link to
        @param weight: The weight of the edge
        @throws ValueError: If the nodes have different parent graphs
        @throws TypeError: If the given node is not a WeightedNode
        @return self
        """
        if not isinstance(node, WeightedNode):
            raise TypeError("Cannot link a weighted node to a non-weighted node")

        if self._graph is not node._graph:
            raise ValueError("Cannot link nodes from different graphs")

        if self is node:
            return self

        if node not in self._out:
            self._out.append((weight, node))
        if self not in node._in:
            node._in.append((weight, self))

        return self

    def unlink(self, node: "Node"):
        """
        @brief: Removes the edge to the given node if there is one
        @throws TypeError: If the given node is not a WeightedNode
        @return self
        """
        if not isinstance(node, WeightedNode):
            raise TypeError("Cannot unlink a weighted node from a non-weighted node")

        self._out = [n for n in self._out if n[1] is not node]
        node._in = [n for n in node._in if n[1] is not self]

        return self

    def remove(self):
        for _, node in self._in:
            node._out = [n for n in node._out if n[1] is not self]
        for _, node in self._out:
            node._in = [n for n in node._in if n[1] is not self]

        del self._graph._nodes[self.id]


class WeightedGraph(Graph):
    @classmethod
    def read_graph(cls):
        raise NotImplementedError

    # Make sure that only `WeightedNode``s are created with this class
    def __init__(self, node_type: type[WeightedNode] = WeightedNode):
        super().__init__(node_type)

    # The following methods are overridden to ensure that the correct type is returned
    # we assert for each of them that the only node in this object is indeed a `WeightedNode`
    def new(self, id: str) -> WeightedNode:
        n = super().new(id)
        assert isinstance(n, WeightedNode)
        return n

    def strongly_connected_components(self) -> Iterator[Iterator[WeightedNode]]:
        return _assert_correctness_2D(super().strongly_connected_components())

    def topological_order(self, *, reverse=False) -> Iterator[WeightedNode]:
        return _assert_correctness(super().topological_order(reverse=reverse))

    def tree_root(self) -> Optional[Node]:
        n = super().tree_root()
        assert n is None or isinstance(n, WeightedNode)
        return n

    def __getitem__(self, id: str) -> WeightedNode:
        n = super().__getitem__(id)
        assert isinstance(n, WeightedNode)
        return n


def _assert_correctness(x: Iterator[Node]) -> Iterator[WeightedNode]:
    for n in x:
        assert isinstance(n, WeightedNode)
        yield n


def _assert_correctness_2D(
    x: Iterator[Iterator[Node]],
) -> Iterator[Iterator[WeightedNode]]:
    for n in x:
        yield _assert_correctness(n)
