"""
İteratif RMVC Yakınsama Deneyi
================================
Farklı seyreklik seviyelerinde matrisler oluşturarak yakınsama davranışını analiz eder.

Araştırma Soruları:
1. Ne zaman tüm değerler 1'e yakınsar?
2. Ne zaman tüm değerler 0'a yakınsar?
3. İterasyon sayısı ile seyreklik arasındaki ilişki nedir?
"""

import numpy as np
import pandas as pd
from fractions import Fraction
import json
from datetime import datetime
import os

# RMVC fonksiyonları (rmvc_app_v2.py'den)

def safe_sort_key(x):
    """Sayısal ve metinsel değerleri karışık sıralamak için güvenli anahtar."""
    try:
        return (0, "", int(x))
    except (ValueError, TypeError):
        try:
            return (0, "", float(x))
        except (ValueError, TypeError):
            return (1, str(x), 0)

def delta_function(e_i, E_named, U):
    """Delta fonksiyonu - Makaledeki formüle göre."""
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
    """Her eleman için toplam skoru hesaplar."""
    scores = {}
    
    for u in U:
        total = Fraction(0, 1)
        for e_i, row in membership_matrix.items():
            total += row.get(u, Fraction(0, 1))
        scores[u] = total
    
    return scores

def threshold_matrix(membership_matrix, U, threshold_value, keep_below_threshold=False, operator=">="):
    """Üyelik matrisini eşikler."""
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
                if keep_below_threshold:
                    new_matrix[e_i][u] = val
                else:
                    new_matrix[e_i][u] = 0
    
    return new_matrix

def generate_random_soft_set(num_params, num_elements, sparsity):
    """
    Rastgele soft set oluşturur.
    
    Args:
        num_params: Parametre sayısı (m)
        num_elements: Eleman sayısı (n)
        sparsity: Seyreklik oranı [0, 1] (0 = yoğun, 1 = çok seyrek)
    
    Returns:
        U: Evrensel küme
        E_named: Parametrelerin içerdiği elemanlar
    """
    U = set(str(i) for i in range(1, num_elements + 1))
    E_named = {}
    
    for i in range(1, num_params + 1):
        e_key = f"e_{i}"
        
        # Her parametre için rastgele eleman seç
        # Seyreklik: her parametrenin kaç eleman içereceğini belirler
        # sparsity=0 → tüm elemanlar, sparsity=1 → çok az eleman
        base_count = max(1, int(num_elements * (1 - sparsity)))
        
        # Seyreklik 0 için bile varyasyon ekle: %80-100 arası rastgele
        if sparsity == 0:
            variation = np.random.uniform(0.8, 1.0)
            num_elements_in_param = max(1, int(num_elements * variation))
        else:
            # Diger seyreklik seviyeleri icin de +/- %20 varyasyon
            variation = np.random.uniform(0.8, 1.2)
            num_elements_in_param = max(1, min(num_elements, int(base_count * variation)))
        
        # Rastgele eleman seç
        selected_elements = set(np.random.choice(list(U), num_elements_in_param, replace=False))
        E_named[e_key] = selected_elements
    
    return U, E_named

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
        'fractional_mean': np.mean(fractional_values) if fractional_values else 0,
        'fractional_min': min(fractional_values) if fractional_values else 0,
        'fractional_max': max(fractional_values) if fractional_values else 0,
    }
    
    return stats

