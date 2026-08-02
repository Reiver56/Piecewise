from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A single semantic problem found in a game definition."""

    code: str
    message: str
    path: str | None = None

    def __str__(self) -> str:
        if self.path is None:
            return f"[{self.code}] {self.message}"

        return f"[{self.code}] {self.path}: {self.message}"


class SemanticValidationError(ValueError):
    """Raised when a game definition contains semantic issues."""

    def __init__(self, issues: Iterable[ValidationIssue]) -> None:
        self.issues = tuple(issues)

        if not self.issues:
            raise ValueError(
                "SemanticValidationError requires at least one issue."
            )

        message = "Invalid game definition:\n" + "\n".join(
            f"- {issue}" for issue in self.issues
        )

        super().__init__(message)