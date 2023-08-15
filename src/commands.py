from typing import List


class BasicCommand:
    def __init__(self, command: str, arguments: List[str]):
        self._command: str = command
        self._arguments: List[str] = arguments

    @property
    def command(self) -> str:
        return self._command

    @property
    def arguments(self) -> List[str]:
        return self._arguments
