# -*- coding: utf-8 -*-
"""
Streamlit uygulamasının kullandığı üyelik matrisini debug et
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import sys
import io

# UTF-8 encoding icin
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Streamlit'deki ayni fonksiyonlar
def csv_to_soft_set(df, rows_are_params=False):
    """CSV'yi soft set formatına çevir (Streamlit uyumlu)"""
    if rows_are_params:
        parametre_ids = df.index.tolist()
        original_columns = df.columns.tolist()
        
        valid_columns = []
        for col in original_columns:
            col_str = str(col).strip()
            if not col_str or col_str.lower() == 'nan' or col_str.startswith('Unnamed'):
                continue
            try:
                col_data = pd.to_numeric(df[col], errors='coerce')
                if col_data.notna().any():
                    valid_columns.append(col)
            except:
                pass
        
        num_products = len(valid_columns)
        eleman_ids = [str(i) for i in range(1, num_products + 1)]
        U = set(eleman_ids)
        
        col_mapping = {str(i+1): valid_columns[i] for i in range(num_products)}
        
        E_named = {}
        E_info = {}
        
        for i, param_id in enumerate(parametre_ids):
            e_key = f"e_{i+1}"
            satir_verisi = df.loc[param_id]
            
            phi_e = set()
            toplam_deger = 0
            
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

# Debug analizi
print("Streamlit Üyelik Matrisi Debug Analizi\n")

# Dosyayı yükle
df = pd.read_excel(r"C:\Users\user\Downloads\RMVC\Example.1..xlsx", index_col=0)
print(f"Orijinal DataFrame:")
print(df)
print(f"\nDataFrame shape: {df.shape}")
print(f"Index: {df.index.tolist()}")
print(f"Columns: {df.columns.tolist()}")

# Soft set'e çevir
U, E_named, E_info, eleman_ids, parametre_ids = csv_to_soft_set(df, rows_are_params=True)

print(f"\nEvrensel Küme (U): {sorted(U)}")
print(f"Eleman IDs: {eleman_ids}")
print(f"Parametre IDs: {parametre_ids}")

print(f"\nE_named (Soft Set):")
for param, elements in E_named.items():
    print(f"  {param}: {sorted(elements)}")

print(f"\nE_info:")
for param, info in E_info.items():
    print(f"  {param}: {info}")

# Üyelik matrisini oluştur
membership_matrix = create_membership_matrix(E_named, U)

print(f"\nÜyelik Matrisi:")
for param in sorted(membership_matrix.keys()):
    values_str = "  ".join([f"{u}:{float(membership_matrix[param][u]):.4f}" for u in sorted(U)])
    print(f"  {param}: {values_str}")

# İstatistikler
all_values = []
for row in membership_matrix.values():
    all_values.extend([float(v) for v in row.values()])

fractional_values = [v for v in all_values if 0 < v < 1]
count_zeros = sum(1 for v in all_values if v == 0.0)
count_ones = sum(1 for v in all_values if v == 1.0)

print(f"\nİstatistikler:")
print(f"Toplam Değer: {len(all_values)}")
print(f"0 Sayısı: {count_zeros}")
print(f"1 Sayısı: {count_ones}")
print(f"Ondalıklı Sayısı: {len(fractional_values)}")

if fractional_values:
    print(f"\nOndalıklı Değerler: {[f'{v:.4f}' for v in sorted(fractional_values)]}")
    print(f"Min: {min(fractional_values):.4f}")
    print(f"Max: {max(fractional_values):.4f}")
    print(f"Ortalama: {np.mean(fractional_values):.4f}")

# Değer frekans tablosu
from collections import Counter
value_counts = Counter([round(v, 4) for v in all_values])
print(f"\nDeğer Frekans Tablosu:")
for value, count in sorted(value_counts.items()):
    percentage = (count / len(all_values)) * 100
    print(f"  {value:.4f}: {count} adet ({percentage:.1f}%)")
