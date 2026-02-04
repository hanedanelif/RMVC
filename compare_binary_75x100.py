# -*- coding: utf-8 -*-
"""
COMPARE BINARY MATRICES (75x100) - ITER 41, 42, 43
==================================================
Bu script, fractional membership matrislerini 0.5 eşiği ile
BINARY (0/1) matrislere dönüştürür ve bunları karşılaştırır.

Hedef: "Set Convergence" (Küme Yakınsaması) durumunda 
Binary matrislerin değişip değişmediğini kanıtlamak.
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import os

# RMVC Fonksiyonları
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

def threshold_matrix_to_df(membership_matrix, U, threshold_value, operator=">="):
    binary_data = {}
    for e_i in membership_matrix.keys():
        binary_data[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            epsilon = 1e-9
            if operator == ">=":
                above_threshold = val >= (threshold_value - epsilon)
            else:
                above_threshold = val > (threshold_value + epsilon)
            binary_data[e_i][u] = 1 if above_threshold else 0
    return pd.DataFrame(binary_data).T

if __name__ == "__main__":
    file_path = 'datasets/movielens_method1_75x100.csv'
    print(f"Loading {file_path} for Binary Comparison...")
    
    df = pd.read_csv(file_path, index_col=0)
    U, E_named = csv_to_soft_set(df, rows_are_params=True)
    
    current_E = {e_i: E_named[e_i].copy() for e_i in E_named.keys()}
    
    # Store binary matrices
    binary_matrices = {}
    
    print("\nStarting iterations...")
    for iteration in range(1, 45):
        # 1. Calc Membership
        membership_matrix = create_membership_matrix_v2(current_E, U)
        
        # 2. Threshold to Binary (This determines the NEXT sets E_{t+1})
        # Note: The RMVC paper implies sets for iter T+1 are derived from thresholding Matrix T
        binary_df = threshold_matrix_to_df(membership_matrix, U, 0.5, ">=")
        
        if iteration in [41, 42, 43]:
            fname = f'movielens_75x100_binary_iter{iteration}.csv'
            binary_df.to_csv(fname)
            binary_matrices[iteration] = binary_df
            print(f"  -> Saved Binary Matrix for Iteration {iteration}")
            
        # Stop after 43
        if iteration == 43:
            break
            
        # 3. Update Sets for next iter
        new_E = {e_i: set() for e_i in E_named.keys()}
        for e_i in binary_df.index:
            for u in binary_df.columns:
                if binary_df.loc[e_i, u] == 1:
                    new_E[e_i].add(u)
        
        if new_E == current_E:
             print(f"  [INFO] Set Stability at Iter {iteration}")
             
        current_E = new_E

    # COMPARISON
    print("\n" + "="*50)
    print("BINARY MATRIX COMPARISON REPORT")
    print("="*50)
    
    # 41 vs 42
    if 41 in binary_matrices and 42 in binary_matrices:
        diff_41_42 = binary_matrices[42] - binary_matrices[41]
        changed = (diff_41_42 != 0).sum().sum()
        print(f"\nComparing Binary Iter 41 vs 42:")
        print(f"  Changed Cells (0 <-> 1): {changed}")
        if changed == 0:
            print("  ✅ IDENTICAL (Stability Reached)")
        else:
            print(f"  ❌ DIFFERENT ({changed} changes)")
            print(diff_41_42.replace(0, np.nan).stack().dropna().head())

    # 42 vs 43
    if 42 in binary_matrices and 43 in binary_matrices:
        diff_42_43 = binary_matrices[43] - binary_matrices[42]
        changed = (diff_42_43 != 0).sum().sum()
        print(f"\nComparing Binary Iter 42 vs 43:")
        print(f"  Changed Cells (0 <-> 1): {changed}")
        if changed == 0:
            print("  ✅ IDENTICAL (Perfect Lock)")
        else:
            print(f"  ❌ DIFFERENT ({changed} changes)")
            
    print("\n" + "="*50)
