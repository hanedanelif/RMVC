# -*- coding: utf-8 -*-
"""
MovieLens + Tekstil - EPSILON DÜZELTMESİ İLE TEST
================================================
Threshold karşılaştırmasına epsilon=1e-9 toleransı eklendi.
Bu, floating point precision hatalarını önler.
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import json
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
    fractional_values = []
    for e_i in membership_matrix:
        for u in membership_matrix[e_i]:
            val = float(membership_matrix[e_i][u])
            if 0 < val < 1:
                fractional_values.append(val)
    if fractional_values:
        return np.mean(fractional_values), len(fractional_values)
    else:
        return 0.5, 0

def threshold_matrix_dynamic_WITH_EPSILON(membership_matrix, U, threshold_value):
    """
    ✅ DÜZELTİLDİ: Epsilon toleransı eklendi!
    """
    epsilon = 1e-9  # ← BURADA EPSİLON!
    binary_matrix = {}
    for e_i in membership_matrix.keys():
        binary_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            # ↓ EPSİLON İLE KARŞILAŞTIRMA ↓
            binary_matrix[e_i][u] = 1 if val >= (threshold_value - epsilon) else 0
    return binary_matrix

def is_binary_matrix(matrix, U):
    for e_i in matrix.keys():
        for u in U:
            val = float(matrix[e_i].get(u, 0))
            if val not in [0.0, 1.0]:
                return False
    return True

def run_single_test(file_path, max_iterations=100):
    df = pd.read_csv(file_path, index_col=0)
    U, E_named = csv_to_soft_set(df, rows_are_params=True)
    
    rows, cols = len(E_named), len(U)
    density = sum(len(v) for v in E_named.values()) / (rows * cols) * 100
    
    current_E = {e_i: E_named[e_i].copy() for e_i in E_named.keys()}
    
    iteration_data = []
    
    for iteration in range(1, max_iterations + 1):
        membership_matrix = create_membership_matrix_v2(current_E, U)
        is_binary = is_binary_matrix(membership_matrix, U)
        threshold, num_fractional = calculate_dynamic_threshold(membership_matrix)
        
        # ↓ EPSİLON İLE THRESHOLD ↓
        binary_matrix = threshold_matrix_dynamic_WITH_EPSILON(membership_matrix, U, threshold)
        
        new_E = {e_i: set() for e_i in E_named.keys()}
        for e_i in E_named.keys():
            for u in U:
                if binary_matrix[e_i][u] == 1:
                    new_E[e_i].add(u)
        
        set_stable = (new_E == current_E)
        
        iteration_data.append({
            'iteration': iteration,
            'is_binary': is_binary,
            'threshold': float(threshold),
            'num_fractional': num_fractional,
            'set_stable': set_stable
        })
        
        if set_stable and is_binary:
            return {
                'file': os.path.basename(file_path),
                'rows': rows,
                'cols': cols,
                'density': round(density, 2),
                'converged': True,
                'final_iteration': iteration,
                'iterations': iteration_data
            }
        
        current_E = new_E
    
    return {
        'file': os.path.basename(file_path),
        'rows': rows,
        'cols': cols,
        'density': round(density, 2),
        'converged': False,
        'final_iteration': max_iterations,
        'iterations': iteration_data
    }

if __name__ == "__main__":
    print("="*70)
    print("EPSİLON DÜZELTMESİ İLE KAPSAMLI TEST")
    print("Epsilon = 1e-9")
    print("="*70)
    
    all_results = []
    
    # MovieLens
    print("\n[1] MOVİELENS TESTLERİ")
    print("-" * 70)
    movielens_files = [
        'datasets/movielens_method1_10x20.csv',
        'datasets/movielens_method1_20x30.csv',
        'datasets/movielens_method1_30x50.csv',
        'datasets/movielens_method1_75x100.csv',
    ]
    
    for f in movielens_files:
        if os.path.exists(f):
            print(f"\nTesting: {os.path.basename(f)}")
            result = run_single_test(f, max_iterations=100)
            result['dataset'] = 'MovieLens'
            all_results.append(result)
            status = f"✅ {result['final_iteration']} iter" if result['converged'] else "❌ No conv"
            print(f"  {status}")
    
    # Tekstil
    print("\n[2] TEKSTİL TESTLERİ")
    print("-" * 70)
    
    dimensions = [('10', '10'), ('10', '20'), ('20', '20'), ('20', '30'), ('30', '50'), ('50', '50')]
    methods = [('miktar_raw', 'Miktar'), ('alimsayisi_raw', 'AlimSayisi'), ('totalscore_raw', 'TotalScore')]
    
    for rows, cols in dimensions:
        for method_id, method_name in methods:
            file_path = f'Textile_data/outputs/raw_matrices/textile_{rows}x{cols}_{method_id}.csv'
            if os.path.exists(file_path):
                print(f"\nTesting: {rows}x{cols} - {method_name}")
                result = run_single_test(file_path, max_iterations=100)
                result['dataset'] = 'Textile'
                result['method'] = method_name
                all_results.append(result)
                status = f"✅ {result['final_iteration']} iter" if result['converged'] else "❌ No conv"
                print(f"  {status}")
    
    # Kaydet
    with open('epsilon_corrected_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("ÖZET")
    print("="*70)
    
    converged = sum(1 for r in all_results if r['converged'])
    total = len(all_results)
    
    print(f"\nToplam Test: {total}")
    print(f"Yakınsayan: {converged}")
    print(f"Yakınsamayan: {total - converged}")
    print(f"Başarı Oranı: {converged/total*100:.1f}%")
    
    print(f"\nSonuçlar: epsilon_corrected_results.json")
