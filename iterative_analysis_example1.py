# -*- coding: utf-8 -*-
"""
Example.1 icin iteratif RMVC analizi
Her iterasyonda ondalikli degerlerin ortalamasini esik olarak kullanir (>= operatoru)
Tum degerler 1 olana kadar devam eder
"""

import pandas as pd
import numpy as np
from fractions import Fraction
from collections import defaultdict
import sys
import io

# UTF-8 encoding icin
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# RMVC fonksiyonlari
def csv_to_soft_set(df, rows_are_params=False):
    """CSV'yi soft set formatına çevir"""
    if rows_are_params:
        # Satırlar = parametreler, sütunlar = elemanlar
        valid_cols = []
        for col in df.columns:
            if pd.isna(col) or str(col).startswith('Unnamed'):
                continue
            if df[col].isna().all():
                continue
            valid_cols.append(col)
        
        df = df[valid_cols]
        # String ID kullan (Streamlit uygulaması ile aynı)
        eleman_ids = [str(i) for i in range(1, len(valid_cols) + 1)]
        parametre_ids = list(range(1, len(df) + 1))
        
        U = set(eleman_ids)
        E_named = {}
        E_info = {}
        
        for idx, (param_idx, row) in enumerate(df.iterrows(), 1):
            param_name = f"e_{idx}"
            E_named[param_name] = set()
            E_info[param_name] = {
                'orijinal_ad': str(param_idx),
                'index': idx
            }
            
            for col_idx, col_name in enumerate(valid_cols, 1):
                try:
                    deger = row[col_name]
                    numeric_val = pd.to_numeric(deger, errors='coerce')
                    if pd.notna(numeric_val) and numeric_val > 0:
                        E_named[param_name].add(str(col_idx))  # String ID ekle
                except:
                    pass
        
        return U, E_named, E_info, eleman_ids, parametre_ids
    
    return None, None, None, None, None

def create_membership_matrix(E_named, U):
    """Üyelik matrisini oluştur"""
    m = len(E_named)
    membership_matrix = {}
    
    for e_i, Phi_ei in E_named.items():
        membership_matrix[e_i] = {}
        
        for u in U:
            if u not in Phi_ei:
                membership_matrix[e_i][u] = Fraction(0, 1)
            else:
                delta_sum = Fraction(0, 1)
                for v in Phi_ei:
                    count = sum(1 for e_j, Phi_ej in E_named.items() 
                              if u in Phi_ej and v in Phi_ej)
                    delta_sum += Fraction(count, 1)
                
                denominator = len(Phi_ei) * (m - 1)
                if denominator == 0:
                    membership_matrix[e_i][u] = Fraction(0, 1)
                else:
                    membership_matrix[e_i][u] = Fraction(delta_sum.numerator, delta_sum.denominator * denominator)
    
    return membership_matrix

def calculate_scores(membership_matrix, U):
    """Skorları hesapla"""
    scores = {}
    for u in U:
        total = Fraction(0, 1)
        for e_i, row in membership_matrix.items():
            total += row.get(u, Fraction(0, 1))
        scores[u] = total
    return scores

def threshold_matrix(membership_matrix, U, threshold_value, operator=">="):
    """Eşikleme uygula"""
    new_matrix = {}
    epsilon = 1e-9
    
    for e_i in membership_matrix.keys():
        new_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            
            if operator == ">=":
                above_threshold = val >= (threshold_value - epsilon)
            else:
                above_threshold = val > threshold_value
            
            new_matrix[e_i][u] = 1 if above_threshold else 0
    
    return new_matrix

def matrix_to_dict(matrix):
    """Matrisi dict formatına çevir"""
    result = {}
    for param, values in matrix.items():
        result[param] = {k: float(v) for k, v in values.items()}
    return result

# Ana analiz
print("Example.1 İteratif RMVC Analizi Başlıyor...\n")

# Dosyayı yükle
df = pd.read_excel(r"C:\Users\user\Downloads\RMVC\Example.1..xlsx", index_col=0)
print(f"Dosya yüklendi: {df.shape[0]} parametre × {df.shape[1]} eleman\n")

# İlk RMVC hesapla
U, E_named, E_info, eleman_ids, parametre_ids = csv_to_soft_set(df, rows_are_params=True)
membership_matrix = create_membership_matrix(E_named, U)
scores = calculate_scores(membership_matrix, U)

# İterasyonları sakla
iterations = []
iterations.append({
    'iteration': 0,
    'membership_matrix': matrix_to_dict(membership_matrix),
    'scores': {k: float(v) for k, v in scores.items()},
    'threshold': None,
    'operator': None
})

print("=" * 80)
print("İTERASYON 0 (Başlangıç)")
print("=" * 80)

# İstatistikleri hesapla
all_values = []
for row in membership_matrix.values():
    all_values.extend([float(v) for v in row.values()])

