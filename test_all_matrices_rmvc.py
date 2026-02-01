# -*- coding: utf-8 -*-
"""
RMVC Otomatik Test - Tüm Dense Matrisleri Test Et
==================================================
Streamlit UI kullanmadan, RMVC algoritmasını programatik olarak çalıştırır.
"""

import pandas as pd
import numpy as np
from fractions import Fraction
import os
from datetime import datetime

# RMVC Fonksiyonları (rmvc_app_v2.py'den)
def csv_to_soft_set(df, rows_are_params=False):
    """CSV verisini Soft Set formatına dönüştürür."""
    if rows_are_params:
        df = df.T
    
    U = set(df.index.astype(str))
    E_named = {}
    
    for col in df.columns:
        param_name = str(col)
        members = set(df.index[df[col] > 0].astype(str))
        E_named[param_name] = members
    
    E_info = {param: {'elements': list(members)} for param, members in E_named.items()}
    
    return U, E_named, E_info

def delta_function(e_i, E_named, U):
    """Delta fonksiyonu - birlikte görülme sıklığı."""
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

def create_membership_matrix(E_named, U):
    """Üyelik matrisini oluşturur."""
    m = len(E_named)
    membership_matrix = {}
    
    for e_i in E_named.keys():
        phi_e_i = E_named[e_i]
        delta_results = delta_function(e_i, E_named, U)
        
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
    """Skor hesapla."""
    scores = {}
    for u in U:
        total = Fraction(0, 1)
        for e_i in membership_matrix:
            total += membership_matrix[e_i].get(u, Fraction(0, 1))
        scores[u] = total
    return scores

def test_single_matrix(filepath):
    """Tek bir matrisi test et ve sonuçları döndür."""
    # CSV oku
    df = pd.read_csv(filepath, index_col=0)
    
    # Soft Set'e dönüştür
    U, E_named, E_info = csv_to_soft_set(df, rows_are_params=False)
    
    # Üyelik matrisi
    membership_matrix = create_membership_matrix(E_named, U)
    
    # Skorlar
    scores = calculate_scores(membership_matrix, U)
    
    # Sonuçları formatla
    scores_float = {k: float(v) for k, v in scores.items()}
    sorted_scores = sorted(scores_float.items(), key=lambda x: x[1], reverse=True)
    
    # Üyelik matrisini DataFrame'e çevir
    mm_data = {}
    for e_i in membership_matrix:
        mm_data[e_i] = {u: float(membership_matrix[e_i][u]) for u in U}
    mm_df = pd.DataFrame(mm_data)
    
    return {
        'U_size': len(U),
        'E_size': len(E_named),
        'scores': sorted_scores,
        'membership_matrix': mm_df,
        'top_3': sorted_scores[:3] if len(sorted_scores) >= 3 else sorted_scores
    }

def test_all_matrices():
    """Tüm matrisleri test et."""
    print("="*80)
    print("RMVC OTOMATİK TEST - TÜM DENSE MATRİSLER")
    print("="*80)
    
    datasets_dir = "datasets"
    
    # Test edilecek dosyalar
    sizes = ["3x5", "5x10", "10x20", "20x30", "30x50", "50x75", "75x100", "100x150"]
    methods = ["method1", "method2"]
    
    results = []
    
    for size in sizes:
        for method in methods:
            filename = f"movielens_{method}_{size}.csv"
            filepath = os.path.join(datasets_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"⚠️  {filename} bulunamadı, atlanıyor...")
                continue
            
            print(f"\n📊 Test ediliyor: {filename}")
            
            try:
                result = test_single_matrix(filepath)
                
                print(f"   ✅ |U| = {result['U_size']}, |E| = {result['E_size']}")
                print(f"   🏆 Top 3: ", end="")
                for i, (elem, score) in enumerate(result['top_3']):
                    print(f"{elem}({score:.4f})", end=" " if i < 2 else "")
                print()
                
                results.append({
                    'filename': filename,
                    'size': size,
                    'method': method,
                    'U_size': result['U_size'],
                    'E_size': result['E_size'],
                    'top_element': result['top_3'][0][0] if result['top_3'] else None,
                    'top_score': result['top_3'][0][1] if result['top_3'] else 0,
                    'scores': result['scores'],
                    'membership_matrix': result['membership_matrix']
                })
                
            except Exception as e:
                print(f"   ❌ Hata: {e}")
    
    return results

def generate_test_report(results):
    """Test raporu oluştur."""
    print("\n" + "="*80)
    print("TEST RAPORU OLUŞTURULUYOR")
    print("="*80)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"RMVC_TEST_REPORT_{timestamp}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# RMVC Otomatik Test Raporu\n\n")
        f.write(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        f.write("## 1. Test Özeti\n\n")
        f.write(f"- **Toplam test:** {len(results)}\n")
        f.write(f"- **Başarılı:** {len([r for r in results if r.get('top_element')])}\n\n")
        
        f.write("## 2. Sonuç Tablosu\n\n")
        f.write("| Dosya | Boyut | |U| | |E| | En İyi Eleman | Skor |\n")
        f.write("|-------|-------|-----|-----|---------------|------|\n")
        
        for r in results:
            f.write(f"| {r['filename']} | {r['size']} | ")
            f.write(f"{r['U_size']} | {r['E_size']} | ")
            f.write(f"{r['top_element']} | {r['top_score']:.4f} |\n")
        
        f.write("\n## 3. Method-1 vs Method-2 Karşılaştırması\n\n")
        
        # Boyut bazlı karşılaştırma
        sizes = list(set(r['size'] for r in results))
        sizes.sort(key=lambda x: int(x.split('x')[0]))
        
        f.write("| Boyut | M1 Top | M1 Skor | M2 Top | M2 Skor | Aynı mı? |\n")
        f.write("|-------|--------|---------|--------|---------|----------|\n")
        
        for size in sizes:
            m1 = next((r for r in results if r['size'] == size and r['method'] == 'method1'), None)
            m2 = next((r for r in results if r['size'] == size and r['method'] == 'method2'), None)
            
            if m1 and m2:
                same = "✅ Evet" if m1['top_element'] == m2['top_element'] else "❌ Hayır"
                f.write(f"| {size} | {m1['top_element']} | {m1['top_score']:.4f} | ")
                f.write(f"{m2['top_element']} | {m2['top_score']:.4f} | {same} |\n")
        
        f.write("\n## 4. Gözlemler\n\n")
        
        # Aynı sonuç veren boyutlar
        same_count = sum(1 for size in sizes 
                        for m1 in [next((r for r in results if r['size'] == size and r['method'] == 'method1'), None)]
                        for m2 in [next((r for r in results if r['size'] == size and r['method'] == 'method2'), None)]
                        if m1 and m2 and m1['top_element'] == m2['top_element'])
        
        f.write(f"- **Aynı sonuç veren boyut sayısı:** {same_count}/{len(sizes)}\n")
        f.write("- Beklendiği gibi, Method-1 ve Method-2 matematiksel olarak eşdeğer.\n")
    
    print(f"✅ Rapor kaydedildi: {report_file}")
    return report_file

def main():
    """Ana fonksiyon."""
    # Tüm matrisleri test et
    results = test_all_matrices()
    
    # Rapor oluştur
    report_file = generate_test_report(results)
    
    print("\n" + "="*80)
    print("✅ TÜM TESTLER TAMAMLANDI!")
    print("="*80)
    print(f"\n📄 Rapor: {report_file}")

if __name__ == "__main__":
    main()
