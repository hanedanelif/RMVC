# -*- coding: utf-8 -*-
"""
TEKSTİL - TÜM MATRİSLER RMVC + İTERATİF
========================================
6 boyut (10×10, 10×20, 20×20, 20×30, 30×50, 50×50) × 4 method = 24 test
"""

import pandas as pd
import numpy as np
from fractions import Fraction
from datetime import datetime
import json
import os

# RMVC fonksiyonları (önceki script'ten)
def csv_to_soft_set_textile(df):
    parametre_ids = df.index.tolist()
    eleman_ids = df.columns.tolist()
    
    U = set(str(eid) for eid in eleman_ids)
    E_named = {}
    
    for i, param_id in enumerate(parametre_ids):
        e_key = f"e_{i+1}"
        satir_verisi = df.loc[param_id]
        phi_e = set()
        
        for eleman_id in eleman_ids:
            try:
                deger = satir_verisi[eleman_id]
                if pd.notna(deger) and int(deger) > 0:
                    phi_e.add(str(eleman_id))
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

def calculate_scores(membership_matrix, U):
    scores = {}
    for u in U:
        total = Fraction(0, 1)
        for e_i, row in membership_matrix.items():
            total += row.get(u, Fraction(0, 1))
        scores[u] = total
    return scores

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

def iterative_rmvc_analysis(binary_matrix, U, E_named, threshold=0.5, operator=">=", max_iterations=100):
    iterations = []
    current_E = {e_i: set() for e_i in E_named.keys()}
    
    for e_i in E_named.keys():
        for u in U:
            if binary_matrix[e_i][u] == 1:
                current_E[e_i].add(u)
    
    iterations.append({
        'iteration': 0,
        'matrix_type': 'binary',
        'is_fully_binary': True
    })
    
    for iteration in range(1, max_iterations + 1):
        membership_matrix = create_membership_matrix_v2(current_E, U)
        is_binary = is_binary_matrix(membership_matrix, U)
        
        iterations.append({
            'iteration': iteration,
            'matrix_type': 'membership',
            'is_fully_binary': is_binary
        })
        
        if is_binary:
            return iterations, True, iteration
        
        binary_matrix = threshold_matrix(membership_matrix, U, threshold, operator)
        
        new_E = {e_i: set() for e_i in E_named.keys()}
        for e_i in E_named.keys():
            for u in U:
                if binary_matrix[e_i][u] == 1:
                    new_E[e_i].add(u)
        
        if new_E == current_E:
            iterations.append({
                'iteration': iteration,
                'matrix_type': 'binary_converged',
                'is_fully_binary': True
            })
            return iterations, True, iteration
        
        current_E = new_E
    
    return iterations, False, max_iterations