fractional_values = [v for v in all_values if 0 < v < 1]
count_zeros = sum(1 for v in all_values if v == 0.0)
count_ones = sum(1 for v in all_values if v == 1.0)

print(f"Toplam Değer: {len(all_values)}")
print(f"0 Sayısı: {count_zeros}")
print(f"1 Sayısı: {count_ones}")
print(f"Ondalıklı Sayısı: {len(fractional_values)}")

if fractional_values:
    frac_mean = np.mean(fractional_values)
    frac_std = np.std(fractional_values)
    frac_min = min(fractional_values)
    frac_max = max(fractional_values)
    print(f"\nOndalıklı Değerler İstatistikleri:")
    print(f"  Min: {frac_min:.4f}")
    print(f"  Max: {frac_max:.4f}")
    print(f"  Ortalama: {frac_mean:.4f}")
    print(f"  Std Sapma: {frac_std:.4f}")
    print(f"  Adet: {len(fractional_values)}")

# Üyelik matrisini göster
print("\nÜyelik Matrisi:")
for param in sorted(membership_matrix.keys()):
    values_str = "  ".join([f"{u}:{float(membership_matrix[param][u]):.4f}" for u in sorted(U)])
    print(f"  {param}: {values_str}")

print("\n")

# İteratif analiz
iteration_num = 1
max_iterations = 20  # Sonsuz döngüyü önlemek için

while len(fractional_values) > 0 and iteration_num <= max_iterations:
    print("=" * 80)
    print(f"İTERASYON {iteration_num}")
    print("=" * 80)
    
    # Eşik değeri: ondalıklı değerlerin ortalaması
    threshold = round(np.mean(fractional_values), 4)
    print(f"Eşik Değeri: {threshold:.4f} (Ondalıklı değerlerin ortalaması)")
    print(f"Operatör: >=")
    print(f"Mod: Binary (Eşik altı 0'a dönüşür)")
    
    # Eşikleme uygula
    thresholded_matrix = threshold_matrix(membership_matrix, U, threshold, operator=">=")
    
    # Eşiklenmiş matrisi soft set formatına çevir
    new_E_named = {}
    for e_key in thresholded_matrix.keys():
        new_E_named[e_key] = set()
        for u, val in thresholded_matrix[e_key].items():
            if val == 1:
                new_E_named[e_key].add(u)
    
    # Yeni RMVC hesapla
    membership_matrix = create_membership_matrix(new_E_named, U)
    scores = calculate_scores(membership_matrix, U)
    
    # İterasyonu kaydet
    iterations.append({
        'iteration': iteration_num,
        'membership_matrix': matrix_to_dict(membership_matrix),
        'scores': {k: float(v) for k, v in scores.items()},
        'threshold': threshold,
        'operator': '>='
    })
    
    # İstatistikleri hesapla
    all_values = []
    for row in membership_matrix.values():
        all_values.extend([float(v) for v in row.values()])
    
    fractional_values = [v for v in all_values if 0 < v < 1]
    count_zeros = sum(1 for v in all_values if v == 0.0)
    count_ones = sum(1 for v in all_values if v == 1.0)
    
    print(f"\nToplam Değer: {len(all_values)}")
    print(f"0 Sayısı: {count_zeros}")
    print(f"1 Sayısı: {count_ones}")
    print(f"Ondalıklı Sayısı: {len(fractional_values)}")
    
    if fractional_values:
        frac_mean = np.mean(fractional_values)
        frac_std = np.std(fractional_values)
        frac_min = min(fractional_values)
        frac_max = max(fractional_values)
        print(f"\nOndalıklı Değerler İstatistikleri:")
        print(f"  Min: {frac_min:.4f}")
        print(f"  Max: {frac_max:.4f}")
        print(f"  Ortalama: {frac_mean:.4f}")
        print(f"  Std Sapma: {frac_std:.4f}")
        print(f"  Adet: {len(fractional_values)}")
    
    # Üyelik matrisini göster
    print("\nÜyelik Matrisi:")
    for param in sorted(membership_matrix.keys()):
        values_str = "  ".join([f"{u}:{float(membership_matrix[param][u]):.4f}" for u in sorted(U)])
        print(f"  {param}: {values_str}")
    
    print("\n")
    iteration_num += 1

print("=" * 80)
print("SONUÇ")
print("=" * 80)
print(f"Toplam İterasyon Sayısı: {len(iterations) - 1}")
print(f"Tüm değerler 1 oldu mu: {'Evet' if len(fractional_values) == 0 else 'Hayır'}")

# Sonuçları JSON olarak kaydet
import json
with open(r"C:\Users\user\Downloads\RMVC\iterative_analysis_results.json", 'w', encoding='utf-8') as f:
    json.dump(iterations, f, indent=2, ensure_ascii=False)

print("\nSonuçlar 'iterative_analysis_results.json' dosyasına kaydedildi.")
