"""Output of a dependency graph as an ASCII tree."""

BRANCH = "|-- "
LAST_BRANCH = "`-- "
BRANCH_PREFIX = "|   "
LAST_PREFIX = "    "
CYCLE_MARK = " (cycle)"
REPEAT_MARK = " (*)"


def _child_items(graph, node, prefix, ancestors):
    """Stack items for the children of a node, last child first."""
    children = graph.get(node, [])
    last_index = len(children) - 1
    items = [
        (child, prefix, index == last_index, ancestors)
        for index, child in enumerate(children)
    ]
    items.reverse()
    return items


def _mark(node, ancestors, shown):
    """Return a mark for a node that must not be expanded again."""
    if node in ancestors:
        return CYCLE_MARK
    if node in shown:
        return REPEAT_MARK
    return ""


def render_tree(graph, root):
    """Return the lines of the ASCII tree of the graph.

    A package that closes a cycle is marked with ``(cycle)``. A package
    whose subtree is already shown above is marked with ``(*)`` and is not
    expanded again. The tree is built without recursion.
    """
    lines = [root]
    shown = {root}
    stack = _child_items(graph, root, "", frozenset([root]))
    while stack:
        node, prefix, last, ancestors = stack.pop()
        connector = LAST_BRANCH if last else BRANCH
        mark = _mark(node, ancestors, shown)
        lines.append(prefix + connector + node + mark)
        if mark:
            continue
        shown.add(node)
        extra = LAST_PREFIX if last else BRANCH_PREFIX
        stack.extend(
            _child_items(graph, node, prefix + extra, ancestors | {node})
        )
    return lines
