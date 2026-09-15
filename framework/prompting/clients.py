"""Provider resolution for the OpenAI-compatible clients ActiveARC talks to.

Every model reaches ActiveARC through an OpenAI-shaped API. Native OpenAI
models use the Responses API; Anthropic and Google models are reached through
OpenRouter, which speaks Chat Completions only. Keeping that asymmetry in one
place means the trial loops and the batch runners never branch on vendor.

Provider is resolved in this order: an explicit argument, then
``ACTIVEARC_PROVIDER``, then the shape of the model id (OpenRouter ids are
``vendor/model``), then OpenAI.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

from framework.prompting.active_arc_tools import DEFAULT_OPENAI_MODEL

PROVIDER_OPENAI = "openai"
PROVIDER_OPENROUTER = "openrouter"
PROVIDERS = (PROVIDER_OPENAI, PROVIDER_OPENROUTER)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_API_KEY_ENV = {
    PROVIDER_OPENAI: "OPENAI_API_KEY",
    PROVIDER_OPENROUTER: "OPENROUTER_API_KEY",
}

_MODEL_ENV = {
    PROVIDER_OPENAI: "OPENAI_MODEL",
    PROVIDER_OPENROUTER: "OPENROUTER_MODEL",
}

# Sent for OpenRouter attribution; ignored by other providers.
_OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://github.com/ClaasBeger/ActiveARC",
    "X-Title": "ActiveARC",
}


def infer_provider(model: Optional[str]) -> Optional[str]:
    """OpenRouter model ids are ``vendor/model``; a bare id is OpenAI's."""
    if model and "/" in model:
        return PROVIDER_OPENROUTER
    return None


def resolve_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> str:
    candidate = provider or os.environ.get("ACTIVEARC_PROVIDER") or infer_provider(model)
    resolved = (candidate or PROVIDER_OPENAI).lower()
    if resolved not in PROVIDERS:
        raise ValueError(
            f"Unknown provider {resolved!r}; expected one of {', '.join(PROVIDERS)}."
        )
    return resolved


def resolve_model(provider: str, model: Optional[str] = None) -> str:
    explicit = model or os.environ.get(_MODEL_ENV[provider])
    if explicit:
        return explicit
    if provider == PROVIDER_OPENAI:
        return DEFAULT_OPENAI_MODEL
    raise RuntimeError(
        "OpenRouter has no default model: pass --model (e.g. "
        "anthropic/claude-sonnet-4.5) or set OPENROUTER_MODEL."
    )


def supports_responses_api(provider: str) -> bool:
    """Both providers serve /responses, including function calling."""
    return provider in PROVIDERS


def uses_response_chaining(provider: str) -> bool:
    """Whether the provider keeps conversation state server-side.

    OpenAI threads a multi-turn Responses conversation with
    ``previous_response_id``. OpenRouter's Responses endpoint rejects that
    field (400 invalid_prompt) because it holds no state, but it does accept
    the whole conversation replayed in ``input`` -- function_call and
    function_call_output items included. Callers that honour this flag keep one
    code path for both.
    """
    return provider == PROVIDER_OPENAI


def resolve_store(provider: str, store: bool) -> bool:
    """Whether the provider will keep the response.

    OpenRouter stores nothing and rejects ``store=true`` outright
    (400 invalid_prompt, "expected false"), so the request is sent unstored
    regardless of what the caller asked for.
    """
    return store and uses_response_chaining(provider)


def resolve_backend(provider: str, backend: str) -> Tuple[str, Optional[str]]:
    """Return the backend actually usable for *provider*, plus a note if changed."""
    if backend == "responses" and not supports_responses_api(provider):
        return "chat", (
            f"{provider} does not implement the Responses API; "
            "falling back to the chat backend."
        )
    return backend, None


def build_client(provider: str) -> Any:
    try:
        from openai import OpenAI
    except ImportError as e:  # pragma: no cover - dependency guard
        raise ImportError("Install the OpenAI SDK: pip install openai") from e

    env_name = _API_KEY_ENV[provider]
    api_key = os.environ.get(env_name)
    if not api_key:
        raise RuntimeError(f"Set {env_name} in the environment.")

    if provider == PROVIDER_OPENROUTER:
        return OpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            default_headers=_OPENROUTER_HEADERS,
        )
    return OpenAI(api_key=api_key)


def reasoning_extra_body(
    provider: str,
    reasoning_effort: Optional[str],
) -> Dict[str, Any]:
    """Chat-backend reasoning controls.

    The Responses API takes ``reasoning`` as a first-class argument; over
    OpenRouter the equivalent rides in the request body, so a reasoning effort
    set on the command line reaches Anthropic and Google models too instead of
    being silently dropped.
    """
    if provider != PROVIDER_OPENROUTER:
        return {}
    if not reasoning_effort or reasoning_effort == "none":
        return {}
    return {"reasoning": {"effort": reasoning_effort}}


class ResponsesConversation:
    """Threads a multi-turn Responses conversation for either provider.

    On OpenAI each request sends only what is new and points at the previous
    response. On OpenRouter there is no server-side state, so the whole
    conversation -- the model's own function_call items included -- is replayed
    in ``input`` every turn. Loops drive this the same way for both: read
    ``create_kwargs()``, then ``record_turn()`` with what came back, then
    ``extend()`` with the tool outputs to send next.
    """

    def __init__(self, provider: str, opening: list) -> None:
        self.chaining = uses_response_chaining(provider)
        self._convo: list = list(opening)
        self._pending: list = list(opening)
        self._previous_response_id: Optional[str] = None

    def create_kwargs(self) -> Dict[str, Any]:
        if self.chaining:
            kwargs: Dict[str, Any] = {"input": self._pending}
            if self._previous_response_id is not None:
                kwargs["previous_response_id"] = self._previous_response_id
            return kwargs
        return {"input": self._convo}

    def record_turn(
        self,
        response: Any,
        calls: list,
        assistant_text: Optional[str] = None,
    ) -> None:
        """Take in the model's output. *calls* are (call_id, name, arguments)."""
        if self.chaining:
            self._previous_response_id = getattr(response, "id", None)
            return
        if assistant_text and not calls:
            self._convo.append({"role": "assistant", "content": assistant_text})
        for call_id, name, arguments in calls:
            self._convo.append(
                {
                    "type": "function_call",
                    "call_id": call_id,
                    "name": name,
                    "arguments": arguments,
                }
            )

    def extend(self, items: list) -> None:
        """Queue what to send next (tool outputs, or a protocol reminder)."""
        if self.chaining:
            self._pending = list(items)
        else:
            self._convo.extend(items)


def resolve_target(
    *,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    backend: Optional[str] = None,
) -> Dict[str, Any]:
    """One-shot resolution used by the batch runners before a run starts."""
    resolved_provider = resolve_provider(provider, model)
    resolved_model = resolve_model(resolved_provider, model)
    info: Dict[str, Any] = {
        "provider": resolved_provider,
        "model": resolved_model,
        "backend": backend,
        "backend_note": None,
    }
    if backend is not None:
        info["backend"], info["backend_note"] = resolve_backend(
            resolved_provider, backend
        )
    return info
