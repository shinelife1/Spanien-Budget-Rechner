import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

class Style:
    GRUEN = '\033[92m'
    BLAU = '\033[94m'
    GELB = '\033[93m'
    ROT = '\033[91m'
    FETT = '\033[1m'
    CYAN = '\033[96m'
    ENDE = '\033[0m'
    LINIE = f"{CYAN}" + "━" * 55 + f"{ENDE}"

DATA_FILE = "spanien_data.json"

def laden():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"budget": {"Miete": 0.0, "Internet": 0.0, "Essen": 0.0, "Freizeit": 0.0}, "gehalt": 0.0}

def speichern(daten):
    with open(DATA_FILE, "w") as f:
        json.dump(daten, f, indent=4)

def zeichne_balken(anteil, breite=15):
    anzeige_anteil = max(0.0, min(1.0, anteil))
    gefuellt = int(anzeige_anteil * breite)
    return f"|{'█' * gefuellt}{'░' * (breite - gefuellt)}| {anteil*100:>3.0f}%"

def zahl_eingeben(text):
    while True:
        try:
            val = input(f"{Style.GELB}{text}{Style.ENDE}").replace(",", ".")
            return float(val)
        except ValueError:
            print(f"{Style.ROT}⚠️  Zahl eingeben!{Style.ENDE}")

def einstellungen(daten):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Style.FETT}{Style.CYAN}⚙️  KATEGORIEN BEARBEITEN{Style.ENDE}\n")
        kategorien = list(daten["budget"].keys())
        for i, kat in enumerate(kategorien, 1):
            print(f"{Style.BLAU}[{i}]{Style.ENDE} {kat:12} ({daten['budget'][kat]:>7.2f}€)")
        print(f"\n{Style.ROT}[0] Zurück zum Hauptmenü{Style.ENDE}")
        wahl = input(f"\n{Style.FETT}Wähle Kategorie: {Style.ENDE}")
        if wahl == "0": break
        if wahl.isdigit() and 1 <= int(wahl) <= len(kategorien):
            ausgewaehlt = kategorien[int(wahl)-1]
            daten["budget"][ausgewaehlt] = zahl_eingeben(f"Neuer Wert für {ausgewaehlt}: ")
            speichern(daten)

# --- START ---
daten = laden()

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Aktuelle Zeit in Berlin holen
    berlin_zeit = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y | %H:%M:%S")
    
    kosten = sum(daten["budget"].values())
    gehalt = daten["gehalt"]
    diff = gehalt - kosten
    gesamt_prozent = kosten / gehalt if gehalt > 0 else 0
    
    print(Style.LINIE)
    print(f"      {Style.FETT}🇪🇸  FINANZ-CHECK SPANIEN 2026{Style.ENDE}")
    print(Style.LINIE)
    # Anzeige von Zeit und Gehalt
    print(f"🕒 {berlin_zeit} | 💰 Netto: {Style.GRUEN}{gehalt:.2f}€{Style.ENDE}")
    print(Style.LINIE)

    for k, v in daten["budget"].items():
        anteil = v / gehalt if gehalt > 0 else 0
        f_balken = Style.BLAU if anteil <= 1.0 else Style.ROT
        print(f"{Style.FETT}{k:12}:{Style.ENDE} {v:>7.2f}€  {f_balken}{zeichne_balken(anteil)}{Style.ENDE}")

    print(Style.LINIE)
    
    farbe_gesamt = Style.GRUEN if gesamt_prozent <= 0.9 else Style.ROT
    print(f"{Style.FETT}GESAMT AUSGABEN: {Style.ROT}{kosten:>8.2f}€{Style.ENDE}  {farbe_gesamt}{zeichne_balken(gesamt_prozent)} (Vom Gehalt){Style.ENDE}")
    
    farbe_status = Style.GRUEN if diff >= 0 else Style.ROT
    print(f"{Style.FETT}RESTBUDGET     : {farbe_status}{diff:>8.2f}€{Style.ENDE}")
    
    if diff < 0:
        print(f"{Style.ROT}{Style.FETT}⚠️  WARNUNG: Du bist im Minus!{Style.ENDE}")
    
    print(Style.LINIE)
    print(f"{Style.BLAU}[1]{Style.ENDE} Kosten anpassen   {Style.BLAU}[2]{Style.ENDE} Gehalt ändern   {Style.ROT}[3]{Style.ENDE} Beenden")
    
    haupt_wahl = input(f"\n{Style.FETT}Deine Wahl: {Style.ENDE}")

    if haupt_wahl == "1": einstellungen(daten)
    elif haupt_wahl == "2":
        daten["gehalt"] = zahl_eingeben("Dein monatliches Netto-Gehalt: ")
        speichern(daten)
    elif haupt_wahl == "3":
        print(f"\n{Style.GRUEN}✅ Daten gesichert. ¡Adiós!{Style.ENDE}")
        break
