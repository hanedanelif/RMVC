# -*- coding: utf-8 -*-
"""
CORRECT THRESHOLD METHOD - 75x100 Reanalysis
=============================================
Bu script, DOĞRU eşikleme metodunu kullanır:
- Her iterasyonda fractional değerlerin ortalaması hesaplanır
- Bu dinamik eşik kullanılarak binary dönüşüm yapılır
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import os

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

def calculate_dynamic_threshold(membership_matrix):
    """
    DOĞRU YÖNTEM: 0 ve 1 dışındaki (fractional) değerlerin ortalamasını al
    """
    fractional_values = []
    for e_i in membership_matrix:
        for u in membership_matrix[e_i]:
            val = float(membership_matrix[e_i][u])
            if 0 < val < 1:  # Sadece ondalıklı değerler
                fractional_values.append(val)
    
    if fractional_values:
        threshold = np.mean(fractional_values)
    else:
        threshold = 0.5  # Fallback (eğer ondalık değer yoksa)
    
    return threshold, len(fractional_values)

def threshold_matrix_dynamic(membership_matrix, U, threshold_value):
    """
    Dinamik eşik kullanarak binary dönüşüm
    """
    binary_matrix = {}
    for e_i in membership_matrix.keys():
        binary_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            # Eşiğe EŞİT veya BÜYÜK olanlar 1 olur
            binary_matrix[e_i][u] = 1 if val >= threshold_value else 0
    return binary_matrix

def is_binary_matrix(matrix, U):
    for e_i in matrix.keys():
        for u in U:
            val = float(matrix[e_i].get(u, 0))
            if val not in [0.0, 1.0]:
                return False
    return True

if __name__ == "__main__":
    file_path = 'datasets/movielens_method1_75x100.csv'
    print(f"Loading {file_path}...")
    print("Using CORRECT threshold method (dynamic mean of fractional values)\n")
    
    df = pd.read_csv(file_path, index_col=0)
    U, E_named = csv_to_soft_set(df, rows_are_params=True)
    
    current_E = {e_i: E_named[e_i].copy() for e_i in E_named.keys()}
    
    print(f"{'Iter':<6} {'Binary?':<10} {'Threshold':<12} {'Fractional':<12} {'Set Stable?':<12}")
    print("="*60)
    
    for iteration in range(1, 50):
        # 1. Calculate Membership Matrix
        membership_matrix = create_membership_matrix_v2(current_E, U)
        
        # 2. Check if already binary
        is_binary = is_binary_matrix(membership_matrix, U)
        
        # 3. Calculate DYNAMIC threshold
        threshold, num_fractional = calculate_dynamic_threshold(membership_matrix)
        
        # 4. Apply threshold to get binary matrix
        binary_matrix = threshold_matrix_dynamic(membership_matrix, U, threshold)
        
        # 5. Update sets for next iteration
        new_E = {e_i: set() for e_i in E_named.keys()}
        for e_i in E_named.keys():
            for u in U:
                if binary_matrix[e_i][u] == 1:
                    new_E[e_i].add(u)
        
        # 6. Check set stability
        set_stable = (new_E == current_E)
        
        # Print status
        print(f"{iteration:<6} {str(is_binary):<10} {threshold:.6f}    {num_fractional:<12} {str(set_stable):<12}")
        
        # 7. Stop conditions
        if set_stable and is_binary:
            print(f"\n✅ CONVERGED at iteration {iteration}")
            print(f"   Sets are stable AND matrix is binary!")
            break
        elif set_stable and not is_binary:
            print(f"\n⚠️ ANOMALY at iteration {iteration}")
            print(f"   Sets are stable BUT matrix is NOT binary!")
            print(f"   Continuing to see if it eventually becomes binary...")
            # Don't break, continue to see what happens
        
        if iteration >= 45:
            print(f"\n⏹️ Stopped at iteration {iteration} (max iterations reached)")
            break
        
        current_E = new_E
