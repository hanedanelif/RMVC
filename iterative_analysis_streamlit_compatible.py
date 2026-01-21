# -*- coding: utf-8 -*-
"""
Example.1 icin iteratif RMVC analizi (Streamlit uyumlu)
Streamlit uygulamasinin kullandigi ayni baslangic matrisini kullanir
"""

import pandas as pd
import numpy as np
from fractions import Fraction
from collections import defaultdict
import sys
import io

# UTF-8 encoding icin
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# RMVC fonksiyonlari (Streamlit'deki ile ayni)
def csv_to_soft_set(df, rows_are_params=False):
    """CSV'yi soft set formatina cevir (Streamlit uyumlu)"""
    if rows_are_params:
        # Hocanın formatı: Satırlar=Parametreler (e1,e2..), Sütunlar=Elemanlar (1,2..)
        
        parametre_ids = df.index.tolist()
        original_columns = df.columns.tolist()
        
        # Hocanın kodu: Sadece sayısal verileri olan sütunları al
        # Boş, NaN, Unnamed ve tamamen 0 olan sütunları filtrele
        valid_columns = []
        for col in original_columns:
            col_str = str(col).strip()
            # Boş string, NaN, Unnamed sütunları atla
            if not col_str or col_str.lower() == 'nan' or col_str.startswith('Unnamed'):
                continue
            # Sütunda en az bir sayısal değer olmalı
            try:
                col_data = pd.to_numeric(df[col], errors='coerce')
                if col_data.notna().any():
                    valid_columns.append(col)
            except:
                pass
        
        # Ürün sayısını belirle (hocanın yaklaşımı: 1'den başla)
        num_products = len(valid_columns)
        
        # U: Evrensel küme - 1'den num_products'a kadar
        eleman_ids = [str(i) for i in range(1, num_products + 1)]
        U = set(eleman_ids)
        
        # Sütun eşleştirmesi: simple_id -> original_col
        col_mapping = {str(i+1): valid_columns[i] for i in range(num_products)}
        
        # E: Parametre kümeleri
        E_named = {}
        E_info = {}
        
        for i, param_id in enumerate(parametre_ids):
            # Hocanın formatı: e_1, e_2, ... şeklinde adlandır
            e_key = f"e_{i+1}"
            satir_verisi = df.loc[param_id]
            
            phi_e = set()
            toplam_deger = 0
            
            # Her ürünü kontrol et
            for simple_id, orig_col in col_mapping.items():
                try:
                    deger = satir_verisi[orig_col]
                    numeric_val = pd.to_numeric(deger, errors='coerce')
                    if pd.notna(numeric_val) and numeric_val > 0:
                        phi_e.add(simple_id)
                        toplam_deger += numeric_val
                except:
                    pass
            
            E_named[e_key] = phi_e
            E_info[e_key] = {
                'orijinal_ad': str(param_id),
                'eleman_sayisi': len(phi_e),
                'toplam_deger': toplam_deger,
                'elemanlar': phi_e
            }
        
        return U, E_named, E_info, eleman_ids, parametre_ids
    
    return None, None, None, None, None

def delta_function(e_i, E_named, U):
    """
    Streamlit uygulamasındaki delta_function ile aynı
    """
    phi_e_i = E_named[e_i]  # Φ(e_i): e_i'ye ait elemanlar
    not_in_phi = U - phi_e_i  # U \ Φ(e_i): e_i'ye ait olmayan elemanlar
    
    results = {}
    
    for u in not_in_phi:
        delta_sum = 0
        
        # Her v ∈ Φ(e_i) için
        for v in phi_e_i:
            # {u, v} ikilisinin bulunduğu küme sayısını say
            pair = {u, v}
            
            # TÜM kümeleri kontrol et
            for e_j, phi_e_j in E_named.items():
                if pair.issubset(phi_e_j):
                    delta_sum += 1
        
        results[u] = delta_sum
    
    return results

def create_membership_matrix(E_named, U):
    """Üyelik matrisini oluştur (Streamlit ile aynı algoritma)"""
    m = len(E_named)  # Toplam parametre sayısı
    
    membership_matrix = {}
    
    for e_i in E_named.keys():
        phi_e_i = E_named[e_i]
        delta_results = delta_function(e_i, E_named, U)
        
        # γ(e_i) = |Φ(e_i)| × (m - 1)
        gamma = len(phi_e_i) * (m - 1)
        
        membership_matrix[e_i] = {}
        
        for u in U:
            if u in phi_e_i:
                # u ∈ Φ(e_i) → Tam üyelik
                membership_matrix[e_i][u] = Fraction(1, 1)
            else:
                # u ∉ Φ(e_i) → Kısmi üyelik
                if gamma > 0 and u in delta_results:
                    delta_val = delta_results[u]
                    membership_matrix[e_i][u] = Fraction(delta_val, gamma)
                else:
                    membership_matrix[e_i][u] = Fraction(0, 1)
    
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
print("Example.1 İteratif RMVC Analizi Başlıyor (Streamlit Uyumlu)...\n")

# Dosyayı yükle
df = pd.read_excel(r"C:\Users\user\Downloads\RMVC\Example.1..xlsx", index_col=0)
print(f"Dosya yüklendi: {df.shape[0]} parametre × {df.shape[1]} eleman\n")

# Streamlit ile aynı başlangıç noktasını kullan
U, E_named, E_info, eleman_ids, parametre_ids = csv_to_soft_set(df, rows_are_params=True)
membership_matrix = create_membership_matrix(E_named, U)
scores = calculate_scores(membership_matrix, U)

# İterasyonları sakla (Streamlit session state gibi)
iterations = []
iterations.append({
    'iteration': 0,
    'membership_matrix': matrix_to_dict(membership_matrix),
    'scores': {k: float(v) for k, v in scores.items()},
    'threshold': None,
    'operator': None
})

print("=" * 80)
print("İTERASYON 0 (Başlangıç - Streamlit ile aynı)")
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
with open(r"C:\Users\user\Downloads\RMVC\iterative_analysis_streamlit_compatible.json", 'w', encoding='utf-8') as f:
    json.dump(iterations, f, indent=2, ensure_ascii=False)

print("\nSonuçlar 'iterative_analysis_streamlit_compatible.json' dosyasına kaydedildi.")
