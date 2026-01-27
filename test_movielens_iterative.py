"""
MovieLens Veri Setleri - Iteratif RMVC Analizi
===============================================
MovieLens veri setlerinde iteratif RMVC yakinsama davranisini inceler.
"""

import pandas as pd
import numpy as np
import os
import sys
from fractions import Fraction
import json
from datetime import datetime

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

def threshold_matrix(membership_matrix, U, threshold_value, operator=">="):
    """Uyelik matrisini esikler."""
    new_matrix = {}
    for e_i in membership_matrix.keys():
        new_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            
            epsilon = 1e-4
            if operator == ">=":
                above_threshold = val >= (threshold_value - epsilon)
            else:
                above_threshold = val > (threshold_value + epsilon)
            
            if above_threshold:
                new_matrix[e_i][u] = 1
            else:
                new_matrix[e_i][u] = 0
    
    return new_matrix

def analyze_matrix_statistics(membership_matrix, U):
    """Matris istatistiklerini hesaplar."""
    all_values = []
    for row in membership_matrix.values():
        all_values.extend([float(v) for v in row.values()])
    
    fractional_values = [v for v in all_values if 0 < v < 1]
    count_zeros = sum(1 for v in all_values if v == 0.0)
    count_ones = sum(1 for v in all_values if v == 1.0)
    
    stats = {
        'total_values': len(all_values),
        'num_zeros': count_zeros,
        'num_ones': count_ones,
        'num_fractional': len(fractional_values),
        'sparsity': count_zeros / len(all_values) if len(all_values) > 0 else 0,
        'density': count_ones / len(all_values) if len(all_values) > 0 else 0,
        'mean': np.mean(all_values) if all_values else 0,
        'min': min(all_values) if all_values else 0,
        'max': max(all_values) if all_values else 0,
    }
    
    return stats

def run_iterative_rmvc(U, E_named, max_iterations=20, threshold_operator=">="):
    """Iteratif RMVC analizi."""
    iterations = []
    current_E = E_named.copy()
    
    for iteration in range(max_iterations):
        # Uyelik matrisini hesapla
        membership_matrix = create_membership_matrix(current_E, U)
        scores = calculate_scores(membership_matrix, U)
        
        # Istatistikleri hesapla
        stats = analyze_matrix_statistics(membership_matrix, U)
        
        # Iterasyon bilgilerini kaydet
        iteration_data = {
            'iteration': iteration,
            'statistics': stats,
            'top_5_scores': sorted([(u, float(s)) for u, s in scores.items()], 
                                  key=lambda x: -x[1])[:5]
        }
        iterations.append(iteration_data)
        
        # Yakinsama kontrolu
        if stats['num_fractional'] == 0:
            convergence_type = 'all_ones' if stats['num_ones'] == stats['total_values'] else 'binary_mixed'
            return {
                'converged': True,
                'type': convergence_type,
                'iterations': iteration,
                'iteration_history': iterations
            }
        
        # Esikleme
        threshold_value = stats['mean']
        thresholded = threshold_matrix(membership_matrix, U, threshold_value, threshold_operator)
        
        # Yeni E_named olustur
        new_E = {}
        for e_i in current_E.keys():
            new_E[e_i] = set(u for u in U if thresholded[e_i][u] == 1)
        
        # Degisim kontrolu
        if new_E == current_E:
            return {
                'converged': True,
                'type': 'binary_mixed',
                'iterations': iteration,
                'iteration_history': iterations
            }
        
        current_E = new_E
    
    return {
        'converged': False,
        'type': 'limit_cycle',
        'iterations': None,
        'iteration_history': iterations
    }

def load_movielens_dataset(filepath):
    """MovieLens RMVC formatindaki Excel dosyasini yukle."""
    df = pd.read_excel(filepath, index_col=0)
    
    U = set(str(col) for col in df.columns)
    E_named = {}
    
    for movie_id in df.index:
        param_key = f"movie_{movie_id}"
        users_who_liked = set(str(col) for col in df.columns if df.loc[movie_id, col] == 1)
        E_named[param_key] = users_who_liked
    
    return U, E_named, df

