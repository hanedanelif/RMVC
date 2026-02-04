# -*- coding: utf-8 -*-
"""
MovieLens'ten 10 Farklı Boyutta Matris Çıkarma
==============================================
"""

import pandas as pd
import numpy as np
import os

# MovieLens 100K veri setini oku
print("MovieLens 100K veri setini yüklüyorum...")

# Ratings dosyasını oku (user_id, movie_id, rating, timestamp)
ratings_file = r'd:\Projects\RMVC\datasets\ml-100k\u.data'

# Farklı formatları dene
try:
    # Tab-separated
    df = pd.read_csv(ratings_file, sep='\t', names=['user_id', 'movie_id', 'rating', 'timestamp'])
    print("Tab-separated format başarılı")
except:
    try:
        # Space-separated
        df = pd.read_csv(ratings_file, sep=' ', names=['user_id', 'movie_id', 'rating', 'timestamp'])
        print("Space-separated format başarılı")
    except:
        # Double colon-separated (MovieLens 1M format)
        df = pd.read_csv(ratings_file, sep='::', names=['user_id', 'movie_id', 'rating', 'timestamp'], engine='python')
        print("Double colon format başarılı")

print(f"Toplam rating: {len(df)}")
print(f"Kullanıcı sayısı: {df['user_id'].nunique()}")
print(f"Film sayısı: {df['movie_id'].nunique()}")
print(f"\nİlk 5 satır:")
print(df.head())

# 10 farklı boyut tanımla
matrix_sizes = [
    (10, 10),
    (10, 20),
    (15, 20),
    (20, 20),
    (20, 30),
    (30, 30),
    (30, 50),
    (40, 50),
    (50, 50),
    (60, 75)
]

print(f"\n{'='*60}")
print(f"10 FARKLI BOYUTTA MATRİS OLUŞTURMA")
print(f"{'='*60}\n")

output_dir = r'd:\Projects\RMVC\datasets'
os.makedirs(output_dir, exist_ok=True)

for rows, cols in matrix_sizes:
    print(f"\n{rows}×{cols} matrisi oluşturuluyor...")
    
    # İlk N kullanıcı ve M film seç
    selected_users = df['user_id'].unique()[:rows]
    selected_movies = df['movie_id'].unique()[:cols]
    
    # Bu kullanıcı ve filmler için ratings'leri filtrele
    filtered_df = df[
        (df['user_id'].isin(selected_users)) & 
        (df['movie_id'].isin(selected_movies))
    ]
    
    # Pivot table oluştur
    pivot = filtered_df.pivot_table(
        index='user_id',
        columns='movie_id',
        values='rating',
        fill_value=0
    )
    
    # Binary dönüşüm: rating >= 4 → 1, else → 0
    binary_matrix = (pivot >= 4).astype(int)
    
    # Boyutu kontrol et ve gerekirse ayarla
    if binary_matrix.shape[0] < rows or binary_matrix.shape[1] < cols:
        print(f"  ⚠️ Uyarı: Yeterli veri yok. Gerçek boyut: {binary_matrix.shape}")
        # Eksik satırları/sütunları 0 ile doldur
        all_users = list(range(1, rows + 1))
        all_movies = list(range(1, cols + 1))
        binary_matrix = binary_matrix.reindex(index=all_users, columns=all_movies, fill_value=0)
    
    # İlk N satır ve M sütunu al
    binary_matrix = binary_matrix.iloc[:rows, :cols]
    
    # Yoğunluk hesapla
    density = (binary_matrix.sum().sum() / (rows * cols)) * 100
    
    # Kaydet
    output_file = os.path.join(output_dir, f'movielens_method1_{rows}x{cols}.csv')
    binary_matrix.to_csv(output_file, index=False, header=False)
    
    print(f"  ✅ Kaydedildi: {output_file}")
    print(f"  📊 Boyut: {binary_matrix.shape}")
    print(f"  📊 Yoğunluk: {density:.2f}%")
    print(f"  📊 1'lerin sayısı: {binary_matrix.sum().sum()}")

print(f"\n{'='*60}")
print(f"TAMAMLANDI! 10 matris oluşturuldu.")
print(f"{'='*60}")
