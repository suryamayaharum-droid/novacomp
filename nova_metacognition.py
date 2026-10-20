"""Bounded metacognitive primitives for Nova; no tool execution or self-deployment."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Iterable
from nova_core import stable_digest


class EvidenceKind(str, Enum):
    OBSERVATION = "observation"
    SOURCE = "source"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Evidence:
    statement: str
    kind: EvidenceKind
    source: str = ""
    observed_at: str = ""
    confidence: float = 0.5

    def __post_init__(self):
        if not self.statement.strip():
            raise ValueError("Evidence statement is required.")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1.")
        if self.kind == EvidenceKind.SOURCE and not self.source.strip():
            raise ValueError("Source evidence needs provenance.")


@dataclass(frozen=True)
class Goal:
    goal_id: str
    description: str
    success_criteria: tuple[str, ...]
    constraints: tuple[str, ...] = ()
    max_iterations: int = 3

    def __post_init__(self):
        if not self.goal_id.strip() or not self.description.strip():
            raise ValueError("Goal ID and description are required.")
        if not self.success_criteria:
            raise ValueError("At least one success criterion is required.")
        if not 1 <= self.max_iterations <= 10:
            raise ValueError("Iteration budget must be between 1 and 10.")


@dataclass(frozen=True)
class CandidateAction:
    action_id: str
    description: str
    risk: RiskLevel
    reversible: bool
    requires_network: bool = False
    requires_physical_actuation: bool = False
    requires_human_approval: bool = False


@dataclass(frozen=True)
class Reflection:
    goal_id: str
    iteration: int
    achieved_criteria: tuple[str, ...]
    unmet_criteria: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    risk_notes: tuple[str, ...]
    next_step: str
    stop: bool
    rationale_digest: str


@dataclass(frozen=True)
class CognitiveState:
    schema_version: int
    goal: Goal
    iteration: int = 1
    evidence: tuple[Evidence, ...] = ()
    tried_actions: tuple[str, ...] = ()
    observations: tuple[str, ...] = ()
    reflections: tuple[Reflection, ...] = ()


def authorize_action(action: CandidateAction, *, network_allowed=False,
                     physical_actuation_allowed=False, approval_granted=False):
    """Fail closed for network, physical, high-impact, and irreversible actions."""
    if action.requires_network and not network_allowed:
        raise PermissionError("Network access is not enabled for this action.")
    if action.requires_physical_actuation and not physical_actuation_allowed:
        raise PermissionError("Physical actuation is disabled.")
    elevated = action.risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}
    if (elevated or not action.reversible or action.requires_human_approval) and not approval_granted:
        raise PermissionError("This action requires explicit human approval.")


def reflect(state: CognitiveState, *, achieved_criteria: Iterable[str] = (),
            observations: Iterable[str] = (), risk_notes: Iterable[str] = ()) -> Reflection:
    """Compare observed evidence to criteria and choose a bounded next step."""
    achieved = set(achieved_criteria)
    unknown = achieved - set(state.goal.success_criteria)
    if unknown:
        raise ValueError(f"Unknown success criteria: {sorted(unknown)}")
    observed = tuple(x.strip() for x in observations if x.strip())
    notes = tuple(x.strip() for x in risk_notes if x.strip())
    unmet = tuple(c for c in state.goal.success_criteria if c not in achieved)
    gaps = tuple(
        f"No recorded evidence for criterion: {c}" for c in unmet
        if not any(e.confidence >= .7 and c.casefold() in e.statement.casefold()
                   for e in state.evidence)
    )
    exhausted = state.iteration >= state.goal.max_iterations
    if not unmet:
        next_step = "checkpoint_and_report"
    elif exhausted:
        next_step = "stop_and_request_review"
    elif notes:
        next_step = "resolve_risk_before_action"
    elif gaps:
        next_step = "collect_evidence_for_unmet_criteria"
    else:
        next_step = "plan_smallest_reversible_next_step"
    stop = not unmet or exhausted or any("stop" in n.casefold() for n in notes)
    material = {"goal_id": state.goal.goal_id, "iteration": state.iteration,
                "achieved": sorted(achieved), "unmet": unmet, "gaps": gaps,
                "risk_notes": notes, "observations": observed,
                "next_step": next_step, "stop": stop}
    return Reflection(state.goal.goal_id, state.iteration,
                      tuple(c for c in state.goal.success_criteria if c in achieved),
                      unmet, gaps, notes, next_step, stop, stable_digest(material))


def propose_recursive_improvement(reflection: Reflection, *, iteration: int,
                                  max_iterations: int) -> dict[str, Any]:
    """Return a proposal only; execution is intentionally disallowed."""
    if not 1 <= max_iterations <= 10 or not 1 <= iteration <= max_iterations:
        raise ValueError("Iteration is outside the allowed budget.")
    if reflection.stop:
        return {"proposal_id": stable_digest({"digest": reflection.rationale_digest,
                "status": "stopped"})[:16], "status": "stopped",
                "execution_allowed": False,
                "reason": "Completion, stop condition, or human review is required."}
    proposal = {"goal_id": reflection.goal_id, "iteration": iteration,
                "next_step": reflection.next_step,
                "unmet_criteria": list(reflection.unmet_criteria),
                "evidence_gaps": list(reflection.evidence_gaps),
                "required_checks": ["collect evidence", "evaluate permissions and risk",
                                    "run focused tests", "record checkpoint"],
                "requires_human_approval": True, "execution_allowed": False}
    proposal["proposal_id"] = stable_digest(proposal)[:16]
    return proposal


def state_to_dict(state: CognitiveState) -> dict[str, Any]:
    """Serialize state for checkpoint storage."""
    return asdict(state)
