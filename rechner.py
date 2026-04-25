import customtkinter as ctk
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

# Design-Einstellungen
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fenster-Setup
        self.title("🇪🇸 Spanien Finanz-Check 2026")
        self.geometry("700x600")
        
        # Daten laden
        self.data_file = "spanien_data.json"
        self.daten = self.laden()

        # Layout
        self.grid_columnconfigure(1, weight=1)
        
        # --- UI ELEMENTE ---
        self.header = ctk.CTkLabel(self, text="FINANZ-CHECK SPANIEN", font=("Arial", 26, "bold"), text_color="#3a7ebf")
        self.header.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # Zeit-Anzeige
        self.zeit_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.zeit_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        self.uhrzeit_update()

        # Eingabe-Bereich
        self.entries = {}
        self.progress_bars = {}
        self.percent_labels = {}

        kategorien = list(self.daten["budget"].keys())
        for i, kat in enumerate(kategorien):
            # Label
            lbl = ctk.CTkLabel(self, text=f"{kat}:", font=("Arial", 14, "bold"))
            lbl.grid(row=i+2, column=0, padx=20, pady=10, sticky="w")
            
            # Eingabefeld
            ent = ctk.CTkEntry(self, width=120)
            ent.insert(0, str(self.daten["budget"][kat]))
            ent.grid(row=i+2, column=1, padx=(0, 200), pady=10, sticky="e")
            self.entries[kat] = ent

            # Fortschrittsbalken
            bar = ctk.CTkProgressBar(self, width=150)
            bar.grid(row=i+2, column=1, padx=(200, 50), pady=10, sticky="e")
            bar.set(0)
            self.progress_bars[kat] = bar

            # Prozent-Label
            p_lbl = ctk.CTkLabel(self, text="0%", font=("Arial", 12))
            p_lbl.grid(row=i+2, column=1, padx=10, pady=10, sticky="e")
            self.percent_labels[kat] = p_lbl

        # Gehalt-Bereich
        self.sep = ctk.CTkLabel(self, text="─" * 60, text_color="gray")
        self.sep.grid(row=7, column=0, columnspan=2)

        self.gehalt_label = ctk.CTkLabel(self, text="Netto-Gehalt:", font=("Arial", 16, "bold"), text_color="#2fa572")
        self.gehalt_label.grid(row=8, column=0, padx=20, pady=20, sticky="w")
        
        self.gehalt_entry = ctk.CTkEntry(self, width=120, border_color="#2fa572")
        self.gehalt_entry.insert(0, str(self.daten["gehalt"]))
        self.gehalt_entry.grid(row=8, column=1, padx=(0, 200), pady=20, sticky="e")

        # Aktualisieren Button
        self.btn = ctk.CTkButton(self, text="BERECHNEN & SPEICHERN", command=self.aktualisieren, 
                                 fg_color="#2fa572", hover_color="#1e6e4c", font=("Arial", 14, "bold"))
        self.btn.grid(row=9, column=0, columnspan=2, pady=20, padx=40, sticky="ew")

        # Dashboard / Ergebnis
        self.result_frame = ctk.CTkFrame(self, fg_color="#212121", corner_radius=15)
        self.result_frame.grid(row=10, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        self.result_text = ctk.CTkLabel(self.result_frame, text="Werte eingeben und berechnen", font=("Arial", 15))
        self.result_text.pack(pady=20)

        # Initialer Check
        self.aktualisieren()

    def uhrzeit_update(self):
        berlin_zeit = datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m.%Y | %H:%M:%S")
        self.zeit_label.configure(text=f"🕒 Berlin: {berlin_zeit}")
        self.after(1000, self.uhrzeit_update) # Jede Sekunde selbst aufrufen

    def laden(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except: pass
        return {"budget": {"Miete": 0.0, "Internet": 0.0, "Essen": 0.0, "Freizeit": 0.0}, "gehalt": 0.0}

    def speichern(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.daten, f, indent=4)
        except PermissionError:
            self.result_text.configure(text="FEHLER: Datei blockiert!", text_color="red")

    def aktualisieren(self):
        try:
            gehalt = float(self.gehalt_entry.get().replace(",", "."))
            self.daten["gehalt"] = gehalt
            gesamt_kosten = 0

            for kat in self.entries:
                wert = float(self.entries[kat].get().replace(",", "."))
                self.daten["budget"][kat] = wert
                gesamt_kosten += wert
                
                # Balken berechnen
                anteil = wert / gehalt if gehalt > 0 else 0
                self.progress_bars[kat].set(min(1.0, anteil))
                self.percent_labels[kat].configure(text=f"{int(anteil*100)}%")
                
                # Farbe des Balkens
                if anteil > 0.5: self.progress_bars[kat].configure(progress_color="orange")
                if anteil > 1.0: self.progress_bars[kat].configure(progress_color="red")
                else: self.progress_bars[kat].configure(progress_color="#3a7ebf")

            diff = gehalt - gesamt_kosten
            prozent_total = gesamt_kosten / gehalt if gehalt > 0 else 0
            
            # Ergebnis-Text
            res_farbe = "#2fa572" if diff >= 0 else "#dc3545"
            warnung = "\n⚠️ WARNUNG: BUDGET ÜBERSCHRITTEN!" if diff < 0 else ""
            
            output = (f"Gesamtausgaben: {gesamt_kosten:.2f}€ ({int(prozent_total*100)}%)\n"
                     f"Restbudget: {diff:.2f}€\n{warnung}")
            
            self.result_text.configure(text=output, text_color=res_farbe)
            self.speichern()

        except ValueError:
            self.result_text.configure(text="⚠️ Fehler: Bitte nur Zahlen eingeben!", text_color="orange")

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
