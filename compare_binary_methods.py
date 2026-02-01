# -*- coding: utf-8 -*-
"""
MovieLens Binary Dönüşüm Yöntemleri Karşılaştırması
====================================================
İki farklı binary dönüşüm yöntemini karşılaştırır ve makale için
detaylı metodoloji raporu oluşturur.

Yöntem-1: Basit Eşikleme (rating >= 4 -> 1)
Yöntem-2: RMVC-Uyumlu Normalizasyon + Eşikleme

Her adım detaylı kaydedilir ve raporlanır.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Stil
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

class BinaryConversionAnalyzer:
    """MovieLens binary dönüşüm yöntemlerini analiz eder."""
    
    def __init__(self):
        self.log = []  # Her adımın kaydı
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def log_step(self, step_name, details):
        """Adım kaydı tutar."""
        self.log.append({
            'step': step_name,
            'details': details,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    def load_raw_ratings(self):
        """1. ADIM: Ham ratings yükle."""
        print("="*80)
        print("ADIM 1: HAM RATINGS YÜKLEME")
        print("="*80)
        
        ratings_file = "datasets/ml-100k/u.data"
        df_ratings = pd.read_csv(ratings_file, sep='\t',
                                 names=['user_id', 'movie_id', 'rating', 'timestamp'])
        
        # Log
        self.log_step("Load Raw Ratings", {
            'total_ratings': len(df_ratings),
            'users': df_ratings['user_id'].nunique(),
            'movies': df_ratings['movie_id'].nunique(),
            'rating_min': df_ratings['rating'].min(),
            'rating_max': df_ratings['rating'].max(),
            'rating_mean': df_ratings['rating'].mean(),
            'rating_std': df_ratings['rating'].std()
        })
        
        print(f"✅ {len(df_ratings)} rating yüklendi")
        print(f"   Min Rating: {df_ratings['rating'].min()}")
        print(f"   Max Rating: {df_ratings['rating'].max()}")
        print(f"   Ortalama: {df_ratings['rating'].mean():.4f}")
        print(f"   Std Sapma: {df_ratings['rating'].std():.4f}")
        
        # Matris oluştur
        df_matrix = df_ratings.pivot_table(
            index='user_id',
            columns='movie_id',
            values='rating',
            fill_value=0
        )
        
        return df_ratings, df_matrix
    
    def method1_simple_threshold(self, df_matrix, threshold=4):
        """YÖNTEM-1: Basit Eşikleme (rating >= threshold -> 1)."""
        print("\n" + "="*80)
        print(f"YÖNTEM-1: BASİT EŞİKLEME (rating >= {threshold})")
        print("="*80)
        
        df_binary_m1 = (df_matrix >= threshold).astype(int)
        
        # İstatistikler
        total_ratings = (df_matrix > 0).sum().sum()
        ones_count = (df_binary_m1 == 1).sum().sum()
        zeros_count = total_ratings - ones_count
        
        details = {
            'method': 'Simple Threshold',
            'threshold': threshold,
            'total_ratings': total_ratings,
            'ones': ones_count,
            'zeros': zeros_count,
            'ones_percentage': (ones_count / total_ratings) * 100,
            'zeros_percentage': (zeros_count / total_ratings) * 100
        }
        
        self.log_step("Method-1: Simple Threshold", details)
        
        print(f"\n📊 Dönüşüm İstatistikleri:")
        print(f"   - Toplam rating: {total_ratings}")
        print(f"   - 1'e dönüşen (>= {threshold}): {ones_count} ({details['ones_percentage']:.2f}%)")
        print(f"   - 0'a dönüşen (< {threshold}): {zeros_count} ({details['zeros_percentage']:.2f}%)")
        
        return df_binary_m1, details
    
    def method2_rmvc_style(self, df_matrix):
        """YÖNTEM-2: RMVC-Uyumlu Normalizasyon + Eşikleme."""
        print("\n" + "="*80)
        print("YÖNTEM-2: RMVC-UYUMLU NORMALİZASYON + EŞİKLEME")
        print("="*80)
        
        # Adım 2.1: Normalizasyon (0-1 arası)
        print("\n[2.1] Normalizasyon (Min-Max Scaling):")
        
        df_normalized = df_matrix.copy()
        
        # Sadece rating olan (>0) hücreleri normalize et
        mask = df_matrix > 0
        min_rating = df_matrix[mask].min().min()
        max_rating = df_matrix[mask].max().max()
        
        df_normalized[mask] = (df_matrix[mask] - min_rating) / (max_rating - min_rating)
        
        print(f"   - Min rating: {min_rating}")
        print(f"   - Max rating: {max_rating}")
        print(f"   - Formül: R_norm = (R - {min_rating}) / ({max_rating} - {min_rating})")
        print(f"   - Normalize edilmiş aralık: [0, 1]")
        
        # Normalize edilmiş matrisin örneğini göster
        print(f"\n   📊 Normalize Edilmiş Matris Örneği (İlk 5 kullanıcı × 5 film):")
        sample_normalized = df_normalized.iloc[:5, :5]
        print(sample_normalized.to_string())
        
        # Rating bazlı normalize değerleri göster
        print(f"\n   🔢 Rating Bazlı Normalize Değerleri:")
        for rating in range(int(min_rating), int(max_rating) + 1):
            norm_val = (rating - min_rating) / (max_rating - min_rating)
            print(f"      {rating} yıldız → {norm_val:.4f}")
        
        # Normalize matrisi kaydet
        normalized_file = f"movielens_normalized_matrix_{self.timestamp}.csv"
        df_normalized.to_csv(normalized_file)
        print(f"\n   💾 Normalize edilmiş matris kaydedildi: {normalized_file}")
        
        # Adım 2.2: Ortalama hesaplama
        print("\n[2.2] Ortalama Hesaplama (Ondalıklı Değerler):")
        
        # Sadece normalize edilmiş değerlerin ortalaması (0 hariç)
        normalized_values = df_normalized[df_normalized > 0].values.flatten()
        mean_normalized = np.mean(normalized_values)
        
        # Ondalıklı değerlerin ortalaması (0 ve 1 hariç, RMVC'deki gibi)
        fractional_values = normalized_values[(normalized_values > 0) & (normalized_values < 1)]
        
        if len(fractional_values) > 0:
            mean_fractional = np.mean(fractional_values)
        else:
            mean_fractional = mean_normalized
        
        print(f"   - Toplam normalize değer sayısı: {len(normalized_values)}")
        print(f"   - Ondalıklı değer sayısı (0 < x < 1): {len(fractional_values)}")
        print(f"   - Ondalıklı değerler: {np.unique(fractional_values)}")
        print(f"   - Tüm normalize değerlerin ortalaması: {mean_normalized:.6f}")
        print(f"   - Ondalıklı değerlerin ortalaması: {mean_fractional:.6f}")
        
        # Hangi ratingler ondalıklı?
        print(f"\n   🔍 Ondalıklı Normalize Değerler Detayı:")
        for rating in range(int(min_rating), int(max_rating) + 1):
            norm_val = (rating - min_rating) / (max_rating - min_rating)
            count = (df_matrix == rating).sum().sum()
            if 0 < norm_val < 1:
                print(f"      {rating}★ → {norm_val:.4f} (Ondalıklı, Sayı: {count})")
            else:
                print(f"      {rating}★ → {norm_val:.4f} (Tam sayı, Sayı: {count})")
        
        # Adım 2.3: Eşik belirleme (RMVC'deki gibi ondalıklı ortalaması)
        threshold_value = mean_fractional
        
        print(f"\n[2.3] Eşik Değeri Belirleme:")
        print(f"   - Seçilen eşik: θ = {threshold_value:.6f} (ondalıklı ortalama)")
        print(f"   - Bu eşik hangi ratingler arasında?")
        for rating in range(int(min_rating), int(max_rating)):
            norm_val_low = (rating - min_rating) / (max_rating - min_rating)
            norm_val_high = (rating + 1 - min_rating) / (max_rating - min_rating)
            if norm_val_low < threshold_value <= norm_val_high:
                print(f"      → {rating}★ ({norm_val_low:.4f}) < θ ({threshold_value:.4f}) <= {rating+1}★ ({norm_val_high:.4f})")
                print(f"      → Yani {rating}★ ve altı → 0, {rating+1}★ ve üstü → 1")
        
        # Adım 2.4: Eşik uygulama
        print(f"\n[2.4] Eşik Uygulama (>= {threshold_value:.6f} → 1):")
        
        df_binary_m2 = (df_normalized >= threshold_value).astype(int)
        
        # İstatistikler
        total_ratings = (df_matrix > 0).sum().sum()
        ones_count = (df_binary_m2 == 1).sum().sum()
        zeros_count = total_ratings - ones_count
        
        # Rating bazlı dönüşüm detayı
        print(f"\n   Rating Bazlı Binary Dönüşüm:")
        for rating in range(int(min_rating), int(max_rating) + 1):
            norm_val = (rating - min_rating) / (max_rating - min_rating)
            binary_val = 1 if norm_val >= threshold_value else 0
            count = (df_matrix == rating).sum().sum()
            symbol = "✅" if binary_val == 1 else "❌"
            print(f"      {symbol} {rating}★ → {norm_val:.4f} → {binary_val} (Sayı: {count})")
        
        details = {
            'method': 'RMVC-Style Normalization + Threshold',
            'min_rating': min_rating,
            'max_rating': max_rating,
            'mean_normalized': mean_normalized,
            'mean_fractional': mean_fractional,
            'fractional_count': len(fractional_values),
            'threshold': threshold_value,
            'total_ratings': total_ratings,
            'ones': ones_count,
            'zeros': zeros_count,
            'ones_percentage': (ones_count / total_ratings) * 100,
            'zeros_percentage': (zeros_count / total_ratings) * 100,
            'normalized_file': normalized_file
        }
        
        self.log_step("Method-2: RMVC-Style", details)
        
        print(f"\n   📊 Genel İstatistik:")
        print(f"   - 1'e dönüşen: {ones_count} ({details['ones_percentage']:.2f}%)")
        print(f"   - 0'a dönüşen: {zeros_count} ({details['zeros_percentage']:.2f}%)")
        
        return df_binary_m2, df_normalized, details
    
    def compare_methods(self, df_matrix, df_binary_m1, df_binary_m2, details_m1, details_m2):
        """İki yöntemi detaylı karşılaştırır."""
        print("\n" + "="*80)
        print("YÖNTEM KARŞILAŞTIRMASI")
        print("="*80)
        
        # Matrisleri sırala (yoğunluk analizi için)
        user_activity = (df_matrix > 0).sum(axis=1)
        sorted_users = user_activity.sort_values(ascending=False).index
        
        movie_popularity = (df_matrix > 0).sum(axis=0)
        sorted_movies = movie_popularity.sort_values(ascending=False).index
        
        df_binary_m1_sorted = df_binary_m1.loc[sorted_users, sorted_movies]
        df_binary_m2_sorted = df_binary_m2.loc[sorted_users, sorted_movies]
        
        # Yoğunluk karşılaştırması (farklı boyutlarda)
        sizes = [(10, 20), (20, 30), (30, 50), (50, 75)]
        
        comparison_results = []
        
        print(f"\n{'Boyut':<12} {'M1 Yoğ':>10} {'M2 Yoğ':>10} {'Fark':>10}")
        print("-" * 50)
        
        for num_users, num_movies in sizes:
            region_m1 = df_binary_m1_sorted.iloc[:num_users, :num_movies]
            region_m2 = df_binary_m2_sorted.iloc[:num_users, :num_movies]
            
            density_m1 = (region_m1.sum().sum() / region_m1.size) * 100
            density_m2 = (region_m2.sum().sum() / region_m2.size) * 100
            diff = density_m2 - density_m1
            
            comparison_results.append({
                'size': f"{num_users}x{num_movies}",
                'density_m1': density_m1,
                'density_m2': density_m2,
                'difference': diff
            })
            
            print(f"{num_users}x{num_movies:<7} {density_m1:>9.2f}% {density_m2:>9.2f}% {diff:>+9.2f}%")
        
        # Farklılıkları analiz et
        print(f"\n📊 Genel Karşılaştırma:")
        print(f"   Yöntem-1 (Basit): {details_m1['ones_percentage']:.2f}% → 1")
        print(f"   Yöntem-2 (RMVC):  {details_m2['ones_percentage']:.2f}% → 1")
        print(f"   Fark: {details_m2['ones_percentage'] - details_m1['ones_percentage']:+.2f}%")
        
        # Hangi ratingler farklı dönüştü?
        different_cells = (df_binary_m1 != df_binary_m2)
        num_different = different_cells.sum().sum()
        
        print(f"\n🔄 Farklı Dönüşen Hücreler:")
        print(f"   - Toplam farklılık: {num_different} hücre")
        print(f"   - Toplam rating: {(df_matrix > 0).sum().sum()}")
        print(f"   - Farklılık oranı: {(num_different / (df_matrix > 0).sum().sum()) * 100:.2f}%")
        
        self.log_step("Method Comparison", {
            'different_cells': num_different,
            'difference_percentage': (num_different / (df_matrix > 0).sum().sum()) * 100,
            'comparison_results': comparison_results
        })
        
        return comparison_results
    
    def visualize_comparison(self, df_matrix, df_binary_m1, df_binary_m2, output_dir='analysis_plots'):
        """Karşılaştırma görselleştirmesi."""
        print("\n" + "="*80)
        print("GÖRSELLEŞTİRME")
        print("="*80)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Matrisleri sırala
        user_activity = (df_matrix > 0).sum(axis=1)
        sorted_users = user_activity.sort_values(ascending=False).index[:30]
        
        movie_popularity = (df_matrix > 0).sum(axis=0)
        sorted_movies = movie_popularity.sort_values(ascending=False).index[:50]
        
        # 30x50 bölge
        region_m1 = df_binary_m1.loc[sorted_users, sorted_movies]
        region_m2 = df_binary_m2.loc[sorted_users, sorted_movies]
        region_diff = (region_m2.astype(int) - region_m1.astype(int))
        
        fig, axes = plt.subplots(1, 3, figsize=(20, 8))
        
        # Yöntem-1
        sns.heatmap(region_m1, ax=axes[0], cmap="Blues", cbar_kws={'label': 'Binary'},
                   xticklabels=False, yticklabels=False)
        axes[0].set_title("Yöntem-1: Basit Eşikleme\n(rating >= 4)", fontsize=14, fontweight='bold')
        axes[0].set_xlabel("Filmler (İlk 50)")
        axes[0].set_ylabel("Kullanıcılar (İlk 30)")
        
        # Yöntem-2
        sns.heatmap(region_m2, ax=axes[1], cmap="Greens", cbar_kws={'label': 'Binary'},
                   xticklabels=False, yticklabels=False)
        axes[1].set_title("Yöntem-2: RMVC-Uyumlu\n(Normalize + Eşik)", fontsize=14, fontweight='bold')
        axes[1].set_xlabel("Filmler (İlk 50)")
        axes[1].set_ylabel("Kullanıcılar (İlk 30)")
        
        # Fark
        sns.heatmap(region_diff, ax=axes[2], cmap="RdBu_r", center=0, vmin=-1, vmax=1,
                   cbar_kws={'label': 'Fark (M2 - M1)'}, xticklabels=False, yticklabels=False)
        axes[2].set_title("Fark Matrisi\n(Kırmızı: M2'de 1, Mavi: M1'de 1)", 
                         fontsize=14, fontweight='bold')
        axes[2].set_xlabel("Filmler (İlk 50)")
        axes[2].set_ylabel("Kullanıcılar (İlk 30)")
        
        plt.tight_layout()
        filename = f"method_comparison_{self.timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✅ {filename} kaydedildi")
        plt.close()
    
    def generate_methodology_report(self, details_m1, details_m2, output_file=None):
        """Makale için metodoloji raporu oluşturur."""
        print("\n" + "="*80)
        print("METODOLOJİ RAPORU OLUŞTURMA")
        print("="*80)
        
        if output_file is None:
            output_file = f"METHODOLOGY_REPORT_{self.timestamp}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# MovieLens Binary Dönüşüm Metodolojisi Karşılaştırması\n\n")
            f.write(f"**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 1. Araştırma Sorusu\n\n")
            f.write("**Soru:** MovieLens veri setini RMVC algoritmasında kullanmak için binary (0/1) formatına ")
            f.write("dönüştürmenin en uygun yöntemi nedir?\n\n")
            
            f.write("## 2. Test Edilen Yöntemler\n\n")
            
            f.write("### Yöntem-1: Basit Eşikleme\n\n")
            f.write("**Matematiksel Tanım:**\n\n")
            f.write("```\n")
            f.write("B(u, m) = {\n")
            f.write("    1, eğer R(u, m) >= 4\n")
            f.write("    0, eğer R(u, m) < 4\n")
            f.write("}\n")
            f.write("```\n\n")
            f.write("Burada:\n")
            f.write("- `R(u, m)`: Kullanıcı u'nun film m için verdiği rating (1-5)\n")
            f.write("- `B(u, m)`: Binary matristeki değer (0/1)\n\n")
            
            f.write("**Sonuçlar:**\n\n")
            f.write(f"- 1'e dönüşen: {details_m1['ones']} rating ({details_m1['ones_percentage']:.2f}%)\n")
            f.write(f"- 0'a dönüşen: {details_m1['zeros']} rating ({details_m1['zeros_percentage']:.2f}%)\n\n")
            
            f.write("---\n\n")
            
            f.write("### Yöntem-2: RMVC-Uyumlu Normalizasyon + Eşikleme\n\n")
            f.write("**Matematiksel Tanım:**\n\n")
            f.write("**Adım 1: Min-Max Normalizasyon**\n\n")
            f.write("```\n")
            f.write("R_norm(u, m) = (R(u, m) - R_min) / (R_max - R_min)\n")
            f.write("```\n\n")
            f.write(f"Burada `R_min = {details_m2['min_rating']}` ve `R_max = {details_m2['max_rating']}`\n\n")
            
            f.write("**Adım 2: Eşik Değeri Hesaplama**\n\n")
            f.write("```\n")
            f.write("θ = mean({R_norm(u, m) | 0 < R_norm(u, m) < 1})\n")
            f.write("```\n\n")
            f.write("Yani, sadece ondalıklı normalize değerlerin ortalaması alınır.\n\n")
            f.write(f"**Hesaplanan Eşik:** θ = {details_m2['threshold']:.4f}\n\n")
            
            f.write("**Adım 3: Binary Dönüşüm**\n\n")
            f.write("```\n")
            f.write("B(u, m) = {\n")
            f.write("    1, eğer R_norm(u, m) >= θ\n")
            f.write("    0, eğer R_norm(u, m) < θ\n")
            f.write("}\n")
            f.write("```\n\n")
            
            f.write("**Sonuçlar:**\n\n")
            f.write(f"- 1'e dönüşen: {details_m2['ones']} rating ({details_m2['ones_percentage']:.2f}%)\n")
            f.write(f"- 0'a dönüşen: {details_m2['zeros']} rating ({details_m2['zeros_percentage']:.2f}%)\n\n")
            
            f.write("---\n\n")
            
            f.write("## 3. Karşılaştırma ve Bulgular\n\n")
            f.write("| Metrik | Yöntem-1 | Yöntem-2 | Fark |\n")
            f.write("|--------|----------|----------|------|\n")
            f.write(f"| 1'e dönüşen (%) | {details_m1['ones_percentage']:.2f}% | ")
            f.write(f"{details_m2['ones_percentage']:.2f}% | ")
            f.write(f"{details_m2['ones_percentage'] - details_m1['ones_percentage']:+.2f}% |\n")
            f.write(f"| 0'a dönüşen (%) | {details_m1['zeros_percentage']:.2f}% | ")
            f.write(f"{details_m2['zeros_percentage']:.2f}% | ")
            f.write(f"{details_m2['zeros_percentage'] - details_m1['zeros_percentage']:+.2f}% |\n\n")
            
            f.write("## 4. Metodolojik Tutarlılık\n\n")
            f.write("**Yöntem-2'nin Avantajları:**\n\n")
            f.write("1. **RMVC ile Uyumlu:** İteratif RMVC analizinde kullanılan eşikleme yaklaşımıyla ")
            f.write("metodolojik olarak tutarlıdır.\n")
            f.write("2. **Veri-Güdümlü:** Eşik değeri, verinin istatistiksel özelliklerinden ")
            f.write("(ondalıklı ortalama) otomatik olarak belirlenir.\n")
            f.write("3. **Normalize Edilmiş Ölçek:** Min-Max normalizasyon, farklı ölçeklerdeki ")
            f.write("veri setlerinin karşılaştırılabilir hale gelmesini sağlar.\n\n")
            
            f.write("## 5. Öneri\n\n")
            f.write("**Makale için önerilen yöntem:** Yöntem-2 (RMVC-Uyumlu Normalizasyon + Eşikleme)\n\n")
            f.write("**Gerekçe:**\n")
            f.write("- RMVC algoritmasının metodolojik felsefesiyle uyumludur\n")
            f.write("- Veri-güdümlü ve tekrarlanabilir bir süreç sunar\n")
            f.write("- İteratif RMVC analizinde kullanılan eşikleme mantığını yansıtır\n\n")
            
            f.write("## 6. Detaylı Adım Kayıtları\n\n")
            for i, log_entry in enumerate(self.log, 1):
                f.write(f"### Adım {i}: {log_entry['step']}\n\n")
                f.write(f"**Zaman:** {log_entry['timestamp']}\n\n")
                f.write("**Detaylar:**\n\n")
                for key, value in log_entry['details'].items():
                    if isinstance(value, (int, float)):
                        if isinstance(value, float):
                            f.write(f"- {key}: {value:.4f}\n")
                        else:
                            f.write(f"- {key}: {value}\n")
                    elif isinstance(value, list):
                        f.write(f"- {key}: [Liste, {len(value)} öğe]\n")
                    else:
                        f.write(f"- {key}: {value}\n")
                f.write("\n")
        
        print(f"✅ Metodoloji raporu kaydedildi: {output_file}")
        return output_file

def main():
    """Ana fonksiyon."""
    print("="*80)
    print("MOVIELENS BINARY DÖNÜŞÜM YÖNTEMLERİ KARŞILAŞTIRMASI")
    print("Makale İçin Detaylı Metodoloji Analizi")
    print("="*80)
    
    analyzer = BinaryConversionAnalyzer()
    
    # 1. Ham ratings yükle
    df_ratings, df_matrix = analyzer.load_raw_ratings()
    
    # 2. Yöntem-1: Basit eşikleme
    df_binary_m1, details_m1 = analyzer.method1_simple_threshold(df_matrix, threshold=4)
    
    # 3. Yöntem-2: RMVC-uyumlu
    df_binary_m2, df_normalized, details_m2 = analyzer.method2_rmvc_style(df_matrix)
    
    # 4. Karşılaştır
    comparison_results = analyzer.compare_methods(df_matrix, df_binary_m1, df_binary_m2, 
                                                   details_m1, details_m2)
    
    # 5. Görselleştir
    analyzer.visualize_comparison(df_matrix, df_binary_m1, df_binary_m2)
    
    # 6. Metodoloji raporu
    report_file = analyzer.generate_methodology_report(details_m1, details_m2)
    
    print("\n" + "="*80)
    print("✅ ANALİZ TAMAMLANDI!")
    print("="*80)
    print("\nOluşan Dosyalar:")
    print(f"   📄 {report_file}")
    print(f"   📊 analysis_plots/method_comparison_*.png")
    print("\nSONRAKİ ADIM:")
    print("Metodoloji raporunu inceleyerek makale için en uygun yöntemi seçebilirsiniz!")
    print("Yöntem-2, RMVC ile metodolojik tutarlılık sağlar ve önerilir.")

if __name__ == "__main__":
    main()
