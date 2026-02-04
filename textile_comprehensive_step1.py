# -*- coding: utf-8 -*-
"""
TEKSTİL KAPSAMLı RMVC ANALİZİ - ADIM 1
======================================
AlimSayisi ve TotalScore Pivot Tablolarını Oluştur

Makale için her şey kaydedilecek!
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

print("="*100)
print("TEKSTİL KAPSAMLı RMVC ANALİZİ - ADIM 1: VERİ HAZIRLAMA")
print("="*100)
print(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Klasörleri oluştur
os.makedirs('Textile_data/outputs/raw_matrices', exist_ok=True)
os.makedirs('Textile_data/outputs/binary_matrices', exist_ok=True)
os.makedirs('Textile_data/outputs/rmvc_results', exist_ok=True)
os.makedirs('Textile_data/outputs/iterative_results', exist_ok=True)
os.makedirs('Textile_data/reports', exist_ok=True)

print("✅ Klasörler oluşturuldu\n")

# ==========================================
# 1. ORİJİNAL VERİYİ YÜKLE
# ==========================================

print("📁 Orijinal veri yükleniyor...")
df = pd.read_csv('Textile_data/FirmaUrunMin9_Miktar_AlimSayisi.csv')

print(f"✅ Veri yüklendi: {len(df):,} kayıt")
print(f"   Sütunlar: {list(df.columns)}\n")

# ==========================================
# 2. TOTALSCORE HESAPLA
# ==========================================

print("🔢 TotalScore hesaplanıyor (Miktar × AlimSayisi)...")
df['TotalScore'] = df['Miktar'] * df['AlimSayisi']

print(f"✅ TotalScore oluşturuldu")
print(f"   İstatistikler:")
print(f"   - Min: {df['TotalScore'].min():,.0f}")
print(f"   - Max: {df['TotalScore'].max():,.0f}")
print(f"   - Ortalama: {df['TotalScore'].mean():,.2f}")
print(f"   - Medyan: {df['TotalScore'].median():,.2f}\n")

# ==========================================
# 3. 3 PIVOT TABLO OLUŞTUR
# ==========================================

print("📊 Pivot tablolar oluşturuluyor...\n")

# 3.1. Miktar Pivot (Zaten var ama yeniden oluşturalım)
print("1/3 Miktar Pivot...")
miktar_pivot = df.pivot_table(
    index='FirmaID',
    columns='UrunTID',
    values='Miktar',
    aggfunc='sum',
    fill_value=0
)
print(f"    ✅ Boyut: {miktar_pivot.shape[0]} firma × {miktar_pivot.shape[1]} ürün")

# 3.2. AlimSayisi Pivot (Yeni)
print("2/3 AlimSayisi Pivot...")
alimsayisi_pivot = df.pivot_table(
    index='FirmaID',
    columns='UrunTID',
    values='AlimSayisi',
    aggfunc='sum',
    fill_value=0
)
print(f"    ✅ Boyut: {alimsayisi_pivot.shape[0]} firma × {alimsayisi_pivot.shape[1]} ürün")

# 3.3. TotalScore Pivot (Yeni)
print("3/3 TotalScore Pivot...")
totalscore_pivot = df.pivot_table(
    index='FirmaID',
    columns='UrunTID',
    values='TotalScore',
    aggfunc='sum',
    fill_value=0
)
print(f"    ✅ Boyut: {totalscore_pivot.shape[0]} firma × {totalscore_pivot.shape[1]} ürün\n")

# ==========================================
# 4. SIRALAMA (Yoğunluğa Göre Permutation)
# ==========================================

print("🔄 Yoğunluğa göre sıralama...\n")

# Miktar bazlı sıralama (En aktif firmalar ve ürünler)
print("   Miktar bazlı sıralama...")
firma_islem_miktar = (miktar_pivot > 0).sum(axis=1)
urun_islem_miktar = (miktar_pivot > 0).sum(axis=0)

sirali_firmalar_miktar = firma_islem_miktar.sort_values(ascending=False).index
sirali_urunler_miktar = urun_islem_miktar.sort_values(ascending=False).index

# Tüm pivotları aynı sırayla sırala
miktar_sorted = miktar_pivot.loc[sirali_firmalar_miktar, sirali_urunler_miktar]
alimsayisi_sorted = alimsayisi_pivot.loc[sirali_firmalar_miktar, sirali_urunler_miktar]
totalscore_sorted = totalscore_pivot.loc[sirali_firmalar_miktar, sirali_urunler_miktar]

print("   ✅ Sıralama tamamlandı (En aktif → En az aktif)\n")

# ==========================================
# 5. YOĞUNLUK ANALİZİ
# ==========================================

print("📊 Yoğunluk analizi...\n")

def calc_density(matrix):
    total = matrix.size
    nonzero = np.count_nonzero(matrix)
    return (nonzero / total) * 100

# Global yoğunluklar
d_miktar = calc_density(miktar_sorted)
d_alimsayisi = calc_density(alimsayisi_sorted)
d_totalscore = calc_density(totalscore_sorted)

print(f"   Global Yoğunluklar:")
print(f"   - Miktar:      {d_miktar:.2f}%")
print(f"   - AlimSayisi:  {d_alimsayisi:.2f}%")
print(f"   - TotalScore:  {d_totalscore:.2f}%\n")

# Test boyutları için yoğunluk
test_sizes = [(10, 20), (20, 30), (30, 50)]

print("   Boyut bazında yoğunluklar:")
print(f"   {'Boyut':<12} {'Miktar':<12} {'AlimSayisi':<12} {'TotalScore'}")
print("   " + "-"*50)

for rows, cols in test_sizes:
    d_m = calc_density(miktar_sorted.iloc[:rows, :cols])
    d_a = calc_density(alimsayisi_sorted.iloc[:rows, :cols])
    d_t = calc_density(totalscore_sorted.iloc[:rows, :cols])
    print(f"   {rows}×{cols:<9} {d_m:>6.2f}%      {d_a:>6.2f}%      {d_t:>6.2f}%")

print()

# ==========================================
# 6. DOSYALARI KAYDET
# ==========================================

print("💾 Sıralanmış pivot tablolar kaydediliyor...\n")

miktar_sorted.to_csv('Textile_data/Firma_Urun_Miktar_Yogun_Sirali.csv')
print("   ✅ Firma_Urun_Miktar_Yogun_Sirali.csv")

alimsayisi_sorted.to_csv('Textile_data/Firma_Urun_AlimSayisi_Yogun_Sirali.csv')
print("   ✅ Firma_Urun_AlimSayisi_Yogun_Sirali.csv")

totalscore_sorted.to_csv('Textile_data/Firma_Urun_TotalScore_Yogun_Sirali.csv')
print("   ✅ Firma_Urun_TotalScore_Yogun_Sirali.csv\n")

# ==========================================
# 7. ADIM 1 RAPORU
# ==========================================

print("📝 ADIM 1 Raporu hazırlanıyor...\n")

rapor = f"""
# TEKSTİL ADIM 1 RAPORU - VERİ HAZIRLAMA

