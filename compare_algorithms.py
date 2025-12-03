# -*- coding: utf-8 -*-
"""
İki algoritmanın karşılaştırması:
1. Hocanın kodu (boş kümeleri dahil eder)
2. Bizim kodumuz (boş kümeleri nasıl işliyor?)
"""

import pandas as pd
from fractions import Fraction

# CSV dosyasını oku - manuel olarak parse et
with open(r"C:\Users\user\Downloads\RMVC\RMVC_Firma_Urun_Matrisi_10x10_Binary.csv", 'r') as f:
    lines = f.readlines()

# Header
header = lines[0].strip().rstrip(',').split(',')
products = header[1:]  # İlk sütun FirmaID

# Data
data = {}
for line in lines[1:]:
    line = line.strip().rstrip(',')
    if not line:
        continue
    parts = line.split(',')
    firma = parts[0]
    values = [int(v) for v in parts[1:]]
    data[firma] = values

# DataFrame oluştur
df = pd.DataFrame(data, index=products).T
df.columns = [str(c) for c in df.columns]

print("="*80)
print("HAM VERİ")
print("="*80)
print(df)
print()

# Veriyi Soft Set formatına dönüştür
U = set(df.columns.astype(str))  # Ürünler: {'1', '2', ..., '10'}

# E_named: Her firma için ürün kümesi
E_named_all = {}  # Hocanın yaklaşımı: TÜM firmalar (boş olanlar dahil)
E_named_filtered = {}  # Bizim yaklaşım: Sadece en az 1 ürünü olanlar

for firma in df.index:
    products = set(df.columns[df.loc[firma] > 0].astype(str))
    E_named_all[firma] = products
    if len(products) > 0:  # Sadece boş olmayanları ekle
        E_named_filtered[firma] = products

print("="*80)
print("KÜME YAPISI")
print("="*80)
print(f"\nU (Evrensel Küme): {sorted(U, key=int)}")
print(f"\nToplam firma sayısı: {len(E_named_all)}")
print(f"Boş olmayan firma sayısı: {len(E_named_filtered)}")

print("\n--- Tüm Firmalar (Hocanın yaklaşımı) ---")
for e, s in E_named_all.items():
    status = "⚠️ BOŞ" if len(s) == 0 else ""
    print(f"  Φ({e}) = {sorted(s, key=int) if s else '∅'} {status}")

print("\n--- Filtrelenmiş Firmalar (Bizim yaklaşım) ---")
for e, s in E_named_filtered.items():
    print(f"  Φ({e}) = {sorted(s, key=int)}")

# ============================================
# DELTA FONKSİYONU
# ============================================

def delta_function(e_name, E_named, U):
    """Delta fonksiyonu - co-occurrence hesaplama"""
    e_set = E_named[e_name]
    not_in_e_set = U - e_set
    results = {}
    
    for element in not_in_e_set:
        total_sum = 0
        for other_element in e_set:
            pair = {element, other_element}
            # Tüm kümelerde bu çifti say
            for s in E_named.values():
                if pair.issubset(s):
                    total_sum += 1
        results[element] = total_sum
    return results

# ============================================
# ÜYELİK MATRİSİ HESAPLAMA
# ============================================

def create_membership_matrix(E_named, U):
    """Üyelik matrisi oluştur"""
    membership_matrix = {}
    m = len(E_named)  # Toplam küme sayısı
    
    for e_key in E_named.keys():
        membership_matrix[e_key] = {}
        e_set = E_named[e_key]
        
        if len(e_set) == 0:
            # Boş küme - tüm elemanlar için 0
            for u in U:
                membership_matrix[e_key][u] = Fraction(0)
            continue
            
        delta_results = delta_function(e_key, E_named, U)
        gamma = len(e_set) * (m - 1) if m > 1 else 1
        
        for u in U:
            if u in e_set:
                membership_matrix[e_key][u] = Fraction(1)
            else:
                delta_val = delta_results.get(u, 0)
                if gamma > 0:
                    membership_matrix[e_key][u] = Fraction(delta_val, gamma)
                else:
                    membership_matrix[e_key][u] = Fraction(0)
    
    return membership_matrix

