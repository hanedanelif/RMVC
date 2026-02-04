# -*- coding: utf-8 -*-
"""
MovieLens Kapsamlı RMVC ve İteratif Analiz
==========================================
Tüm MovieLens matrislerini V2 ile test eder ve iteratif analiz yapar.
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import os
from datetime import datetime

# ==========================================
# RMVC FONKSİYONLARI (V2 - HOCANIN METODU)
# ==========================================

def csv_to_soft_set(df, rows_are_params=False):
    """CSV'yi Soft Set formatına dönüştür"""
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
    else:
        eleman_ids = df.index.tolist()
        parametre_ids = df.columns.tolist()
        U = set(str(eid) for eid in eleman_ids)
        E_named = {}
        
        for i, param_id in enumerate(parametre_ids):
            e_key = f"e_{i+1}"
            sutun_verisi = df[param_id]
            phi_e = set()
            
            for eleman_id, deger in sutun_verisi.items():
                try:
                    numeric_val = pd.to_numeric(deger, errors='coerce')
                    if numeric_val > 0:
                        phi_e.add(str(eleman_id))
                except:
                    pass
            
            E_named[e_key] = phi_e
    
    return U, E_named

def delta_function_v2(e_i, E_named, U):
    """V2 delta fonksiyonu - Hocanın metodu (kendi kümesi dahil)"""
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
    """V2 üyelik matrisi"""
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
    """Skorları hesapla"""
    scores = {}
    for u in U:
        total = Fraction(0, 1)
        for e_i, row in membership_matrix.items():
            total += row.get(u, Fraction(0, 1))
        scores[u] = total
    return scores

# ==========================================
# İTERATİF ANALİZ FONKSİYONLARI
# ==========================================

def threshold_matrix(membership_matrix, U, threshold_value, operator=">="):
    """Üyelik matrisini eşik değerine göre binary'ye dönüştür"""
    binary_matrix = {}
    for e_i in membership_matrix.keys():
        binary_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            epsilon = 1e-9
            
            if operator == ">=":
                above_threshold = val >= (threshold_value - epsilon)
            else:  # ">"
                above_threshold = val > (threshold_value + epsilon)
            
            binary_matrix[e_i][u] = 1 if above_threshold else 0
    return binary_matrix

def is_binary_matrix(matrix, U):
    """Matrisin tamamen binary (0 veya 1) olup olmadığını kontrol et"""
    for e_i in matrix.keys():
        for u in U:
            val = float(matrix[e_i].get(u, 0))
            if val not in [0.0, 1.0]:
                return False
    return True

def iterative_rmvc_analysis(binary_matrix, U, E_named, threshold=0.5, operator=">=", max_iterations=20):
    """
    İteratif RMVC analizi - Eşik >= ile
    Binary matris -> RMVC -> Threshold -> Binary (tekrar)
    Tamamen binary olana kadar devam et
    """
    iterations = []
    current_E = {e_i: set() for e_i in E_named.keys()}
    
    # İlk binary'den E_named oluştur
    for e_i in E_named.keys():
        for u in U:
            if binary_matrix[e_i][u] == 1:
                current_E[e_i].add(u)
    
    iteration = 0
    
    # İlk durum (iteration 0)
    iterations.append({
        'iteration': 0,
        'E_named': {k: v.copy() for k, v in current_E.items()},
        'matrix_type': 'binary',
        'is_fully_binary': True
    })
    
    for iteration in range(1, max_iterations + 1):
        # RMVC hesapla
        membership_matrix = create_membership_matrix_v2(current_E, U)
        
        # Binary mi kontrol et
        is_binary = is_binary_matrix(membership_matrix, U)
        
        iterations.append({
            'iteration': iteration,
            'membership_matrix': membership_matrix,
            'matrix_type': 'membership',
            'is_fully_binary': is_binary
        })
        
        if is_binary:
            print(f"  ✅ İterasyon {iteration}: Tamamen binary matris elde edildi!")
            break
        
        # Threshold uygula
        binary_matrix = threshold_matrix(membership_matrix, U, threshold, operator)
        
        # Yeni E_named oluştur
        new_E = {e_i: set() for e_i in E_named.keys()}
        for e_i in E_named.keys():
            for u in U:
                if binary_matrix[e_i][u] == 1:
                    new_E[e_i].add(u)
        
        # Değişiklik var mı kontrol et
        if new_E == current_E:
            print(f"  ⚠️ İterasyon {iteration}: Küme değişmedi, yakınsama sağlandı")
            iterations.append({
                'iteration': iteration,
                'E_named': {k: v.copy() for k, v in new_E.items()},
                'matrix_type': 'binary_converged',
                'is_fully_binary': True
            })
            break
        
        current_E = new_E
    
    return iterations

# ==========================================
# TEST RUNNER
# ==========================================

