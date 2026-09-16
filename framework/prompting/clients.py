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
    """Return the backend to use for *provider*, plus a note if it was changed.

    OpenRouter serves both surfaces, but only chat completions carries
    reasoning_details -- the documented way to hand a model back its own signed
    thinking. Its Responses translation exposes reasoning items that have to be
    reassembled by hand, and Gemini rejects the result intermittently with
    "Corrupted thought signature". So OpenRouter is routed to chat regardless of
    what was asked for, and OpenAI keeps Responses, where previous_response_id
    already keeps reasoning server-side.
    """
    if backend == "responses" and provider == PROVIDER_OPENROUTER:
        return "chat", (
            "OpenRouter carries signed reasoning only on chat completions "
            "(reasoning_details); using the chat backend."
        )
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


# OpenRouter's id for the vendor's own first-party endpoint, where the id prefix
# is not already it.
_UPSTREAM_PROVIDER = {"google": "google-ai-studio"}


def provider_routing(model: str) -> Dict[str, Any]:
    """Pin the serving provider for an OpenRouter model.

    OpenRouter load-balances across several upstreams by default, so successive
    trials of the same experiment could be answered by different serving stacks
    with different reasoning-serialization behaviour. An experiment wants one
    known upstream, and no silent fallback to another.
    """
    vendor = model.split("/", 1)[0] if "/" in model else model
    upstream = _UPSTREAM_PROVIDER.get(vendor, vendor)
    return {"order": [upstream], "allow_fallbacks": False}


def cache_control_block(text: str) -> Dict[str, Any]:
    """A prompt-cache breakpoint for the stable prefix of a chat conversation.

    Reads of a cached prefix cost about a tenth of a fresh one, which matters
    because a replayed conversation resends its whole history every turn. The
    first call pays a write premium, so this only pays off in a trial that takes
    more than one turn.
    """
    return {"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}


def _item_dict(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        return item
    if hasattr(item, "model_dump"):
        try:
            return item.model_dump()
        except Exception:  # pragma: no cover - defensive
            pass
    return {}


def _item_type(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("type", ""))
    return str(getattr(item, "type", ""))


# Carried back verbatim; ``status`` is output-only and the request schema rejects it.
_REASONING_REPLAY_FIELDS = (
    "type", "id", "summary", "content", "encrypted_content", "signature", "format",
)


def _replayable_reasoning(item: Any) -> Optional[Dict[str, Any]]:
    """A reasoning item stripped to the fields the request schema accepts.

    Anthropic returns the thinking as ``content`` plus a ``signature``; Gemini
    and OpenAI return ``encrypted_content``. Either way it is opaque to us and
    is passed straight back so the next turn continues the same reasoning.
    """
    d = _item_dict(item)
    if not d:
        return None
    out = {k: d[k] for k in _REASONING_REPLAY_FIELDS if d.get(k) is not None}
    return out or None


class ResponsesConversation:
    """Threads a multi-turn Responses conversation for either provider.

    On OpenAI each request sends only what is new and points at the previous
    response. On OpenRouter there is no server-side state, so the whole
    conversation -- the model's own function_call items included -- is replayed
    in ``input`` every turn. Loops drive this the same way for both: read
    ``create_kwargs()``, then ``record_turn()`` with what came back, then
    ``extend()`` with the tool outputs to send next.
    """

    # Gemini rejects a replayed conversation carrying reasoning from several
    # turns at once ("Corrupted thought signature"): its thought signatures go
    # stale behind the newest one. Keeping a window of the most recent reasoning
    # item preserves turn-to-turn continuity without accumulating dead
    # signatures. None means keep every one, which the other providers accept.
    _REASONING_WINDOW = {PROVIDER_OPENROUTER: 1}

    def __init__(self, provider: str, opening: list) -> None:
        self.chaining = uses_response_chaining(provider)
        self._convo: list = list(opening)
        self._pending: list = list(opening)
        self._previous_response_id: Optional[str] = None
        self._reasoning_window = self._REASONING_WINDOW.get(provider)
        override = os.environ.get("ACTIVEARC_REASONING_WINDOW")
        if override:
            low = override.strip().lower()
            self._reasoning_window = (
                None if low == "all" else 0 if low == "none" else int(low)
            )

    def _trim_reasoning(self, keep: int) -> None:
        """Drop all but the newest *keep* reasoning items already in the replay."""
        idx = [i for i, it in enumerate(self._convo)
               if isinstance(it, dict) and it.get("type") == "reasoning"]
        for i in reversed(idx[:max(0, len(idx) - keep)]):
            del self._convo[i]

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
        """Take in the model's output. *calls* are (call_id, name, arguments).

        Without chaining every output item has to be replayed, reasoning items
        included. Dropping those would discard the model's thinking at each turn
        and leave a replayed conversation strictly worse than a chained one --
        the model would rediscover its own reasoning from its tool calls alone.
        """
        if self.chaining:
            self._previous_response_id = getattr(response, "id", None)
            return

        replayed_calls = False
        for item in (getattr(response, "output", None) or []):
            kind = _item_type(item)
            if kind == "reasoning":
                sanitized = _replayable_reasoning(item)
                if sanitized is not None:
                    if self._reasoning_window is not None:
                        self._trim_reasoning(self._reasoning_window - 1)
                    self._convo.append(sanitized)
            elif kind == "function_call":
                d = _item_dict(item)
                self._convo.append(
                    {
                        "type": "function_call",
                        "call_id": d.get("call_id"),
                        "name": d.get("name"),
                        "arguments": d.get("arguments"),
                    }
                )
                replayed_calls = True

        if not replayed_calls and calls:
            # Caller parsed calls we did not find on the response object.
            for call_id, name, arguments in calls:
                self._convo.append(
                    {
                        "type": "function_call",
                        "call_id": call_id,
                        "name": name,
                        "arguments": arguments,
                    }
                )
            replayed_calls = True

        if assistant_text and not replayed_calls:
            self._convo.append({"role": "assistant", "content": assistant_text})

    def fork(self) -> "ResponsesConversation":
        """A branch that carries this conversation's history but not its future.

        The test phase asks about each held-out item on its own branch, so every
        item is answered with the whole exploration behind it -- queries and the
        reasoning across them -- while no item can see another one's grid or
        answer. Chaining forks share the same previous_response_id, which is what
        makes the server-side branch; replayed conversations copy the list.
        """
        other = object.__new__(ResponsesConversation)
        other.chaining = self.chaining
        other._convo = list(self._convo)
        other._pending = list(self._pending)
        other._previous_response_id = self._previous_response_id
        other._reasoning_window = self._reasoning_window
        return other

    def append(self, items: list) -> None:
        """Add to what is already queued, rather than replacing it.

        ``extend`` sets the next request's payload, which is what a normal turn
        wants. A branch instead adds its own prompt on top of a payload that is
        already queued -- the tool output closing the turn it forked from --
        and replacing that would leave a function call unanswered.
        """
        if self.chaining:
            self._pending = list(self._pending) + list(items)
        else:
            self._convo.extend(items)

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
