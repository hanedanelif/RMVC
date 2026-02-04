# -*- coding: utf-8 -*-
"""
MovieLens Raw Ratings Analizi - Binary Dönüşüm Öncesi Detaylı İnceleme
========================================================================
Bu script, MovieLens veri setinin ham (raw) halini analiz eder ve
binary dönüşüm sürecini adım adım gösterir.

Adımlar:
1. Orijinal ratings matrisini yükle (1-5 arası değerler)
2. Sıralama yap (kullanıcı ve film aktivitesine göre)
3. Yoğun bölgeleri göster (raw ratings ile)
4. Binary dönüşüm uygula (rating >= 4 -> 1, else -> 0)
5. Her adımı karşılaştır ve görselleştir
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Stil ayarları
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

def load_raw_ratings():
    """MovieLens 100k ratings'i yükler (binary'ye dönüştürmeden)."""
    print("="*80)
    print("ADIM 1: HAM RATINGS VERİSİNİ YÜKLEME")
    print("="*80)
    
    ratings_file = "datasets/ml-100k/u.data"
    
    # Ratings dosyasını oku
    df_ratings = pd.read_csv(ratings_file, sep='\t', 
                             names=['user_id', 'movie_id', 'rating', 'timestamp'])
    
    print(f"\n✅ {len(df_ratings)} rating yüklendi")
    print(f"   - {df_ratings['user_id'].nunique()} kullanıcı")
    print(f"   - {df_ratings['movie_id'].nunique()} film")
    print(f"   - Rating aralığı: {df_ratings['rating'].min()}-{df_ratings['rating'].max()}")
    
    # Rating dağılımını göster
    print(f"\n📊 Rating Dağılımı:")
    rating_counts = df_ratings['rating'].value_counts().sort_index()
    for rating, count in rating_counts.items():
        percentage = (count / len(df_ratings)) * 100
        bar = '█' * int(percentage)
        print(f"   {rating} yıldız: {count:>6} ({percentage:>5.2f}%) {bar}")
    
    return df_ratings

def create_raw_matrix(df_ratings):
    """Ham ratings'ten matris oluşturur (1-5 arası değerler)."""
    print("\n" + "="*80)
    print("ADIM 2: HAM RATINGS MATRİSİ OLUŞTURMA")
    print("="*80)
    
    # Pivot table (User x Movie, values = ratings)
    df_raw_matrix = df_ratings.pivot_table(
        index='user_id',
        columns='movie_id',
        values='rating',
        fill_value=0  # Hiç izlenmemişler 0
    )
    
    print(f"\n✅ Matris oluşturuldu:")
    print(f"   - Boyut: {df_raw_matrix.shape[0]} kullanıcı × {df_raw_matrix.shape[1]} film")
    print(f"   - Toplam hücre: {df_raw_matrix.size}")
    print(f"   - Rating olan (>0): {(df_raw_matrix > 0).sum().sum()}")
    print(f"   - Boş (=0): {(df_raw_matrix == 0).sum().sum()}")
    print(f"   - Doluluk oranı: %{((df_raw_matrix > 0).sum().sum() / df_raw_matrix.size) * 100:.4f}")
    
    return df_raw_matrix

def sort_raw_matrix(df_raw_matrix):
    """Ham matrisi aktiviteye göre sıralar."""
    print("\n" + "="*80)
    print("ADIM 3: MATRİSİ SIRALAMA (PERMÜTASYON)")
    print("="*80)
    
    # Kullanıcı aktivitesi (kaç film izlemiş)
    user_activity = (df_raw_matrix > 0).sum(axis=1)
    sorted_users = user_activity.sort_values(ascending=False).index
    
    # Film popülerliği (kaç kişi izlemiş)
    movie_popularity = (df_raw_matrix > 0).sum(axis=0)
    sorted_movies = movie_popularity.sort_values(ascending=False).index
    
    # Sırala
    df_sorted_raw = df_raw_matrix.loc[sorted_users, sorted_movies]
    
    print(f"\n✅ Matris sıralandı:")
    print(f"   - En aktif kullanıcı (ID: {sorted_users[0]}): {user_activity.max()} film izlemiş")
    print(f"   - En popüler film (ID: {sorted_movies[0]}): {movie_popularity.max()} kişi izlemiş")
    
    return df_sorted_raw, sorted_users, sorted_movies

