from typing import Mapping, Any, Sequence
from uniflow.node import Node
from uniflow.op.op import Op


class ExpandOp(Op):
    """Expand operation class."""

    def __init__(self, name: str, split_function: callable) -> None:
        """Constructor of ExpandOp class.

        Args:
            name (str): Name of the ExpandOp.
            split_function (callable): Function to split the root node into expand_1 and expand_2.
        """
        super().__init__(name)
        self.split_function = split_function

    def __call__(self, root: Node) -> Sequence[Node]:
        """Call ExpandOp.

        Args:
            root (Node): Root node.

        Returns:
            Sequence[Node]: Output nodes.
        """
        expand_1_dict, expand_2_dict = self.split_function(root.value_dict)

        expand_1 = Node(
            name=self.unique_name(),
            value_dict=expand_1_dict,
            prev_nodes=[root]
        )
        expand_2 = Node(
            name=self.unique_name(),
            value_dict=expand_2_dict,
            prev_nodes=[root]
        )

        return [expand_1, expand_2]