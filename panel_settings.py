"""Validate panel input independently of Windows and the UI."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Settings:
    steps: int = 6
    step_seconds: float = .30
    key: str = 'e'
    wait: float = 7.
    press_seconds: float = .20
    repeats: int = 1
    during_walk: bool = False

    @property
    def walk_seconds(self):
        return self.steps*self.step_seconds

    @classmethod
    def parse(cls, raw, supported_keys):
        try:
            steps=int(str(raw['steps']).strip())
            seconds=float(str(raw['step_seconds']).replace(',','.'))
            wait=float(str(raw['wait']).replace(',','.'))
            press=float(str(raw.get('press_seconds',.20)).replace(',','.'))
            repeats=int(str(raw.get('repeats',1)).strip())
        except (KeyError, ValueError, TypeError):
            raise ValueError('Introdu un număr întreg de pași și durate numerice.') from None
        key=str(raw.get('key','')).strip().lower()
        if not 1 <= steps <= 1000:
            raise ValueError('Numărul de pași trebuie să fie între 1 și 1000.')
        if not math.isfinite(seconds) or not .05 <= seconds <= 2:
            raise ValueError('Durata unui pas trebuie să fie între 0,05 și 2 secunde.')
        if not math.isfinite(wait) or not 0 <= wait <= 3600:
            raise ValueError('Așteptarea trebuie să fie între 0 și 3600 secunde.')
        if not math.isfinite(press) or not .05 <= press <= 1:
            raise ValueError('Durata apăsării trebuie să fie între 0,05 și 1 secundă.')
        if key not in supported_keys or key in ('n','w'):
            raise ValueError('Tastă invalidă. N este pentru pauză, iar W pentru mers.')
        during=raw.get('during_walk',False)
        if type(during) is not bool:
            raise ValueError('Opțiunea de apăsare în mers trebuie bifată sau debifată.')
        if not 1 <= repeats <= 1000:
            raise ValueError('Numărul de apăsări trebuie să fie între 1 și 1000.')
        if during and steps*seconds < repeats*(press+.05):
            raise ValueError('Prea multe apăsări pentru durata mersului. Redu numărul sau mărește durata mersului.')
        return cls(steps,seconds,key,wait,press,repeats,during)
