# -*- coding: utf-8 -*-
"""
TEKSTİL - STEP 2 GÜNCELLEMEE: Kare Matrisler Eklendi
=====================================================
10×10, 20×20, 50×50 kare matrisleri ekle
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

print("="*100)
print("TEKSTİL - KARE MATRİSLER EKLENİYOR (10×10, 20×20, 50×50)")
print("="*100)
print(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ==========================================
# SORTED PİVOTLARI YÜKLE
# ==========================================

print("📁 Sıralanmış pivot tablolar yükleniyor...\n")

miktar_sorted = pd.read_csv('Textile_data/Firma_Urun_Miktar_Yogun_Sirali.csv', index_col=0)
alimsayisi_sorted = pd.read_csv('Textile_data/Firma_Urun_AlimSayisi_Yogun_Sirali.csv', index_col=0)
totalscore_sorted = pd.read_csv('Textile_data/Firma_Urun_TotalScore_Yogun_Sirali.csv', index_col=0)

print(f"   ✅ Matrisler yüklendi\n")

# ==========================================
# YENİ KARE BOYUTLAR
# ==========================================

new_sizes = [(10, 10), (20, 20), (50, 50)]

print(f"🎯 Yeni Kare Boyutlar: {', '.join([f'{r}×{c}' for r, c in new_sizes])}\n")

# ==========================================
# SUB-MATRİSLERİ KES VE KAYDET
# ==========================================

print("✂️ Kare sub-matrisler kesiliyor...\n")

raw_matrices_info = []

for rows, cols in new_sizes:
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
# BINARY CONVERSION - 4 METHOD
# ==========================================

print("🔄 Binary conversion (4 Method) - Kare Matrisler...\n")

binary_info = []

for rows, cols in new_sizes:
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
    median_miktar = miktar_raw[miktar_raw > 0].values.flatten()
    median_miktar = np.median(median_miktar) if len(median_miktar) > 0 else 0
    
    binary_m3 = (miktar_raw >= median_miktar).astype(int) if median_miktar > 0 else (miktar_raw > 0).astype(int)
    filename_m3 = f'Textile_data/outputs/binary_matrices/textile_{rows}x{cols}_method3.csv'
    binary_m3.to_csv(filename_m3)
    
    density_m3 = (binary_m3.sum().sum() / binary_m3.size) * 100
    print(f"      ✅ Method 3 (Miktar >= {median_miktar:.0f}): {density_m3:.2f}% yoğunluk")
    
    # METHOD 4: TotalScore >= Median
    median_totalscore = totalscore_raw[totalscore_raw > 0].values.flatten()
    median_totalscore = np.median(median_totalscore) if len(median_totalscore) > 0 else 0
    
    binary_m4 = (totalscore_raw >= median_totalscore).astype(int) if median_totalscore > 0 else (totalscore_raw > 0).astype(int)
    filename_m4 = f'Textile_data/outputs/binary_matrices/textile_{rows}x{cols}_method4.csv'
    binary_m4.to_csv(filename_m4)
    
    density_m4 = (binary_m4.sum().sum() / binary_m4.size) * 100
    print(f"      ✅ Method 4 (TotalScore >= {median_totalscore:.0f}): {density_m4:.2f}% yoğunluk")
    
    binary_info.append({
        'size': f'{rows}x{cols}',
        'method1': {'density': density_m1},
        'method2': {'density': density_m2},
        'method3': {'density': density_m3, 'threshold': float(median_miktar)},
        'method4': {'density': density_m4, 'threshold': float(median_totalscore)}
    })
    
    print()

# ==========================================
# ÖZET
# ==========================================

print("="*100)
print("✅ KARE MATRİSLER EKLENDİ!")
print("="*100)

print(f"\nYeni Eklenen:")
print(f"  📁 Raw Sub-Matrisler: {len(new_sizes) * 3} adet")
print(f"  🔄 Binary Matrisler: {len(new_sizes) * 4} adet")

print(f"\n📊 Toplam (Eski + Yeni):")
print(f"  • Raw: {(3 + len(new_sizes)) * 3} = {(3 + len(new_sizes)) * 3} matris")
print(f"  • Binary: {(3 + len(new_sizes)) * 4} = {(3 + len(new_sizes)) * 4} matris")

print(f"\nYoğunluk Özeti (Kare Matrisler):")
for info in binary_info:
    print(f"  {info['size']}: {info['method1']['density']:.2f}%")

print(f"\nSonraki: RMVC + İteratif (12 yeni test)")
print(f"\nBitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*100)
