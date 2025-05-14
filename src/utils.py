"""utils module."""

from typing import Optional

from haystack import Pipeline
from haystack.components.generators import HuggingFaceLocalGenerator
from haystack.utils import Secret

from transformers import AutoTokenizer


def chunk_text(text, model_name: str, max_tokens=256):
    """Split text into chunks of max_tokens."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokens = tokenizer.encode(text)
    chunks = [tokens[i : i + max_tokens] for i in range(0, len(tokens), max_tokens)]

    return [tokenizer.decode(chunk) for chunk in chunks]


def build_translate_pipeline(model_name: str, token: Optional[str] = None) -> Pipeline:
    """Build translation pipeline."""
    hf_token = (
        Secret.from_token(token) if token else Secret.from_env_var("HF_API_TOKEN")
    )
    generator = HuggingFaceLocalGenerator(
        model_name,
        task="text2text-generation",
        token=hf_token,
        generation_kwargs={
            "max_new_tokens": 500,
        },
    )
    generator.warm_up()
    pipeline = Pipeline()
    pipeline.add_component("translater", generator)

    return pipeline
