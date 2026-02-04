# -*- coding: utf-8 -*-
"""
REPRODUCE 75x100 ANOMALY
========================
Bu script, 75x100 MovieLens matrisindeki anomaliyi yeniden üretir ve
final üyelik matrisini CSV olarak kaydeder.
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

def is_binary_matrix(matrix, U):
    for e_i in matrix.keys():
        for u in U:
            val = float(matrix[e_i].get(u, 0))
            if val not in [0.0, 1.0]:
                return False
    return True

# Main Reproduction Logic
if __name__ == "__main__":
    file_path = 'datasets/movielens_method1_75x100.csv'
    print(f"Loading {file_path} to reproduce anomaly...")
    
    df = pd.read_csv(file_path, index_col=0)
    U, E_named = csv_to_soft_set(df, rows_are_params=True)
    
    # Initialize binary matrix
    binary_matrix = {}
    for e_i in E_named.keys():
        binary_matrix[e_i] = {}
        for u in U:
            binary_matrix[e_i][u] = 1 if u in E_named[e_i] else 0
            
    current_E = {e_i: E_named[e_i].copy() for e_i in E_named.keys()}
    
    print("\nStarting iterations (max 45)...")
    for iteration in range(1, 46):
        membership_matrix = create_membership_matrix_v2(current_E, U)
        is_binary = is_binary_matrix(membership_matrix, U)
        
        # Apply threshold
        binary_matrix_next = threshold_matrix(membership_matrix, U, 0.5, ">=")
        
        # New sets
        new_E = {e_i: set() for e_i in E_named.keys()}
        for e_i in E_named.keys():
            for u in U:
                if binary_matrix_next[e_i][u] == 1:
                    new_E[e_i].add(u)
                    
        # Check set stability
        set_stable = (new_E == current_E)
        
        print(f"Iter {iteration}: Binary={is_binary}, Set Stable={set_stable}")
        
        if set_stable and not is_binary:
            print(f"\n!!!! ANOMALY DETECTED AT ITERATION {iteration} !!!!")
            print("Sets have stabilized, but matrix is NOT binary.")
            
            # Save the fractional matrix
            output_file = 'movielens_75x100_anomaly_membership.csv'
            
            # Convert Fraction objects to floats for CSV
            float_matrix = {}
            fractional_values = []
            
            for e_i in membership_matrix:
                float_matrix[e_i] = {}
                for u in membership_matrix[e_i]:
                    val = float(membership_matrix[e_i][u])
                    float_matrix[e_i][u] = val
                    if val > 0 and val < 1:
                        fractional_values.append(val)
            
            df_out = pd.DataFrame(float_matrix).T
            df_out.to_csv(output_file)
            print(f"Saved anomaly matrix to: {output_file}")
            
            # Print sample fractional values
            print("\nSample fractional values (near 0.5):")
            near_threshold = [v for v in fractional_values if 0.45 < v < 0.55]
            print(f"Total non-binary values: {len(fractional_values)}")
            print(f"Values between 0.45 and 0.55: {len(near_threshold)}")
            print(f" Examples: {near_threshold[:10]}")
            
            break
            
        current_E = new_E
