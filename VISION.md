# Dovleci — urmărire pe rânduri, experimental

Windows/FiveM. N pornește/pune pe pauză; Ctrl+C în consolă închide. Scriptul nu
implementează ocolire anti-cheat și nu garantează nedetectabilitatea sau
completarea întregului câmp.

## Instalare / actualizare

Instalează Python 3.12 pe 64 de biți și dezarhivează versiunea completă nouă.
Deschide PowerShell în folderul care conține `vision_bot.py`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe vision_bot.py --preview
```

Previzualizarea nu comandă jocul. Q o închide. Magenta marchează ținta aleasă,
verde candidații și cercul alb punctul de interacțiune. Captura se face numai din
zona interioară a ferestrei procesului FiveM aflat în prim-plan. Discord poate
rămâne pornit în fundal. Captura se suspendă dacă treci în Discord sau consolă.
După lansarea previzualizării, revino în FiveM; preview-ul poate rămâne înghețat
când propria sa fereastră are focusul.

Pentru control efectiv:

```powershell
.\.venv\Scripts\python.exe vision_bot.py
```

Aliniază personajul și camera pe primul rând pentru inițializare, pune jocul în prim-plan și
apasă N. La actualizare închide procesul vechi și înlocuiește toate fișierele
proiectului, nu doar `vision_bot.py`. Nu sunt necesare drepturi de administrator.
Fișierele `.bat` oferă aceleași comenzi dacă Windows permite rularea lor.

## Comportament

- Inițializează un rând din geometria dovlecilor și păstrează apartenența la acel
  rând, în loc să aleagă mereu cel mai apropiat dovleac de pe orice rând.
- Urmărește terenul prin flux optic și o proiecție geometrică între capturi.
  Actualizează rândul și pozițiile memorate la mișcarea imaginii. Dacă proiecția
  nu este fiabilă, eliberează tastele și pune pe pauză, fără a alege alt rând.
- Pentru distanțe mai lungi ține W + Shift între capturi, astfel încât deplasarea
  înainte nu mai este o succesiune de opriri la fiecare cadru. Aproape de țintă
  eliberează doar Shift și păstrează W apăsat continuu: mersul normal al jocului,
  fără impulsuri de mers sau modificări de viteză. Eliberează W înainte de E,
  pierderea țintei sau pauză.
- Nu apasă Ctrl sau tasta de ghemuit. Nu poate anula automat un stil de mers sau
  o animație impusă de server. Shift presupune configurația standard de alergare.
- Apasă E o dată și așteaptă 9 secunde pentru animație. Nu verifică tichetele
  sau dispariția dovleacului. Consideră interacțiunea executată și exclude acea
  poziție din selecțiile următoare. Dacă E a eșuat, poziția poate rămâne nerecoltată.
- Înainte de E cere poziție apropiată/aliniată, lățime de minimum 5,5% din
  imagine, înălțime de minimum 3% și stabilitate timp de 0,35 secunde. Dacă ținta
  este prea mică, continuă W. După prima interacțiune, un nou E necesită progres
  vizual observat la aceeași țintă în urma unei comenzi W, plus expirarea pauzei.
  Simpla trecere a timpului nu autorizează încă un E. Și prima apăsare E
  necesită apropiere observată după W.
- Pe rând folosește numai deplasare înainte (W, cu Shift la distanță) și E.
  Nu corectează cu A/D/S. Dacă ținta este laterală sau depășită, pune pe pauză
  în loc să plece în altă direcție. Deplasarea laterală este rezervată
  tranziției dintre rânduri. Nu rotește camera în timpul urmăririi/recoltării.
- După cel puțin o apăsare E, fără poziții memorate rămase și 2,5 secunde fără candidați pe rând,
  încearcă o trecere laterală și o singură întoarcere. Dacă o poziție memorată
  încă există, dar nu se mai vede, nu schimbă rândul. Direcția laterală alternează
  la fiecare rând. Absența vizuală nu dovedește terminarea fizică a unui rând.
- Dacă nu poate găsi un rând nou, se oprește. Nu declară întregul câmp complet.

## Calibrarea întoarcerii

```powershell
.\.venv\Scripts\python.exe vision_bot.py --turn-pixels 1800 --row-shift 0.65 --wait 9
```

`--turn-pixels` reprezintă deplasarea mouse-ului pentru o întoarcere de aproximativ
180 de grade. **1800 este o valoare inițială, neverificată în joc**, nu un unghi
măsurat. Depinde de sensibilitatea mouse-ului și a camerei din FiveM.
`--row-shift` reprezintă secundele de deplasare laterală dintre rânduri; 0,65 este
și ea o valoare inițială. `--collect-y` (implicit 0,66) ajustează poziția verticală
normalizată de interacțiune. `--max-minutes` (implicit 120) limitează sesiunea.
`--min-width` (implicit 0,055) ajustează pragul vizual de apropiere. Este un prag
în pixeli relativi, nu o măsurătoare a distanței fizice; camera și zoom-ul îl pot
afecta. La pornire apare versiunea `v0.5`, pentru identificarea fișierelor noi.

## Limite și verificări

37 de teste automate au trecut, inclusiv blocarea lui E pentru ținte îndepărtate,
blocarea repetării fără deplasare observată și cerința de stabilitate. Sunt acoperite selectarea ferestrei, detectorul
sintetic, proiecția rândului la mișcarea camerei, fluxul optic, păstrarea rândului în fața unor ținte
laterale, recuperarea după o lipsă temporară a detecției și condițiile de final
vizual de rând. Unele teste păstrează simularea vechiului controler din
`navigation.py`; botul folosește acum `RowServo` din `rows.py`.

Cele două clipuri au fost decodate offline; statisticile versiunii anterioare se
păstrează în `clip-validation.json`. Ele nu validează noua deplasare în joc.
Comenzile Windows, alergarea, întoarcerile și animațiile serverului nu au fost
verificate în acest mediu Linux.

Modelul de rând folosește geometria imaginii, nu o hartă globală. Camera trebuie
să permită inițializarea rândului. Rotirea liberă/arbitrară nu este garantată:
proiecția terenului poate eșua, în special la schimbări mari de unghi, obstacole
sau texturi repetitive. Scriptul nu are coordonatele lumii jocului.
Solul/utilajele pot produce false detecții. Nu există ocolire fiabilă a
obstacolelor sau garanție de acoperire completă. Este necesară o probă în joc
pentru calibrarea întoarcerii și a trecerii laterale.

Numărul de pași nu este fixat la 5–6: distanța inițială poate varia, iar E este
condiționat de apropierea vizuală. v0.5 nu este validată în joc; nu oferă
măsurarea reală a distanței sau independență față de orice unghi al camerei.
