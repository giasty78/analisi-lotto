
import csv
import datetime
import glob
import zipfile
import urllib.request
from collections import defaultdict
from pathlib import Path

URL = "https://www.brightstarlottery.it/STORICO_ESTRAZIONI_LOTTO/storico01-oggi.zip"
RUOTE = ["BA", "CA", "FI", "GE", "MI", "NA", "PA", "RO", "TO", "VE", "NZ"]

urllib.request.urlretrieve(URL, "storico.zip")

Path("archivio").mkdir(exist_ok=True)

with zipfile.ZipFile("storico.zip") as z:
    z.extractall("archivio")

files = glob.glob("archivio/**/*.txt", recursive=True)

if not files:
    raise SystemExit("File TXT non trovato nell'archivio")

dati = defaultdict(dict)

with open(files[0], encoding="latin-1") as f:
    for line in f:
        p = line.split()

        if len(p) < 7:
            continue

        data, ruota = p[0], p[1]
        ruota = {"RM": "RO"}.get(ruota, ruota)

        if ruota not in RUOTE:
            continue

        try:
            data = datetime.datetime.strptime(
                data, "%Y/%m/%d"
            ).strftime("%d/%m/%Y")
            numeri = [int(x) for x in p[2:7]]
        except ValueError:
            continue

        if all(1 <= n <= 90 for n in numeri):
            dati[data][ruota] = numeri

intestazione = ["Data", "Estrazione"] + [
    r + str(n) for r in RUOTE for n in range(1, 6)
]

righe = []

for data, valori in dati.items():
    if all(r in valori for r in RUOTE):
        riga = [data, ""]

        for r in RUOTE:
            riga.extend(valori[r])

        righe.append((
            datetime.datetime.strptime(data, "%d/%m/%Y"),
            riga
        ))

righe.sort(key=lambda x: x[0])

with open(
    "archivio_lotto_ufficiale.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:
    writer = csv.writer(f)
    writer.writerow(intestazione)

    for i, (_, riga) in enumerate(righe, 1):
        riga[1] = i
        writer.writerow(riga)

print("Estrazioni salvate:", len(righe))

if not righe:
    raise SystemExit("Errore: nessuna estrazione completa")
  
