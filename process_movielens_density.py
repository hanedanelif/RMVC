# -*- coding: utf-8 -*-
"""
MovieLens Density Analysis - Tekstil Veri Seti Yaklaşımının MovieLens'e Uyarlanması
=====================================================================================
Bu script, tekstil veri setinde yapılan yoğunlaştırma (densification) işlemini
MovieLens 100k veri setine uygular:

1. Kullanıcıları ve Filmleri aktiviteye göre sıralar (Permütasyon)
2. Farklı boyutlarda yoğun çekirdek bölgeler keser (3x5, 5x10, 10x20 vb.)
3. Her bölge için yoğunluk analizi yapar
4. Görselleştirme ve CSV export yapar
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dataset_loader import DatasetLoader

# Stil ayarları
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 8)

def calculate_density(matrix):
    """Matrisin yoğunluğunu (doluluk oranını) hesaplar."""
    total_elements = matrix.size
    non_zero_elements = np.count_nonzero(matrix)
    density = (non_zero_elements / total_elements) * 100
    return density

def sort_matrix_by_activity(df_binary):
    """
    Matrisi aktiviteye göre sıralar (Permütasyon).
    
    Args:
        df_binary: Binary matris (User x Movie)
    
    Returns:
        df_sorted: Sıralanmış matris
        user_activity: Kullanıcı aktiviteleri
        movie_popularity: Film popülerlikleri
    """
    print("\n" + "="*80)
    print("ADIM 1: MATRİSİ AKTİVİTEYE GÖRE SIRALAMA (PERMÜTASYON)")
    print("="*80)
    
    # Kullanıcı aktivitesi: Her kullanıcının kaç film izlediği (0'dan büyük sayısı)
    user_activity = (df_binary > 0).sum(axis=1)
    sorted_users = user_activity.sort_values(ascending=False).index
    
    # Film popülerliği: Her filmi kaç kullanıcının izlediği
    movie_popularity = (df_binary > 0).sum(axis=0)
    sorted_movies = movie_popularity.sort_values(ascending=False).index
    
    # Matrisi yeniden sırala
    df_sorted = df_binary.loc[sorted_users, sorted_movies]
    
    print(f"✅ Matris sıralandı:")
    print(f"   - En aktif kullanıcı: {sorted_users[0]} ({user_activity.max()} film)")
    print(f"   - En popüler film: {sorted_movies[0]} ({movie_popularity.max()} izlenme)")
    
    return df_sorted, user_activity, movie_popularity

def analyze_density_regions(df_sorted, region_sizes):
    """
    Farklı boyutlardaki bölgelerin yoğunluğunu analiz eder.
    
    Args:
        df_sorted: Sıralanmış matris
        region_sizes: (num_users, num_movies) tuple listesi
    
    Returns:
        results: Analiz sonuçları
    """
    print("\n" + "="*80)
    print("ADIM 2: FARKLI BOYUTLARDA YOĞUNLUK ANALİZİ")
    print("="*80)
    
    # Global yoğunluk
    global_density = calculate_density(df_sorted)
    print(f"\n📊 GLOBAL MATRİS İSTATİSTİKLERİ:")
    print(f"   - Boyut: {df_sorted.shape[0]} kullanıcı × {df_sorted.shape[1]} film")
    print(f"   - Genel Yoğunluk: %{global_density:.4f}")
    
    # Her bölge için analiz
    results = []
    print(f"\n🔍 BÖLGE BAZLI YOĞUNLUKlar:")
    print(f"{'Boyut':<15} {'Yoğunluk':>10} {'İyileşme':>12}")
    print("-" * 40)
    
    for num_users, num_movies in region_sizes:
        # Matrisi kes
        region = df_sorted.iloc[:num_users, :num_movies]
        
        # Yoğunluğu hesapla
        region_density = calculate_density(region)
        improvement_factor = region_density / global_density if global_density > 0 else 0
        
        results.append({
            'size': f"{num_users}x{num_movies}",
            'num_users': num_users,
            'num_movies': num_movies,
            'density': region_density,
            'improvement': improvement_factor,
            'matrix': region
        })
        
        print(f"{num_users}x{num_movies:<10} %{region_density:>8.4f}   {improvement_factor:>8.2f}x")
    
    return results, global_density

def visualize_regions(results, output_dir='analysis_plots'):
    """
    Bölgeleri görselleştirir.
    
    Args:
        results: Analiz sonuçları
        output_dir: Çıktı klasörü
    """
    print("\n" + "="*80)
    print("ADIM 3: GÖRSELLEŞTİRME")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Her bölge için heatmap
    num_plots = len(results)
    cols = 3
    rows = (num_plots + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(18, rows * 5))
    axes = axes.flatten() if num_plots > 1 else [axes]
    
    for idx, result in enumerate(results):
        ax = axes[idx]
        matrix = result['matrix']
        
        # Heatmap
        sns.heatmap(
            matrix,
            ax=ax,
            cmap="YlGnBu",
            cbar=True,
            xticklabels=False,
            yticklabels=False,
            cbar_kws={'label': 'Rating (Binary)'}
        )
        
        ax.set_title(
            f"{result['size']} Matris\n"
            f"Yoğunluk: %{result['density']:.2f} "
            f"(İyileşme: {result['improvement']:.2f}x)",
            fontsize=12,
            fontweight='bold'
        )
        ax.set_xlabel(f"Filmler (İlk {result['num_movies']})")
        ax.set_ylabel(f"Kullanıcılar (İlk {result['num_users']})")
    
    # Boş grafikleri gizle
    for idx in range(num_plots, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    heatmap_path = os.path.join(output_dir, 'movielens_density_heatmaps.png')
    plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
    print(f"✅ Heatmap kaydedildi: {heatmap_path}")
    plt.close()
    
    # Yoğunluk karşılaştırma grafiği
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sizes = [r['size'] for r in results]
    densities = [r['density'] for r in results]
    improvements = [r['improvement'] for r in results]
    
    x = np.arange(len(sizes))
    width = 0.35
    
    ax.bar(x - width/2, densities, width, label='Yoğunluk (%)', color='skyblue')
    ax.bar(x + width/2, improvements, width, label='İyileşme Faktörü (x)', color='coral')
    
    ax.set_xlabel('Matris Boyutu', fontsize=12)
    ax.set_ylabel('Değer', fontsize=12)
    ax.set_title('MovieLens Yoğunluk Analizi - Boyut Karşılaştırması', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(sizes, rotation=45)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    comparison_path = os.path.join(output_dir, 'movielens_density_comparison.png')
    plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
    print(f"✅ Karşılaştırma grafiği kaydedildi: {comparison_path}")
    plt.close()

def export_matrices(results, output_dir='datasets'):
    """
    Yoğun matrisleri CSV olarak kaydeder.
    
    Args:
        results: Analiz sonuçları
        output_dir: Çıktı klasörü
    """
    print("\n" + "="*80)
    print("ADIM 4: MATRİSLERİ CSV OLARAK KAYDETME")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    for result in results:
        filename = f"movielens_dense_{result['size']}.csv"
        filepath = os.path.join(output_dir, filename)
        
        matrix = result['matrix']
        matrix.to_csv(filepath)
        
        print(f"✅ {filename} kaydedildi ({matrix.shape[0]}x{matrix.shape[1]}, %{result['density']:.2f} yoğunluk)")

def create_summary_report(results, global_density, output_file='MOVIELENS_DENSITY_REPORT.md'):
    """
    Özet rapor oluşturur.
    
    Args:
        results: Analiz sonuçları
        global_density: Global yoğunluk
        output_file: Çıktı dosyası
    """
    print("\n" + "="*80)
    print("ADIM 5: ÖZET RAPOR OLUŞTURMA")
    print("="*80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 📊 MovieLens Yoğunluk Analizi Raporu\n\n")
        f.write(f"**Tarih:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        f.write("## 1. Genel Bilgiler\n\n")
        f.write(f"- **Veri Seti:** MovieLens 100k\n")
        f.write(f"- **Global Yoğunluk:** %{global_density:.4f}\n")
        f.write(f"- **Analiz Edilen Bölge Sayısı:** {len(results)}\n\n")
        
        f.write("## 2. Bölge Bazlı Yoğunluk Analizi\n\n")
        f.write("| Boyut | Yoğunluk (%) | İyileşme Faktörü |\n")
        f.write("|-------|--------------|------------------|\n")
        
        for result in results:
            f.write(f"| {result['size']} | {result['density']:.4f} | {result['improvement']:.2f}x |\n")
        
        f.write("\n## 3. Sonuçlar\n\n")
        
        # En yoğun bölgeyi bul
        best_result = max(results, key=lambda x: x['density'])
        f.write(f"- **En Yoğun Bölge:** {best_result['size']} (%{best_result['density']:.4f})\n")
        f.write(f"- **Maksimum İyileşme:** {best_result['improvement']:.2f}x\n\n")
        
        f.write("## 4. Yorum\n\n")
        f.write("Tekstil veri setinde olduğu gibi, MovieLens veri setinde de **Pareto İlkesi** geçerlidir:\n\n")
        f.write("- En aktif kullanıcılar ve en popüler filmler matrisin sol üst köşesinde toplanır.\n")
        f.write("- Bu bölge, genel matrise kıyasla çok daha yoğundur.\n")
        f.write("- RMVC algoritması için bu yoğun bölgeler, daha iyi sonuçlar üretebilir.\n\n")
        
        f.write("## 5. Öneriler\n\n")
        f.write("1. RMVC analizini önce yoğun bölgelerde test edin.\n")
        f.write("2. Farklı boyutlardaki matrisleri karşılaştırarak optimal boyutu belirleyin.\n")
        f.write("3. Cold start problemini azaltmak için yoğun bölgedeki kullanıcıları önceliklendirin.\n")
    
    print(f"✅ Rapor kaydedildi: {output_file}")

def main():
    """Ana fonksiyon."""
    print("="*80)
    print("MOVIELENS 100K YOĞUNLUK ANALİZİ")
    print("Tekstil Veri Seti Yaklaşımının Uyarlanması")
    print("="*80)
    
    # Loader oluştur
    loader = DatasetLoader()
    
    # MovieLens 100k yükle
    print("\n📂 MovieLens 100k veri seti yükleniyor...")
    df_binary, metadata = loader.load_movielens_100k(min_rating=4)
    
    print(f"\n📊 Veri Seti Özeti:")
    print(f"   - {metadata['num_users']} kullanıcı")
    print(f"   - {metadata['num_movies']} film")
    print(f"   - {metadata['num_ratings']} rating")
    print(f"   - Minimum Rating Eşiği: {metadata['min_rating_threshold']}")
    
    # Matrisi sırala
    df_sorted, user_activity, movie_popularity = sort_matrix_by_activity(df_binary)
    
    # Farklı boyutlarda yoğunluk analizi
    region_sizes = [
        (3, 5),      # Çok küçük
        (5, 10),     # Mini
        (10, 20),    # Küçük
        (20, 30),    # Orta-Küçük
        (30, 50),    # Orta
        (50, 75),    # Orta-Büyük
        (75, 100),   # Büyük
        (100, 150),  # Çok Büyük
    ]
    
    results, global_density = analyze_density_regions(df_sorted, region_sizes)
    
    # Görselleştir
    visualize_regions(results)
    
    # Matrisleri kaydet
    export_matrices(results)
    
    # Rapor oluştur
    create_summary_report(results, global_density)
    
    print("\n" + "="*80)
    print("✅ ANALİZ TAMAMLANDI!")
    print("="*80)
    print("\nOluşan Dosyalar:")
    print("   📁 datasets/movielens_dense_*.csv (Yoğun matrisler)")
    print("   📊 analysis_plots/movielens_density_heatmaps.png")
    print("   📈 analysis_plots/movielens_density_comparison.png")
    print("   📄 MOVIELENS_DENSITY_REPORT.md")
    print("\nSONRAKİ ADIM:")
    print("Bu matrisleri rmvc_app_v2.py ile yükleyebilir veya")
    print("convergence_experiment.py ile iteratif analiz yapabilirsiniz!")

if __name__ == "__main__":
    main()
