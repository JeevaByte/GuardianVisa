"""
tool_dispatcher.py – Routes Vertex AI function calls to Python handlers.

Public API:
    dispatch_tool_call(function_name, function_args) -> dict
        Calls the matching handler and returns its result dict.

    run_agent_turn(prompt, student_id=None) -> AgentTurnResult
        Runs a full agentic loop with the GuardianVisa model:
          1. Sends the prompt to Gemini.
          2. If Gemini requests a tool call, dispatches it via dispatch_tool_call.
          3. Sends the tool result back to Gemini as a function response.
          4. Repeats until Gemini returns a plain text response (max 5 iterations).
        Returns the final text response and the list of tool calls made.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from tools import (
    handle_check_visa_hours,
    handle_draft_safe_response,
    handle_get_emergency_resources,
    handle_get_student_profile,
    handle_scan_scam_signals,
)

log = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 5  # Guard against infinite agentic loops


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class ToolCallRecord:
    """Stores one tool invocation for frontend reasoning-step display."""
    name: str
    args: dict
    result: dict


@dataclass
class AgentTurnResult:
    """Returned by run_agent_turn; carries both the answer and the reasoning trace."""
    final_text: Optional[str]       # Raw JSON string from Gemini
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    used_mock: bool = False         # True when Vertex AI was unavailable


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

async def dispatch_tool_call(function_name: str, function_args: dict) -> dict:
    """
    Routes a Vertex AI function call to the correct Python handler.

    Raises ValueError for unknown tool names so the caller can surface the
    error gracefully rather than silently returning empty data.
    """
    handlers = {
        "get_student_profile":    handle_get_student_profile,
        "check_visa_hours":       handle_check_visa_hours,
        "scan_scam_signals":      handle_scan_scam_signals,
        "get_emergency_resources": handle_get_emergency_resources,
        "draft_safe_response":    handle_draft_safe_response,
    }

    handler = handlers.get(function_name)
    if not handler:
        raise ValueError(
            f"Unknown tool '{function_name}'. "
            f"Available tools: {list(handlers.keys())}"
        )

    return await handler(**function_args)


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------

async def run_agent_turn(
    prompt: str,
    student_id: Optional[str] = None,
) -> AgentTurnResult:
    """
    Execute one full agent turn:
      1. Initialise the GuardianVisa GenerativeModel.
      2. Send *prompt* to Gemini.
      3. If Gemini issues a function call, dispatch it and return the result.
      4. Loop (max MAX_TOOL_ITERATIONS) until Gemini produces a text response.
      5. Return the final text + every tool call made (for frontend display).

    Falls back gracefully when Vertex AI is unavailable (GCP not configured).
    """
    tool_calls: list[ToolCallRecord] = []

    # Attempt to get the configured model.
    try:
        from agent_config import get_agent_model  # noqa: PLC0415
        model = get_agent_model()
    except Exception as exc:
        log.warning("Could not load agent model: %s", exc)
        model = None

    if model is None:
        # LLM unavailable – signal the caller to use mock data.
        return AgentTurnResult(final_text=None, tool_calls=[], used_mock=True)

    try:
        import llm  # noqa: PLC0415

        generation_config = llm.make_generation_config(
            temperature=0.2,
            max_output_tokens=1500,
        )

        # Start a multi-turn chat session so we can inject tool results.
        chat = llm.start_chat(model)

        # Optionally prime the context with the student's profile if we have
        # the ID but the caller hasn't explicitly asked for it in the prompt.
        initial_message = prompt
        if student_id and "student_id" not in prompt.lower():
            initial_message = f"[Student ID: {student_id}]\n\n{prompt}"

        response = llm.send_message(
            chat, initial_message,
            generation_config=generation_config,
        )

        for iteration in range(MAX_TOOL_ITERATIONS):
            # Check if Gemini has requested a function call.
            fn_call = llm.extract_function_call(response)

            if fn_call is None:
                # No function call – Gemini returned a final text response.
                break

            name = fn_call["name"]
            args = fn_call["args"]

            print(f"🔧 Tool called: {name}({json.dumps(args, ensure_ascii=False)})")

            # Execute the tool.
            try:
                result = await dispatch_tool_call(name, args)
            except Exception as exc:
                log.warning("Tool %s raised an error: %s", name, exc)
                result = {"error": str(exc)}

            # Record for reasoning-step display.
            tool_calls.append(ToolCallRecord(name=name, args=args, result=result))

            # Send the function result back to Gemini.
            response = llm.send_message(
                chat,
                llm.make_function_response_part(name=name, response=result),
                generation_config=generation_config,
            )

        # Extract the final text from the last response.
        final_text = llm.extract_text(response)

        if iteration == MAX_TOOL_ITERATIONS - 1 and llm.extract_function_call(response):
            log.warning(
                "Agent loop hit MAX_TOOL_ITERATIONS (%d) without resolving.",
                MAX_TOOL_ITERATIONS,
            )

        return AgentTurnResult(
            final_text=final_text,
            tool_calls=tool_calls,
            used_mock=False,
        )

    except Exception as exc:
        log.warning("Agent turn failed: %s", exc)
        return AgentTurnResult(final_text=None, tool_calls=tool_calls, used_mock=True)


# ---------------------------------------------------------------------------
# LLM response helpers (delegated to llm.py)
# ---------------------------------------------------------------------------

# _extract_function_call, _extract_text, _proto_to_dict are now in llm.py