def run_iterative_rmvc(U, E_named, max_iterations=20, threshold_operator=">="):
    """
    İteratif RMVC analizi yapar ve yakınsama davranışını kaydeder.
    
    Returns:
        dict: Deney sonuçları
    """
    iterations = []
    current_E = E_named.copy()
    
    for iteration in range(max_iterations):
        # Üyelik matrisini hesapla
        membership_matrix = create_membership_matrix(current_E, U)
        scores = calculate_scores(membership_matrix, U)
        
        # İstatistikleri hesapla
        stats = analyze_matrix_statistics(membership_matrix, U)
        
        # İterasyon bilgilerini kaydet
        iteration_data = {
            'iteration': iteration,
            'statistics': stats,
            'membership_matrix': {
                e_i: {u: float(v) for u, v in row.items()}
                for e_i, row in membership_matrix.items()
            }
        }
        iterations.append(iteration_data)
        
        # Yakınsama kontrolü
        if stats['num_fractional'] == 0:
            # Yakınsama tamamlandı
            if stats['num_ones'] == stats['total_values']:
                convergence_type = 'all_ones'
            elif stats['num_zeros'] == stats['total_values']:
                convergence_type = 'all_zeros'
            else:
                convergence_type = 'binary_mixed'
            
            return {
                'converged': True,
                'convergence_type': convergence_type,
                'iterations_to_converge': iteration,
                'iterations': iterations
            }
        
        # Eşik değerini hesapla (ondalıklı değerlerin ortalaması)
        all_values = []
        for row in membership_matrix.values():
            all_values.extend([float(v) for v in row.values()])
        
        fractional_values = [v for v in all_values if 0 < v < 1]
        
        if not fractional_values:
            break
        
        threshold = np.mean(fractional_values)
        
        # Eşikleme uygula
        thresholded_matrix = threshold_matrix(
            membership_matrix, U, threshold, 
            keep_below_threshold=False, 
            operator=threshold_operator
        )
        
        # Yeni E_named oluştur
        new_E = {}
        for e_key in thresholded_matrix.keys():
            new_E[e_key] = set()
            for u, val in thresholded_matrix[e_key].items():
                if val == 1:
                    new_E[e_key].add(u)
        
        # Limit cycle kontrolü
        if iteration > 0:
            # Önceki iterasyonla aynı mı?
            prev_stats = iterations[-2]['statistics']
            if (stats['num_fractional'] == prev_stats['num_fractional'] and
                abs(stats['fractional_mean'] - prev_stats['fractional_mean']) < 1e-6):
                # Limit cycle
                return {
                    'converged': False,
                    'convergence_type': 'limit_cycle',
                    'iterations_to_converge': None,
                    'iterations': iterations
                }
        
        current_E = new_E
    
    # Max iterasyona ulaşıldı
    return {
        'converged': False,
        'convergence_type': 'max_iterations_reached',
        'iterations_to_converge': None,
        'iterations': iterations
    }

def run_experiment_suite():
    """Kapsamlı deney seti çalıştırır."""
    
    # Deney parametreleri
    # NOT: Seyreklik 0.0 yerine 0.00-0.10 arası rastgele değerler kullanılıyor
    # Böylece her matris gerçekten farklı oluyor (makale için önemli)
    sparsity_levels = [0.0, 0.25, 0.5, 0.75, 0.9]
    matrix_sizes = [
        (3, 3),   # 9 değer
        (4, 5),   # 20 değer (Example.1)
        (5, 5),   # 25 değer
        (6, 8),   # 48 değer
        (8, 10),  # 80 değer
    ]
    
    num_trials_per_config = 10  # Her konfigürasyon için 10 deneme
    
    results = []
    experiment_id = 0
    
    print("=" * 80)
    print("ITERATIF RMVC YAKINSAMA DENEYI")
    print("=" * 80)
    print(f"Toplam Deney Sayisi: {len(sparsity_levels) * len(matrix_sizes) * num_trials_per_config}")
    print()
    
    for sparsity in sparsity_levels:
        for num_params, num_elements in matrix_sizes:
            print(f"\n{'='*60}")
            print(f"Seyreklik: {sparsity:.2f} | Boyut: {num_params}×{num_elements}")
            print(f"{'='*60}")
            
            for trial in range(num_trials_per_config):
                experiment_id += 1
                
                # Seyreklik 0.0 için her denemede farklı değer (0.00-0.10 arası)
                # Böylece her matris gerçekten farklı oluyor
                actual_sparsity = sparsity
                if sparsity == 0.0:
                    actual_sparsity = np.random.uniform(0.0, 0.10)
                
                # Rastgele soft set oluştur
                U, E_named = generate_random_soft_set(num_params, num_elements, actual_sparsity)
                
                # İlk üyelik matrisini hesapla
                initial_membership = create_membership_matrix(E_named, U)
                initial_stats = analyze_matrix_statistics(initial_membership, U)
                
                # İteratif RMVC çalıştır
                result = run_iterative_rmvc(U, E_named)
                
                # Sonuçları kaydet
                experiment_result = {
                    'experiment_id': experiment_id,
                    'config': {
                        'target_sparsity': sparsity,
                        'num_params': num_params,
                        'num_elements': num_elements,
                        'matrix_size': num_params * num_elements,
                        'param_element_ratio': num_params / num_elements
                    },
                    'initial_statistics': initial_stats,
                    'convergence': {
                        'converged': result['converged'],
                        'type': result['convergence_type'],
                        'iterations': result['iterations_to_converge']
                    },
                    'iteration_history': result['iterations']
                }
                
                results.append(experiment_result)
                
                # İlerleme göster
                conv_str = f"{result['convergence_type']}"
                iter_str = f"{result['iterations_to_converge']}" if result['iterations_to_converge'] is not None else "N/A"
                print(f"  Deneme {trial+1:2d}: {conv_str:20s} | Iterasyon: {iter_str:3s} | "
                      f"Baslangic Seyreklik: {initial_stats['sparsity']:.3f}")
    
    return results

