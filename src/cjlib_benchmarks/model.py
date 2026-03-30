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
    warmup_iterations: int | None = None
    probe_iterations: int | None = None
    summary_iterations: int | None = None
    roundtrip_iterations: int | None = None

    def warmup_for(self, defaults: OperationDefaults) -> int:
        return defaults.warmup_iterations if self.warmup_iterations is None else self.warmup_iterations

    def iterations_for(self, operation: OperationName, defaults: OperationDefaults) -> int:
        match operation:
            case "probe":
                return defaults.probe_iterations if self.probe_iterations is None else self.probe_iterations
            case "summary":
                return defaults.summary_iterations if self.summary_iterations is None else self.summary_iterations
            case "roundtrip":
                return (
                    defaults.roundtrip_iterations
                    if self.roundtrip_iterations is None
                    else self.roundtrip_iterations
                )
            case _:
                raise ValueError(f"unsupported operation: {operation}")


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
                warmup_iterations=item.get("warmup_iterations"),
                probe_iterations=item.get("probe_iterations"),
                summary_iterations=item.get("summary_iterations"),
                roundtrip_iterations=item.get("roundtrip_iterations"),
            )
            for item in payload["cases"]
        )
        return cls(
            version=payload["version"],
            defaults=defaults,
            targets=targets,
            cases=cases,
        )