def analyze_iterative_convergence(filepath, dataset_name):
    """Iteratif yakinsama analizi."""
    print(f"\n{'='*80}")
    print(f"ITERATIF ANALIZ: {dataset_name}")
    print(f"{'='*80}")
    
    # Veri setini yukle
    print(f"\n[1/3] Veri seti yukleniyor...")
    U, E_named, df_original = load_movielens_dataset(filepath)
    
    # Bos parametreleri cikar
    empty_params = [k for k, v in E_named.items() if len(v) == 0]
    for k in empty_params:
        del E_named[k]
    
    print(f"  - Kullanici: {len(U)}, Film: {len(E_named)}")
    
    # Baslangic istatistikleri
    total_ones = sum(len(users) for users in E_named.values())
    total_cells = len(E_named) * len(U)
    initial_density = total_ones / total_cells if total_cells > 0 else 0
    
    print(f"  - Baslangic yogunluk: {initial_density:.4f}")
    
    # Iteratif analiz
    print(f"\n[2/3] Iteratif RMVC calistiriliyor...")
    result = run_iterative_rmvc(U, E_named, max_iterations=20, threshold_operator=">=")
    
    print(f"  - Yakinsama: {'EVET' if result['converged'] else 'HAYIR'}")
    print(f"  - Yakinsama tipi: {result['type']}")
    print(f"  - Iterasyon sayisi: {result['iterations'] if result['iterations'] is not None else 'N/A'}")
    
    # Iterasyon gecmisi
    print(f"\n[3/3] Iterasyon gecmisi:")
    print(f"  {'Iter':<6} {'Seyreklik':<12} {'Yogunluk':<12} {'Ortalama':<12} {'Ondalik':<12}")
    print(f"  {'-'*60}")
    
    for iter_data in result['iteration_history']:
        stats = iter_data['statistics']
        print(f"  {iter_data['iteration']:<6} {stats['sparsity']:<12.4f} {stats['density']:<12.4f} "
              f"{stats['mean']:<12.4f} {stats['num_fractional']:<12}")
    
    return {
        'dataset_name': dataset_name,
        'filepath': filepath,
        'num_users': len(U),
        'num_movies': len(E_named),
        'initial_density': initial_density,
        'convergence': result
    }

def main():
    """Ana fonksiyon."""
    print("="*80)
    print("MOVIELENS - ITERATIF RMVC YAKINSAMA ANALIZI")
    print("="*80)
    print()
    
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
            results = analyze_iterative_convergence(filepath, name)
            all_results.append(results)
        except Exception as e:
            print(f"\n[HATA] {name} analiz edilirken hata: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Ozet rapor
    print(f"\n{'='*80}")
    print("OZET RAPOR - ITERATIF YAKINSAMA")
    print(f"{'='*80}")
    print()
    
    print(f"{'Dataset':<20} {'Boyut':<12} {'Bas.Yog':<12} {'Yakinsama':<15} {'Iterasyon':<12}")
    print("-"*80)
    
    for r in all_results:
        size_str = f"{r['num_movies']}x{r['num_users']}"
        iter_str = str(r['convergence']['iterations']) if r['convergence']['iterations'] is not None else 'N/A'
        print(f"{r['dataset_name']:<20} {size_str:<12} {r['initial_density']:<12.4f} "
              f"{r['convergence']['type']:<15} {iter_str:<12}")
    
    # Sonuclari kaydet
    output_file = os.path.join(os.path.dirname(__file__), 
                               f"movielens_iterative_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print("TAMAMLANDI!")
    print(f"{'='*80}")
    print(f"\nSonuclar kaydedildi: {output_file}")

if __name__ == "__main__":
    main()
