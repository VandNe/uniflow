from typing import Any, Mapping, Sequence
from uniflow.flow.flow import Flow
from uniflow.node import Node
from uniflow.op.basic.expand_op import ExpandOp
from uniflow.op.basic.reduce_op import ReduceOp
from uniflow.constants import EXPANDREDUCE

class ERFlow(Flow):
    """ExpandReduceFlow class."""

    def __init__(self) -> None:
        """Initialize ExpandReduceFlow class."""
        super().__init__()
    def run(self, nodes: Sequence[Node]) -> Sequence[Node]:
        """Run ExpandReduceFlow.

        Args:
            nodes (Sequence[Node]): Nodes.

        Returns:
            Sequence[Node]: Nodes.
        """
        def custom_merge_function(value_dict_1: Mapping[str, Any], value_dict_2: Mapping[str, Any]) -> Mapping[str, Any]:
            merged_dict = {}

            # 自定义合并逻辑
            for key in value_dict_1:
                if key in value_dict_2:
                    merged_dict[key] = f"{value_dict_1[key]} {value_dict_2[key]}"

            return merged_dict
            
        expand_op = ExpandOp("ExpandOp", split_function= lambda n: n // 2)
        reduce_op = ReduceOp("ReduceOp", merge_function=custom_merge_function)

        expand_1, expand_2 = expand_op(nodes[0])

        reduce_1 = reduce_op(expand_1, expand_2)

        return [reduce_1]

class ExpandReduceFlow(ERFlow):
    """ExpandReduce Flow Class."""

    TAG = EXPANDREDUCE