"""
MovieLens Veri Setlerini RMVC ile Test Etme
============================================
5 farkli MovieLens alt kumesini RMVC ile test eder ve sonuclari kaydeder.
"""

import pandas as pd
import numpy as np
import os
import sys
from fractions import Fraction
import json
from datetime import datetime

# RMVC fonksiyonlarini import et
sys.path.append(os.path.dirname(__file__))

def delta_function(u, e_i, E_named):
    """Delta fonksiyonu."""
    if u not in E_named[e_i]:
        return 0
    
    phi_ei = E_named[e_i]
    total = 0
    
    for v in phi_ei:
        if v == u:
            continue
        
        count = sum(1 for e_j, phi_ej in E_named.items() 
                   if u in phi_ej and v in phi_ej)
        total += count
    
    return total

def create_membership_matrix(E_named, U):
    """Uyelik matrisini olustur."""
    m = len(E_named)
    membership_matrix = {}
    
    for e_i in E_named.keys():
        membership_matrix[e_i] = {}
        phi_ei = E_named[e_i]
        phi_ei_size = len(phi_ei)
        
        if phi_ei_size == 0:
            for u in U:
                membership_matrix[e_i][u] = Fraction(0, 1)
            continue
        
        for u in U:
            delta_val = delta_function(u, e_i, E_named)
            denominator = phi_ei_size * (m - 1)
            
            if denominator == 0:
                membership_matrix[e_i][u] = Fraction(0, 1)
            else:
                membership_matrix[e_i][u] = Fraction(delta_val, denominator)
    
    return membership_matrix

def calculate_scores(membership_matrix, U):
    """Skor hesapla."""
    scores = {}
    
    for u in U:
        total = Fraction(0, 1)
        for e_i, row in membership_matrix.items():
            total += row.get(u, Fraction(0, 1))
        scores[u] = total
    
    return scores

def load_movielens_dataset(filepath):
    """MovieLens RMVC formatindaki Excel dosyasini yukle."""
    df = pd.read_excel(filepath, index_col=0)
    
    # RMVC formatinda: Satirlar=Filmler (parametreler), Sutunlar=Kullanicilar (elemanlar)
    # Soft set formatina donustur
    U = set(str(col) for col in df.columns)
    E_named = {}
    
    for movie_id in df.index:
        param_key = f"movie_{movie_id}"
        # Bu filmi begenen kullanicilar (deger=1 olanlar)
        users_who_liked = set(str(col) for col in df.columns if df.loc[movie_id, col] == 1)
        E_named[param_key] = users_who_liked
    
    return U, E_named, df

