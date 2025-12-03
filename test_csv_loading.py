# -*- coding: utf-8 -*-
"""
CSV dosyasını test et - hangi ayarlarla yüklenmeli?
"""

import pandas as pd
from fractions import Fraction

# CSV dosyasını oku
df = pd.read_csv(r"C:\Users\user\Downloads\RMVC\RMVC_Firma_Urun_Matrisi_10x10_Binary.csv", index_col=0)

print("="*60)
print("DOSYA YAPISI ANALİZİ")
print("="*60)

print(f"\nOrijinal DataFrame:")
print(df)
print(f"\nBoyut: {df.shape}")
print(f"Satırlar (index): {list(df.index)}")
print(f"Sütunlar: {list(df.columns)}")

# Bizim uygulamamızın beklediği format:
# Satırlar = Elemanlar (U) - yani ürünler (1,2,3...)
# Sütunlar = Parametreler (E) - yani firmalar (e1, e2...)

# Bu dosyada:
# Satırlar = Firmalar (e1, e2...) 
# Sütunlar = Ürünler (1, 2, 3...)

print("\n" + "="*60)
print("YORUM")
print("="*60)

print("""
Bu CSV dosyasında:
- Satırlar = Firmalar (e1, e2, ..., e10) → Bunlar PARAMETRELER
- Sütunlar = Ürünler (1, 2, ..., 10) → Bunlar ELEMANLAR

Hocanın kodu bu formatı direkt kullanıyor:
- E = {e1, e2, ..., e10} (firmalar = parametre kümeleri)
- U = {1, 2, ..., 10} (ürünler = evrensel küme)

Bizim uygulamamız varsayılan olarak:
- Satırlar = Elemanlar
- Sütunlar = Parametreler

Bu yüzden TRANSPOSE GEREKLİ DEĞİL!
Çünkü dosyada zaten:
- Satırlar = e1, e2... (parametreler olarak okunacak)
- Sütunlar = 1, 2... (elemanlar olarak okunacak)

AMA BEKLEYİN - uygulamamız satırları eleman, sütunları parametre olarak okuyor.
Bu dosyada satırlar firma (parametre), sütunlar ürün (eleman).

Yani TRANSPOSE LAZIM!
""")

print("\n" + "="*60)
print("TRANSPOSE SONRASI")
print("="*60)

df_t = df.T
print(f"\nTranspose DataFrame:")
print(df_t)
print(f"\nBoyut: {df_t.shape}")
print(f"Satırlar (index): {list(df_t.index)}")
print(f"Sütunlar: {list(df_t.columns)}")

print("""
Transpose sonrası:
- Satırlar = Ürünler (1, 2, ..., 10) → ELEMANLAR (U)
- Sütunlar = Firmalar (e1, e2, ..., e10) → PARAMETRELER (E)

Bu bizim uygulamamızın beklediği format!
""")

# Şimdi hocanın yaklaşımıyla hesaplayalım
print("\n" + "="*60)
print("HOCANIN YAKLAŞIMIYLA HESAPLAMA (m=10, boş kümeler dahil)")
print("="*60)

# Soft Set oluştur - TRANSPOSE OLMADAN (hocanın formatı)
U = set(str(c) for c in df.columns)  # Ürünler: 1-10
E_named = {}
for firma in df.index:
    products = set(str(c) for c in df.columns if df.loc[firma, c] > 0)
    E_named[firma] = products

print(f"\nU = {sorted(U, key=lambda x: int(x))}")
print(f"m = {len(E_named)} (toplam parametre/firma sayısı)")
print("\nΦ kümeleri:")
for e, s in E_named.items():
    status = "⚠️ BOŞ" if len(s) == 0 else ""
    print(f"  Φ({e}) = {sorted(s, key=lambda x: int(x)) if s else '∅'} {status}")

# Delta ve üyelik hesapla
def delta_function(e_name, E_named, U):
    e_set = E_named[e_name]
    not_in_e_set = U - e_set
    results = {}
    for element in not_in_e_set:
        total_sum = 0
        for other_element in e_set:
            pair = {element, other_element}
            for s in E_named.values():
                if pair.issubset(s):
                    total_sum += 1
        results[element] = total_sum
    return results

def create_membership_matrix(E_named, U):
    membership_matrix = {}
    m = len(E_named)
    for e_key in E_named.keys():
        membership_matrix[e_key] = {}
        e_set = E_named[e_key]
        if len(e_set) == 0:
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

membership_matrix = create_membership_matrix(E_named, U)

# Skorları hesapla
scores = {u: Fraction(0) for u in U}
for e_key in membership_matrix:
    for u in U:
        scores[u] += membership_matrix[e_key][u]

print("\n" + "="*60)
print("SONUÇLAR (Hocanın yaklaşımı)")
print("="*60)

sorted_scores = sorted(scores.items(), key=lambda x: (-float(x[1]), x[0]))
print("\n| Sıra | Ürün | Skor |")
print("|------|------|------|")
for rank, (u, score) in enumerate(sorted_scores, 1):
    print(f"| {rank:>4} | {u:>4} | {float(score):.4f} |")

print(f"\n🏆 KAZANAN: Ürün {sorted_scores[0][0]} (Skor: {float(sorted_scores[0][1]):.4f})")