def test_movielens_matrix(file_path, method_name, matrix_size):
    """Tek bir MovieLens matrisini test et"""
    print(f"\n{'='*80}")
    print(f"TEST: {method_name} - {matrix_size}")
    print(f"Dosya: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
    try:
        # Veriyi yükle
        df = pd.read_csv(file_path, index_col=0)
        print(f"✅ Veri yüklendi: {df.shape[0]} satır × {df.shape[1]} sütun")
        
        # Soft Set'e dönüştür
        U, E_named = csv_to_soft_set(df, rows_are_params=True)
        print(f"✅ Soft Set: |U|={len(U)}, m={len(E_named)}")
        
        # İlk binary matris oluştur
        binary_matrix = {}
        for e_i in E_named.keys():
            binary_matrix[e_i] = {}
            for u in U:
                binary_matrix[e_i][u] = 1 if u in E_named[e_i] else 0
        
        # RMVC hesapla (iteration 1)
        print(f"\n🔄 RMVC hesaplanıyor...")
        membership_matrix = create_membership_matrix_v2(E_named, U)
        scores = calculate_scores(membership_matrix, U)
        
        # Skorları sırala
        sorted_scores = sorted(scores.items(), key=lambda x: (-float(x[1]), x[0]))
        best_element = sorted_scores[0][0]
        best_score = float(sorted_scores[0][1])
        
        print(f"✅ RMVC tamamlandı")
        print(f"  🏆 En iyi eleman: {best_element} (Skor: {best_score:.4f})")
        
        # İteratif analiz
        print(f"\n🔄 İteratif analiz başlıyor (Eşik: 0.5, Operatör: >=)...")
        iterations = iterative_rmvc_analysis(
            binary_matrix, U, E_named, 
            threshold=0.5, 
            operator=">=",
            max_iterations=20
        )
        
        total_iterations = len(iterations) - 1  # İlk durum hariç
        
        result = {
            'method': method_name,
            'size': matrix_size,
            'file': os.path.basename(file_path),
            'users': len(U),
            'params': len(E_named),
            'best_element': best_element,
            'best_score': best_score,
            'total_iterations': total_iterations,
            'converged': iterations[-1]['is_fully_binary'],
            'iterations_detail': iterations
        }
        
        print(f"\n📊 SONUÇ:")
        print(f"  • Toplam İterasyon: {total_iterations}")
        print(f"  • Yakınsama: {'✅ Evet' if result['converged'] else '❌ Hayır'}")
        
        return result
        
    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    print("="*80)
    print("MOVIELENS KAPSAMLI RMVC VE İTERATİF ANALİZ (V2)")
    print("="*80)
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # MovieLens dosyalarını tanımla
    datasets_dir = "datasets"
    
    test_files = [
        ('movielens_method1_3x5.csv', 'Method 1', '3x5'),
        ('movielens_method1_5x10.csv', 'Method 1', '5x10'),
        ('movielens_method1_10x20.csv', 'Method 1', '10x20'),
        ('movielens_method1_20x30.csv', 'Method 1', '20x30'),
        ('movielens_method1_30x50.csv', 'Method 1', '30x50'),
        ('movielens_method1_50x75.csv', 'Method 1', '50x75'),
        ('movielens_method1_75x100.csv', 'Method 1', '75x100'),
        
        ('movielens_method2_3x5.csv', 'Method 2', '3x5'),
        ('movielens_method2_5x10.csv', 'Method 2', '5x10'),
        ('movielens_method2_10x20.csv', 'Method 2', '10x20'),
        ('movielens_method2_20x30.csv', 'Method 2', '20x30'),
        ('movielens_method2_30x50.csv', 'Method 2', '30x50'),
        ('movielens_method2_50x75.csv', 'Method 2', '50x75'),
        ('movielens_method2_75x100.csv', 'Method 2', '75x100'),
        ('movielens_method2_100x150.csv', 'Method 2', '100x150'),
    ]
    
    results = []
    
    for filename, method, size in test_files:
        file_path = os.path.join(datasets_dir, filename)
        if os.path.exists(file_path):
            result = test_movielens_matrix(file_path, method, size)
            if result:
                results.append(result)
        else:
            print(f"\n⚠️ Dosya bulunamadı: {filename}")
    
    # SONUÇLARI ÖZETLE
    print(f"\n\n{'='*80}")
    print("ÖZET RAPOR")
    print(f"{'='*80}\n")
    
    print(f"{'Method':<15} {'Boyut':<10} {'Kullanıcı':<10} {'Param':<8} {'İterasyon':<12} {'Yakınsama'}")
    print("-" * 80)
    
    for r in results:
        conv_status = "✅" if r['converged'] else "❌"
        print(f"{r['method']:<15} {r['size']:<10} {r['users']:<10} {r['params']:<8} "
              f"{r['total_iterations']:<12} {conv_status}")
    
    # Method karşılaştırması
    print(f"\n{'='*80}")
    print("METHOD 1 vs METHOD 2 KARŞILAŞTIRMASI")
    print(f"{'='*80}\n")
    
    method1_results = [r for r in results if r['method'] == 'Method 1']
    method2_results = [r for r in results if r['method'] == 'Method 2']
    
    if method1_results:
        avg_iter_m1 = sum(r['total_iterations'] for r in method1_results) / len(method1_results)
        print(f"Method 1: Ortalama İterasyon = {avg_iter_m1:.2f}")
    
    if method2_results:
        avg_iter_m2 = sum(r['total_iterations'] for r in method2_results) / len(method2_results)
        print(f"Method 2: Ortalama İterasyon = {avg_iter_m2:.2f}")
    
    print(f"\n✅ Tüm testler tamamlandı! Toplam: {len(results)} matris")
