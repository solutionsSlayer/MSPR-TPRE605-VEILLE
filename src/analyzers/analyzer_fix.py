def run_full_analysis(self):
    """
    Méthode d'adaptation qui appelle run_complete_analysis pour maintenir la compatibilité
    avec le code existant dans main.py
    """
    print("Info: Redirection de run_full_analysis() vers run_complete_analysis()")
    return self.run_complete_analysis()

# Ajouter la méthode à la classe QuantumCryptoAnalyzer
import sys
import importlib.util
from src.analyzers.quantum_crypto_analyzer import QuantumCryptoAnalyzer

# Ajouter la méthode dynamiquement
QuantumCryptoAnalyzer.run_full_analysis = run_full_analysis

print("Fix appliqué: Méthode run_full_analysis ajoutée à QuantumCryptoAnalyzer")