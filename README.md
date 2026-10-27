# Dovleci — navigare vizuală experimentală v2

Script Windows/FiveM care caută dovleci în tot ecranul, inclusiv pe rândurile
vecine. F3 pornește/pune pe pauză. Nu este verificat pentru recoltarea completă a
câmpului și nu garantează nedetectabilitatea. Nu implementează ocolire anti-cheat.

## Instalare

1. Instalează Python **3.12, 64-bit** de pe python.org, cu Python Launcher.
2. Dezarhivează tot directorul într-un loc unde ai drept de scriere.
3. Rulează `INSTALARE.bat`.
4. Cu jocul vizibil, rulează `PREVIZUALIZARE.bat`. Nu transmite comenzi jocului.
   Verde = candidați, magenta = ținta aleasă, cerc alb = punctul de interacțiune.
   Q închide previzualizarea. Dacă marchează solul sau utilajele, nu porni controlul.
5. Rulează `PORNIRE.bat`, apoi pune FiveM în prim-plan și apasă **F3**.

La pauză tastele se eliberează. Ctrl+C în consolă închide. Pierderea focusului
pune pe pauză. Programul nu cere drepturi de administrator. Ține consola
vizibilă când verifici prima funcționare.

## Ce face automat

- Alege o țintă apropiată din tot câmpul vizibil, fără restricție la rândul central.
- Încearcă să urmărească aceeași țintă prin flux optic între capturi.
- Trimite impulsuri scurte W/A/S/D și adaptează modelul de deplasare după mișcarea
  observată. Aceasta este o aproximare în coordonatele ecranului.
- Apasă E o singură dată când ținta ajunge în zona de interacțiune.
- Așteaptă cel puțin 9 secunde, apoi cere absența țintei timp de o secundă.
- Caută următoarea țintă și, dacă nu mai găsește, rotește vederea în pași.
- Abandonează o țintă persistentă după expirarea așteptării și schimbă vederea.
  Oprește după trei interacțiuni nereușite sau trei urmăriri prea lungi.
- Oprește după 24 de pași de căutare fără ținte ori 120 de minute de sesiune.
  Lipsa țintelor NU înseamnă că întregul câmp a fost recoltat.

## Limite care rămân

Nu există hartă globală, localizare în teren, plan de acoperire completă sau
ocolire fiabilă a obstacolelor. Trecerea între rândurile vizibile folosește ținte
vizuale; nu există o întoarcere geometrică verificată la capătul fiecărui rând.
Rotirea mouse-ului depinde de sensibilitatea jocului și nu este calibrată la
360 de grade. O țintă ascunsă de cameră/personaj poate părea recoltată.
Mesajul cu tichete nu este citit. Culorile solului și utilajele pot produce ținte
false, iar camera dinamică poate împiedica urmărirea și adaptarea comenzilor.

Scriptul necesită proba efectivă pe Windows/FiveM pentru calibrarea controlului
și verificarea completării câmpului. Clipurile permit doar verificări offline;
nu demonstrează că mișcările generate vor funcționa în joc.

## Opțiuni

În PowerShell, în directorul proiectului:

```powershell
.\.venv\Scripts\python.exe bot.py --preview
.\.venv\Scripts\python.exe bot.py --collect-y 0.66 --wait 9 --scan-pixels 240 --monitor 1
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`collect-y`: coordonata verticală normalizată a bazei țintei la interacțiune.
`scan-pixels`: deplasarea mouse-ului la fiecare pas de căutare, dependentă de
sensibilitate. `monitor`: monitorul MSS pe care este jocul. Rezoluția și camera
influențează toate aceste valori.

## Verificare realizată

15 teste automate trecute: detecție sintetică, așteptare/dispariție, alegerea
țintelor din rânduri laterale, urmărire optică pe translație sintetică, căutare
limitată și convergența comenzilor într-o simulare cu model de cameră liniar.
Compilarea Python a trecut. Simularea nu reproduce camera și coliziunile FiveM.

Cele două clipuri finale au fost decodate integral (700 și 439 cadre). La
analiza fiecărui al șaselea cadru, au existat candidați în 116/116, respectiv
64/73 cadre. Urmărirea optică a acceptat 78/115, respectiv 49/63 asocieri.
Aceste valori sunt statistici de diagnostic, nu precizie măsurată cu etichete
manuale și nu teste ale controlului în joc. Detaliile sunt în
`clip-validation.json`. Comenzile Windows și rotirea camerei nu au fost rulate
în acest mediu Linux.
