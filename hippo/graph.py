from typing import List, Set, Tuple, Optional, Iterator, Dict, TextIO, TypeVar
import itertools
import enum
import queue
import sys


class Node:
    _id: str
    _in: List["Node"]
    _out: List["Node"]
    _graph: "Graph"

    T = TypeVar("T", bound="Node")

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
        @note: The iterator starts with the node itself
        @note: This is an adapter for `self.dfs_path`.
        If you care for path recunstruction, you should use that method instead.
        """
        return (n.node for n in self.dfs_path(reverse=reverse, _visited=_visited))

    def dfs_path(
        self,
        *,
        reverse=False,
        _visited: Optional[Set["Node"]] = None,
        _search_node: Optional["SearchNode"] = None,
    ) -> Iterator["SearchNode"]:
        """
        @brief: Depth-first search iterator with path recunsturction
        @param reverse: If True, the search will be done in the inverse graph
            i.e. following the ingoing edges.
        @return: An iterator over the reachable nodes as `SearchNode` in dfs order
        @note: The iterator starts with `SearchNode(0, self)` itself
        """
        if _visited is None:
            _visited = set()

        if self in _visited:
            return
        _visited.add(self)

        if _search_node is None:
            _search_node = SearchNode(self, 0)

        for node in self.out_nodes if not reverse else self.in_nodes:
            yield from node.dfs_path(
                _visited=_visited,
                reverse=reverse,
                _search_node=_search_node.next_node(node),
            )
        yield _search_node

    def bfs(
        self, *, max_depth: Optional[int] = None, reverse=False
    ) -> Iterator[Iterator["Node"]]:
        """
        @brief: Breadth-first search iterator
        @param max_depth: The maximum depth to search for, unlimited by default.
        @param reverse: If True, the search will be done in the inverse graph
            i.e. following the ingoing edges.
        @return: An iterator over each layer of the bfs tree
        @note: The first group in the return iterator
            has the root node as its sole element
        @note: This is an adapter for `self.bfs_path`.
            If you care for path recunstruction, you should use that method instead.
        """

        search_nodes = self.bfs_path(max_depth=max_depth, reverse=reverse)
        layers = itertools.groupby(search_nodes, key=lambda x: x.dist)
        layers = (x[1] for x in layers)
        layers = ((x.node for x in layer) for layer in layers)

        return layers

    def bfs_path(
        self, *, max_depth: Optional[int] = None, reverse=False
    ) -> Iterator["SearchNode"]:
        """
        @brief: Breadth-first search iterator with path recunstruction
        @param max_depth: The maximum depth to search for, unlimited by default.
        @param reverse: If True, the search will be done in the inverse graph
            i.e. following the ingoing edges.
        @return: An iterator over `SearchNode`s in bfs order
        @note: The first node is `SearchNode(0, self)`
        """
        visited: Set["Node"] = set()
        visited.add(self)

        q: queue.Queue["SearchNode"] = queue.Queue()
        q.put(SearchNode(self, 0))
        while not q.empty():
            search_node = q.get()
            yield search_node
            if max_depth is not None and search_node.dist == max_depth:
                continue

            for adj_node in (
                search_node.node.out_nodes if not reverse else search_node.node.in_nodes
            ):
                if adj_node not in visited:
                    visited.add(adj_node)
                    q.put(search_node.next_node(adj_node))

    def edges_iter(
        self,
        *,
        reverse=False,
        _visited: Optional[Dict["Node", "_VisitedType"]] = None,
        _search_node: Optional["SearchNode"] = None,
    ) -> Iterator[Tuple["EdgeType", "SearchNode"]]:
        """
        @brief: Edge iterator
        @param reverse: If True, the search will be done in the inverse graph
            i.e. following the ingoing edges.
        @return: An iterator over `(edge_type, search_node)` tuples,
        where `edge_type` is the type of the edge.
        The edge leads into `search_node.node`
        from `search_node.parent.node`
        """
        if _visited is None:
            _visited = {}
        if self in _visited:
            return
        if _search_node is None:
            _search_node = SearchNode(self, 0)

        _visited[self] = _VisitedType.EXPLORED

        for adj_node in self.out_nodes if not reverse else self.in_nodes:
            sn = _search_node.next_node(adj_node)
            if adj_node not in _visited:
                yield EdgeType.TREE_EDGE, sn
            elif _visited[adj_node] == _VisitedType.EXPLORED:
                if _search_node.parent.node is adj_node:
                    yield EdgeType.TRIVIAL_BACK_EDGE, sn
                else:
                    yield EdgeType.BACK_EDGE, sn
            else:
                yield EdgeType.CROSS_EDGE, sn
            yield from adj_node.edges_iter(
                reverse=reverse, _visited=_visited, _search_node=sn
            )

        _visited[self] = _VisitedType.VISITED

    def __str__(self) -> str:
        return self.id

    def __repr__(self) -> str:
        return f"Node({str(self)})"


class SearchNode:
    """Helper class for single source search algorithms"""

    _node: Node.T
    _dist: int
    _parent: Optional["SearchNode"]

    @property
    def node(self) -> Node.T:
        """The encapsulated node"""
        return self._node

    @property
    def dist(self) -> int:
        """The distance from the root of the search to this node"""
        return self._dist

    @property
    def parent(self) -> "SearchNode":
        """
        @brief: The node that leads into this one in the search
        @throws Exception: If the node is the root of the search
        """
        if self._parent is None:
            raise Exception("No parent")
        return self._parent

    def next_node(self, node: Node, added_distance=1) -> "SearchNode":
        """Constructs the next node in the search"""
        return SearchNode(node, self._dist + added_distance, self)

    def __init__(self, node: Node.T, dist: int, parent: Optional["SearchNode"] = None):
        self._node = node
        self._dist = dist
        self._parent = parent

    def _backtrack(self) -> Iterator["SearchNode"]:
        if self._parent is not None:
            yield from self._parent._backtrack()
        yield self

    def path(self) -> List[Node.T]:
        """Returns the path from the root of the search to this node"""
        return [n._node for n in self._backtrack()]

    def path_as_node(self) -> List["SearchNode"]:
        """
        @brief: Returns the path from the root of the search to this node as `SearchNode`
        @note: This is useful in case you need the distance from root for each node in the path
            If you're only interested in the ordering of the nodes, consider using `self.path` instead
        """

        return list(self._backtrack())

    def __str__(self) -> str:
        return str((self._dist, self._node))

    def __repr__(self) -> str:
        return f"SearchNode{str(self)}"


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
        @throws ValueError: If any line fails to be split into two
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

    def strongly_connected_components(self) -> Iterator[Iterator[Node]]:
        """Provides an iterator over the strongly connected components of the graph"""
        order = self.topological_order(reverse=True)
        visited: Set[Node] = set()
        for node in order:
            if node not in visited:
                yield node.dfs(_visited=visited)

    def topological_order(self, *, reverse=False) -> Iterator[Node]:
        """
        @brief: Topological order iterator
        @warning: This method is only guaranteed to yield
            a valid topological order if the graph is a acyclic
        @param reverse: If true, iterate in reverse topological order
        @return: An iterator over the nodes in topological order
        """
        visited: Set[Node] = set()
        for node in self:
            yield from node.dfs(reverse=not reverse, _visited=visited)

    def has_cycle(
        self, *, allow_cross_edges=True, allow_trivial_back_edges=False
    ) -> bool:
        """
        @brief: Checks if the graph has a cycle
        @param allow_cross_edges: If False, cross edges will be considered cycles
        @param allow_trivial_back_edges: If False, trivial back edges will be considered cycles
        """
        _visited: Dict[Node, _VisitedType] = {}
        for node in self:
            if any(
                True
                for x in node.edges_iter(_visited=_visited)
                if x[0]
                in [EdgeType.BACK_EDGE]
                + ([EdgeType.TRIVIAL_BACK_EDGE] if not allow_trivial_back_edges else [])
                + ([EdgeType.CROSS_EDGE] if not allow_cross_edges else [])
            ):
                return True
        return False

    def tree_root(self) -> Optional[Node]:
        """
        @brief: Checks if the graph is a tree and returns its root
        @return: Tree root or None if graph is not in the form of a tree
        """
        if not self or self.has_cycle(
            allow_cross_edges=False, allow_trivial_back_edges=False
        ):
            return None
        return next(self.topological_order())

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


class EdgeType(enum.Enum):
    TREE_EDGE = 0
    TRIVIAL_BACK_EDGE = 1
    BACK_EDGE = 2
    CROSS_EDGE = 3


class _VisitedType(enum.Enum):
    VISITED = 0
    EXPLORED = 1


def _forever() -> Iterator[None]:
    """An infinite iterator"""
    while True:
        yield None
