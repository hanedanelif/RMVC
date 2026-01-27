"""
Oneri Sistemi Veri Setlerini RMVC Formatina Donusturme
=======================================================
MovieLens, Book-Crossing gibi veri setlerini RMVC icin uygun formata donusturur.
"""

import pandas as pd
import numpy as np
import os
import urllib.request
import zipfile
from io import BytesIO

class DatasetLoader:
    """Veri setlerini yukler ve RMVC formatina donusturur."""
    
    def __init__(self, data_dir='datasets'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def download_movielens_100k(self):
        """MovieLens 100K veri setini indir."""
        url = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
        zip_path = os.path.join(self.data_dir, "ml-100k.zip")
        extract_path = os.path.join(self.data_dir, "ml-100k")
        
        if os.path.exists(extract_path):
            print(f"[OK] MovieLens 100K zaten indirilmis: {extract_path}")
            return extract_path
        
        print(f"[1/3] MovieLens 100K indiriliyor: {url}")
        urllib.request.urlretrieve(url, zip_path)
        
        print(f"[2/3] Dosya cikartiliyor...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.data_dir)
        
        print(f"[3/3] Tamamlandi: {extract_path}")
        return extract_path
    
    def load_movielens_100k(self, min_rating=4):
        """
        MovieLens 100K veri setini yukle ve binary matrise donustur.
        
        Args:
            min_rating: Bu deger ve uzeri rating'ler 1, altindakiler 0 olur
        
        Returns:
            df: Binary matris (User x Movie)
            metadata: Veri seti hakkinda bilgi
        """
        extract_path = self.download_movielens_100k()
        
        # Ratings dosyasini oku
        ratings_file = os.path.join(extract_path, "u.data")
        print(f"\n[1/4] Ratings dosyasi okunuyor: {ratings_file}")
        
        # Kolonlar: user_id, item_id, rating, timestamp
        df_ratings = pd.read_csv(ratings_file, sep='\t', 
                                 names=['user_id', 'movie_id', 'rating', 'timestamp'])
        
        print(f"  - {len(df_ratings)} rating yuklendi")
        print(f"  - {df_ratings['user_id'].nunique()} kullanici")
        print(f"  - {df_ratings['movie_id'].nunique()} film")
        print(f"  - Rating araligi: {df_ratings['rating'].min()}-{df_ratings['rating'].max()}")
        
        # Binary'ye donustur
        print(f"\n[2/4] Binary matrise donusturuluyor (rating >= {min_rating} -> 1)")
        df_ratings['binary_rating'] = (df_ratings['rating'] >= min_rating).astype(int)
        
        # Pivot table olustur (User x Movie)
        print(f"[3/4] Pivot table olusturuluyor...")
        df_binary = df_ratings.pivot_table(
            index='user_id', 
            columns='movie_id', 
            values='binary_rating',
            fill_value=0
        )
        
        print(f"  - Matris boyutu: {df_binary.shape[0]} kullanici x {df_binary.shape[1]} film")
        print(f"  - Toplam deger: {df_binary.shape[0] * df_binary.shape[1]}")
        print(f"  - 1'lerin sayisi: {df_binary.sum().sum()}")
        print(f"  - Seyreklik: {1 - (df_binary.sum().sum() / (df_binary.shape[0] * df_binary.shape[1])):.4f}")
        
        # Metadata
        metadata = {
            'dataset': 'MovieLens 100K',
            'num_users': df_binary.shape[0],
            'num_movies': df_binary.shape[1],
            'num_ratings': len(df_ratings),
            'min_rating_threshold': min_rating,
            'sparsity': 1 - (df_binary.sum().sum() / (df_binary.shape[0] * df_binary.shape[1])),
            'density': df_binary.sum().sum() / (df_binary.shape[0] * df_binary.shape[1])
        }
        
        print(f"\n[4/4] Tamamlandi!")
        return df_binary, metadata
    
    def sample_subset(self, df, num_users=50, num_items=30, min_interactions=5):
        """
        Buyuk veri setinden kucuk bir alt kume al.
        
        Args:
            df: Binary matris
            num_users: Alinacak kullanici sayisi
            num_items: Alinacak item sayisi
            min_interactions: Minimum etkilesim sayisi
        
        Returns:
            df_subset: Alt kume matrisi
        """
        print(f"\n[SUBSET] Alt kume olusturuluyor...")
        print(f"  - Hedef: {num_users} kullanici x {num_items} item")
        
        # En aktif kullanicilari sec
        user_activity = df.sum(axis=1).sort_values(ascending=False)
        active_users = user_activity[user_activity >= min_interactions].head(num_users).index
        
        # En populer itemlari sec
        item_popularity = df.sum(axis=0).sort_values(ascending=False)
        popular_items = item_popularity[item_popularity >= min_interactions].head(num_items).index
        
        # Alt kume olustur
        df_subset = df.loc[active_users, popular_items]
        
        print(f"  - Gercek boyut: {df_subset.shape[0]} x {df_subset.shape[1]}")
        print(f"  - 1'lerin sayisi: {df_subset.sum().sum()}")
        print(f"  - Seyreklik: {1 - (df_subset.sum().sum() / (df_subset.shape[0] * df_subset.shape[1])):.4f}")
        
        return df_subset
    
    def convert_to_rmvc_format(self, df, output_file='movielens_rmvc.xlsx'):
        """
        Binary matrisi RMVC formatina donustur ve Excel'e kaydet.
        
        RMVC formati:
        - Satirlar = Parametreler (filmler)
        - Sutunlar = Elemanlar (kullanicilar)
        - Degerler = 0 veya 1
        
        Args:
            df: Binary matris (User x Movie)
            output_file: Cikti dosyasi
        
        Returns:
            filepath: Kaydedilen dosya yolu
        """
        print(f"\n[RMVC FORMAT] RMVC formatina donusturuluyor...")
        
        # Transpose et (User x Movie -> Movie x User)
        # Cunku RMVC'de satirlar=parametreler, sutunlar=elemanlar
        df_rmvc = df.T
        
        # Index ve column isimlerini duzenle
        df_rmvc.index.name = 'Movie_ID'
        df_rmvc.columns.name = 'User_ID'
        
        # Excel'e kaydet
        filepath = os.path.join(self.data_dir, output_file)
        df_rmvc.to_excel(filepath)
        
        print(f"  - Format: {df_rmvc.shape[0]} parametre (film) x {df_rmvc.shape[1]} eleman (kullanici)")
        print(f"  - Dosya kaydedildi: {filepath}")
        
        return filepath
    
    def create_multiple_subsets(self, df, sizes=[(10, 5), (20, 10), (30, 15), (50, 25)]):
        """
        Farkli boyutlarda alt kumeler olustur.
        
        Args:
            df: Binary matris
            sizes: (num_users, num_items) tuple listesi
        
        Returns:
            subsets: Alt kume sozlugu
        """
        print(f"\n[MULTIPLE SUBSETS] {len(sizes)} farkli boyutta alt kume olusturuluyor...")
        
        subsets = {}
        for i, (num_users, num_items) in enumerate(sizes, 1):
            print(f"\n--- Alt Kume {i}/{len(sizes)} ---")
            subset_name = f"{num_users}x{num_items}"
            
            subset = self.sample_subset(df, num_users, num_items)
            subsets[subset_name] = subset
            
            # RMVC formatinda kaydet
            output_file = f"movielens_{subset_name}_rmvc.xlsx"
            self.convert_to_rmvc_format(subset, output_file)
        
        return subsets


def main():
    """Ana fonksiyon."""
    print("=" * 80)
    print("ONERI SISTEMI VERI SETLERI - RMVC FORMATINA DONUSTURME")
    print("=" * 80)
    print()
    
    # Loader olustur
    loader = DatasetLoader()
    
    # MovieLens 100K yukle
    print("\n" + "=" * 80)
    print("1. MOVIELENS 100K YUKLENIYOR")
    print("=" * 80)
    
    df_full, metadata = loader.load_movielens_100k(min_rating=4)
    
    # Metadata goster
    print("\n" + "=" * 80)
    print("2. VERI SETI METADATA")
    print("=" * 80)
    for key, value in metadata.items():
        print(f"  {key:25s}: {value}")
    
    # Farkli boyutlarda alt kumeler olustur
    print("\n" + "=" * 80)
    print("3. ALT KUMELER OLUSTURULUYOR")
    print("=" * 80)
    
    sizes = [
        (10, 5),   # Cok kucuk (test icin)
        (20, 10),  # Kucuk
        (30, 15),  # Orta
        (50, 25),  # Buyuk
        (100, 50)  # Cok buyuk
    ]
    
    subsets = loader.create_multiple_subsets(df_full, sizes)
    
    # Ozet
    print("\n" + "=" * 80)
    print("4. TAMAMLANDI!")
    print("=" * 80)
    print(f"\nOlusturulan dosyalar (datasets/ klasorunde):")
    for i, (name, subset) in enumerate(subsets.items(), 1):
        print(f"  {i}. movielens_{name}_rmvc.xlsx ({subset.shape[0]}x{subset.shape[1]})")
    
    print("\n" + "=" * 80)
    print("SONRAKI ADIM:")
    print("=" * 80)
    print("Bu dosyalari rmvc_app_v2.py uygulamasinda yukleyip test edebilirsiniz!")
    print("Ayrica iteratif RMVC analizini de calistirabiliriz.")


if __name__ == "__main__":
    main()