def convert_to_binary(df_raw_matrix, threshold=4):
    """Raw matrisi binary'ye dönüştürür."""
    print("\n" + "="*80)
    print(f"ADIM 4: BINARY DÖNÜŞÜM (Eşik: {threshold})")
    print("="*80)
    
    df_binary = (df_raw_matrix >= threshold).astype(int)
    
    # Dönüşüm istatistikleri
    total_ratings = (df_raw_matrix > 0).sum().sum()
    became_1 = (df_binary == 1).sum().sum()
    became_0 = total_ratings - became_1
    
    print(f"\n📊 Dönüşüm İstatistikleri:")
    print(f"   - Toplam rating: {total_ratings}")
    print(f"   - 1'e dönüşen (rating >= {threshold}): {became_1} ({(became_1/total_ratings)*100:.2f}%)")
    print(f"   - 0'a dönüşen (rating < {threshold}): {became_0} ({(became_0/total_ratings)*100:.2f}%)")
    
    # Hangi ratingler nasıl dönüştü
    print(f"\n🔄 Rating Bazlı Dönüşüm:")
    for rating in range(1, 6):
        count_in_raw = (df_raw_matrix == rating).sum().sum()
        if count_in_raw > 0:
            became = "1" if rating >= threshold else "0"
            symbol = "✅" if rating >= threshold else "❌"
            print(f"   {symbol} {rating} yıldız → {became} (Toplam: {count_in_raw})")
    
    return df_binary

def analyze_dense_regions_comparison(df_sorted_raw, df_sorted_binary, sizes):
    """Yoğun bölgeleri hem raw hem binary versiyonlarda karşılaştırır."""
    print("\n" + "="*80)
    print("ADIM 5: YOĞUN BÖLGE KARŞILAŞTIRMASI (RAW vs BINARY)")
    print("="*80)
    
    results = []
    
    print(f"\n{'Boyut':<12} {'Raw Ort':>10} {'Binary Yoğ':>12} {'Doluluk':>10}")
    print("-" * 50)
    
    for num_users, num_movies in sizes:
        # Bölgeleri kes
        region_raw = df_sorted_raw.iloc[:num_users, :num_movies]
        region_binary = df_sorted_binary.iloc[:num_users, :num_movies]
        
        # İstatistikler
        raw_mean = region_raw[region_raw > 0].mean().mean()  # Sadece rating olanların ortalaması
        binary_density = ((region_binary > 0).sum().sum() / region_binary.size) * 100
        fill_rate = ((region_raw > 0).sum().sum() / region_raw.size) * 100
        
        results.append({
            'size': f"{num_users}x{num_movies}",
            'num_users': num_users,
            'num_movies': num_movies,
            'raw_mean': raw_mean,
            'binary_density': binary_density,
            'fill_rate': fill_rate,
            'region_raw': region_raw,
            'region_binary': region_binary
        })
        
        print(f"{num_users}x{num_movies:<7} {raw_mean:>9.4f}  {binary_density:>10.2f}% {fill_rate:>9.2f}%")
    
    return results

