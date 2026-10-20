"""Bounded recursive improvement planner for NovaComp.

Proposes measurable system improvements from explicit observations. It never edits
source code, runs arbitrary commands, or deploys changes itself.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Iterable
from nova_core import stable_digest

class ChangeRisk(str, Enum):
    DOCS = "docs"
    TESTS = "tests"
    INTERNAL_CODE = "internal_code"
    EXTERNAL_EFFECT = "external_effect"
    SECURITY = "security"

@dataclass(frozen=True)
class Metric:
    name: str
    value: float
    target: float
    direction: str = "higher"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Metric name must not be empty.")
        if self.direction not in {"higher", "lower"}:
            raise ValueError("Metric direction must be 'higher' or 'lower'.")

    @property
    def met(self) -> bool:
        return self.value >= self.target if self.direction == "higher" else self.value <= self.target

@dataclass(frozen=True)
class Observation:
    run_id: str
    summary: str
    metrics: tuple[Metric, ...]
    known_failures: tuple[str, ...] = ()

@dataclass(frozen=True)
class ImprovementProposal:
    proposal_id: str
    iteration: int
    objective: str
    evidence: tuple[str, ...]
    change_risk: ChangeRisk
    required_checks: tuple[str, ...]
    requires_human_approval: bool
    execution_allowed: bool = False

def propose_next_iteration(
    observation: Observation,
    *,
    iteration: int,
    max_iterations: int = 5,
    allowed_risks: Iterable[ChangeRisk] = (ChangeRisk.DOCS, ChangeRisk.TESTS),
) -> ImprovementProposal:
    """Create one bounded, reviewable next-step proposal from measured evidence."""
    if not observation.run_id.strip() or not observation.summary.strip():
        raise ValueError("Observation must include a run_id and summary.")
    if iteration < 1 or max_iterations < 1 or iteration > max_iterations:
        raise ValueError("Iteration must be between 1 and max_iterations.")
    if not observation.metrics and not observation.known_failures:
        raise ValueError("At least one metric or known failure is required.")
    allowed = set(allowed_risks)
    failed = [m for m in observation.metrics if not m.met]
    if observation.known_failures:
        objective = "Resolve the highest-priority observed failure and add a regression test."
        evidence = tuple(observation.known_failures[:5])
    elif failed:
        worst = sorted(failed, key=lambda m: abs(m.target - m.value), reverse=True)[0]
        objective = f"Improve metric '{worst.name}' from {worst.value:g} toward {worst.target:g}."
        evidence = tuple(f"{m.name}: value={m.value:g}, target={m.target:g}, direction={m.direction}" for m in failed[:5])
    else:
        objective = "Preserve passing behavior and add a regression/contract test for the current capability."
        evidence = tuple(f"{m.name}: target met ({m.value:g} vs {m.target:g})" for m in observation.metrics[:5])
    risk = ChangeRisk.TESTS if ChangeRisk.TESTS in allowed else ChangeRisk.DOCS
    material: dict[str, Any] = {
        "run_id": observation.run_id, "iteration": iteration,
        "objective": objective, "evidence": evidence, "risk": risk.value,
    }
    return ImprovementProposal(
        proposal_id=stable_digest(material)[:16],
        iteration=iteration, objective=objective, evidence=evidence,
        change_risk=risk,
        required_checks=(
            "write or update a focused regression test",
            "run the full test suite",
            "inspect the diff for scope and secret leakage",
            "compare the same metrics before and after",
            "record the result in a versioned checkpoint",
        ),
        requires_human_approval=(risk not in {ChangeRisk.DOCS, ChangeRisk.TESTS}),
        execution_allowed=False,
    )

def proposal_to_dict(proposal: ImprovementProposal) -> dict[str, Any]:
    """Return a JSON-safe proposal envelope suitable for review or persistence."""
    result = asdict(proposal)
    result["change_risk"] = proposal.change_risk.value
    return result
