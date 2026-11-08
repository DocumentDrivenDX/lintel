"""Stable, safe preparation refusal types."""


class PreparationError(ValueError):
    """Safe, stable API preparation refusal."""

    def __init__(self, code: str, reference: str = "") -> None:
        self.code = code
        self.reference = reference
        super().__init__(code)