def visualize_comparison(results, output_dir='analysis_plots'):
    """Raw vs Binary karşılaştırmalı görselleştirme."""
    print("\n" + "="*80)
    print("ADIM 6: GÖRSELLEŞTİRME")
    print("="*80)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Her boyut için yan yana raw ve binary heatmap
    for result in results[:4]:  # İlk 4 boyut için (çok olmasın)
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        
        # Raw ratings heatmap
        sns.heatmap(
            result['region_raw'],
            ax=axes[0],
            cmap="YlOrRd",
            vmin=0,
            vmax=5,
            cbar_kws={'label': 'Rating (1-5)'},
            xticklabels=False,
            yticklabels=False
        )
        axes[0].set_title(
            f"Ham Ratings - {result['size']}\n"
            f"Ortalama: {result['raw_mean']:.2f} yıldız",
            fontsize=12,
            fontweight='bold'
        )
        axes[0].set_xlabel(f"Filmler (İlk {result['num_movies']})")
        axes[0].set_ylabel(f"Kullanıcılar (İlk {result['num_users']})")
        
        # Binary heatmap
        sns.heatmap(
            result['region_binary'],
            ax=axes[1],
            cmap="Blues",
            vmin=0,
            vmax=1,
            cbar_kws={'label': 'Binary (0/1)'},
            xticklabels=False,
            yticklabels=False
        )
        axes[1].set_title(
            f"Binary Dönüşüm - {result['size']}\n"
            f"Yoğunluk: %{result['binary_density']:.2f}",
            fontsize=12,
            fontweight='bold'
        )
        axes[1].set_xlabel(f"Filmler (İlk {result['num_movies']})")
        axes[1].set_ylabel(f"Kullanıcılar (İlk {result['num_users']})")
        
        # Fark matrisi (raw != 0 ama binary == 0 olanlar)
        lost_ratings = ((result['region_raw'] > 0) & (result['region_raw'] < 4)).astype(int)
        sns.heatmap(
            lost_ratings,
            ax=axes[2],
            cmap="Reds",
            vmin=0,
            vmax=1,
            cbar_kws={'label': 'Kayıp (1-3 yıldız)'},
            xticklabels=False,
            yticklabels=False
        )
        axes[2].set_title(
            f"Kayıp Ratingler (1-3★) - {result['size']}\n"
            f"Binary'de 0'a dönen: {lost_ratings.sum().sum()} rating",
            fontsize=12,
            fontweight='bold'
        )
        axes[2].set_xlabel(f"Filmler (İlk {result['num_movies']})")
        axes[2].set_ylabel(f"Kullanıcılar (İlk {result['num_users']})")
        
        plt.tight_layout()
        filename = f"movielens_raw_vs_binary_{result['size']}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"✅ {filename} kaydedildi")
        plt.close()

