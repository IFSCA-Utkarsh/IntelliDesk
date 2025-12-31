# backend/chat/state_manager.py

import time
import uuid
from datetime import datetime
from typing import Dict, Optional, List

from llm.orchestrator_llm import run_orchestrator

# ======================================================
# CONFIGURATION
# ======================================================

FLOW_TTL_SECONDS = 15 * 60  # 15 minutes expiry

# In-memory store (single-node design)
# {
#   user_id: {
#       flow_id: flow_dict
#   }
# }
_FLOW_STORE: Dict[str, Dict[str, dict]] = {}

# ======================================================
# INTERNAL HELPERS
# ======================================================

def _now_ts() -> int:
    return int(time.time())


def _today_str() -> str:
    # Always UTC, deterministic
    return datetime.utcnow().strftime("%d/%m/%Y")


def _ensure_runtime_fields(flow: dict) -> None:
    """
    Self-heal all mandatory runtime fields.
    This function GUARANTEES shape compatibility.
    """

    # ---- flow_id / id compatibility (CRITICAL) ----
    if "id" in flow and "flow_id" not in flow:
        flow["flow_id"] = flow["id"]
    elif "flow_id" in flow and "id" not in flow:
        flow["id"] = flow["flow_id"]

    # ---- Required runtime fields ----
    if "current_date" not in flow:
        flow["current_date"] = _today_str()

    if "history" not in flow:
        flow["history"] = []

    if "data" not in flow:
        flow["data"] = {}

    if "step" not in flow:
        flow["step"] = "collect"


def _cleanup_expired_flows(user_id: str) -> None:
    """
    Remove expired flows for a user.
    """
    user_flows = _FLOW_STORE.get(user_id)
    if not user_flows:
        return

    now = _now_ts()
    expired_ids = [
        fid for fid, f in user_flows.items()
        if f.get("expires_at", 0) <= now
    ]

    for fid in expired_ids:
        del user_flows[fid]

    if not user_flows:
        _FLOW_STORE.pop(user_id, None)

# ======================================================
# PUBLIC API
# ======================================================

def create_flow(user_id: str, message: str, request_id: str) -> Optional[dict]:
    """
    Create a NEW flow.
    Orchestrator is called ONLY here.
    """

    decision = run_orchestrator(message)

    if decision.get("confidence", 0.0) < 0.6:
        return None

    route = decision.get("route")

    if route == "meeting_booking":
        flow_type = "meeting"
    elif route == "equipment_assignment":
        flow_type = "equipment"
    elif route == "tickets":
        flow_type = "ticket"
    else:
        return None

    flow_id = f"flow-{uuid.uuid4().hex[:8]}"

    flow = {
        "id": flow_id,
        "flow_id": flow_id,  
        "user_id": user_id,
        "type": flow_type,
        "data": {},
        "history": [],
        "step": "collect",
        "current_date": _today_str(),
        "expires_at": _now_ts() + FLOW_TTL_SECONDS,
    }

    _FLOW_STORE.setdefault(user_id, {})[flow_id] = flow
    return flow


def get_active_flows(user_id: str) -> List[dict]:
    """
    Return all active (non-expired) flows for a user.
    """
    _cleanup_expired_flows(user_id)

    flows = list(_FLOW_STORE.get(user_id, {}).values())
    for f in flows:
        _ensure_runtime_fields(f)

    return flows


def get_flow(user_id: str, flow_id: str) -> Optional[dict]:
    """
    Retrieve a specific flow.
    Always self-heals runtime fields.
    """
    _cleanup_expired_flows(user_id)

    flow = _FLOW_STORE.get(user_id, {}).get(flow_id)
    if not flow:
        return None

    _ensure_runtime_fields(flow)
    return flow


def save_flow(user_id: str, flow: dict) -> None:
    """
    Persist updated flow and refresh TTL.
    """
    _ensure_runtime_fields(flow)
    flow["expires_at"] = _now_ts() + FLOW_TTL_SECONDS

    _FLOW_STORE.setdefault(user_id, {})[flow["flow_id"]] = flow


def delete_flow(user_id: str, flow_id: str) -> None:
    """
    Explicitly delete a flow.
    """
    user_flows = _FLOW_STORE.get(user_id)
    if not user_flows:
        return

    user_flows.pop(flow_id, None)

    if not user_flows:
        _FLOW_STORE.pop(user_id, None)


def reset_flow(user_id: str, flow_id: str) -> Optional[dict]:
    """
    Full rejection reset:
    - Deletes existing flow
    - Creates a NEW flow of SAME TYPE
    - Does NOT call orchestrator again
    """
    flow = get_flow(user_id, flow_id)
    if not flow:
        return None

    flow_type = flow["type"]
    delete_flow(user_id, flow_id)

    new_flow_id = f"flow-{uuid.uuid4().hex[:8]}"

    new_flow = {
        "id": new_flow_id,
        "flow_id": new_flow_id,
        "user_id": user_id, 
        "type": flow_type,
        "data": {},
        "history": [],
        "step": "collect",
        "current_date": _today_str(),
        "expires_at": _now_ts() + FLOW_TTL_SECONDS,
    }

    _FLOW_STORE.setdefault(user_id, {})[new_flow_id] = new_flow
    return new_flow


def append_history(*args) -> None:
    """
    BACKWARD + FORWARD compatible history appender.

    Supported signatures:
    1) append_history(user_id, flow_id, role, content)
    2) append_history(flow_id, role, content)   # legacy
    """

    # -------- NEW SIGNATURE --------
    if len(args) == 4:
        user_id, flow_id, role, content = args

    # -------- LEGACY SIGNATURE --------
    elif len(args) == 3:
        flow_id, role, content = args

        # Find owning user deterministically
        user_id = None
        for uid, flows in _FLOW_STORE.items():
            if flow_id in flows:
                user_id = uid
                break

        if user_id is None:
            return

    else:
        return

    flow = get_flow(user_id, flow_id)
    if not flow:
        return

    flow["history"].append({
        "role": role,
        "content": content
    })

    save_flow(user_id, flow)

def update_flow_data(flow_id: str, updates: dict):
    for flow in _FLOW_STORE.values():
        if flow.get("flow_id") == flow_id:
            flow["data"].update(updates)
            return



def update_flow_step(user_id: str, flow_id: str, step: str) -> None:
    """
    Update the flow step safely.
    """
    flow = get_flow(user_id, flow_id)
    if not flow:
        return

    if not isinstance(step, str):
        return

    flow["step"] = step
    save_flow(user_id, flow)