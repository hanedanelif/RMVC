# -*- coding: utf-8 -*-
"""
10x10 Textile DETAILED ITERATION ANALYSIS
==========================================
Her iterasyondaki tüm detayları kaydeder:
- Tam membership matrix
- Fractional değerler listesi
- Threshold değeri
- Binary matrix
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import json

def csv_to_soft_set(df, rows_are_params=False):
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
        for i, param_id in enumerate(parametre_ids):
            e_key = f"e_{i+1}"
            satir_verisi = df.loc[param_id]
            phi_e = set()
            for simple_id, orig_col in col_mapping.items():
                try:
                    deger = satir_verisi[orig_col]
                    numeric_val = pd.to_numeric(deger, errors='coerce')
                    if pd.notna(numeric_val) and numeric_val > 0:
                        phi_e.add(simple_id)
                except:
                    pass
            E_named[e_key] = phi_e
    return U, E_named

def delta_function_v2(e_i, E_named, U):
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    results = {}
    for u in not_in_phi:
        delta_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            for e_j, phi_e_j in E_named.items():
                if pair.issubset(phi_e_j):
                    delta_sum += 1
        results[u] = delta_sum
    return results

def create_membership_matrix_v2(E_named, U):
    m = len(E_named)
    membership_matrix = {}
    for e_i in E_named.keys():
        phi_e_i = E_named[e_i]
        delta_results = delta_function_v2(e_i, E_named, U)
        gamma = len(phi_e_i) * (m - 1)
        membership_matrix[e_i] = {}
        for u in U:
            if u in phi_e_i:
                membership_matrix[e_i][u] = Fraction(1, 1)
            else:
                if gamma > 0 and u in delta_results:
                    delta_val = delta_results[u]
                    membership_matrix[e_i][u] = Fraction(delta_val, gamma)
                else:
                    membership_matrix[e_i][u] = Fraction(0, 1)
    return membership_matrix

def matrix_to_float_dict(membership_matrix):
    """Fraction'ları float'a çevir"""
    float_matrix = {}
    for e_i in membership_matrix:
        float_matrix[e_i] = {}
        for u in membership_matrix[e_i]:
            float_matrix[e_i][u] = float(membership_matrix[e_i][u])
    return float_matrix

def calculate_dynamic_threshold(membership_matrix):
    fractional_values = []
    fractional_cells = []  # Hangi hücreler fractional
    
    for e_i in membership_matrix:
        for u in membership_matrix[e_i]:
            val = float(membership_matrix[e_i][u])
            if 0 < val < 1:
                fractional_values.append(val)
                fractional_cells.append({
                    'row': e_i,
                    'col': u,
                    'value': val,
                    'fraction': str(membership_matrix[e_i][u])
                })
    
    if fractional_values:
        threshold = np.mean(fractional_values)
    else:
        threshold = 0.5
        
    return threshold, fractional_cells

def threshold_matrix_dynamic(membership_matrix, U, threshold_value):
    binary_matrix = {}
    for e_i in membership_matrix.keys():
        binary_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            binary_matrix[e_i][u] = 1 if val >= threshold_value else 0
    return binary_matrix

if __name__ == "__main__":
    file_path = 'Textile_data/outputs/raw_matrices/textile_10x10_miktar_raw.csv'
    
    print("="*70)
    print("10×10 TEXTILE (MIKTAR) - DETAYLI İTERASYON ANALİZİ")
    print("="*70)
    
    df = pd.read_csv(file_path, index_col=0)
    U, E_named = csv_to_soft_set(df, rows_are_params=True)
    
    print(f"\nBaşlangıç Bilgileri:")
    print(f"  Satır (Parametre) Sayısı: {len(E_named)}")
    print(f"  Sütun (Ürün) Sayısı: {len(U)}")
    print(f"  Yoğunluk: {sum(len(v) for v in E_named.values()) / (len(E_named) * len(U)) * 100:.1f}%")
    
    current_E = {e_i: E_named[e_i].copy() for e_i in E_named.keys()}
    
    all_iterations = []
    
    # Maximum 15 iterasyon kaydet (yeterince detaylı)
    for iteration in range(1, 16):
        print(f"\n{'='*70}")
        print(f"İTERASYON {iteration}")
        print(f"{'='*70}")
        
        # 1. Membership Matrix hesapla
        membership_matrix = create_membership_matrix_v2(current_E, U)
        float_matrix = matrix_to_float_dict(membership_matrix)
        
        # 2. Threshold ve fractional cells
        threshold, fractional_cells = calculate_dynamic_threshold(membership_matrix)
        
        print(f"\n1. MEMBERSHIP MATRİS:")
        df_membership = pd.DataFrame(float_matrix).T
        print(df_membership.to_string())
        
        print(f"\n2. ONDALIKLI HÜCRELER ({len(fractional_cells)} adet):")
        if fractional_cells:
            for i, cell in enumerate(fractional_cells, 1):
                print(f"   {i}. {cell['row']}, Col {cell['col']}: {cell['value']:.6f} ({cell['fraction']})")
            print(f"\n   ORTALAMA (THRESHOLD): {threshold:.6f}")
        else:
            print("   Tüm değerler binary (0 veya 1)!")
        
        # 3. Binary matrix
        binary_matrix = threshold_matrix_dynamic(membership_matrix, U, threshold)
        df_binary = pd.DataFrame(binary_matrix).T
        
        print(f"\n3. BINARY MATRİS (τ={threshold:.6f}):")
        print(df_binary.to_string())
        
        # 4. Yeni kümeler
        new_E = {e_i: set() for e_i in E_named.keys()}
        for e_i in E_named.keys():
            for u in U:
                if binary_matrix[e_i][u] == 1:
                    new_E[e_i].add(u)
        
        # 5. Kararlılık kontrolü
        set_stable = (new_E == current_E)
        is_binary = (len(fractional_cells) == 0)
        
        print(f"\n4. DURUM:")
        print(f"   Set Stability: {'✅ STAB' if set_stable else '❌ DEĞİŞİYOR'}")
        print(f"   Binary Matrix: {'✅ TAM BINARY' if is_binary else f'❌ {len(fractional_cells)} FRACTIONAL'}")
        
        # Kaydet
        iteration_data = {
            'iteration': iteration,
            'threshold': float(threshold),
            'num_fractional': len(fractional_cells),
            'fractional_cells': fractional_cells,
            'membership_matrix': float_matrix,
            'binary_matrix': {e_i: binary_matrix[e_i] for e_i in binary_matrix},
            'set_stable': set_stable,
            'is_binary': is_binary
        }
        all_iterations.append(iteration_data)
        
        # Matrisleri CSV olarak kaydet
        df_membership.to_csv(f'textile_10x10_iter{iteration}_membership.csv')
        df_binary.to_csv(f'textile_10x10_iter{iteration}_binary.csv')
        
        if set_stable and is_binary:
            print(f"\n{'='*70}")
            print(f"✅ YAKINSAMA: İterasyon {iteration}")
            print(f"{'='*70}")
            break
        elif set_stable and not is_binary:
            print(f"\n{'='*70}")
            print(f"⚠️ ANOMALİ: Küme stabil ama {len(fractional_cells)} fractional hücre var!")
            print(f"{'='*70}")
            # Anomali durumunda 5 iterasyon daha kaydet
            if iteration >= 15:
                break
        
        current_E = new_E
    
    # JSON'a kaydet
    with open('textile_10x10_detailed_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(all_iterations, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n{'='*70}")
    print("KAYITLI DOSYALAR:")
    print("="*70)
    print(f"  JSON: textile_10x10_detailed_analysis.json")
    for i in range(1, min(16, len(all_iterations)+1)):
        print(f"  CSV: textile_10x10_iter{i}_membership.csv, textile_10x10_iter{i}_binary.csv")
