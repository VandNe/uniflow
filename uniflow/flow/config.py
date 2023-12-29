"""Extract, Transform and Pipeline config module."""

from dataclasses import dataclass, field
from typing import Dict, Optional

from uniflow import Context, GuidedPrompt
from uniflow.op.extract.split.constants import PARAGRAPH_SPLITTER
from uniflow.op.model.model_config import (
    HuggingfaceModelConfig,
    LMQGModelConfig,
    ModelConfig,
    NougatModelConfig,
    OpenAIModelConfig,
)

###########################################################
#                   All Extract Configs                   #
###########################################################


@dataclass
class ExtractConfig:
    """Extract Config Class."""

    flow_name: str
    num_thread: int = 1
    model_config: Optional[ModelConfig] = None
    splitter: Optional[str] = None


@dataclass
class ExtractTxtConfig(ExtractConfig):
    """Extract Txt Config Class."""

    flow_name: str = "ExtractTxtFlow"


@dataclass
class ExtractPDFConfig(ExtractConfig):
    """Nougat Config Class."""

    flow_name: str = "ExtractPDFFlow"
    model_config: ModelConfig = NougatModelConfig()
    splitter: str = PARAGRAPH_SPLITTER


@dataclass
class ExtractMarkdownConfig(ExtractConfig):
    """Extract Markdown Config Class."""

    flow_name: str = "ExtractMarkdownFlow"


@dataclass
class ExtractIpynbConfig(ExtractConfig):
    """Extract ipynb Config Class."""

    flow_name: str = "ExtractIpynbFlow"


###########################################################
#                   All Transform Configs                 #
###########################################################


@dataclass
class TransformConfig:
    """Transform Base Config Class."""

    flow_name: str
    model_config: ModelConfig
    num_thread: int = 1
    guided_prompt_template: GuidedPrompt = GuidedPrompt(
        instruction="""Generate one question and its corresponding answer based on the last context in the last
    example. Follow the format of the examples below to include context, question, and answer in the response""",
        examples=[
            Context(
                context="The quick brown fox jumps over the lazy black dog.",
                question="What is the color of the fox?",
                answer="brown.",
            ),
            Context(
                context="The quick brown fox jumps over the lazy black dog.",
                question="What is the color of the dog?",
                answer="black.",
            ),
        ],
    )


@dataclass
class TransformOpenAIConfig(TransformConfig):
    """Transform OpenAI Config Class."""

    flow_name: str = "TransformOpenAIFlow"
    model_config: ModelConfig = OpenAIModelConfig()


@dataclass
class TransformHuggingFaceConfig(TransformConfig):
    """Transform Hugging Face Config Class."""

    flow_name: str = "TransformHuggingFaceFlow"
    model_config: ModelConfig = HuggingfaceModelConfig()


@dataclass
class TransformLMQGConfig(TransformConfig):
    """Transform LMQG Config Class."""

    flow_name: str = "TransformLMQGFlow"
    guided_prompt_template: GuidedPrompt = GuidedPrompt(instruction="", examples=[])
    model_config: ModelConfig = LMQGModelConfig()


@dataclass
class TransformCopyConfig(TransformConfig):
    """Transform Linear Config Class."""

    flow_name: str = "TransformCopyFlow"
    guided_prompt_template: GuidedPrompt = GuidedPrompt(instruction="", examples=[])
    model_config: ModelConfig = field(default_factory=lambda: {})


###########################################################
#                   All AutoRater Config                  #
###########################################################
@dataclass
class RaterConfig:
    """Rater Config Class."""

    flow_name: str
    model_config: ModelConfig
    label2score: Dict[str, float]
    guided_prompt_template: GuidedPrompt
    num_thread: int = 1

    def __post_init__(self):
        """Post-initialization to perform label check."""
        incompatible_labels = self.check_labels()
        unexprected_labels = incompatible_labels["unexpected_labels"]
        missing_labels = incompatible_labels["missing_labels"]
        if unexprected_labels:
            raise ValueError(
                "Inconsistent labels found in guided_prompt_template examples, "
                f"example label {unexprected_labels} not in label2score has keys {list(self.label2score.keys())}",
            )
        if missing_labels:
            print(f"The label2score label {missing_labels} not in example label.")

    def check_labels(self) -> Dict[str, list]:
        """
        Check if every label in the guided_prompt_template's examples is a key in label2score.

        Returns:
            Dict: Incompatible Keys, fields:
                - 'missing_labels' (List[str]): labels in label2score but not in examples, this may cause performance lose.
                - 'unxpected_labels' (List[str]): labels in examples but not in label2score, this cause ValueError.
        """
        # TODO: Does label strictly match in upper/lower letter?
        example_labels = set()
        for example in self.guided_prompt_template.examples:
            example_labels.add(example.label)
        label2score_labels = set(self.label2score.keys())

        missing_labels = label2score_labels - example_labels
        unexpected_labels = example_labels - label2score_labels
        return {
            "missing_labels": list(missing_labels),
            "unexpected_labels": list(unexpected_labels),
        }