def analyze_dataset(filepath, dataset_name):
    """Veri setini analiz et."""
    print(f"\n{'='*80}")
    print(f"DATASET: {dataset_name}")
    print(f"{'='*80}")
    
    # Veri setini yukle
    print(f"\n[1/5] Veri seti yukleniyor: {filepath}")
    U, E_named, df_original = load_movielens_dataset(filepath)
    
    print(f"  - Kullanici sayisi (|U|): {len(U)}")
    print(f"  - Film sayisi (m): {len(E_named)}")
    print(f"  - Matris boyutu: {len(E_named)} x {len(U)}")
    print(f"  - Toplam deger: {len(E_named) * len(U)}")
    
    # Baslangic istatistikleri
    total_ones = sum(len(users) for users in E_named.values())
    total_cells = len(E_named) * len(U)
    density = total_ones / total_cells if total_cells > 0 else 0
    sparsity = 1 - density
    
    print(f"  - 1'lerin sayisi: {total_ones}")
    print(f"  - Yogunluk: {density:.4f}")
    print(f"  - Seyreklik: {sparsity:.4f}")
    
    # Bos parametreleri kontrol et
    empty_params = [k for k, v in E_named.items() if len(v) == 0]
    if empty_params:
        print(f"  - UYARI: {len(empty_params)} bos parametre var (hic kullanici begenmedis)")
        # Bos parametreleri cikar
        for k in empty_params:
            del E_named[k]
        print(f"  - Bos parametreler cikarildi. Yeni m: {len(E_named)}")
    
    # RMVC hesapla
    print(f"\n[2/5] RMVC hesaplaniyor...")
    membership_matrix = create_membership_matrix(E_named, U)
    scores = calculate_scores(membership_matrix, U)
    
    # Skorlari sirala
    sorted_scores = sorted(scores.items(), key=lambda x: (-float(x[1]), x[0]))
    
    print(f"  - Uyelik matrisi olusturuldu")
    print(f"  - Skorlar hesaplandi")
    
    # Istatistikler
    score_values = [float(s) for s in scores.values()]
    print(f"\n[3/5] Skor istatistikleri:")
    print(f"  - Ortalama skor: {np.mean(score_values):.4f}")
    print(f"  - Std skor: {np.std(score_values):.4f}")
    print(f"  - Min skor: {min(score_values):.4f}")
    print(f"  - Max skor: {max(score_values):.4f}")
    print(f"  - Medyan skor: {np.median(score_values):.4f}")
    
    # En iyi secimler
    best_score = float(sorted_scores[0][1])
    best_choices = [u for u, s in sorted_scores if float(s) == best_score]
    
    print(f"\n[4/5] Optimal secim:")
    print(f"  - En iyi skor: {best_score:.4f}")
    print(f"  - En iyi kullanici sayisi: {len(best_choices)}")
    print(f"  - En iyi kullanicilar: {', '.join(best_choices[:5])}" + 
          (f" ... (+{len(best_choices)-5} daha)" if len(best_choices) > 5 else ""))
    
    # Top 10 kullanici
    print(f"\n[5/5] Top 10 kullanici:")
    for i, (user, score) in enumerate(sorted_scores[:10], 1):
        print(f"  {i:2d}. Kullanici {user:10s}: {float(score):.4f}")
    
    # Sonuclari kaydet
    results = {
        'dataset_name': dataset_name,
        'filepath': filepath,
        'num_users': len(U),
        'num_movies': len(E_named),
        'matrix_size': len(E_named) * len(U),
        'density': density,
        'sparsity': sparsity,
        'total_ones': total_ones,
        'score_statistics': {
            'mean': float(np.mean(score_values)),
            'std': float(np.std(score_values)),
            'min': float(min(score_values)),
            'max': float(max(score_values)),
            'median': float(np.median(score_values))
        },
        'best_score': best_score,
        'num_best_choices': len(best_choices),
        'best_choices': best_choices[:10],
        'top_10_users': [(u, float(s)) for u, s in sorted_scores[:10]],
        'all_scores': {u: float(s) for u, s in scores.items()}
    }
    
    return results

def main():
    """Ana fonksiyon."""
    print("="*80)
    print("MOVIELENS VERI SETLERI - RMVC TESTI")
    print("="*80)
    print()
    
    # Veri setleri
    datasets_dir = os.path.join(os.path.dirname(__file__), "datasets")
    
    datasets = [
        ("movielens_10x5_rmvc.xlsx", "MovieLens 10x5"),
        ("movielens_20x10_rmvc.xlsx", "MovieLens 20x10"),
        ("movielens_30x15_rmvc.xlsx", "MovieLens 30x15"),
        ("movielens_50x25_rmvc.xlsx", "MovieLens 50x25"),
        ("movielens_100x50_rmvc.xlsx", "MovieLens 100x50")
    ]
    
    all_results = []
    
    for filename, name in datasets:
        filepath = os.path.join(datasets_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"\n[UYARI] Dosya bulunamadi: {filepath}")
            continue
        
        try:
            results = analyze_dataset(filepath, name)
            all_results.append(results)
        except Exception as e:
            print(f"\n[HATA] {name} analiz edilirken hata: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Ozet rapor
    print(f"\n{'='*80}")
    print("OZET RAPOR")
    print(f"{'='*80}")
    print()
    
    print(f"{'Dataset':<20} {'Boyut':<12} {'Yogunluk':<12} {'Ort Skor':<12} {'En Iyi Skor':<12}")
    print("-"*80)
    
    for r in all_results:
        size_str = f"{r['num_movies']}x{r['num_users']}"
        print(f"{r['dataset_name']:<20} {size_str:<12} {r['density']:<12.4f} "
              f"{r['score_statistics']['mean']:<12.4f} {r['best_score']:<12.4f}")
    
    # Sonuclari kaydet
    output_file = os.path.join(os.path.dirname(__file__), 
                               f"movielens_rmvc_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("TAMAMLANDI!")
    print(f"{'='*80}")
    print(f"\nSonuclar kaydedildi: {output_file}")
    print("\nSonraki adim: Iteratif RMVC analizi")

if __name__ == "__main__":
    main()
