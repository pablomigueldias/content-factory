from dataclasses import dataclass
from typing import Protocol


@dataclass
class GroundingResult:

    fact_index: int | None
    score: float
    verified: bool


class Verifier(Protocol):
    def ground(self, claim: str,
               candidate_facts: list[str]) -> GroundingResult: ...
