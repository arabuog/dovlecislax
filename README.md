# Dovleci — mod simplu

Fără detecție, capturi, rotiri sau schimbări de rând. Necesită Windows și Python
3.12 pe 64 de biți. N pornește/pune pe pauză. La reluare ciclul începe cu mersul.

Ciclul: W ținut 1,8 secunde → W eliberat → E apăsat o dată timp de 0,05 secunde
→ E eliberat → așteptare 7 secunde → repetare. Nu folosește Shift, Ctrl sau mouse.
Cele 1,8 secunde sunt o valoare inițială, nu 5–6 pași măsurați în joc.

## PowerShell

Din folderul care conține `bot.py`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-simple.txt
.\.venv\Scripts\python.exe bot.py
```

Revino în FiveM și apasă N. Alt+Tab pune automat pe pauză și eliberează tastele.
Ctrl+C în consolă închide. Nu sunt necesare drepturi de administrator.

Pentru o distanță mai mare sau mai mică, schimbă durata mersului:

```powershell
.\.venv\Scripts\python.exe bot.py --walk 2.2
.\.venv\Scripts\python.exe bot.py --walk 1.4
```

Așteptarea rămâne 7 secunde. Opțional se poate ajusta cu `--wait`.
Sunt disponibile și `INSTALARE.bat` și `PORNIRE.bat`, dacă Windows permite rularea.

Acest mod nu știe unde sunt dovlecii sau când rândul s-a terminat. Utilizatorul
supraveghează, aliniază personajul și pune pe pauză la capătul rândului.
Nu confirmă recoltarea, nu garantează nedetectabilitatea și nu ocolește anti-cheat.

Testele temporizării au trecut (4 teste noi, 41 în total cu testele versiunii
vechi). Rularea efectivă pe Windows/FiveM nu a fost verificată în mediul Linux.
Versiunea vizuală anterioară este păstrată în `vision_bot.py`; documentația ei
este în `VISION.md`. Nu este folosită de modul simplu și necesită vechile
dependențe din `requirements.txt` dacă este lansată separat.
