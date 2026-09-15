"""Serialize OpenAI Responses API objects for trial transcripts."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def _to_plain(obj: Any) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {str(k): _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain(v) for v in obj]
    if hasattr(obj, "model_dump"):
        try:
            return _to_plain(obj.model_dump())
        except Exception:
            pass
    out: Dict[str, Any] = {}
    for key in (
        "id",
        "object",
        "created_at",
        "status",
        "model",
        "error",
        "incomplete_details",
        "usage",
        "output_text",
    ):
        if hasattr(obj, key):
            val = getattr(obj, key)
            if val is not None:
                out[key] = _to_plain(val)
    return out if out else str(obj)


def _output_item_summary(item: Any) -> Dict[str, Any]:
    if isinstance(item, dict):
        typ = str(item.get("type", ""))
        if typ == "function_call":
            return {
                "type": typ,
                "call_id": item.get("call_id"),
                "name": item.get("name"),
                "arguments": item.get("arguments"),
            }
        if typ == "message":
            blocks: List[Dict[str, Any]] = []
            for block in item.get("content") or []:
                if isinstance(block, dict):
                    blocks.append(
                        {
                            "type": block.get("type"),
                            "text": block.get("text"),
                        }
                    )
            return {"type": typ, "content": blocks}
        if typ == "reasoning":
            summary = item.get("summary")
            if summary is not None:
                return {"type": typ, "summary": _to_plain(summary)}
        return {"type": typ or "unknown", "raw": _to_plain(item)}
    typ = str(getattr(item, "type", ""))
    if typ == "function_call":
        return {
            "type": typ,
            "call_id": getattr(item, "call_id", None),
            "name": getattr(item, "name", None),
            "arguments": getattr(item, "arguments", None),
        }
    if typ == "message":
        blocks = []
        for block in getattr(item, "content", []) or []:
            blocks.append(
                {
                    "type": getattr(block, "type", None),
                    "text": getattr(block, "text", None),
                }
            )
        return {"type": typ, "content": blocks}
    if typ == "reasoning":
        return {"type": typ, "summary": _to_plain(getattr(item, "summary", None))}
    return {"type": typ or "unknown"}


def summarize_response(response: Any) -> Dict[str, Any]:
    """Compact per-turn log: ids, status, usage, and structured output items."""
    summary = _to_plain(response)
    output = getattr(response, "output", None) or []
    summary["output_items"] = [_output_item_summary(item) for item in output]
    return summary


def usage_totals(turns: List[Dict[str, Any]]) -> Dict[str, int]:
    totals: Dict[str, Any] = {
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "total_tokens": 0,
    }
    cost = 0.0
    saw_cost = False
    for turn in turns:
        response = turn.get("response") or {}
        usage = response.get("usage") if isinstance(response, dict) else None
        if usage is None:
            usage = turn.get("usage")
        if not usage:
            continue
        if not isinstance(usage, dict):
            usage = _to_plain(usage)
        totals["input_tokens"] += int(usage.get("input_tokens") or 0)
        totals["output_tokens"] += int(usage.get("output_tokens") or 0)
        totals["total_tokens"] += int(usage.get("total_tokens") or 0)
        in_det = usage.get("input_tokens_details") or {}
        out_det = usage.get("output_tokens_details") or {}
        if isinstance(in_det, dict):
            totals["cached_input_tokens"] += int(in_det.get("cached_tokens") or 0)
        if isinstance(out_det, dict):
            totals["reasoning_tokens"] += int(out_det.get("reasoning_tokens") or 0)
        if usage.get("cost") is not None:
            cost += float(usage.get("cost") or 0.0)
            saw_cost = True
    if saw_cost:
        totals["cost"] = round(cost, 6)
    return totals


def chat_usage_to_responses_shape(usage: Any) -> Optional[Dict[str, Any]]:
    """Rename Chat Completions usage fields to the Responses API's spelling.

    ``usage_totals`` reads Responses-shaped keys. Chat Completions (and so every
    model reached through OpenRouter) reports ``prompt_tokens`` /
    ``completion_tokens`` instead, which would otherwise total to zero and make
    non-OpenAI runs look free.
    """
    if usage is None:
        return None
    if not isinstance(usage, dict):
        usage = _to_plain(usage)
    if not isinstance(usage, dict):
        return None
    prompt_details = usage.get("prompt_tokens_details") or {}
    completion_details = usage.get("completion_tokens_details") or {}
    shaped: Dict[str, Any] = {
        "input_tokens": usage.get("prompt_tokens") or 0,
        "output_tokens": usage.get("completion_tokens") or 0,
        "total_tokens": usage.get("total_tokens") or 0,
    }
    if isinstance(prompt_details, dict):
        shaped["input_tokens_details"] = {
            "cached_tokens": prompt_details.get("cached_tokens") or 0
        }
    if isinstance(completion_details, dict):
        shaped["output_tokens_details"] = {
            "reasoning_tokens": completion_details.get("reasoning_tokens") or 0
        }
    # OpenRouter reports billed cost per call; keep it for compute reporting.
    if usage.get("cost") is not None:
        shaped["cost"] = usage.get("cost")
    return shaped