# ============================================
# SKORLARI HESAPLA
# ============================================

def calculate_scores(membership_matrix, U):
    """Sütun toplamlarını hesapla"""
    scores = {u: Fraction(0) for u in U}
    for e_key in membership_matrix:
        for u in U:
            scores[u] += membership_matrix[e_key][u]
    return scores

# ============================================
# KARŞILAŞTIRMA
# ============================================

print("\n" + "="*80)
print("HOCANIN YAKLAŞIMI (Boş kümeler DAHİL, m=10)")
print("="*80)

matrix_hoca = create_membership_matrix(E_named_all, U)
scores_hoca = calculate_scores(matrix_hoca, U)

print(f"\nm (küme sayısı) = {len(E_named_all)}")
print(f"gamma örneği (e1 için): |Φ(e1)| × (m-1) = {len(E_named_all['e1'])} × {len(E_named_all)-1} = {len(E_named_all['e1']) * (len(E_named_all)-1)}")

print("\nSkorlar:")
sorted_hoca = sorted(scores_hoca.items(), key=lambda x: float(x[1]), reverse=True)
for rank, (u, score) in enumerate(sorted_hoca, 1):
    print(f"  {rank}. Ürün {u}: {float(score):.4f} ({score})")

print("\n" + "="*80)
print("BİZİM YAKLAŞIMIMIZ (Boş kümeler HARİÇ, m=7)")
print("="*80)

matrix_biz = create_membership_matrix(E_named_filtered, U)
scores_biz = calculate_scores(matrix_biz, U)

print(f"\nm (küme sayısı) = {len(E_named_filtered)}")
print(f"gamma örneği (e1 için): |Φ(e1)| × (m-1) = {len(E_named_filtered['e1'])} × {len(E_named_filtered)-1} = {len(E_named_filtered['e1']) * (len(E_named_filtered)-1)}")

print("\nSkorlar:")
sorted_biz = sorted(scores_biz.items(), key=lambda x: float(x[1]), reverse=True)
for rank, (u, score) in enumerate(sorted_biz, 1):
    print(f"  {rank}. Ürün {u}: {float(score):.4f} ({score})")

# ============================================
# FARK ANALİZİ
# ============================================

print("\n" + "="*80)
print("FARK ANALİZİ")
print("="*80)

print("\n| Ürün | Hoca Skoru | Bizim Skor | Fark |")
print("|------|------------|------------|------|")
for u in sorted(U, key=int):
    h = float(scores_hoca[u])
    b = float(scores_biz[u])
    diff = abs(h - b)
    print(f"| {u:>4} | {h:>10.4f} | {b:>10.4f} | {diff:.4f} |")

print("\n" + "="*80)
print("SIRALAMA KARŞILAŞTIRMASI")
print("="*80)

print("\n| Sıra | Hoca | Bizim |")
print("|------|------|-------|")
for i in range(len(sorted_hoca)):
    h_prod = sorted_hoca[i][0]
    b_prod = sorted_biz[i][0]
    match = "✅" if h_prod == b_prod else "❌"
    print(f"| {i+1:>4} | {h_prod:>4} | {b_prod:>5} | {match}")

print("\n" + "="*80)
print("SONUÇ")
print("="*80)
winner_hoca = sorted_hoca[0][0]
winner_biz = sorted_biz[0][0]
print(f"\nHocanın yaklaşımı kazanan: Ürün {winner_hoca}")
print(f"Bizim yaklaşım kazanan: Ürün {winner_biz}")

if winner_hoca == winner_biz:
    print("\n✅ AYNI SONUÇ! Kazanan aynı.")
else:
    print("\n⚠️ FARKLI SONUÇ! Kazananlar farklı.")
