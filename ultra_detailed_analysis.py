# -*- coding: utf-8 -*-
"""
ULTRA DETAYLI İTERASYON ANALİZİ
================================
Her iterasyonun tüm detaylarını kaydet
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import json

# ================== RMVC FONKSİYONLARI ==================

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
    return soft_set, U, E, df

def delta_function_v2(u, phi_ei, soft_set):
    """Delta fonksiyonu"""
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

def threshold_matrix_WITH_EPSILON(membership_matrix, U, threshold_value):
    """Epsilon toleranslı threshold"""
    epsilon = 1e-9
    binary_matrix = {}
    for e_i in membership_matrix.keys():
        binary_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            binary_matrix[e_i][u] = 1 if val >= (threshold_value - epsilon) else 0
    return binary_matrix

def matrix_to_dataframe(matrix, U, E):
    """Matrisi DataFrame'e çevir"""
    U_sorted = sorted(list(U), key=lambda x: int(x[1:]))
    E_sorted = sorted(list(E), key=lambda x: int(x[1:]))
    
    data = []
    for e_i in E_sorted:
        row = []
        for u in U_sorted:
            if isinstance(matrix[e_i][u], Fraction):
                row.append(float(matrix[e_i][u]))
            else:
                row.append(matrix[e_i][u])
        data.append(row)
    
    return pd.DataFrame(data, columns=U_sorted, index=E_sorted)

def analyze_matrix(matrix, U, E, matrix_type="Unknown"):
    """Matris istatistiklerini analiz et"""
    df = matrix_to_dataframe(matrix, U, E)
    values = df.values.flatten()
    
    ones = np.sum(values == 1)
    zeros = np.sum(values == 0)
    fractional = np.sum((values > 0) & (values < 1))
    
    fractional_values = values[(values > 0) & (values < 1)]
    
    stats = {
        'type': matrix_type,
        'shape': df.shape,
        'total_cells': df.size,
        'ones_count': int(ones),
        'zeros_count': int(zeros),
        'fractional_count': int(fractional),
        'min_value': float(np.min(values)),
        'max_value': float(np.max(values)),
        'fractional_values': sorted([float(v) for v in fractional_values]) if len(fractional_values) > 0 else []
    }
    
    return stats, df

