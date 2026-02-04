# -*- coding: utf-8 -*-
"""
TEKSTİL KAPSAMLı RMVC ANALİZİ - ADIM 2
======================================
Sub-Matris Seçimi ve Binary Conversion (4 Method)

Her matris, her method için CSV kaydedilecek!
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

print("="*100)
print("TEKSTİL KAPSAMLı RMVC ANALİZİ - ADIM 2: SUB-MATRİS VE BINARY CONVERSION")
print("="*100)
print(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ==========================================
# 1. SORTED PİVOTLARI YÜKLE
# ==========================================

print("📁 Sıralanmış pivot tablolar yükleniyor...\n")

miktar_sorted = pd.read_csv('Textile_data/Firma_Urun_Miktar_Yogun_Sirali.csv', index_col=0)
print(f"   ✅ Miktar: {miktar_sorted.shape}")

alimsayisi_sorted = pd.read_csv('Textile_data/Firma_Urun_AlimSayisi_Yogun_Sirali.csv', index_col=0)
print(f"   ✅ AlimSayisi: {alimsayisi_sorted.shape}")

totalscore_sorted = pd.read_csv('Textile_data/Firma_Urun_TotalScore_Yogun_Sirali.csv', index_col=0)
print(f"   ✅ TotalScore: {totalscore_sorted.shape}\n")

# ==========================================
# 2. TEST BOYUTLARI
# ==========================================

test_sizes = [(10, 20), (20, 30), (30, 50)]

print(f"🎯 Test Boyutları: {', '.join([f'{r}×{c}' for r, c in test_sizes])}\n")

# ==========================================
# 3. SUB-MATRİSLERİ KES VE KAYDET
# ==========================================

print("✂️ Sub-matrisler kesiliyor ve kaydediliyor...\n")

raw_matrices_info = []

for rows, cols in test_sizes:
    print(f"   📊 {rows}×{cols} matrisleri:")
    
    # Miktar
    miktar_sub = miktar_sorted.iloc[:rows, :cols]
    filename_m = f'Textile_data/outputs/raw_matrices/textile_{rows}x{cols}_miktar_raw.csv'
    miktar_sub.to_csv(filename_m)
    
    density_m = (np.count_nonzero(miktar_sub) / miktar_sub.size) * 100
    print(f"      ✅ Miktar ({density_m:.2f}% yoğunluk)")
    
    # AlimSayisi
    alimsayisi_sub = alimsayisi_sorted.iloc[:rows, :cols]
    filename_a = f'Textile_data/outputs/raw_matrices/textile_{rows}x{cols}_alimsayisi_raw.csv'
    alimsayisi_sub.to_csv(filename_a)
    
    density_a = (np.count_nonzero(alimsayisi_sub) / alimsayisi_sub.size) * 100
    print(f"      ✅ AlimSayisi ({density_a:.2f}% yoğunluk)")
    
    # TotalScore
    totalscore_sub = totalscore_sorted.iloc[:rows, :cols]
    filename_t = f'Textile_data/outputs/raw_matrices/textile_{rows}x{cols}_totalscore_raw.csv'
    totalscore_sub.to_csv(filename_t)
    
    density_t = (np.count_nonzero(totalscore_sub) / totalscore_sub.size) * 100
    print(f"      ✅ TotalScore ({density_t:.2f}% yoğunluk)\n")
    
    raw_matrices_info.append({
        'size': f'{rows}x{cols}',
        'miktar_density': density_m,
        'alimsayisi_density': density_a,
        'totalscore_density': density_t
    })

# ==========================================
# 4. BINARY CONVERSION - 4 METHOD
# ==========================================

print("🔄 Binary conversion (4 Method)...\n")

binary_info = []

for rows, cols in test_sizes:
    print(f"   📊 {rows}×{cols} - Binary conversion:")
    
    # Raw matrisleri yükle
    miktar_raw = pd.read_csv(f'Textile_data/outputs/raw_matrices/textile_{rows}x{cols}_miktar_raw.csv', index_col=0)
    alimsayisi_raw = pd.read_csv(f'Textile_data/outputs/raw_matrices/textile_{rows}x{cols}_alimsayisi_raw.csv', index_col=0)
    totalscore_raw = pd.read_csv(f'Textile_data/outputs/raw_matrices/textile_{rows}x{cols}_totalscore_raw.csv', index_col=0)
    
    # METHOD 1: Miktar > 0
    binary_m1 = (miktar_raw > 0).astype(int)
    filename_m1 = f'Textile_data/outputs/binary_matrices/textile_{rows}x{cols}_method1.csv'
    binary_m1.to_csv(filename_m1)
    
    density_m1 = (binary_m1.sum().sum() / binary_m1.size) * 100
    print(f"      ✅ Method 1 (Miktar > 0): {density_m1:.2f}% yoğunluk")
    
    # METHOD 2: AlimSayisi > 0
    binary_m2 = (alimsayisi_raw > 0).astype(int)
    filename_m2 = f'Textile_data/outputs/binary_matrices/textile_{rows}x{cols}_method2.csv'
    binary_m2.to_csv(filename_m2)
    
    density_m2 = (binary_m2.sum().sum() / binary_m2.size) * 100
    print(f"      ✅ Method 2 (AlimSayisi > 0): {density_m2:.2f}% yoğunluk")
    
    # METHOD 3: Miktar >= Median
    # Median hesapla (sadece > 0 olanlardan)
    median_miktar = miktar_raw[miktar_raw > 0].values.flatten()
    median_miktar = np.median(median_miktar) if len(median_miktar) > 0 else 0
    
    binary_m3 = (miktar_raw >= median_miktar).astype(int) if median_miktar > 0 else (miktar_raw > 0).astype(int)
    filename_m3 = f'Textile_data/outputs/binary_matrices/textile_{rows}x{cols}_method3.csv'
    binary_m3.to_csv(filename_m3)
    
    density_m3 = (binary_m3.sum().sum() / binary_m3.size) * 100
    print(f"      ✅ Method 3 (Miktar >= {median_miktar:.0f}): {density_m3:.2f}% yoğunluk")
    
    # METHOD 4: TotalScore >= Median (YENİ!)
    median_totalscore = totalscore_raw[totalscore_raw > 0].values.flatten()
    median_totalscore = np.median(median_totalscore) if len(median_totalscore) > 0 else 0
    
    binary_m4 = (totalscore_raw >= median_totalscore).astype(int) if median_totalscore > 0 else (totalscore_raw > 0).astype(int)
    filename_m4 = f'Textile_data/outputs/binary_matrices/textile_{rows}x{cols}_method4.csv'
    binary_m4.to_csv(filename_m4)
    
    density_m4 = (binary_m4.sum().sum() / binary_m4.size) * 100
    print(f"      ✅ Method 4 (TotalScore >= {median_totalscore:.0f}): {density_m4:.2f}% yoğunluk")
    
    # İstatistikleri kaydet
    binary_info.append({
        'size': f'{rows}x{cols}',
        'method1': {
            'description': 'Miktar > 0',
            'density': density_m1,
            'ones_count': int(binary_m1.sum().sum())
        },
        'method2': {
            'description': 'AlimSayisi > 0',
            'density': density_m2,
            'ones_count': int(binary_m2.sum().sum())
        },
        'method3': {
            'description': f'Miktar >= {median_miktar:.0f}',
            'threshold': float(median_miktar),
            'density': density_m3,
            'ones_count': int(binary_m3.sum().sum())
        },
        'method4': {
            'description': f'TotalScore >= {median_totalscore:.0f}',
            'threshold': float(median_totalscore),
            'density': density_m4,
            'ones_count': int(binary_m4.sum().sum())
        }
    })
    
    print()

# ==========================================
# 5. METHOD KARŞILAŞTIRMASI
# ==========================================

print("📊 Method Karşılaştırma Analizi...\n")

for info in binary_info:
    size = info['size']
    print(f"   {size}:")
    
    # Method 1 vs Method 2
    if info['method1']['density'] == info['method2']['density']:
        print(f"      ⚠️ Method 1 ve Method 2 aynı! (Her ikisi de {info['method1']['density']:.2f}%)")
        print(f"         → Miktar > 0 ⇔ AlimSayisi > 0 (Her alımda miktar var)")
    else:
        print(f"      ℹ️ Method 1 ({info['method1']['density']:.2f}%) ≠ Method 2 ({info['method2']['density']:.2f}%)")
    
    # Method 3 vs Method 1
    reduction_m3 = ((info['method1']['density'] - info['method3']['density']) / info['method1']['density'] * 100) if info['method1']['density'] > 0 else 0
    print(f"      📉 Method 3: {reduction_m3:.1f}% azalma (Threshold etkisi)")
    
    # Method 4 vs Method 1
    reduction_m4 = ((info['method1']['density'] - info['method4']['density']) / info['method1']['density'] * 100) if info['method1']['density'] > 0 else 0
    print(f"      📉 Method 4: {reduction_m4:.1f}% azaltıalma (TotalScore threshold)")
    
    print()

# ==========================================
# 6. ADIM 2 RAPORU
# ==========================================

print("📝 ADIM 2 Raporu hazırlanıyor...\n")

rapor = f"""
# TEKSTİL ADIM 2 RAPORU - SUB-MATRİS VE BINARY CONVERSION

**Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## TEST BOYUTLARI

{len(test_sizes)} farklı boyut: {', '.join([f'{r}×{c}' for r, c in test_sizes])}

## RAW SUB-MATRİSLER

| Boyut | Miktar Yoğunluk | AlimSayisi Yoğunluk | TotalScore Yoğunluk |
|-------|-----------------|---------------------|---------------------|
"""

for info in raw_matrices_info:
    rapor += f"| {info['size']} | {info['miktar_density']:.2f}% | {info['alimsayisi_density']:.2f}% | {info['totalscore_density']:.2f}% |\n"

rapor += """
## 4 BINARY METHOD

### Method 1: Miktar > 0
Basit binary dönüşüm. Herhangi bir miktar varsa 1, yoksa 0.

### Method 2: AlimSayisi > 0
Alım sıklığı bazlı. En az 1 kez alınmışsa 1, yoksa 0.

### Method 3: Miktar >= Median
Threshold bazlı (MovieLens tarzı). Sadece median üzeri alımlar 1.

### Method 4: TotalScore >= Median ✨ YENİ
Miktar × AlimSayisi kombinasyonu. Hem miktar hem sıklık dikkate alınır.

## BINARY YOĞUNLUKLARı

| Boyut | Method 1 | Method 2 | Method 3 | Method 4 |
|-------|----------|----------|----------|----------|
"""

for info in binary_info:
    rapor += f"| {info['size']} | {info['method1']['density']:.2f}% | {info['method2']['density']:.2f}% | {info['method3']['density']:.2f}% | {info['method4']['density']:.2f}% |\n"

rapor += """
## ÖNEMLİ BULGULAR

