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


def reasoning_carry(provider: str) -> str:
    """How a provider keeps the model's thinking across turns.

    "server_side": the chain holds it, so nothing about it appears in the
    request and a per-turn count of replayed reasoning blocks is meaningless.
    "replayed": it rides in the conversation we resend, so the count is real
    and a zero there would mean the thinking was dropped.

    Recorded on every trial so a reader can tell an inapplicable field from a
    missing one without knowing which provider does which.
    """
    return "server_side" if uses_response_chaining(provider) else "replayed"


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
            max_retries=_MAX_RETRIES,
        )
    return OpenAI(api_key=api_key, max_retries=_MAX_RETRIES)


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


# The upstream to pin per model-id prefix. Most vendors serve their own models
# under a name close to the prefix, but that is a convention rather than a rule:
# Google's endpoint is "google-ai-studio", and DeepSeek's own endpoint is listed
# yet not routable on this account, so its models are served by third parties.
# A wrong name is not a silent fallback -- OpenRouter answers 404 "no endpoints
# found" -- so the mapping is checked rather than guessed.
_UPSTREAM_PROVIDER = {
    "google": "google-ai-studio",
    "anthropic": "anthropic",
    "openai": "openai",
    # DeepSeek publishes ~19 upstreams and the first-party one 404s here.
    # Relace, DeepInfra, Together, Novita and Fireworks all pin cleanly, but
    # they are not interchangeable: they differ in how much the model thinks
    # (1,080 vs 3,000 reasoning tokens on the same first turn), so a run wants
    # one of them throughout and the record says which. DeepInfra over Relace
    # because Relace throttles hardest on the shared free pool -- it answered a
    # burst at 7.4s a call against DeepInfra's 2.1s, and 429'd a real run
    # outright.
    "deepseek": "DeepInfra",
    "moonshotai": "Moonshot AI",
    "x-ai": "xAI",
    # Inkling has no first-party endpoint at all: DeepInfra, BaseTen and Together
    # serve it.
    "thinkingmachines": "DeepInfra",
}

# Whether the pinned upstream is the model vendor's own endpoint. It is not a
# routing concern -- every pin above is verified to route -- but a result served
# by a third party is a different provenance claim than one served by the vendor,
# and that belongs in the write-up rather than in someone's memory.
FIRST_PARTY_UPSTREAM = {
    "anthropic": True,
    "google": True,
    "openai": True,
    "x-ai": True,
    "moonshotai": True,
    "deepseek": False,        # DeepSeek's own endpoint is listed but 404s here
    "thinkingmachines": False,  # no first-party endpoint exists
}


def upstream_is_first_party(model: str) -> bool:
    """Whether the pinned upstream for *model* is the vendor's own endpoint."""
    vendor = model.split("/", 1)[0] if "/" in model else model
    return bool(FIRST_PARTY_UPSTREAM.get(vendor, False))


# Pinning matters more the more upstreams a model has: unpinned, successive
# trials of one experiment can be answered by different serving stacks with
# different quantisation and different reasoning handling.
ROUTING_OVERRIDE_ENV = "ACTIVEARC_UPSTREAM"

# A shared upstream pool throttles in bursts, and a 429 that the SDK gives up on
# becomes an error record for a task that was fine -- the run then has holes that
# only a second pass fills. The SDK default is 2 tries; this rides out a longer
# squeeze, with the SDK's own exponential backoff between attempts.
_MAX_RETRIES = int(os.environ.get("ACTIVEARC_MAX_RETRIES", "8"))


def responses_extras(
    provider: str, model: str, reasoning_effort: Optional[str]
) -> Dict[str, Any]:
    """The per-request extras a Responses call needs: thinking budget and pin.

    Every loop used to spell the reasoning block out inline and none of them
    sent a provider order, so an OpenRouter run was pinned in the chat arm and
    unpinned everywhere else -- the static and teacher arms could be served by a
    different upstream on every trial. Both belong to the same decision, so they
    are built in one place.
    """
    extras: Dict[str, Any] = {}
    if reasoning_effort is not None:
        extras["reasoning"] = {"effort": reasoning_effort}
    if provider == PROVIDER_OPENROUTER:
        extras["extra_body"] = {"provider": provider_routing(model)}
    return extras


def provider_routing(model: str) -> Dict[str, Any]:
    """Pin the serving provider for an OpenRouter model.

    OpenRouter load-balances across several upstreams by default, so successive
    trials of the same experiment could be answered by different serving stacks
    with different reasoning-serialization behaviour. An experiment wants one
    known upstream, and no silent fallback to another.
    """
    override = os.environ.get(ROUTING_OVERRIDE_ENV)
    if override:
        return {"order": [override], "allow_fallbacks": False}
    vendor = model.split("/", 1)[0] if "/" in model else model
    upstream = _UPSTREAM_PROVIDER.get(vendor)
    if upstream is None:
        raise RuntimeError(
            f"No upstream pin known for {model!r}. Add its provider to "
            f"_UPSTREAM_PROVIDER, or set {ROUTING_OVERRIDE_ENV}. Guessing the "
            "name gives a 404, and running unpinned lets different trials be "
            "answered by different serving stacks."
        )
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
        self.provider = provider
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
        other.provider = self.provider
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
