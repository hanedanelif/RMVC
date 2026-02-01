# -*- coding: utf-8 -*-
"""
MovieLens Yoğun Matrisler - Method-1 vs Method-2 Karşılaştırması
=================================================================
Her iki yöntemle de farklı boyutlarda yoğun matrisler oluşturur.

Method-1: rating >= 4 → 1 (sabit eşik)
Method-2: Normalize + her parça için adaptif eşik
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

class DenseMatrixGenerator:
    """Yoğun matris üreteci - iki yöntem karşılaştırması."""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        
    def load_and_sort_raw_ratings(self):
        """Ham ratings'i yükle ve sırala."""
        print("="*80)
        print("ADIM 1: HAM RATINGS YÜKLEME VE SIRALAMA")
        print("="*80)
        
        # Ratings yükle
        ratings_file = "datasets/ml-100k/u.data"
        df_ratings = pd.read_csv(ratings_file, sep='\t',
                                 names=['user_id', 'movie_id', 'rating', 'timestamp'])
        
        # Matris oluştur
        df_matrix = df_ratings.pivot_table(
            index='user_id',
            columns='movie_id',
            values='rating',
            fill_value=0
        )
        
        print(f"\n✅ Matris oluşturuldu: {df_matrix.shape[0]} × {df_matrix.shape[1]}")
        
        # Sırala (aktiviteye göre)
        user_activity = (df_matrix > 0).sum(axis=1)
        sorted_users = user_activity.sort_values(ascending=False).index
        
        movie_popularity = (df_matrix > 0).sum(axis=0)
        sorted_movies = movie_popularity.sort_values(ascending=False).index
        
        df_sorted = df_matrix.loc[sorted_users, sorted_movies]
        
        print(f"✅ Matris sıralandı (yoğun bölge sol üstte)")
        
        return df_sorted
    
    def method1_simple_threshold(self, df_region, size_name, threshold=4):
        """Method-1: Basit eşikleme."""
        df_binary = (df_region >= threshold).astype(int)
        
        density = (df_binary.sum().sum() / df_binary.size) * 100
        
        return {
            'method': 'Method-1 (rating >= 4)',
            'size': size_name,
            'threshold': threshold,
            'density': density,
            'matrix': df_binary
        }
    
    def method2_adaptive_threshold(self, df_region, size_name):
        """Method-2: Adaptif normalize + eşikleme."""
        
        # 1. Normalize et
        df_normalized = df_region.copy()
        mask = df_region > 0
        
        if mask.sum().sum() == 0:
            # Hiç rating yoksa
            return None
        
        min_rating = df_region[mask].min().min()
        max_rating = df_region[mask].max().max()
        
        if min_rating == max_rating:
            # Tüm ratingler aynı
            df_normalized[mask] = 1.0
            threshold = 0.5
        else:
            df_normalized[mask] = (df_region[mask] - min_rating) / (max_rating - min_rating)
            
            # 2. Ondalıklı ortalama hesapla
            normalized_values = df_normalized[df_normalized > 0].values.flatten()
            fractional_values = normalized_values[(normalized_values > 0) & (normalized_values < 1)]
            
            if len(fractional_values) > 0:
                threshold = np.mean(fractional_values)
            else:
                threshold = 0.5
        
        # 3. Binary'ye dönüştür
        df_binary = (df_normalized >= threshold).astype(int)
        
        density = (df_binary.sum().sum() / df_binary.size) * 100
        
        return {
            'method': 'Method-2 (Adaptive)',
            'size': size_name,
            'threshold': threshold,
            'min_rating': min_rating,
            'max_rating': max_rating,
            'density': density,
            'matrix': df_binary,
            'normalized': df_normalized
        }
    
    def generate_all_sizes(self, df_sorted):
        """Tüm boyutlar için her iki yöntemi de uygula."""
        print("\n" + "="*80)
        print("ADIM 2: FARKLI BOYUTLARDA YOĞundefined BÖLGELER OLUŞTURMA")
        print("="*80)
        
        sizes = [
            (3, 5),
            (5, 10),
            (10, 20),
            (20, 30),
            (30, 50),
            (50, 75),
            (75, 100),
            (100, 150)
        ]
        
        print(f"\n{'Boyut':<12} {'M1 Eşik':>10} {'M1 Yoğ':>10} {'M2 Eşik':>10} {'M2 Yoğ':>10} {'Fark':>10}")
        print("-" * 70)
        
        for num_users, num_movies in sizes:
            size_name = f"{num_users}x{num_movies}"
            
            # Bölgeyi kes
            region = df_sorted.iloc[:num_users, :num_movies]
            
            # Method-1
            result_m1 = self.method1_simple_threshold(region, size_name)
            
            # Method-2
            result_m2 = self.method2_adaptive_threshold(region, size_name)
            
            if result_m2 is None:
                continue
            
            # Karşılaştır
            diff = result_m2['density'] - result_m1['density']
            
            print(f"{size_name:<12} {result_m1['threshold']:>10.2f} {result_m1['density']:>9.2f}% "
                  f"{result_m2['threshold']:>10.4f} {result_m2['density']:>9.2f}% {diff:>+9.2f}%")
            
            # Kaydet
            self.results.append({
                'size': size_name,
                'num_users': num_users,
                'num_movies': num_movies,
                'method1': result_m1,
                'method2': result_m2,
                'difference': diff
            })
            
            # CSV kaydet
            output_dir = "datasets"
            os.makedirs(output_dir, exist_ok=True)
            
            m1_file = f"movielens_method1_{size_name}.csv"
            m2_file = f"movielens_method2_{size_name}.csv"
            
            result_m1['matrix'].to_csv(os.path.join(output_dir, m1_file))
            result_m2['matrix'].to_csv(os.path.join(output_dir, m2_file))
        
        print(f"\n✅ {len(self.results)} farklı boyutta matris oluşturuldu")
    
    def visualize_comparison(self):
        """Karşılaştırma görselleri."""
        print("\n" + "="*80)
        print("ADIM 3: GÖRSELLEŞTİRME")
        print("="*80)
        
        os.makedirs("analysis_plots", exist_ok=True)
        
        # 1. Yoğunluk karşılaştırması
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sizes = [r['size'] for r in self.results]
        m1_densities = [r['method1']['density'] for r in self.results]
        m2_densities = [r['method2']['density'] for r in self.results]
        
        x = np.arange(len(sizes))
        width = 0.35
        
        ax.bar(x - width/2, m1_densities, width, label='Method-1 (rating >= 4)', color='skyblue')
        ax.bar(x + width/2, m2_densities, width, label='Method-2 (Adaptive)', color='coral')
        
        ax.set_xlabel('Matris Boyutu', fontsize=12)
        ax.set_ylabel('Yoğunluk (%)', fontsize=12)
        ax.set_title('Yöntem Karşılaştırması - Yoğunluk', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(sizes, rotation=45)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"analysis_plots/method_comparison_densities_{self.timestamp}.png", dpi=300)
        print("✅ Yoğunluk karşılaştırma grafiği kaydedildi")
        plt.close()
        
        # 2. Eşik değerleri grafiği
        fig, ax = plt.subplots(figsize=(12, 6))
        
        m2_thresholds = [r['method2']['threshold'] for r in self.results]
        
        ax.plot(sizes, m2_thresholds, marker='o', linewidth=2, markersize=8, color='green')
        ax.axhline(y=4, color='red', linestyle='--', label='Method-1 Eşiği (rating = 4)')
        
        # Method-1'in normalize karşılığı
        m1_threshold_normalized = (4 - 1) / (5 - 1)  # 0.75
        ax.axhline(y=m1_threshold_normalized, color='orange', linestyle='--', 
                  label=f'Method-1 Normalize ({m1_threshold_normalized:.2f})')
        
        ax.set_xlabel('Matris Boyutu', fontsize=12)
        ax.set_ylabel('Eşik Değeri', fontsize=12)
        ax.set_title('Method-2 Adaptif Eşik Değerleri', fontsize=14, fontweight='bold')
        ax.set_xticklabels(sizes, rotation=45)
        ax.legend()
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"analysis_plots/method2_adaptive_thresholds_{self.timestamp}.png", dpi=300)
        print("✅ Adaptif eşik grafiği kaydedildi")
        plt.close()
    
    def generate_report(self):
        """Detaylı rapor oluştur."""
        print("\n" + "="*80)
        print("ADIM 4: RAPOR OLUŞTURMA")
        print("="*80)
        
        report_file = f"DENSE_MATRICES_COMPARISON_REPORT_{self.timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# MovieLens Yoğun Matrisler - Yöntem Karşılaştırması\n\n")
            f.write(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 1. Yaklaşım\n\n")
            f.write("**Method-1:** Sabit eşik (rating >= 4)\n\n")
            f.write("**Method-2:** Adaptif eşik\n")
            f.write("- Her parça için ayrı normalize edilir\n")
            f.write("- Her parçanın ondalıklı ortalaması eşik olarak kullanılır\n")
            f.write("- Parça boyutu büyüdükçe eşik değişebilir\n\n")
            
            f.write("## 2. Sonuçlar\n\n")
            f.write("| Boyut | M1 Eşik | M1 Yoğ. | M2 Eşik | M2 Yoğ. | Fark |\n")
            f.write("|-------|---------|---------|---------|---------|------|\n")
            
            for result in self.results:
                f.write(f"| {result['size']} | ")
                f.write(f"{result['method1']['threshold']:.0f} | ")
                f.write(f"{result['method1']['density']:.2f}% | ")
                f.write(f"{result['method2']['threshold']:.4f} | ")
                f.write(f"{result['method2']['density']:.2f}% | ")
                f.write(f"{result['difference']:+.2f}% |\n")
            
            f.write("\n## 3. Gözlemler\n\n")
            
            # En büyük fark
            max_diff_result = max(self.results, key=lambda x: abs(x['difference']))
            f.write(f"- **En büyük fark:** {max_diff_result['size']} ({max_diff_result['difference']:+.2f}%)\n")
            
            # Ortalama fark
            avg_diff = np.mean([r['difference'] for r in self.results])
            f.write(f"- **Ortalama fark:** {avg_diff:+.2f}%\n\n")
            
            f.write("## 4. Sonuç\n\n")
            f.write("Method-2, her parça için **adaptif eşik** kullanır. ")
            f.write("Küçük parçalarda eşik daha yüksek (daha seçici), ")
            f.write("büyük parçalarda daha düşük (daha kapsayıcı) olabilir.\n\n")
            
            f.write("## 5. Oluşturulan Dosyalar\n\n")
            for result in self.results:
                f.write(f"- `movielens_method1_{result['size']}.csv`\n")
                f.write(f"- `movielens_method2_{result['size']}.csv`\n")
        
        print(f"✅ Rapor kaydedildi: {report_file}")
        return report_file

def main():
    """Ana fonksiyon."""
    print("="*80)
    print("MOVIELENS YOĞUN MATRİSLER - METHOD-1 VS METHOD-2")
    print("="*80)
    
    generator = DenseMatrixGenerator()
    
    # 1. Yükle ve sırala
    df_sorted = generator.load_and_sort_raw_ratings()
    
    # 2. Her iki yöntemle de matrisleri oluştur
    generator.generate_all_sizes(df_sorted)
    
    # 3. Görselleştir
    generator.visualize_comparison()
    
    # 4. Rapor
    report_file = generator.generate_report()
    
    print("\n" + "="*80)
    print("✅ ANALİZ TAMAMLANDI!")
    print("="*80)
    print("\nOluşan Dosyalar:")
    print("   📁 datasets/movielens_method1_*.csv (Method-1 matrisleri)")
    print("   📁 datasets/movielens_method2_*.csv (Method-2 matrisleri)")
    print("   📊 analysis_plots/method_comparison_densities_*.png")
    print("   📈 analysis_plots/method2_adaptive_thresholds_*.png")
    print(f"   📄 {report_file}")

if __name__ == "__main__":
    main()
