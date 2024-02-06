from .DirectedGraph import Node, Graph


def Undirected(n):
    if issubclass(n, Node):

        class UndirectedNode(n):
            def link(self, node: Node, *args, **kwargs):
                n.link(self, node, *args, **kwargs)
                n.link(node, self, *args, **kwargs)

            def unlink(self, node: Node, *args, **kwargs):
                n.unlink(self, node, *args, **kwargs)
                n.unlink(node, self, *args, **kwargs)

        return UndirectedNode
    elif issubclass(n, Graph):
        raise NotImplementedError

    raise NotImplementedError


@Undirected
class UndirectedNode(Node):
    pass
