from dataclasses import dataclass

class CliError(RuntimeError):
    pass

@dataclass
class SubtitleRow:
    start: str
    end: str
    en: str
    ja: str = ""

    @property
    def time_range(self) -> str:
        return f"{self.start} --> {self.end}"
