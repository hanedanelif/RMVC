# -*- coding: utf-8 -*-
"""
75x100 Derin Analiz - Yüksek İterasyon Limiti
==============================================
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import os
from datetime import datetime

# ==========================================
# RMVC FONKSİYONLARI (V2)
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
    
    return U, E_named

def delta_function_v2(e_i, E_named, U):
    """V2 delta fonksiyonu"""
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

def threshold_matrix(membership_matrix, U, threshold_value, operator=">="):
    """Eşik uygula"""
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
    """Binary kontrol"""
    for e_i in matrix.keys():
        for u in U:
            val = float(matrix[e_i].get(u, 0))
            if val not in [0.0, 1.0]:
                return False
    return True

def deep_iterative_analysis(binary_matrix, U, E_named, threshold=0.5, operator=">=", max_iterations=100):
    """
    Derin iteratif analiz - 100 iterasyona kadar
    """
    iterations = []
    current_E = {e_i: set() for e_i in E_named.keys()}
    
    # İlk binary'den E_named oluştur
    for e_i in E_named.keys():
        for u in U:
            if binary_matrix[e_i][u] == 1:
                current_E[e_i].add(u)
    
    iteration = 0
    previous_E = None
    
    print(f"\n🔬 DERİN İTERATİF ANALİZ BAŞLADI")
    print(f"   Max İterasyon: {max_iterations}")
    print(f"   Eşik: {threshold}, Operatör: {operator}")
    print(f"   Başlangıç: |U|={len(U)}, m={len(E_named)}\n")
    
    # İlk durum
    iterations.append({
        'iteration': 0,
        'E_named': {k: v.copy() for k, v in current_E.items()},
        'matrix_type': 'binary',
        'is_fully_binary': True,
        'change_from_previous': None
    })
    
    for iteration in range(1, max_iterations + 1):
        # RMVC hesapla
        membership_matrix = create_membership_matrix_v2(current_E, U)
        
        # Binary mi kontrol et
        is_binary = is_binary_matrix(membership_matrix, U)
        
        # Değişiklik sayısı
        change_count = 0
        if previous_E:
            for e_i in E_named.keys():
                change_count += len(current_E[e_i].symmetric_difference(previous_E[e_i]))
        
        iterations.append({
            'iteration': iteration,
            'membership_matrix': membership_matrix,
            'matrix_type': 'membership',
            'is_fully_binary': is_binary,
            'change_from_previous': change_count
        })
        
        if iteration % 10 == 0:
            print(f"   İterasyon {iteration}: Binary={is_binary}, Değişim={change_count if previous_E else 'N/A'}")
        
        if is_binary:
            print(f"\n   ✅ İterasyon {iteration}: Tamamen binary matris elde edildi!")
            print(f"      Son değişim: {change_count if previous_E else 0} eleman")
            break
        
        # Threshold uygula
        binary_matrix = threshold_matrix(membership_matrix, U, threshold, operator)
        
        # Yeni E_named oluştur
        previous_E = {k: v.copy() for k, v in current_E.items()}
        new_E = {e_i: set() for e_i in E_named.keys()}
        for e_i in E_named.keys():
            for u in U:
                if binary_matrix[e_i][u] == 1:
                    new_E[e_i].add(u)
        
        # Değişiklik var mı kontrol et
        if new_E == current_E:
            print(f"\n   ⚠️ İterasyon {iteration}: Küme değişmedi, yakınsama sağlandı")
            print(f"      (Ama matris hala binary değil)")
            iterations.append({
                'iteration': iteration,
                'E_named': {k: v.copy() for k, v in new_E.items()},
                'matrix_type': 'binary_converged',
                'is_fully_binary': False,
                'change_from_previous': 0
            })
            break
        
        current_E = new_E
    
    if iteration >= max_iterations:
        print(f"\n   ❌ {max_iterations} iterasyon sonunda yakınsamadı!")
    
    return iterations

# ==========================================
# 75x100 TEST
# ==========================================

def test_75x100_deep(file_path, method_name):
    """75x100 matrisini derin analiz"""
    print(f"\n{'='*80}")
    print(f"75x100 DERİN ANALİZ - {method_name}")
    print(f"Dosya: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
    try:
        # Veriyi yükle
        df = pd.read_csv(file_path, index_col=0)
        print(f"✅ Veri yüklendi: {df.shape[0]} satır × {df.shape[1]} sütun")
        
        # Soft Set'e dönüştür
        U, E_named = csv_to_soft_set(df, rows_are_params=True)
        print(f"✅ Soft Set: |U|={len(U)}, m={len(E_named)}")
        
        # Yoğunluk analizi
        total_cells = len(U) * len(E_named)
        filled_cells = sum(len(v) for v in E_named.values())
        density = (filled_cells / total_cells) * 100
        print(f"📊 Başlangıç Yoğunluğu: {density:.2f}%")
        
        # İlk binary matris
        binary_matrix = {}
        for e_i in E_named.keys():
            binary_matrix[e_i] = {}
            for u in U:
                binary_matrix[e_i][u] = 1 if u in E_named[e_i] else 0
        
        # RMVC hesapla
        print(f"\n🔄 İlk RMVC hesaplanıyor...")
        membership_matrix = create_membership_matrix_v2(E_named, U)
        scores = calculate_scores(membership_matrix, U)
        
        sorted_scores = sorted(scores.items(), key=lambda x: (-float(x[1]), x[0]))
        best_element = sorted_scores[0][0]
        best_score = float(sorted_scores[0][1])
        
        print(f"✅ RMVC tamamlandı")
        print(f"  🏆 En iyi eleman: {best_element} (Skor: {best_score:.4f})")
        
        # Derin iteratif analiz (100 iterasyon limiti)
        iterations = deep_iterative_analysis(
            binary_matrix, U, E_named,
            threshold=0.5,
            operator=">=",
            max_iterations=100
        )
        
        total_iterations = len([i for i in iterations if i['matrix_type'] != 'binary']) - 1
        converged = iterations[-1].get('is_fully_binary', False)
        
        print(f"\n{'='*80}")
        print(f"SONUÇ RAPORU")
        print(f"{'='*80}")
        print(f"Toplam İterasyon: {total_iterations}")
        print(f"Yakınsama Durumu: {'✅ Evet' if converged else '❌ Hayır'}")
        
        # İterasyon geçmişini göster
        print(f"\nİterasyon Geçmişi:")
        print(f"{'İter':<6} {'Tip':<20} {'Binary?':<10} {'Değişim'}")
        print("-" * 60)
        for i in iterations[:10]:  # İlk 10
            iter_num = i['iteration']
            matrix_type = i['matrix_type']
            is_bin = '✅' if i['is_fully_binary'] else '❌'
            change = i.get('change_from_previous', '-')
            print(f"{iter_num:<6} {matrix_type:<20} {is_bin:<10} {change}")
        
        if len(iterations) > 20:
            print("...")
            for i in iterations[-10:]:  # Son 10
                iter_num = i['iteration']
                matrix_type = i['matrix_type']
                is_bin = '✅' if i['is_fully_binary'] else '❌'
                change = i.get('change_from_previous', '-')
                print(f"{iter_num:<6} {matrix_type:<20} {is_bin:<10} {change}")
        
        return {
            'method': method_name,
            'total_iterations': total_iterations,
            'converged': converged,
            'best_element': best_element,
            'best_score': best_score,
            'density': density,
            'iterations': iterations
        }
        
    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    print("="*80)
    print("75x100 DERİN ANALİZ - YÜKSEK İTERASYON LİMİTİ")
    print("="*80)
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test edilecek dosyalar
    test_files = [
        ('datasets/movielens_method1_75x100.csv', 'Method 1'),
        ('datasets/movielens_method2_75x100.csv', 'Method 2'),
    ]
    
    results = []
    
    for file_path, method in test_files:
        if os.path.exists(file_path):
            result = test_75x100_deep(file_path, method)
            if result:
                results.append(result)
        else:
            print(f"\n⚠️ Dosya bulunamadı: {file_path}")
    
    # KARŞILAŞTIRMA
    print(f"\n\n{'='*80}")
    print("METHOD 1 vs METHOD 2 - 75x100 KARŞILAŞTIRMASI")
    print(f"{'='*80}\n")
    
    for r in results:
        print(f"{r['method']}:")
        print(f"  • Toplam İterasyon: {r['total_iterations']}")
        print(f"  • Yakınsama: {'✅ Evet' if r['converged'] else '❌ Hayır'}")
        print(f"  • En İyi Eleman: {r['best_element']} (Skor: {r['best_score']:.4f})")
        print(f"  • Başlangıç Yoğunluğu: {r['density']:.2f}%")
        print()
    
    print("="*80)
    print("✅ Derin analiz tamamlandı!")
