# -*- coding: utf-8 -*-
"""
10+10 Matris Karşılaştırmalı Test
=================================
MovieLens ve Tekstil'den 10'ar matris epsilon ile test
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import json
from pathlib import Path

# ================== RMVC FONKSİYONLARI (EPSİLON İLE) ==================

def csv_to_soft_set(csv_file):
    """CSV dosyasından yumuşak küme oluştur"""
    df = pd.read_csv(csv_file, header=None)
    E = [f"e{i+1}" for i in range(len(df))]
    U_temp = [f"u{j+1}" for j in range(len(df.columns))]
    
    soft_set = {}
    for i, e_i in enumerate(E):
        soft_set[e_i] = set()
        for j, u in enumerate(U_temp):
            if df.iloc[i, j] == 1:
                soft_set[e_i].add(u)
    
    U = set(U_temp)
    return soft_set, U, E

def delta_function_v2(u, phi_ei, soft_set):
    """Delta fonksiyonu - V2"""
    delta_sum = 0
    for v in phi_ei:
        if v == u:
            continue
        for e_j, phi_ej in soft_set.items():
            if u in phi_ej and v in phi_ej:
                delta_sum += 1
    return delta_sum

def create_membership_matrix_v2(soft_set, U):
    """Üyelik matrisi oluştur"""
    membership_matrix = {}
    m = len(soft_set)
    
    for e_i, phi_ei in soft_set.items():
        membership_matrix[e_i] = {}
        gamma_ei = len(phi_ei) * (m - 1) if len(phi_ei) > 0 else 1
        
        for u in U:
            if u in phi_ei:
                membership_matrix[e_i][u] = Fraction(1, 1)
            else:
                delta_u = delta_function_v2(u, phi_ei, soft_set)
                membership_matrix[e_i][u] = Fraction(delta_u, gamma_ei)
    
    return membership_matrix

def calculate_dynamic_threshold(membership_matrix):
    """Dinamik threshold hesapla"""
    fractional_values = []
    for e_i, row in membership_matrix.items():
        for u, val in row.items():
            val_float = float(val)
            if 0 < val_float < 1:
                fractional_values.append(val_float)
    
    if fractional_values:
        return np.mean(fractional_values)
    return 0.5

def threshold_matrix_dynamic_WITH_EPSILON(membership_matrix, U, threshold_value):
    """EPSİLON TOLERANSLI threshold uygula"""
    epsilon = 1e-9  # ✅ EPSILON
    binary_matrix = {}
    for e_i in membership_matrix.keys():
        binary_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            binary_matrix[e_i][u] = 1 if val >= (threshold_value - epsilon) else 0
    return binary_matrix

def is_binary_matrix(membership_matrix):
    """Matrisin binary olup olmadığını kontrol et"""
    for e_i, row in membership_matrix.items():
        for u, val in row.items():
            val_float = float(val)
            if 0 < val_float < 1:
                return False
    return True

def sets_are_equal(soft_set1, soft_set2):
    """Kümelerin eşit olup olmadığını kontrol et"""
    if soft_set1.keys() != soft_set2.keys():
        return False
    for key in soft_set1.keys():
        if soft_set1[key] != soft_set2[key]:
            return False
    return True

def calculate_density(csv_file):
    """Yoğunluk hesapla"""
    df = pd.read_csv(csv_file, header=None)
    total = df.shape[0] * df.shape[1]
    ones = (df == 1).sum().sum()
    return (ones / total) * 100 if total > 0 else 0

def run_rmvc_test(csv_file, max_iterations=100):
    """RMVC testi çalıştır"""
    soft_set, U, E = csv_to_soft_set(csv_file)
    
    iteration_history = []
    prev_soft_set = None
    
    for iteration in range(1, max_iterations + 1):
        membership_matrix = create_membership_matrix_v2(soft_set, U)
        
        if is_binary_matrix(membership_matrix):
            iteration_history.append({
                'iteration': iteration,
                'is_binary': True,
                'threshold': 0.5,
                'num_fractional': 0,
                'set_stable': True
            })
            return True, iteration, iteration_history
        
        threshold = calculate_dynamic_threshold(membership_matrix)
        num_fractional = sum(1 for e_i in membership_matrix 
                           for val in membership_matrix[e_i].values() 
                           if 0 < float(val) < 1)
        
        binary_matrix = threshold_matrix_dynamic_WITH_EPSILON(membership_matrix, U, threshold)
        
        new_soft_set = {}
        for e_i in E:
            new_soft_set[e_i] = set()
            for u in U:
                if binary_matrix[e_i][u] == 1:
                    new_soft_set[e_i].add(u)
        
        set_stable = sets_are_equal(soft_set, new_soft_set) if prev_soft_set else False
        
        iteration_history.append({
            'iteration': iteration,
            'is_binary': False,
            'threshold': threshold,
            'num_fractional': num_fractional,
            'set_stable': set_stable
        })
        
        if set_stable:
            return True, iteration, iteration_history
        
        prev_soft_set = soft_set
        soft_set = new_soft_set
    
    return False, max_iterations, iteration_history

# ================== TEST SENARYOLARI ==================

print("="*70)
print("10+10 MATRİS KARŞILAŞTIRMALI TEST - EPSİLON TOLERANSLI")
print("="*70)

# MovieLens matrisler
movielens_matrices = [
    'movielens_method1_10x10.csv',
    'movielens_method1_10x20.csv',
    'movielens_method1_15x20.csv',
    'movielens_method1_20x20.csv',
    'movielens_method1_20x30.csv',
    'movielens_method1_30x30.csv',
    'movielens_method1_30x50.csv',
    'movielens_method1_40x50.csv',
    'movielens_method1_50x50.csv',
    'movielens_method1_60x75.csv'
]

# Tekstil matrisler (Method 1 - Miktar)
textile_matrices = [
    'textile_10x10_method1.csv',
    'textile_10x20_method1.csv',
    'textile_15x20_method1.csv',  # Yoksa en yakınını kullan
    'textile_20x20_method1.csv',
    'textile_20x30_method1.csv',
    'textile_30x30_method1.csv',  # Yoksa en yakınını kullan
    'textile_30x50_method1.csv',
    'textile_40x50_method1.csv',  # Yoksa en yakınını kullan
    'textile_50x50_method1.csv',
    'textile_60x75_method1.csv'   # Yoksa en yakınını kullan
]

# Yedek matrisler (eğer tam eşleşme yoksa)
textile_alternatives = {
    'textile_15x20_method1.csv': 'textile_10x20_method1.csv',
    'textile_30x30_method1.csv': 'textile_30x50_method1.csv',
    'textile_40x50_method1.csv': 'textile_30x50_method1.csv',
    'textile_60x75_method1.csv': 'textile_50x50_method1.csv'
}

results = []

print("\nMOVIELENS TESTLERİ:")
print("-" * 70)

for matrix_file in movielens_matrices:
    file_path = Path(f'd:/Projects/RMVC/datasets/{matrix_file}')
    
    if not file_path.exists():
        print(f"❌ {matrix_file} - Dosya bulunamadı")
        continue
    
    size = matrix_file.replace('movielens_method1_', '').replace('.csv', '')
    density = calculate_density(file_path)
    
    converged, final_iter, history = run_rmvc_test(file_path)
    
    result = {
        'file': matrix_file,
        'size': size,
        'density': round(density, 2),
        'converged': converged,
        'final_iteration': final_iter,
        'iterations': history,
        'dataset': 'MovieLens'
    }
    results.append(result)
    
    status = "✅" if converged else "❌"
    print(f"{status} {size:10s} | Yoğunluk: {density:5.2f}% | İter: {final_iter:2d}")

print("\nTEKSTİL TESTLERİ:")
print("-" * 70)

for matrix_file in textile_matrices:
    # Alternatif dosya kontrolü
    if matrix_file in textile_alternatives:
        actual_file = textile_alternatives[matrix_file]
        print(f"📝 {matrix_file} → {actual_file} (alternatif)")
        matrix_file = actual_file
    
    file_path = Path(f'd:/Projects/RMVC/Textile_data/outputs/binary_matrices/{matrix_file}')
    
    if not file_path.exists():
        print(f"❌ {matrix_file} - Dosya bulunamadı")
        continue
    
    size = matrix_file.replace('textile_', '').replace('_method1.csv', '')
    density = calculate_density(file_path)
    
    converged, final_iter, history = run_rmvc_test(file_path)
    
    result = {
        'file': matrix_file,
        'size': size,
        'density': round(density, 2),
        'converged': converged,
        'final_iteration': final_iter,
        'iterations': history,
        'dataset': 'Tekstil'
    }
    results.append(result)
    
    status = "✅" if converged else "❌"
    print(f"{status} {size:10s} | Yoğunluk: {density:5.2f}% | İter: {final_iter:2d}")

# JSON'a kaydet
output_file = 'd:/Projects/RMVC/equal_10x10_results.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n{'='*70}")
print(f"ÖZET")
print(f"{'='*70}")
print(f"Toplam Test: {len(results)}")
print(f"MovieLens: {sum(1 for r in results if r['dataset'] == 'MovieLens')}")
print(f"Tekstil: {sum(1 for r in results if r['dataset'] == 'Tekstil')}")
print(f"Yakınsama Oranı: {sum(1 for r in results if r['converged'])}/{len(results)}")
print(f"\nSonuçlar kaydedildi: {output_file}")