def test_textile_matrix(file_path, method_name, matrix_size):
    try:
        df = pd.read_csv(file_path, index_col=0)
        density = (df.sum().sum() / df.size) * 100
        
        U, E_named = csv_to_soft_set_textile(df)
        
        binary_matrix = {}
        for e_i in E_named.keys():
            binary_matrix[e_i] = {}
            for u in U:
                binary_matrix[e_i][u] = 1 if u in E_named[e_i] else 0
        
        membership_matrix = create_membership_matrix_v2(E_named, U)
        scores = calculate_scores(membership_matrix, U)
        
        sorted_scores = sorted(scores.items(), key=lambda x: (-float(x[1]), x[0]))
        best_element = sorted_scores[0][0]
        best_score = float(sorted_scores[0][1])
        
        # Üyelik matrisini kaydet
        membership_df = pd.DataFrame({
            e_i: {u: float(membership_matrix[e_i][u]) for u in U}
            for e_i in E_named.keys()
        }).T
        
        membership_file = file_path.replace('binary_matrices', 'rmvc_results').replace('.csv', '_membership.csv')
        membership_df.to_csv(membership_file)
        
        # İteratif analiz
        iterations, converged, total_iterations = iterative_rmvc_analysis(
            binary_matrix, U, E_named, 
            threshold=0.5, 
            operator=">=",
            max_iterations=100
        )
        
        total_iterations = len(iterations) - 1
        
        # İteratif sonuçları kaydet
        iterative_file = file_path.replace('binary_matrices', 'iterative_results').replace('.csv', '_iterations.json')
        with open(iterative_file, 'w', encoding='utf-8') as f:
            json.dump({
                'method': method_name,
                'size': matrix_size,
                'total_iterations': total_iterations,
                'converged': converged,
                'best_product': best_element,
                'best_score': best_score,
                'iterations': [{
                    'iteration': it['iteration'],
                    'matrix_type': it['matrix_type'],
                    'is_fully_binary': it['is_fully_binary']
                } for it in iterations],
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        result = {
            'method': method_name,
            'size': matrix_size,
            'file': os.path.basename(file_path),
            'firms': df.shape[0],
            'products': df.shape[1],
            'density': density,
            'best_element': best_element,
            'best_score': best_score,
            'total_iterations': total_iterations,
            'converged': converged
        }
        
        print(f"  ✅ {matrix_size} - {method_name}: {total_iterations} iter, {'Yakınsadı' if converged else 'Yakınsamadı'}")
        
        return result
        
    except Exception as e:
        print(f"  ❌ HATA {matrix_size} - {method_name}: {str(e)}")
        return None

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    print("="*100)
    print("TEKSTİL - TÜM MATRİSLER RMVC + İTERATİF (24 TEST)")
    print("="*100)
    print(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Tüm boyutlar (eskiler + yeniler)
    all_sizes = [
        (10, 10), (10, 20),  # 10'lu
        (20, 20), (20, 30),  # 20'li
        (30, 50), (50, 50)   # Büyükler
    ]
    
    methods = ['method1', 'method2', 'method3', 'method4']
    
    print(f"🎯 {len(all_sizes)} boyut × {len(methods)} method = {len(all_sizes) * len(methods)} test\n")
    
    results = []
    test_count = 0
    total_tests = len(all_sizes) * len(methods)
    
    for rows, cols in all_sizes:
        size = f'{rows}x{cols}'
        print(f"\n📊 {size} Matrisleri:")
        
        for method in methods:
            test_count += 1
            file_path = f'Textile_data/outputs/binary_matrices/textile_{size}_{method}.csv'
            
            if os.path.exists(file_path):
                result = test_textile_matrix(file_path, method.upper().replace('METHOD', 'Method '), size)
                if result:
                    results.append(result)
            else:
                print(f"  ⚠️ Dosya bulunamadı: {method}")
    
    # ==========================================
    # SONUÇ RAPORU
    # ==========================================
    
    print(f"\n\n{'='*100}")
    print("FINAL ÖZET RAPOR - 24 TEST")
    print(f"{'='*100}\n")
    
    print(f"{'Method':<12} {'Boyut':<10} {'Firma':<8} {'Ürün':<8} {'Yoğunluk':<10} {'İterasyon':<12} {'Yakınsama'}")
    print("-" * 100)
    
    for r in results:
        conv_status = "✅" if r['converged'] else "❌"
        print(f"{r['method']:<12} {r['size']:<10} {r['firms']:<8} {r['products']:<8} "
              f"{r['density']:>6.2f}%    {r['total_iterations']:<12} {conv_status}")
    
    # Method karşılaştırması
    print(f"\n{'='*100}")
    print("METHOD PERFORMANSI")
    print(f"{'='*100}\n")
    
    for method in ['Method 1', 'Method 2', 'Method 3', 'Method 4']:
        method_results = [r for r in results if r['method'] == method]
        if method_results:
            avg_iter = sum(r['total_iterations'] for r in method_results) / len(method_results)
            conv_rate = sum(1 for r in method_results if r['converged']) / len(method_results) * 100
            print(f"{method}: Ortalama İterasyon = {avg_iter:.2f}, Yakınsama Oranı = {conv_rate:.1f}%")
    
    # Boyut bazında analiz
    print(f"\n{'='*100}")
    print("BOYUT BAZINDA PERFORMANS")
    print(f"{'='*100}\n")
    
    for rows, cols in all_sizes:
        size = f'{rows}x{cols}'
        size_results = [r for r in results if r['size'] == size]
        if size_results:
            avg_iter = sum(r['total_iterations'] for r in size_results) / len(size_results)
            avg_density = sum(r['density'] for r in size_results) / len(size_results)
            print(f"{size}: Yoğunluk = {avg_density:.2f}%, Ortalama İterasyon = {avg_iter:.2f}")
    
    # JSON kaydet
    with open('Textile_data/reports/FINAL_ALL_TESTS_SUMMARY.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_tests': len(results),
            'test_sizes': [f'{r}x{c}' for r, c in all_sizes],
            'methods': methods,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n💾 FINAL_ALL_TESTS_SUMMARY.json kaydedildi")
    print(f"\n✅ TÜM 24 TEST TAMAMLANDI!")
    print(f"\nBitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
