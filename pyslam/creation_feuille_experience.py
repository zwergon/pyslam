import csv
from pathlib import Path


class CreationFeuilleExperience:
    def __init__(self, liste_noms_colonnes_csv: list[str], liste_types_colonnes_csv: list[str], path_csv: Path|str):
        self.liste_noms = liste_noms_colonnes_csv
        self.liste_types = liste_types_colonnes_csv
        self.rows_csv = []
        self.path = path_csv
    
    def ajout_ligne(self, ligne: list):
        self.rows_csv.append(ligne)

    def exporte_csv(self):
        with open(self.path, "w", newline='') as f:
            writer = csv.writer(f, delimiter=";") # On utilise la convention française ici à savoir que les délimitations sont faites par des ";" et pas par des ","
            writer.writerow(self.liste_noms)
            writer.writerow(self.liste_types)
            writer.writerows(self.rows_csv)