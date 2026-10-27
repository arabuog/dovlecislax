"""Validate panel input independently of Windows and the UI."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Settings:
    steps: int = 6
    step_seconds: float = .30
    key: str = 'e'
    wait: float = 7.

    @property
    def walk_seconds(self):
        return self.steps*self.step_seconds

    @classmethod
    def parse(cls, raw, supported_keys):
        try:
            steps=int(str(raw['steps']).strip())
            seconds=float(str(raw['step_seconds']).replace(',','.'))
            wait=float(str(raw['wait']).replace(',','.'))
        except (KeyError, ValueError, TypeError):
            raise ValueError('Introdu un număr întreg de pași și durate numerice.') from None
        key=str(raw.get('key','')).strip().lower()
        if not 1 <= steps <= 1000:
            raise ValueError('Numărul de pași trebuie să fie între 1 și 1000.')
        if not math.isfinite(seconds) or not .05 <= seconds <= 2:
            raise ValueError('Durata unui pas trebuie să fie între 0,05 și 2 secunde.')
        if not math.isfinite(wait) or not 0 <= wait <= 3600:
            raise ValueError('Așteptarea trebuie să fie între 0 și 3600 secunde.')
        if key not in supported_keys or key in ('n','w'):
            raise ValueError('Tastă invalidă. N este pentru pauză, iar W pentru mers.')
        return cls(steps,seconds,key,wait)
