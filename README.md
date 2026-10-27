# Dovleci — urmărire pe rânduri, experimental

Windows/FiveM. F3 pornește/pune pe pauză; Ctrl+C în consolă închide. Scriptul nu
implementează ocolire anti-cheat și nu garantează nedetectabilitatea sau
completarea întregului câmp.

## Instalare / actualizare

Instalează Python 3.12 pe 64 de biți și dezarhivează versiunea completă nouă.
Deschide PowerShell în folderul care conține `bot.py`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe bot.py --preview
```

Previzualizarea nu comandă jocul. Q o închide. Magenta marchează ținta aleasă,
verde candidații și cercul alb punctul de interacțiune. Captura se face numai din
zona interioară a ferestrei procesului FiveM aflat în prim-plan. Discord poate
rămâne pornit în fundal. Captura se suspendă dacă treci în Discord sau consolă.
După lansarea previzualizării, revino în FiveM; preview-ul poate rămâne înghețat
când propria sa fereastră are focusul.

Pentru control efectiv:

```powershell
.\.venv\Scripts\python.exe bot.py
```

Aliniază personajul și camera drept pe primul rând, pune jocul în prim-plan și
apasă F3. La actualizare închide procesul vechi și înlocuiește toate fișierele
proiectului, nu doar `bot.py`. Nu sunt necesare drepturi de administrator.
Fișierele `.bat` oferă aceleași comenzi dacă Windows permite rularea lor.

## Comportament

- Inițializează un rând din geometria dovlecilor și păstrează apartenența la acel
  rând, în loc să aleagă mereu cel mai apropiat dovleac de pe orice rând.
- Urmărește mișcarea țintei între capturi. Actualizează poziția estimată a rândului.
- Pentru distanțe mai lungi ține W + Shift între capturi, astfel încât deplasarea
  înainte nu mai este o succesiune de opriri la fiecare cadru. Aproape de țintă
  eliberează doar Shift și păstrează W apăsat continuu: mersul normal al jocului,
  fără impulsuri de mers sau modificări de viteză. Eliberează W înainte de E,
  corecții laterale, pierderea țintei sau pauză.
- Nu apasă Ctrl sau tasta de ghemuit. Nu poate anula automat un stil de mers sau
  o animație impusă de server. Shift presupune configurația standard de alergare.
- Apasă E o dată și așteaptă minimum 9 secunde, apoi cere dispariția vizuală a
  țintei timp de o secundă. Nu citește mesajul cu tichete.
- Nu rotește camera în timpul urmăririi/recoltării. La nereușită pune pe pauză.
- După cel puțin o dispariție observată și 2,5 secunde fără candidați pe rând,
  încearcă o trecere laterală și o singură întoarcere. Direcția laterală alternează
  la fiecare rând. Absența vizuală nu dovedește terminarea fizică a unui rând.
- Dacă nu poate găsi un rând nou, se oprește. Nu declară întregul câmp complet.

## Calibrarea întoarcerii

```powershell
.\.venv\Scripts\python.exe bot.py --turn-pixels 1800 --row-shift 0.65 --wait 9
```

`--turn-pixels` reprezintă deplasarea mouse-ului pentru o întoarcere de aproximativ
180 de grade. **1800 este o valoare inițială, neverificată în joc**, nu un unghi
măsurat. Depinde de sensibilitatea mouse-ului și a camerei din FiveM.
`--row-shift` reprezintă secundele de deplasare laterală dintre rânduri; 0,65 este
și ea o valoare inițială. `--collect-y` (implicit 0,66) ajustează poziția verticală
normalizată de interacțiune. `--max-minutes` (implicit 120) limitează sesiunea.

## Limite și verificări

27 de teste automate au trecut. Sunt acoperite selectarea ferestrei, detectorul
sintetic, confirmarea vizuală, fluxul optic, păstrarea rândului în fața unor ținte
laterale, recuperarea după o lipsă temporară a detecției și condițiile de final
vizual de rând. Unele teste păstrează simularea vechiului controler din
`navigation.py`; botul folosește acum `RowServo` din `rows.py`.

Cele două clipuri au fost decodate offline; statisticile versiunii anterioare se
păstrează în `clip-validation.json`. Ele nu validează noua deplasare în joc.
Comenzile Windows, alergarea, întoarcerile și animațiile serverului nu au fost
verificate în acest mediu Linux.

Modelul de rând folosește geometria imaginii, nu o hartă globală. Camera trebuie
să fie orientată pe rând. Solul/utilajele pot produce false detecții. Ocluzia sau
mișcarea camerei pot părea dispariția unui dovleac. Nu există ocolire fiabilă a
obstacolelor sau garanție de acoperire completă. Este necesară o probă în joc
pentru calibrarea întoarcerii și a trecerii laterale.
