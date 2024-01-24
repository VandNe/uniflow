from typing import Mapping, Any, Sequence
from uniflow.node import Node
from uniflow.op.op import Op


class ReduceOp(Op):
    """Reduce operation class."""

    def __init__(self, name: str, merge_function: callable) -> None:
        """Constructor of ReduceOp class.

        Args:
            name (str): Name of the ReduceOp.
            merge_function (callable): Function to merge expand_1 and expand_2 into reduce_1.
        """
        super().__init__(name)
        self.merge_function = merge_function

    def __call__(self, expand_1: Node, expand_2: Node) -> Node:
        """Call ReduceOp.

        Args:
            expand_1 (Node): expand_1 node.
            expand_2 (Node): expand_2 node.

        Returns:
            Node: Output node (reduce_1).
        """
        value_dict = self.merge_function(expand_1.value_dict, expand_2.value_dict)

        reduce_1 = Node(
            name=f"{self.unique_name()}_reduce_1",
            value_dict=value_dict,
            prev_nodes=[expand_1, expand_2]
        )

        return reduce_1