**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## VERİ SETİ

- **Kayıt Sayısı:** {len(df):,}
- **Benzersiz Firma:** {df['FirmaID'].nunique()}
- **Benzersiz Ürün:** {df['UrunTID'].nunique()}

## OLUŞTURULAN PİVOT TABLOLAR

### 1. Miktar Pivot
- **Boyut:** {miktar_pivot.shape[0]} × {miktar_pivot.shape[1]}
- **Global Yoğunluk:** {d_miktar:.2f}%

### 2. AlimSayisi Pivot (Yeni)
- **Boyut:** {alimsayisi_pivot.shape[0]} × {alimsayisi_pivot.shape[1]}
- **Global Yoğunluk:** {d_alimsayisi:.2f}%

### 3. TotalScore Pivot (Miktar × AlimSayisi)
- **Boyut:** {totalscore_pivot.shape[0]} × {totalscore_pivot.shape[1]}
- **Global Yoğunluk:** {d_totalscore:.2f}%
- **Min:** {df['TotalScore'].min():,.0f}
- **Max:** {df['TotalScore'].max():,.0f}
- **Ortalama:** {df['TotalScore'].mean():,.2f}
- **Medyan:** {df['TotalScore'].median():,.2f}

## SIRALAMA

Firmalar ve ürünler **Miktar bazlı işlem sayısına** göre sıralandı (En aktif → En az aktif).

## YOĞUNLUK ANALİZİ (Test Boyutları)

| Boyut | Miktar | AlimSayisi | TotalScore |
|-------|--------|------------|------------|
"""

for rows, cols in test_sizes:
    d_m = calc_density(miktar_sorted.iloc[:rows, :cols])
    d_a = calc_density(alimsayisi_sorted.iloc[:rows, :cols])
    d_t = calc_density(totalscore_sorted.iloc[:rows, :cols])
    rapor += f"| {rows}×{cols} | {d_m:.2f}% | {d_a:.2f}% | {d_t:.2f}% |\n"

rapor += f"""
## OLUŞTURULAN DOSYALAR

1. `Firma_Urun_Miktar_Yogun_Sirali.csv`
2. `Firma_Urun_AlimSayisi_Yogun_Sirali.csv` ✨ Yeni
3. `Firma_Urun_TotalScore_Yogun_Sirali.csv` ✨ Yeni

## SONRAKİ ADIM

ADIM 2: Sub-matris seçimi ve Binary conversion
"""

with open('Textile_data/reports/ADIM1_VeriHazirlama_Raporu.md', 'w', encoding='utf-8') as f:
    f.write(rapor)

print("   ✅ ADIM1_VeriHazirlama_Raporu.md\n")

# ==========================================
# ÖZET
# ==========================================

print("="*100)
print("✅ ADIM 1 TAMAMLANDI!")
print("="*100)
print(f"\nOluşturulan Matrisler:")
print(f"  1. Miktar:      {miktar_sorted.shape[0]} × {miktar_sorted.shape[1]} ({d_miktar:.2f}% yoğunluk)")
print(f"  2. AlimSayisi:  {alimsayisi_sorted.shape[0]} × {alimsayisi_sorted.shape[1]} ({d_alimsayisi:.2f}% yoğunluk)")
print(f"  3. TotalScore:  {totalscore_sorted.shape[0]} × {totalscore_sorted.shape[1]} ({d_totalscore:.2f}% yoğunluk)")

print(f"\nTest Boyutları: {', '.join([f'{r}×{c}' for r, c in test_sizes])}")
print(f"\nSonraki Adım: ADIM 2 - Sub-matris Seçimi ve Binary Conversion")
print(f"\nBitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)
