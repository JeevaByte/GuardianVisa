import logging
import os
from typing import Optional

log = logging.getLogger(__name__)


def is_vertex_ai():
    """Returns True if Vertex AI should be used, False if Gemini API key."""
    return bool(os.getenv("GCP_PROJECT_ID")) and not bool(os.getenv("GOOGLE_API_KEY"))


def _get_model_name():
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# ---------------------------------------------------------------------------
# Model factory – returns an object compatible with start_chat / send_message
# ---------------------------------------------------------------------------

def get_model(model_name=None, tools=None, system_instruction=None):
    if model_name is None:
        model_name = _get_model_name()
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return _GoogleGenAIModel(model_name, api_key, tools=tools, system_instruction=system_instruction)
    import vertexai
    vertexai.init(
        project=os.getenv("GCP_PROJECT_ID"),
        location=os.getenv("GCP_LOCATION", "us-central1"),
    )
    from vertexai.generative_models import GenerativeModel
    return GenerativeModel(model_name, tools=tools or [], system_instruction=system_instruction)


def start_chat(model):
    return model.start_chat()


def send_message(chat, content, generation_config=None):
    kwargs = {}
    if generation_config is not None:
        kwargs["generation_config"] = generation_config
    return chat.send_message(content, **kwargs)


def make_generation_config(**kwargs):
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        from google.genai import types
        return types.GenerateContentConfig(**kwargs)
    from vertexai.generative_models import GenerationConfig
    return GenerationConfig(**kwargs)


def make_function_response_part(name, response):
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        from google.genai import types
        return types.Part(function_response=types.FunctionResponse(
            name=name, response=response,
        ))
    from vertexai.generative_models import Part
    return Part.from_function_response(name=name, response=response)


def extract_function_call(response):
    try:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    args = dict(fc.args) if fc.args else {}
                    args = _proto_to_dict(args)
                    return {"name": fc.name, "args": args}
    except Exception as exc:
        log.debug("Could not extract function call: %s", exc)
    return None


def extract_text(response):
    try:
        parts = []
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    parts.append(part.text)
        return "".join(parts) if parts else None
    except Exception as exc:
        log.debug("Could not extract text: %s", exc)
    return None


def generate_content(model, prompt, generation_config=None):
    kwargs = {}
    if generation_config is not None:
        kwargs["generation_config"] = generation_config
    return model.generate_content(prompt, **kwargs)


def _proto_to_dict(value):
    if hasattr(value, "items"):
        return {k: _proto_to_dict(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_proto_to_dict(v) for v in value]
    return value


# ---------------------------------------------------------------------------
# Google Gen AI wrapper – mimics Vertex AI model / chat interface
# ---------------------------------------------------------------------------

class _GoogleGenAIModel:
    """Wraps google.genai.Client so it looks like a Vertex AI GenerativeModel."""

    def __init__(self, model_name: str, api_key: str, tools=None, system_instruction=None):
        from google import genai
        self._model_name = model_name
        self._client = genai.Client(api_key=api_key)
        self._tools = tools or []
        self._system_instruction = system_instruction

    def start_chat(self):
        from google.genai import types
        config_kw = {}
        if self._system_instruction:
            config_kw["system_instruction"] = self._system_instruction
        if self._tools:
            config_kw["tools"] = self._tools
        config = types.GenerateContentConfig(**config_kw) if config_kw else None
        chat = self._client.chats.create(
            model=self._model_name,
            config=config,
        )
        return _GoogleGenAIChat(chat, self._model_name, self._client, tools=self._tools)

    def generate_content(self, prompt, generation_config=None):
        kwargs = dict(model=self._model_name, contents=prompt)
        if generation_config is not None:
            kwargs["config"] = generation_config
        return self._client.models.generate_content(**kwargs)


class _GoogleGenAIChat:
    """Wraps google.genai.ChatSession so it looks like a Vertex AI chat."""

    def __init__(self, chat_session, model_name: str, client, tools=None):
        self._chat = chat_session
        self._model_name = model_name
        self._client = client
        self._tools = tools

    def send_message(self, content, generation_config=None):
        return self._chat.send_message(content)