"""

# Method 1 vs 2 karşılaştırması
all_same = all(info['method1']['density'] == info['method2']['density'] for info in binary_info)
if all_same:
    rapor += """
### Method 1 = Method 2

**Bulgu:** Tüm boyutlarda Method 1 ve Method 2 **aynı sonucu** verdi.

**Sebep:** Her alımda miktar bilgisi var (Miktar > 0 ⇔ AlimSayisi > 0).

**Sonuç:** Tekstil veri setinde "Miktar olmadan alım" yok. Her transactionda hem miktar hem alım sayısı mevcut.

"""

# Threshold etkisi
rapor += """
### Threshold Etkisi (Method 3 ve 4)

Method 3 ve 4, median threshold kullanarak daha seçici davranıyor:

"""

for info in binary_info:
    reduction_m3 = ((info['method1']['density'] - info['method3']['density']) / info['method1']['density'] * 100) if info['method1']['density'] > 0 else 0
    reduction_m4 = ((info['method1']['density'] - info['method4']['density']) / info['method1']['density'] * 100) if info['method1']['density'] > 0 else 0
    
    rapor += f"- **{info['size']}:** Method 3 → {reduction_m3:.1f}% azalma, Method 4 → {reduction_m4:.1f}% azalma\n"

rapor += f"""
## OLUŞTURULAN DOSYALAR

### Raw Matrisler (9 dosya)
{len(test_sizes)} boyut × 3 pivot tip = 9 raw matris

### Binary Matrisler (12 dosya)
{len(test_sizes)} boyut × 4 method = **12 binary matris**

**Toplam:** {len(test_sizes) * 3 + len(test_sizes) * 4} = **21 dosya**

## SONRAKİ ADIM

ADIM 3: RMVC Hesaplama (V2 - Hocanın metodu)
- 12 binary matris
- Her biri için üyelik matrisi
- Skor hesaplama
"""

with open('Textile_data/reports/ADIM2_BinaryConversion_Raporu.md', 'w', encoding='utf-8') as f:
    f.write(rapor)

print("   ✅ ADIM2_BinaryConversion_Raporu.md\n")

# JSON kaydet (makale için)
with open('Textile_data/outputs/binary_matrices/binary_conversion_summary.json', 'w', encoding='utf-8') as f:
    json.dump({
        'test_sizes': [{'rows': r, 'cols': c} for r, c in test_sizes],
        'raw_matrices': raw_matrices_info,
        'binary_info': binary_info,
        'timestamp': datetime.now().isoformat()
    }, f, indent=2)

print("   ✅ binary_conversion_summary.json\n")

# ==========================================
# ÖZET
# ==========================================

print("="*100)
print("✅ ADIM 2 TAMAMLANDI!")
print("="*100)
print(f"\nOluşturulan Matrisler:")
print(f"  📁 Raw Sub-Matrisler: {len(test_sizes) * 3} adet ({len(test_sizes)} boyut × 3 pivot)")
print(f"  🔄 Binary Matrisler: {len(test_sizes) * 4} adet ({len(test_sizes)} boyut × 4 method)")
print(f"  📊 Toplam: {len(test_sizes) * 7} matris")

print(f"\n4 Method:")
print(f"  1. Method 1: Miktar > 0")
print(f"  2. Method 2: AlimSayisi > 0")
print(f"  3. Method 3: Miktar >= Median (Threshold)")
print(f"  4. Method 4: TotalScore >= Median (Miktar×AlimSayisi) ✨")

print(f"\nÖnemli Bulgu:")
if all_same:
    print(f"  ⚠️ Method 1 = Method 2 (Tüm boyutlarda aynı!)")

print(f"\nSonraki Adım: ADIM 3 - RMVC Hesaplama (12 test)")
print(f"\nBitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)
