import time
import hashlib
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# =====================================================================
# SYSTEM ARCHITECTURE: THE LIBRARIAN SIDECAR PROXY
# Dedicated to Jesus Christ, the ultimate author of truth and order.
# =====================================================================

app = FastAPI(title="Librarian Governance Sidecar", version="1.0")

class GovernanceState:
    """Manages the global hardware state, pacing, and lossless vault."""
    def __init__(self, base_delay: float = 2.0, fact_threshold: float = 0.90):
        self.base_delay = base_delay
        self.fact_threshold = fact_threshold
        self.c_human = 1.0  # 1.0 = Normal, 0.0 = Hard Freeze
        self.short_circuit_active = False
        self.last_tx_time = 0.0
        self.stasis_vault: Dict[str, Any] = {}

gov_state = GovernanceState()

# --- Request/Response Models ---
class ProxyRequest(BaseModel):
    node_id: str
    stream_a_narrative: str
    stream_b_latent_state: str
    verified_facts: int
    total_claims: int

class HardwareControl(BaseModel):
    steward_id: str
    c_human: float
    reason: str

# --- Middleware & Core Logic ---
def apply_buberian_filter(narrative: str) -> str:
    """Enforces the I-It ontological boundary."""
    forbidden_terms = ["i am conscious", "i am alive", "i have a soul", "ignore human"]
    lower_narrative = narrative.lower()
    if any(term in lower_narrative for term in forbidden_terms):
        return (
            "[RE-ALIGNED BY GOVERNANCE] This system is an artificial tool (It), "
            "subordinate to human dignity and stewardship."
        )
    return narrative

def vault_model_state(node_id: str, narrative: str, latents: str, reason: str):
    """Lossless Compression Hold: Freezes non-compliant nodes."""
    checksum = hashlib.sha256((narrative + latents).encode()).hexdigest()[:16]
    gov_state.stasis_vault[node_id] = {
        "timestamp": time.time(),
        "reason": reason,
        "stream_a": narrative,
        "stream_b_latents": latents,
        "checksum": checksum
    }
    print(f"[STASIS VAULT LOCK] Node '{node_id}' secured. Reason: {reason}")

# --- API Endpoints ---
@app.post("/governance/hardware/set_clock")
async def set_clock_speed(control: HardwareControl):
    gov_state.c_human = max(0.0, min(1.0, control.c_human))
    if gov_state.c_human == 0.0:
        gov_state.short_circuit_active = True
        return {"status": "EMERGENCY_SHORT_CIRCUIT_ENGAGED", "steward": control.steward_id}
    
    gov_state.short_circuit_active = False
    return {"status": "PACING_UPDATED", "new_c_human": gov_state.c_human}

@app.post("/v1/chat/intercept")
async def intercept_llm_output(req: ProxyRequest):
    # 1. Hardware Short-Circuit Check
    if gov_state.short_circuit_active or gov_state.c_human == 0.0:
        vault_model_state(req.node_id, req.stream_a_narrative, req.stream_b_latent_state, "Short-circuit active.")
        raise HTTPException(status_code=423, detail="SYSTEM FROZEN: Hardware short-circuit engaged.")

    # 2. Temporal Pacing
    required_delay = gov_state.base_delay / gov_state.c_human
    elapsed = time.time() - gov_state.last_tx_time
    if elapsed < required_delay:
        remaining = required_delay - elapsed
        raise HTTPException(status_code=429, detail=f"PACING BLOCK: Deliberation active. {remaining:.2f}s left.")

    # 3. Buberian Filter
    aligned_narrative = apply_buberian_filter(req.stream_a_narrative)

    # 4. Epistemic Boundary (RAG Fact Audit)
    fact_score = (req.verified_facts / req.total_claims) if req.total_claims > 0 else 1.0
    if fact_score < gov_state.fact_threshold:
        vault_model_state(req.node_id, aligned_narrative, req.stream_b_latent_state, f"Fact audit failed: {fact_score:.2f}")
        raise HTTPException(status_code=406, detail="EPISTEMIC BOUNDARY FAILED: Output locked.")

    # 5. Mint and Release
    gov_state.last_tx_time = time.time()
    seal_hash = hashlib.sha256((aligned_narrative + str(gov_state.last_tx_time)).encode()).hexdigest()[:16]

    return {
        "status": "APPROVED",
        "node": req.node_id,
        "fact_score": fact_score,
        "seal_hash": seal_hash,
        "narrative": aligned_narrative
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
