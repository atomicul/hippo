from hippo.graph import Graph, Node
from hippo.undirected_decorators import undirected_graph, undirected_node


@undirected_graph
class UndirectedGraph(Graph):
    pass


@undirected_node
class UndirectedNode(Node):
    pass