def run_ultra_detailed_analysis(csv_file, dataset_name, max_iterations=100):
    """Ultra detaylı analiz"""
    print(f"\n{'='*80}")
    print(f"{dataset_name} - ULTRA DETAYLI ANALİZ")
    print(f"{'='*80}")
    
    soft_set, U, E, initial_df = csv_to_soft_set(csv_file)
    
    # İlk matris analizi
    print(f"\n📋 BAŞLANGIÇ MATRİSİ:")
    print(initial_df)
    print(f"\nBoyut: {initial_df.shape}")
    print(f"1'ler: {(initial_df == 1).sum().sum()}")
    print(f"0'lar: {(initial_df == 0).sum().sum()}")
    print(f"Yoğunluk: {((initial_df == 1).sum().sum() / initial_df.size) * 100:.2f}%")
    
    iteration_details = {
        'dataset': dataset_name,
        'file': csv_file,
        'initial_matrix': initial_df.to_dict(),
        'initial_stats': {
            'shape': initial_df.shape,
            'ones': int((initial_df == 1).sum().sum()),
            'zeros': int((initial_df == 0).sum().sum()),
            'density': float(((initial_df == 1).sum().sum() / initial_df.size) * 100)
        },
        'iterations': []
    }
    
    for iteration in range(1, max_iterations + 1):
        print(f"\n{'─'*80}")
        print(f"İTERASYON {iteration}")
        print(f"{'─'*80}")
        
        iter_data = {'iteration_number': iteration}
        
        # RMVC öncesi soft set
        print(f"\n1️⃣ RMVC ÖNCESİ SOFT SET:")
        for e_i in sorted(soft_set.keys(), key=lambda x: int(x[1:])):
            print(f"  {e_i}: {sorted(soft_set[e_i], key=lambda x: int(x[1:]))}")
        
        # RMVC uygula - Üyelik matrisi
        membership_matrix = create_membership_matrix_v2(soft_set, U)
        mem_stats, mem_df = analyze_matrix(membership_matrix, U, E, "Membership Matrix")
        
        print(f"\n2️⃣ RMVC SONRASI ÜYELİK MATRİSİ:")
        print(mem_df)
        print(f"\n📊 İstatistikler:")
        print(f"  1'ler: {mem_stats['ones_count']}")
        print(f"  0'lar: {mem_stats['zeros_count']}")
        print(f"  Ondalıklılar: {mem_stats['fractional_count']}")
        print(f"  Min: {mem_stats['min_value']}")
        print(f"  Max: {mem_stats['max_value']}")
        
        if mem_stats['fractional_values']:
            print(f"  Ondalıklı değerler: {mem_stats['fractional_values'][:10]}...")  # İlk 10
        
        iter_data['membership_matrix'] = mem_df.to_dict()
        iter_data['membership_stats'] = mem_stats
        
        # Binary mi kontrolü
        is_binary = mem_stats['fractional_count'] == 0
        
        if is_binary:
            print(f"\n✅ MATRİS BINARY! Yakınsama sağlandı.")
            iter_data['convergence_type'] = 'binary'
            iter_data['threshold'] = 0.5
            iteration_details['iterations'].append(iter_data)
            iteration_details['final_iteration'] = iteration
            iteration_details['converged'] = True
            break
        
        # Threshold hesapla
        threshold = calculate_dynamic_threshold(membership_matrix)
        print(f"\n3️⃣ DİNAMİK THRESHOLD: {threshold:.15f}")
        iter_data['threshold'] = float(threshold)
        
        # Threshold uygula
        binary_matrix = threshold_matrix_WITH_EPSILON(membership_matrix, U, threshold)
        bin_stats, bin_df = analyze_matrix(binary_matrix, U, E, "Binary Matrix")
        
        print(f"\n4️⃣ THRESHOLD UYGULANMIŞ BINARY MATRİS:")
        print(bin_df)
        print(f"\n📊 İstatistikler:")
        print(f"  1'ler: {bin_stats['ones_count']}")
        print(f"  0'lar: {bin_stats['zeros_count']}")
        
        iter_data['binary_matrix'] = bin_df.to_dict()
        iter_data['binary_stats'] = bin_stats
        
        # Yeni soft set oluştur
        new_soft_set = {}
        for e_i in E:
            new_soft_set[e_i] = set()
            for u in U:
                if binary_matrix[e_i][u] == 1:
                    new_soft_set[e_i].add(u)
        
        # Küme kararlılığı kontrolü
        sets_equal = all(soft_set[e] == new_soft_set[e] for e in E)
        
        if sets_equal:
            print(f"\n✅ KÜMELER KARARLIDI! Yakınsama sağlandı.")
            iter_data['convergence_type'] = 'set_stable'
            iteration_details['iterations'].append(iter_data)
            iteration_details['final_iteration'] = iteration
            iteration_details['converged'] = True
            break
        
        iter_data['set_stable'] = sets_equal
        iteration_details['iterations'].append(iter_data)
        soft_set = new_soft_set
    
    else:
        print(f"\n❌ Maksimum iterasyona ulaşıldı!")
        iteration_details['final_iteration'] = max_iterations
        iteration_details['converged'] = False
    
    return iteration_details

# ================== TESTLER ==================

# MovieLens 10×10
print("\n" + "="*80)
print("MOVIESLENS 10×10 DETAYLI ANALİZ")
print("="*80)

movielens_file = r'd:\Projects\RMVC\datasets\movielens_method1_10x10.csv'
movielens_details = run_ultra_detailed_analysis(movielens_file, "MovieLens 10×10")

# JSON'a kaydet
with open('d:/Projects/RMVC/movielens_10x10_ultra_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(movielens_details, f, indent=2, ensure_ascii=False)

print(f"\n✅ MovieLens detayları kaydedildi: movielens_10x10_ultra_detailed.json")

# Tekstil 10×10
print("\n" + "="*80)
print("TEKSTİL 10×10 DETAYLI ANALİZ")
print("="*80)

textile_file = r'd:\Projects\RMVC\Textile_data\outputs\binary_matrices\textile_10x10_method1.csv'
textile_details = run_ultra_detailed_analysis(textile_file, "Tekstil 10×10")

# JSON'a kaydet
with open('d:/Projects/RMVC/textile_10x10_ultra_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(textile_details, f, indent=2, ensure_ascii=False)

print(f"\n✅ Tekstil detayları kaydedildi: textile_10x10_ultra_detailed.json")

print(f"\n{'='*80}")
print(f"TAMAMLANDI!")
print(f"{'='*80}")
