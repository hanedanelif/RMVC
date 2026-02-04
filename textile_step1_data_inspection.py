# -*- coding: utf-8 -*-
"""
ADIM 1: Tekstil Veri İnceleme ve Hazırlık
=========================================
FirmaUrunMin9_Miktar_AlimSayisi.csv veri setini inceler ve özet bilgiler verir.
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("ADIM 1: TEKSTİL VERİ İNCELEME VE HAZIRLIK")
print("="*80)
print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ==========================================
# VERİ YÜKLEME
# ==========================================

file_path = "Textile_data/FirmaUrunMin9_Miktar_AlimSayisi.csv"

print(f"📁 Dosya yükleniyor: {file_path}")
df = pd.read_csv(file_path)

print(f"✅ Veri yüklendi!")
print(f"   Toplam kayıt: {len(df):,}")
print(f"   Sütunlar: {list(df.columns)}\n")

# ==========================================
# VERİ YAPISI ANALİZİ
# ==========================================

print("="*80)
print("VERİ YAPISI")
print("="*80)

print("\n📊 İlk 10 kayıt:")
print(df.head(10).to_string())

print("\n📊 Sütun Bilgileri:")
print(df.info())

print("\n📊 İstatistiksel Özet:")
print(df.describe())

# ==========================================
# EKSİK DEĞER ANALİZİ
# ==========================================

print("\n" + "="*80)
print("EKSİK DEĞER ANALİZİ")
print("="*80)

missing = df.isnull().sum()
print(f"\nEksik değerler:")
for col in df.columns:
    missing_count = missing[col]
    missing_pct = (missing_count / len(df)) * 100
    print(f"  {col}: {missing_count} ({missing_pct:.2f}%)")

# ==========================================
# BENZERSIZ DEĞERLER
# ==========================================

print("\n" + "="*80)
print("BENZERSIZ DEĞERLER")
print("="*80)

unique_firms = df['FirmaID'].nunique()
unique_products = df['UrunTID'].nunique()

print(f"\n✅ Benzersiz Firma Sayısı: {unique_firms}")
print(f"✅ Benzersiz Ürün Sayısı: {unique_products}")
print(f"✅ Toplam İlişki Sayısı: {len(df)}")

# İlişki yoğunluğu
total_possible = unique_firms * unique_products
density = (len(df) / total_possible) * 100
print(f"\n📊 Teorik Maksimum İlişki: {total_possible:,}")
print(f"📊 Gerçek İlişki Sayısı: {len(df):,}")
print(f"📊 Veri Yoğunluğu: {density:.2f}%")

# ==========================================
# MİKTAR VE ALIMsayısı ANALİZİ
# ==========================================

print("\n" + "="*80)
print("MİKTAR VE ALIMSAYIsı ANALİZİ")
print("="*80)

print("\n📊 Miktar İstatistikleri:")
print(f"  Min: {df['Miktar'].min():,}")
print(f"  Max: {df['Miktar'].max():,}")
print(f"  Ortalama: {df['Miktar'].mean():,.2f}")
print(f"  Medyan: {df['Miktar'].median():,.2f}")

print("\n📊 AlimSayisi İstatistikleri:")
print(f"  Min: {df['AlimSayisi'].min()}")
print(f"  Max: {df['AlimSayisi'].max()}")
print(f"  Ortalama: {df['AlimSayisi'].mean():.2f}")
print(f"  Medyan: {df['AlimSayisi'].median():.2f}")

# ==========================================
# EN AKTİF FİRMA VE ÜRÜNLER
# ==========================================

print("\n" + "="*80)
print("EN AKTİF FİRMA VE ÜRÜNLER")
print("="*80)

# Firma bazında analiz
firm_stats = df.groupby('FirmaID').agg({
    'UrunTID': 'count',  # Kaç farklı ürün
    'Miktar': 'sum',
    'AlimSayisi': 'sum'
}).rename(columns={'UrunTID': 'UrunSayisi'})

firm_stats = firm_stats.sort_values('UrunSayisi', ascending=False)

print("\n📊 En Çok Ürün Alan 10 Firma:")
print(firm_stats.head(10).to_string())

# Ürün bazında analiz
product_stats = df.groupby('UrunTID').agg({
    'FirmaID': 'count',  # Kaç farklı firma
    'Miktar': 'sum',
    'AlimSayisi': 'sum'
}).rename(columns={'FirmaID': 'FirmaSayisi'})

product_stats = product_stats.sort_values('FirmaSayisi', ascending=False)

print("\n📊 En Çok Firma Tarafından Alınan 10 Ürün:")
print(product_stats.head(10).to_string())

# ==========================================
# MATRİS BOYUTU TAVSİYESİ
# ==========================================

print("\n" + "="*80)
print("MATRİS BOYUTU TAVSİYESİ")
print("="*80)

print(f"\nTam Matris Boyutu: {unique_firms} × {unique_products}")
print(f"Tahmini Hücre Sayısı: {total_possible:,}")
print(f"Yoğunluk: {density:.2f}%")

# MovieLens tarzı dense sub-matris önerileri
recommendations = [
    (10, 20, "Küçük Test Matrisi"),
    (20, 30, "Orta Test Matrisi"),
    (30, 50, "Büyük Test Matrisi"),
    (50, 75, "Kapsamlı Analiz"),
]

print("\n📋 Önerilen Alt-Matris Boyutları:")
print(f"{'Boyut':<15} {'Açıklama':<25} {'Tahmini Hücre'}")
print("-" * 60)
for firms, products, desc in recommendations:
    cells = firms * products
    print(f"{firms}×{products:<12} {desc:<25} {cells:,}")

# ==========================================
# ÖZET RAPOR
# ==========================================

print("\n" + "="*80)
print("ÖZET RAPOR")
print("="*80)

summary = f"""
VERİ SETİ ÖZETİ:
- Toplam Kayıt: {len(df):,}
- Benzersiz Firma: {unique_firms}
- Benzersiz Ürün: {unique_products}
- Veri Formatı: Long (FirmaID, UrunTID, Miktar, AlimSayisi)
- Yoğunluk: {density:.2f}%

VERİ KALİTESİ:
- Eksik Değer: {df.isnull().sum().sum()}
- Tüm sütunlar dolu: {df.isnull().sum().sum() == 0}

SONRAKİ ADIM:
- ADIM 2: Pivot tablo ile wide format'a dönüştür
- Binary matris oluştur (Miktar > 0 veya AlimSayisi > 0)
- Yoğun alt-matrisler seç (density analysis)
"""

print(summary)

# Raporu kaydet
with open("Textile_data/outputs/step1_data_inspection_report.txt", "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("ADIM 1: TEKSTİL VERİ İNCELEME RAPORU\n")
    f.write("="*80 + "\n\n")
    f.write(summary)

print("\n✅ ADIM 1 TAMAMLANDI!")
print(f"   Rapor kaydedildi: Textile_data/outputs/step1_data_inspection_report.txt")