def save_results(results, filename=None):
    """Sonuçları JSON dosyasına kaydeder."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"convergence_experiment_{timestamp}.json"
    
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Sonuclar kaydedildi: {filepath}")
    return filepath

def analyze_results(results):
    """Deney sonuçlarını analiz eder ve özet çıkarır."""
    
    print("\n" + "=" * 80)
    print("DENEY SONUCLARI ANALIZI")
    print("=" * 80)
    
    # Yakınsama tiplerine göre grupla
    convergence_types = {}
    for r in results:
        conv_type = r['convergence']['type']
        if conv_type not in convergence_types:
            convergence_types[conv_type] = []
        convergence_types[conv_type].append(r)
    
    print(f"\nToplam Deney Sayisi: {len(results)}")
    print("\nYakinsama Tipleri:")
    for conv_type, experiments in convergence_types.items():
        percentage = (len(experiments) / len(results)) * 100
        print(f"  {conv_type:20s}: {len(experiments):4d} ({percentage:5.1f}%)")
    
    # Yakınsama olan deneyleri analiz et
    converged_experiments = [r for r in results if r['convergence']['converged']]
    
    if converged_experiments:
        print(f"\nYakinsama Istatistikleri (n={len(converged_experiments)}):")
        
        iterations = [r['convergence']['iterations'] for r in converged_experiments]
        print(f"  Ortalama Iterasyon: {np.mean(iterations):.2f}")
        print(f"  Min Iterasyon: {min(iterations)}")
        print(f"  Max Iterasyon: {max(iterations)}")
        print(f"  Std Iterasyon: {np.std(iterations):.2f}")
        
        # Seyrekliğe göre analiz
        print("\nSeyrekllige Gore Yakinsama:")
        sparsity_groups = {}
        for r in converged_experiments:
            sparsity = r['config']['target_sparsity']
            if sparsity not in sparsity_groups:
                sparsity_groups[sparsity] = []
            sparsity_groups[sparsity].append(r['convergence']['iterations'])
        
        for sparsity in sorted(sparsity_groups.keys()):
            iters = sparsity_groups[sparsity]
            print(f"  Seyreklik {sparsity:.2f}: Ort İter={np.mean(iters):.2f}, "
                  f"Min={min(iters)}, Max={max(iters)}")
    
    # all_ones yakınsama analizi
    all_ones = [r for r in results if r['convergence']['type'] == 'all_ones']
    if all_ones:
        print(f"\nTum 1'e Yakinsama Analizi (n={len(all_ones)}):")
        
        initial_densities = [r['initial_statistics']['density'] for r in all_ones]
        print(f"  Baslangic Yogunluk Ortalamasi: {np.mean(initial_densities):.3f}")
        
        initial_means = [r['initial_statistics']['mean'] for r in all_ones]
        print(f"  Baslangic Deger Ortalamasi: {np.mean(initial_means):.3f}")
    
    # all_zeros yakınsama analizi
    all_zeros = [r for r in results if r['convergence']['type'] == 'all_zeros']
    if all_zeros:
        print(f"\nTum 0'a Yakinsama Analizi (n={len(all_zeros)}):")
        
        initial_sparsities = [r['initial_statistics']['sparsity'] for r in all_zeros]
        print(f"  Baslangic Seyreklik Ortalamasi: {np.mean(initial_sparsities):.3f}")
        
        initial_means = [r['initial_statistics']['mean'] for r in all_zeros]
        print(f"  Baslangic Deger Ortalamasi: {np.mean(initial_means):.3f}")

if __name__ == "__main__":
    print("Iteratif RMVC Yakinsama Deneyi Baslatiliyor...")
    print()
    
    # Deneyleri çalıştır
    results = run_experiment_suite()
    
    # Sonuçları kaydet
    filepath = save_results(results)
    
    # Sonuçları analiz et
    analyze_results(results)
    
    print("\n" + "=" * 80)
    print("DENEY TAMAMLANDI")
    print("=" * 80)
    print(f"Sonuc dosyasi: {filepath}")
    print("\nSonraki adim: Gorsellestirme ve detayli analiz icin")
    print("convergence_analysis.py scriptini calistirin.")