@dataclass
class RaterClassificationConfig(RaterConfig):
    """Rater classification Config Class."""

    flow_name: str = "RaterClassificationFlow"
    model_config: ModelConfig = OpenAIModelConfig()
    label2score: Dict[str, float] = field(default_factory=lambda: {"Yes": 1.0, "No": 0.0})
    guided_prompt_template: GuidedPrompt = GuidedPrompt(
        instruction="""Rate the answer based on the question and the context.
        Follow the format of the examples below to include context, question, answer, and label in the response.
        The response should not include examples in the prompt.""",
        examples=[
            Context(
                context="The Eiffel Tower, located in Paris, France, is one of the most famous landmarks in the world. It was constructed in 1889 and stands at a height of 324 meters.",
                question="When was the Eiffel Tower constructed?",
                answer="The Eiffel Tower was constructed in 1889.",
                explanation="The context explicitly mentions that the Eiffel Tower was constructed in 1889, so the answer is correct.",
                label="Yes",
            ),
            Context(
                context="Photosynthesis is a process used by plants to convert light energy into chemical energy. This process primarily occurs in the chloroplasts of plant cells.",
                question="Where does photosynthesis primarily occur in plant cells?",
                answer="Photosynthesis primarily occurs in the mitochondria of plant cells.",
                explanation="The context mentions that photosynthesis primarily occurs in the chloroplasts of plant cells, so the answer is incorrect.",
                label="No",
            ),
        ],
    )


@dataclass
class RaterForGeneratedAnswerConfig(RaterConfig):
    """Rater classification Config Class."""

    flow_name: str = "RaterForGeneratedAnswerFlow"
    model_config: ModelConfig = OpenAIModelConfig()
    label2score: Dict[str, float] = field(
        default_factory=lambda: {
            "Strong accept": 2.0,
            "Accept": 1.0,
            "Equivalent": 0.0,
            "Reject": -1.0,
            "Strong reject": -2.0,
        }
    )
    # NOTE: This flow seems very sensitive to the choice of prompt.
    # For a more stable performance, prompt should be improved.
    guided_prompt_template: GuidedPrompt = GuidedPrompt(
        instruction="""Rate the generated answer compared to the grounding answer to the question. Accept means the generated answer is better than the grounding answer and reject means worse.
        Follow the format of the examples below to include context, question, grounding answer, generated answer and label in the response.
        The response should not include examples in the prompt.""",
        examples=[
            Context(
                context="Basic operating system features were developed in the 1950s, and more complex functions were introduced in the 1960s.",
                question="When were basic operating system features developed?",
                grounding_answer="In the 1960s, people developed some basic operating system functions.",
                generated_answer="Basic operating system features were developed in the 1950s.",
                explanation="The generated answer is much better because it correctly identifies the 1950s as the time when basic operating system features were developed",
                label="Strong accept",
            ),
            Context(
                context="Early computers were built to perform a series of single tasks, like a calculator. Basic operating system could automatically run different programs in succession to speed up processing.",
                question="Did early computers function like modern calculators?",
                grounding_answer="No. Early computers were used primarily for complex calculating.",
                generated_answer="Yes. Early computers were built to perform a series of single tasks, similar to a calculator.",
                explanation="The generated answer is better as it correctly captures the essence of the early computers' functionality, which was to perform single tasks akin to calculators.",
                label="Accept",
            ),
            Context(
                context="Operating systems did not exist in their modern and more complex forms until the early 1960s. Hardware features were added, that enabled use of runtime libraries, interrupts, and parallel processing.",
                question="When did operating systems start to resemble their modern forms?",
                grounding_answer="Operating systems started to resemble their modern forms in the early 1960s.",
                generated_answer="Modern and more complex forms of operating systems began to emerge in the early 1960s.",
                explanation="Both answers are equally good as they accurately pinpoint the early 1960s as the period when modern operating systems began to develop.",
                label="Equivalent",
            ),
            Context(
                context="Operating systems did not exist in their modern and more complex forms until the early 1960s. Hardware features were added, that enabled use of runtime libraries, interrupts, and parallel processing.",
                question="What features were added to hardware in the 1960s?",
                grounding_answer="Hardware in the 1960s saw the addition of features like runtime libraries and parallel processing.",
                generated_answer="The 1960s saw the addition of input output control and compatible timesharing capabilities in hardware.",
                explanation="The generated answer is worse because it inaccurately suggests the addition of capabilities of hardware in 1960s which is not supported by the context.",
                label="Reject",
            ),
            Context(
                context="Operating systems did not exist in their modern and more complex forms until the early 1960s. When personal computers became popular in the 1980s, operating systems were made for them similar in concept to those used on larger computers.",
                question="When did operating systems in personal computer were similar to those used on larger computers?",
                grounding_answer="In 1980s, as personal computers became popular.",
                generated_answer="In the early 1960s, as operating system became more complex.",
                explanation="The generated answer is much worse as it incorrectly states the early 1960s as the period of popularity for personal computers, contradicting the context which indicates the 1980s.",
                label="Strong reject",
            ),
        ],
    )


###########################################################
#                    Pipeline Config                      #
###########################################################
@dataclass
class PipelineConfig:
    """MultiFlowsPipeline Config Class."""

    extract_config: ExtractConfig
    transform_config: TransformConfig
