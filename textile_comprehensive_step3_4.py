# -*- coding: utf-8 -*-
"""
TEKSTİL KAPSAMLı RMVC ANALİZİ - ADIM 3 & 4
==========================================
RMVC Hesaplama (V2) ve İteratif Analiz

12 binary matris × RMVC + İteratif = 12 test
Her şey makale için kaydedilecek!
"""

import pandas as pd
import numpy as np
from fractions import Fraction
from datetime import datetime
import json
import os

print("="*100)
print("TEKSTİL KAPSAMLı RMVC ANALİZİ - ADIM 3 & 4: RMVC + İTERATİF ANALIZ")
print("="*100)
print(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ==========================================
# RMVC V2 FONKSİYONLARI (MovieLens'ten)
# ==========================================

def csv_to_soft_set_textile(df):
    """Tekstil binary matrisini soft set'e dönüştür"""
    # Satırlar = Firmalar (parameters)
    # Sütunlar = Ürünler (elements)
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
# İTERATİF ANALİZ FONKSIYONLARI
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

def iterative_rmvc_analysis(binary_matrix, U, E_named, threshold=0.5, operator=">=", max_iterations=100):
    """
    İteratif RMVC analizi - 75x100 için 42 iterasyon sürdü, o yüzden max=100
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
            'matrix_type': 'membership',
            'is_fully_binary': is_binary
        })
        
        if is_binary:
            return iterations, True, iteration
        
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
            iterations.append({
                'iteration': iteration,
                'matrix_type': 'binary_converged',
                'is_fully_binary': True
            })
            return iterations, True, iteration
        
        current_E = new_E
    
    return iterations, False, max_iterations

# ==========================================
# TEST RUNNER
# ==========================================

def test_textile_matrix(file_path, method_name, matrix_size):
    """Tek bir tekstil matrisini test et"""
    print(f"\n{'='*80}")
    print(f"TEST: {method_name} - {matrix_size}")
    print(f"Dosya: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
    try:
        # Veriyi yükle
        df = pd.read_csv(file_path, index_col=0)
        print(f"✅ Veri yüklendi: {df.shape[0]} firma × {df.shape[1]} ürün")
        
        # Yoğunluk
        density = (df.sum().sum() / df.size) * 100
        print(f"   Binary yoğunluk: {density:.2f}%")
        
        # Soft Set'e dönüştür
        U, E_named = csv_to_soft_set_textile(df)
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
        print(f"  🏆 En iyi ürün: {best_element} (Skor: {best_score:.4f})")
        
        # Üyelik matrisini kaydet (Makale için!)
        membership_df = pd.DataFrame({
            e_i: {u: float(membership_matrix[e_i][u]) for u in U}
            for e_i in E_named.keys()
        }).T
        
        membership_file = file_path.replace('binary_matrices', 'rmvc_results').replace('.csv', '_membership.csv')
        membership_df.to_csv(membership_file)
        print(f"  💾 Üyelik matrisi kaydedildi")
        
        # İteratif analiz
        print(f"\n🔄 İteratif analiz başlıyor (Eşik: 0.5, Operatör: >=, Max: 100)...")
        iterations, converged,total_iterations = iterative_rmvc_analysis(
            binary_matrix, U, E_named, 
            threshold=0.5, 
            operator=">=",
            max_iterations=100
        )
        
        total_iterations = len(iterations) - 1  # İlk durum hariç
        
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
            'converged': converged,
            'membership_file': os.path.basename(membership_file)
        }
        
        # İteratif sonuçları kaydet (Makale için!)
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
        
        print(f"\n📊 SONUÇ:")
        print(f"  • Toplam İterasyon: {total_iterations}")
        print(f"  • Yakınsama: {'✅ Evet' if converged else '❌ Hayır'}")
        print(f"  💾 İteratif sonuçlar kaydedildi")
        
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
    # Test boyutları ve methodlar
    test_sizes = [(10, 20), (20, 30), (30, 50)]
    methods = ['method1', 'method2', 'method3', 'method4']
    
    results = []
    
    print(f"🎯 {len(test_sizes)} boyut × {len(methods)} method = {len(test_sizes) * len(methods)} test\n")
    
    test_count = 0
    total_tests = len(test_sizes) * len(methods)
    
    for rows, cols in test_sizes:
        for method in methods:
            test_count += 1
            size = f'{rows}x{cols}'
            file_path = f'Textile_data/outputs/binary_matrices/textile_{size}_{method}.csv'
            
            print(f"\n[{test_count}/{total_tests}]")
            
            if os.path.exists(file_path):
                result = test_textile_matrix(file_path, method.upper().replace('METHOD', 'Method '), size)
                if result:
                    results.append(result)
            else:
                print(f"⚠️ Dosya bulunamadı: {file_path}")
    
    # ==========================================
    # SONUÇLARI ÖZETLE VE RAPOR OLUŞTUR
    # ==========================================
    
    print(f"\n\n{'='*100}")
    print("ÖZET RAPOR")
    print(f"{'='*100}\n")
    
    print(f"{'Method':<12} {'Boyut':<10} {'Firma':<8} {'Ürün':<8} {'Yoğunluk':<10} {'İterasyon':<12} {'Yakınsama'}")
    print("-" * 100)
    
    for r in results:
        conv_status = "✅" if r['converged'] else "❌"
        print(f"{r['method']:<12} {r['size']:<10} {r['firms']:<8} {r['products']:<8} "
              f"{r['density']:>6.2f}%    {r['total_iterations']:<12} {conv_status}")
    
    # Method karşılaştırması
    print(f"\n{'='*100}")
    print("METHOD KARŞILAŞTIRMASI")
    print(f"{'='*100}\n")
    
    for method in ['Method 1', 'Method 2', 'Method 3', 'Method 4']:
        method_results = [r for r in results if r['method'] == method]
        if method_results:
            avg_iter = sum(r['total_iterations'] for r in method_results) / len(method_results)
            conv_rate = sum(1 for r in method_results if r['converged']) / len(method_results) * 100
            print(f"{method}: Ortalama İterasyon = {avg_iter:.2f}, Yakınsama Oranı = {conv_rate:.1f}%")
    
    # JSON kaydet (Makale için)
    with open('Textile_data/reports/ADIM3_4_RMVC_Iterative_Summary.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_tests': len(results),
            'test_sizes': [f'{r}x{c}' for r, c in test_sizes],
            'methods': methods,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n💾 ADIM3_4_RMVC_Iterative_Summary.json kaydedildi")
    
    print(f"\n✅ Tüm testler tamamlandı! Toplam: {len(results)} matris")
    print(f"\nBitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