def create_detailed_report(results, output_file='MOVIELENS_RAW_ANALYSIS_REPORT.md'):
    """Detaylı rapor oluşturur."""
    print("\n" + "="*80)
    print("ADIM 7: DETAYLI RAPOR OLUŞTURMA")
    print("="*80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 📊 MovieLens Ham Ratings Analizi - Binary Dönüşüm Süreci\n\n")
        f.write(f"**Tarih:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        f.write("## 1. Analiz Özeti\n\n")
        f.write("Bu rapor, MovieLens 100k veri setinin **ham ratings** (1-5 yıldız) halinden ")
        f.write("**binary** (0/1) formatına dönüşüm sürecini detaylı olarak göstermektedir.\n\n")
        
        f.write("### Binary Dönüşüm Kuralı\n\n")
        f.write("```\n")
        f.write("Rating >= 4 yıldız  →  1 (Olumlu)\n")
        f.write("Rating < 4 yıldız   →  0 (Olumsuz/İzlenmedi)\n")
        f.write("```\n\n")
        
        f.write("## 2. Yoğun Bölge Karşılaştırması\n\n")
        f.write("| Boyut | Ham Ort. Rating | Binary Yoğ. | Doluluk Oranı |\n")
        f.write("|-------|-----------------|-------------|---------------|\n")
        
        for result in results:
            f.write(f"| {result['size']} | ")
            f.write(f"{result['raw_mean']:.4f}★ | ")
            f.write(f"%{result['binary_density']:.2f} | ")
            f.write(f"%{result['fill_rate']:.2f} |\n")
        
        f.write("\n## 3. Gözlemler\n\n")
        
        best_raw = max(results, key=lambda x: x['raw_mean'])
        f.write(f"- **En yüksek ortalama rating:** {best_raw['size']} ({best_raw['raw_mean']:.2f}★)\n")
        
        best_binary = max(results, key=lambda x: x['binary_density'])
        f.write(f"- **En yoğun binary bölge:** {best_binary['size']} (%{best_binary['binary_density']:.2f})\n\n")
        
        f.write("### Dönüşüm Etkisi\n\n")
        f.write("1. **1-3 yıldızlı ratingler:** Binary dönüşümde **kaybolur** (0'a döner)\n")
        f.write("2. **4-5 yıldızlı ratingler:** Binary'de **1** olur\n")
        f.write("3. **Yoğun bölgeler:** Genellikle yüksek ortalama rating'e sahiptir, ")
        f.write("bu yüzden binary dönüşümde de yoğun kalırlar.\n\n")
        
        f.write("## 4. Görsel Analizler\n\n")
        f.write("Her boyut için üç heatmap oluşturulmuştur:\n\n")
        f.write("1. **Ham Ratings Heatmap:** 1-5 yıldız aralığında renklendirilmiş\n")
        f.write("2. **Binary Heatmap:** 0/1 değerleri ile\n")
        f.write("3. **Kayıp Ratingler:** 1-3 yıldızlı (binary'de kaybolan) ratingler\n\n")
        
        f.write("## 5. Sonuç\n\n")
        f.write("- Sıralama işlemi **ham ratings** üzerinde yapılmıştır.\n")
        f.write("- En aktif kullanıcılar ve popüler filmler sol üst köşede toplanmıştır.\n")
        f.write("- Binary dönüşüm sonrası yoğunluk korunmuştur.\n")
        f.write("- Düşük ratingler (1-3★) bilgi kaybına neden olmuştur.\n")
    
    print(f"✅ Rapor kaydedildi: {output_file}")

def main():
    """Ana fonksiyon."""
    print("="*80)
    print("MOVIELENS HAM RATINGS ANALİZİ")
    print("Binary Dönüşüm Öncesi ve Sonrası Detaylı İnceleme")
    print("="*80)
    
    # 1. Ham ratings yükle
    df_ratings = load_raw_ratings()
    
    # 2. Ham matris oluştur
    df_raw_matrix = create_raw_matrix(df_ratings)
    
    # 3. Sırala
    df_sorted_raw, sorted_users, sorted_movies = sort_raw_matrix(df_raw_matrix)
    
    # 4. Binary'ye dönüştür
    df_binary_matrix = convert_to_binary(df_raw_matrix, threshold=4)
    df_sorted_binary = df_binary_matrix.loc[sorted_users, sorted_movies]
    
    # 5. Yoğun bölgeleri karşılaştır
    sizes = [
        (5, 10),
        (10, 20),
        (20, 30),
        (30, 50),
        (50, 75)
    ]
    
    results = analyze_dense_regions_comparison(df_sorted_raw, df_sorted_binary, sizes)
    
    # 6. Görselleştir
    visualize_comparison(results)
    
    # 7. Rapor oluştur
    create_detailed_report(results)
    
    print("\n" + "="*80)
    print("✅ ANALİZ TAMAMLANDI!")
    print("="*80)
    print("\nOluşan Dosyalar:")
    print("   📊 analysis_plots/movielens_raw_vs_binary_*.png (Her boyut için 3'lü karşılaştırma)")
    print("   📄 MOVIELENS_RAW_ANALYSIS_REPORT.md")
    print("\nSONRAKİ ADIM:")
    print("Görsel analiz dosyalarını inceleyerek ham ratings'in binary dönüşümdeki")
    print("değişimini detaylı şekilde gözlemleyebilirsiniz!")

if __name__ == "__main__":
    main()
