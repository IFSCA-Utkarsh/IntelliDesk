from chat.state_manager import (
    append_history,
    update_flow_step,
    update_flow_data,
    delete_flow,
)
from llm.portal_llm import run_portal_llm
from llm.ticket_llm import run_ticket_llm
from engines.meeting_engine import execute_meeting
from audit.logger import log_event


def route_new_message(flow: dict, request_id: str):
    flow_type = flow["type"]
    user_id = flow["user_id"]

    # ---------------- MEETING / EQUIPMENT ----------------
    if flow_type in {"meeting", "equipment"}:
        llm_result = run_portal_llm(flow)

        append_history(flow["flow_id"], "assistant", llm_result["question"] if llm_result["status"] == "incomplete" else "SUMMARY_READY")

        if llm_result["status"] == "incomplete":
            return {
                "flow_id": flow["flow_id"],
                "type": flow_type,
                "step": "collect",
                "response": llm_result["question"],
                "summary": None,
            }

        # COMPLETE → CONFIRMATION
        update_flow_data(flow["flow_id"], llm_result["data"])
        update_flow_step(flow["flow_id"], "confirm")

        return {
            "flow_id": flow["flow_id"],
            "type": flow_type,
            "step": "confirm",
            "response": "Please confirm the details. YES / NO",
            "summary": llm_result["data"],
        }

    # ---------------- TICKETS ----------------
    if flow_type == "ticket":
        result = run_ticket_llm(flow)

        append_history(flow["flow_id"], "assistant", "TROUBLESHOOTING")

        return {
            "flow_id": flow["flow_id"],
            "type": "ticket",
            "step": "collect",
            "response": "\n".join(result["steps"]) or "Issue noted.",
            "summary": None,
        }

    raise RuntimeError("Unknown flow type")