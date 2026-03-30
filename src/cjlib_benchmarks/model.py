from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


OperationName = str


@dataclass(frozen=True)
class OperationDefaults:
    warmup_iterations: int
    probe_iterations: int
    summary_iterations: int
    roundtrip_iterations: int

    def iterations_for(self, operation: OperationName) -> int:
        match operation:
            case "probe":
                return self.probe_iterations
            case "summary":
                return self.summary_iterations
            case "roundtrip":
                return self.roundtrip_iterations
            case _:
                raise ValueError(f"unsupported operation: {operation}")


@dataclass(frozen=True)
class TargetConfig:
    identifier: str
    command: tuple[str, ...]


@dataclass(frozen=True)
class CaseConfig:
    identifier: str
    kind: str
    description: str
    source_path: str | None = None
    profile_path: str | None = None
    seed: int | None = None


@dataclass(frozen=True)
class Manifest:
    version: int
    defaults: OperationDefaults
    targets: tuple[TargetConfig, ...]
    cases: tuple[CaseConfig, ...]

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        payload = json.loads(path.read_text(encoding="utf-8"))
        defaults = OperationDefaults(**payload["defaults"])
        targets = tuple(
            TargetConfig(identifier=item["id"], command=tuple(item["command"]))
            for item in payload["targets"]
        )
        cases = tuple(
            CaseConfig(
                identifier=item["id"],
                kind=item["kind"],
                description=item["description"],
                source_path=item.get("source_path"),
                profile_path=item.get("profile_path"),
                seed=item.get("seed"),
            )
            for item in payload["cases"]
        )
        return cls(
            version=payload["version"],
            defaults=defaults,
            targets=targets,
            cases=cases,
        )
