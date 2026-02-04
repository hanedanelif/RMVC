# -*- coding: utf-8 -*-
"""
REPRODUCE 75x100 ANOMALY - COMPARE ITER 41 vs 42
================================================
Bu script, 75x100 MovieLens matrisindeki anomaliyi yeniden üretir.
Özellikle İterasyon 41 ve 42'yi kaydedip aralarındaki farkı analiz eder.
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import os

# RMVC Fonksiyonları (V2)
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

def threshold_matrix(membership_matrix, U, threshold_value, operator=">="):
    binary_matrix = {}
    for e_i in membership_matrix.keys():
        binary_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            epsilon = 1e-9
            if operator == ">=":
                above_threshold = val >= (threshold_value - epsilon)
            else:
                above_threshold = val > (threshold_value + epsilon)
            binary_matrix[e_i][u] = 1 if above_threshold else 0
    return binary_matrix

def matrix_to_float_df(membership_matrix):
    float_matrix = {}
    for e_i in membership_matrix:
        float_matrix[e_i] = {}
        for u in membership_matrix[e_i]:
            float_matrix[e_i][u] = float(membership_matrix[e_i][u])
    return pd.DataFrame(float_matrix).T

# Main Reproduction Logic
if __name__ == "__main__":
    file_path = 'datasets/movielens_method1_75x100.csv'
    print(f"Loading {file_path}...")
    
    df = pd.read_csv(file_path, index_col=0)
    U, E_named = csv_to_soft_set(df, rows_are_params=True)
    
    current_E = {e_i: E_named[e_i].copy() for e_i in E_named.keys()}
    
    # Saklamak için değişkenler
    matrix_iter_41 = None
    matrix_iter_42 = None
    
    print("\nStarting iterations to capture 41 and 42...")
    for iteration in range(1, 46):
        print(f"Processing Iteration {iteration}...")
        
        # RMVC Hesapla
        membership_matrix = create_membership_matrix_v2(current_E, U)
        
        # İterasyon 41'i yakala
        if iteration == 41:
            matrix_iter_41 = matrix_to_float_df(membership_matrix)
            matrix_iter_41.to_csv('movielens_75x100_iter41.csv')
            print("  -> Saved Iteration 41 matrix")
            
        # İterasyon 42'yi yakala
        if iteration == 42:
            matrix_iter_42 = matrix_to_float_df(membership_matrix)
            matrix_iter_42.to_csv('movielens_75x100_iter42.csv')
            print("  -> Saved Iteration 42 matrix")
            
            # Fark Analizi
            print("\nCalculating Difference (Iter 42 - Iter 41)...")
            diff_matrix = matrix_iter_42 - matrix_iter_41
            diff_matrix.to_csv('movielens_75x100_diff_41_42.csv')
            
            # İstatistikler
            total_cells = diff_matrix.size
            changed_cells = (diff_matrix != 0).sum().sum()
            max_change = diff_matrix.max().max()
            min_change = diff_matrix.min().min()
            mean_abs_change = diff_matrix.abs().mean().mean()
            
            print(f"  Total Cells: {total_cells}")
            print(f"  Changed Cells: {changed_cells} ({(changed_cells/total_cells)*100:.2f}%)")
            print(f"  Max Positive Change: {max_change:.6f}")
            print(f"  Max Negative Change: {min_change:.6f}")
            print(f"  Mean Absolute Change: {mean_abs_change:.6f}")
            
            # En büyük değişimin olduğu hücreleri göster
            print("\n  Top 5 Largest Changes:")
            diff_stacked = diff_matrix.stack()
            diff_abs = diff_stacked.abs().sort_values(ascending=False)
            print(diff_stacked.loc[diff_abs.index[:5]])
            
            break
        
        # Threshold ve Update
        binary_matrix_next = threshold_matrix(membership_matrix, U, 0.5, ">=")
        new_E = {e_i: set() for e_i in E_named.keys()}
        for e_i in E_named.keys():
            for u in U:
                if binary_matrix_next[e_i][u] == 1:
                    new_E[e_i].add(u)
                    
        # Check stability just for info, though we force stop at 42
        if new_E == current_E:
            print(f"  Set Stability Reached at Iter {iteration}")
            
        current_E = new_E
