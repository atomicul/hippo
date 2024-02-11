from typing import Set, Iterator
from .DirectedGraph import Node, Graph


def UndirectedNode(n: type[Node]):
    """
    @brief: A decorator that makes a Node class undirected

    It ensures that linking is done in both directions
    """

    if hasattr(n, "__UNDIRECTED"):
        return n

    class UNode(n):
        __UNDIRECTED = True

        def link(self, node: Node, *args, **kwargs):
            n.link(self, node, *args, **kwargs)
            n.link(node, self, *args, **kwargs)

        def unlink(self, node: Node, *args, **kwargs):
            n.unlink(self, node, *args, **kwargs)
            n.unlink(node, self, *args, **kwargs)

    return UNode


def UndirectedGraph(n: type[Graph]):
    """
    @brief: A decorator that specializes a graph to an undirected graph

    It ensures that all nodes are undirected.
    It also provieds additional methods for such graphs.
    """

    class UGraph(n):
        def __init__(self, node: type[Node] = Node):
            n.__init__(self, UndirectedNode(node))

        def connected_components(self) -> Iterator[Iterator[Node]]:
            """Provides an iterator over the connected components of the graph"""
            visited: Set[Node] = set()
            for node in self:
                if node in visited:
                    continue
                yield node.dfs(_visited=visited)

    return UGraph
