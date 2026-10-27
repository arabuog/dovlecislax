# Panou de control v1.2 — mers, tastă, așteptare

Windows, Python 3.12 pe 64 de biți. Fără detecție, capturi de ecran sau schimbări
automate de rând. Utilizatorul supraveghează și aliniază personajul în joc.

## Pornire în PowerShell

În folderul noii versiuni care conține `panel.py`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-simple.txt
.\.venv\Scripts\python.exe panel.py
```

Și `bot.py` sau `PORNIRE.bat` deschid acum panoul. Tkinter este inclus în
instalarea standard Python pentru Windows; nu necesită instalare prin pip.
Nu sunt necesare drepturi de administrator.

## Setările panoului

- **Număr de pași:** de exemplu 6.
- **Tastă de apăsat:** E, F, G, Space, Enter, cifre sau alt nume acceptat de
  PyDirectInput. N și W sunt rezervate pornirii/pauzei și mersului.
- **Așteptare după tastă:** de exemplu 7 secunde; poate fi și 0.
- **Număr de apăsări pe ciclu:** de câte ori se apasă tasta aleasă, implicit 1.
- **Apasă tasta și în timpul mersului:** bifă opțională, implicit debifată.
- **Durata unui pas:** implicit 0,30 secunde. Este parametrul de calibrare.
- **Durata apăsării tastei:** implicit 0,20 secunde; poți crește la 0,30 dacă
  jocul nu înregistrează apăsarea. Este o singură apăsare, nu o serie de comenzi.

Ciclul ține W timp de `pași × durata unui pas`, eliberează W, apasă tasta aleasă
o singură dată timp de 0,20 secunde (reglabil), o eliberează și așteaptă timpul configurat.
Între eliberarea W și apăsarea tastei există o pauză de oprire de 0,25 secunde.
Apoi repetă. Nu ține Shift și nu trimite comenzi mouse-ului. Numărul pașilor
este aproximat prin timp; programul nu măsoară animația picioarelor sau distanța.

**N** pornește/pune pe pauză când jocul are focusul. Alternativ, butonul
**Pornește în 3 secunde** îți lasă timp să revii în FiveM. Dacă nu revii în joc,
pornirea se anulează. **Oprește**, N, închiderea panoului sau pierderea focusului
eliberează tastele. Reluarea începe un ciclu nou cu mersul. Modificarea setărilor
oprește bucla; repornește pentru a folosi valorile noi.

Setările se salvează local în `panel-settings.json` la pornire și se încarcă la
următoarea deschidere. Nu conțin credențiale și nu sunt trimise pe Internet.

## Verificare

61 de teste automate trecute în Linux, inclusiv validarea setărilor, pornirea
cu întârziere, o singură apăsare a tastei alese, așteptarea, pauza și eliberarea
tastelor la pierderea focusului/închiderea panoului. Testele panoului folosesc
componente simulate, fără afișaj și fără input real Windows. Interfața Tk și
controlul efectiv în FiveM trebuie verificate pe calculatorul Windows.

Modul simplu din consolă rămâne disponibil separat:

```powershell
.\.venv\Scripts\python.exe simple_bot.py --walk 1.8 --wait 7
```

Versiunea vizuală anterioară este păstrată în `vision_bot.py`, cu documentația
în `VISION.md`; nu este folosită de panou. Programul nu implementează ocolirea
anti-cheat și nu garantează nedetectabilitatea.

## Verificarea separată a tastei

În v1.2, alege E și apasă **Testează doar tasta în 3 secunde**, apoi revino în
FiveM lângă un dovleac. Trimite doar o apăsare, fără W și fără repetare, apoi
se oprește. Dacă testul nu produce interacțiune, nu este o problemă de număr de
pași; verifică și dacă E funcționează apăsat manual în același loc.
Acest test nu dovedește automat că jocul a acceptat comanda; utilizatorul
verifică rezultatul. Windows și FiveM nu au fost disponibile pentru proba reală.

## Apăsări repetate și apăsări în mers (v1.2)

Cu bifa debifată, se merge, se eliberează W și se așteaptă 0,25 secunde, apoi se
execută numărul configurat de apăsări. Între apăsări sunt 0,10 secunde cu tasta
eliberată. Așteptarea configurată începe după ultima eliberare.

Cu bifa activată, W rămâne ținut continuu, iar apăsările sunt distribuite uniform
pe durata mersului. Numărul este pe ciclu, nu pe secundă. Nu se mai trimite un
lot suplimentar după oprire. Exemplu: 4 apăsări într-un mers de 2 secunde înseamnă
aproximativ o apăsare la fiecare 0,5 secunde. La final sunt eliberate ambele taste,
se așteaptă timpul configurat și se repetă ciclul.

Panoul respinge un număr de apăsări care nu încape în durata mersului cu durata
selectată și minimum 0,05 secunde pentru eliberare. Dacă PC-ul este blocat sau
întârzie excesiv, comenzile ratate din mers nu sunt executate după oprire; în
acest caz pot fi trimise mai puține decât numărul configurat. N și pierderea
focusului eliberează atât W, cât și tasta de acțiune. Testul separat rămâne o
singură apăsare fără mers, indiferent de numărul de apăsări din bucla normală.

Verificările automate suplimentare acoperă numărul de apăsări, păstrarea lui W
între apăsări, așteptarea după ultima apăsare, reluarea pe ciclu și pauza cu două
taste ținute. Proba efectivă pe Windows/FiveM rămâne necesară.
