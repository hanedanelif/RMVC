# -*- coding: utf-8 -*-
"""
RMVC İteratif Analiz - Example.1..xlsx
======================================
Arayüzle karşılaştırma için detaylı analiz.
"""

import pandas as pd
import numpy as np
from fractions import Fraction

print("="*80)
print("RMVC İTERATİF ANALİZ - Example.1..xlsx")
print("="*80)

# 1. Veriyi yükle
print("\n" + "="*80)
print("ADIM 1: VERİ YÜKLEME")
print("="*80)

df = pd.read_excel("Example.1..xlsx", index_col=0)
print("\n📊 Girdi Matrisi:")
print(df)
print(f"\n   Boyut: {df.shape[0]} satır × {df.shape[1]} sütun")
print(f"   Satırlar: {list(df.index)}")
print(f"   Sütunlar: {list(df.columns)}")

# NOT: Bu dosyada satırlar = parametreler (e1, e2, e3, e4)
# Sütunlar = elemanlar (1, 2, 3, 4, 5)
# Yani transpose gerekli!

print("\n⚠️ NOT: Bu dosyada:")
print("   - Satırlar = Parametreler (e1, e2, e3, e4)")
print("   - Sütunlar = Elemanlar (1, 2, 3, 4, 5)")
print("   - Yani TRANSPOSE gerekli!")

# 2. Soft Set'e dönüştür (rows_are_params=True)
print("\n" + "="*80)
print("ADIM 2: SOFT SET DÖNÜŞÜMÜ")
print("="*80)

# Satırlar parametre olduğu için transpose yapıyoruz
df_t = df.T  # Transpose: şimdi satırlar=elemanlar, sütunlar=parametreler

# U = Evrensel küme (elemanlar: 1, 2, 3, 4, 5)
U = set(df_t.index.astype(str))
print(f"\n   U (Evrensel Küme - Elemanlar) = {sorted(U)}")
print(f"   |U| = {len(U)}")

# E = Parametre kümesi (e1, e2, e3, e4)
E_named = {}
for col in df_t.columns:
    param_name = str(col)
    members = set(df_t.index[df_t[col] > 0].astype(str))
    E_named[param_name] = members

print(f"\n   E (Parametre Kümesi) = {list(E_named.keys())}")
print(f"   |E| = {len(E_named)}")

print("\n   Parametre kümeleri:")
for param, members in E_named.items():
    print(f"   Φ({param}) = {sorted(members)}")

# 3. Delta fonksiyonu ve Üyelik Matrisi
print("\n" + "="*80)
print("ADIM 3: ÜYELİK MATRİSİ HESAPLAMA")
print("="*80)

def delta_function(e_i, E_named, U):
    """Delta fonksiyonu - birlikte görülme sayısı."""
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    
    results = {}
    for u in not_in_phi:
        delta_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            for e_j, phi_e_j in E_named.items():
                if pair.issubset(phi_e_j):
                    delta_sum += 1
        results[u] = delta_sum
    return results

def create_membership_matrix(E_named, U):
    """Üyelik matrisi oluştur."""
    m = len(E_named)
    membership_matrix = {}
    
    for e_i in E_named.keys():
        phi_e_i = E_named[e_i]
        delta_results = delta_function(e_i, E_named, U)
        
        # gamma = |Φ(e_i)| × (m - 1)
        gamma = len(phi_e_i) * (m - 1)
        
        membership_matrix[e_i] = {}
        
        for u in U:
            if u in phi_e_i:
                membership_matrix[e_i][u] = Fraction(1, 1)
            else:
                if gamma > 0 and u in delta_results:
                    delta_val = delta_results[u]
                    membership_matrix[e_i][u] = Fraction(delta_val, gamma)
                else:
                    membership_matrix[e_i][u] = Fraction(0, 1)
    
    return membership_matrix

def matrix_to_df(membership_matrix, U):
    """Matrisi DataFrame'e çevir (sıralı)."""
    sorted_U = sorted(U)
    sorted_E = sorted(membership_matrix.keys())
    data = {}
    for e_i in sorted_E:
        data[e_i] = {u: float(membership_matrix[e_i][u]) for u in sorted_U}
    df = pd.DataFrame(data)
    df.index = sorted_U
    return df

def matrix_to_df_fraction(membership_matrix, U):
    """Matrisi kesirli olarak DataFrame'e çevir."""
    sorted_U = sorted(U)
    sorted_E = sorted(membership_matrix.keys())
    data = {}
    for e_i in sorted_E:
        data[e_i] = {u: str(membership_matrix[e_i][u]) for u in sorted_U}
    df = pd.DataFrame(data)
    df.index = sorted_U
    return df

def calculate_scores(membership_matrix, U):
    """Skorları hesapla."""
    scores = {}
    for u in U:
        total = Fraction(0, 1)
        for e_i in membership_matrix:
            total += membership_matrix[e_i].get(u, Fraction(0, 1))
        scores[u] = total
    return scores

# İlk üyelik matrisi
membership_matrix = create_membership_matrix(E_named, U)
mm_df = matrix_to_df(membership_matrix, U)
mm_df_frac = matrix_to_df_fraction(membership_matrix, U)

print("\n📊 Üyelik Matrisi (Ondalıklı):")
print(mm_df.to_string())

print("\n📊 Üyelik Matrisi (Kesirli):")
print(mm_df_frac.to_string())

# Skorlar
scores = calculate_scores(membership_matrix, U)
print("\n📊 Skorlar (Başlangıç):")
for u in sorted(U):
    score = scores[u]
    print(f"   Eleman {u}: {float(score):.4f} ({score})")

avg_score = np.mean([float(s) for s in scores.values()])
max_score = max([float(s) for s in scores.values()])
print(f"\n   Ortalama Skor: {avg_score:.4f}")
print(f"   Max Skor: {max_score:.4f}")

# 4. İteratif Analiz
print("\n" + "="*80)
print("ADIM 4: İTERATİF ANALİZ")
print("="*80)

iteration = 0
max_iterations = 10

while iteration < max_iterations:
    iteration += 1
    print(f"\n{'='*40}")
    print(f"İTERASYON {iteration}")
    print(f"{'='*40}")
    
    # Ondalıklı değerleri bul
    fractional_values = []
    for e_i in membership_matrix:
        for u in U:
            val = float(membership_matrix[e_i][u])
            if 0 < val < 1:
                fractional_values.append(val)
    
    print(f"\n   Ondalıklı değer sayısı: {len(fractional_values)}")
    
    if len(fractional_values) == 0:
        print("   ✅ Tüm değerler 0 veya 1. İterasyon tamamlandı!")
        break
    
    # Eşik hesapla
    threshold = np.mean(fractional_values)
    print(f"   Ondalıklı değerler: {sorted(set(fractional_values))}")
    print(f"   Eşik (ortalama): {threshold:.4f}")
    
    # Eşik uygula
    print(f"\n   Eşik uygulanıyor (>= {threshold:.4f} → 1)...")
    
    changes = 0
    for e_i in sorted(membership_matrix.keys()):
        for u in sorted(U):
            val = float(membership_matrix[e_i][u])
            if 0 < val < 1:
                if val >= threshold:
                    new_val = 1
                else:
                    new_val = 0
                old_val = val
                membership_matrix[e_i][u] = Fraction(new_val, 1)
                changes += 1
                print(f"      Eleman {u} @ {e_i}: {old_val:.4f} → {new_val}")
    
    print(f"\n   Değiştirilen hücre sayısı: {changes}")
    
    # Yeni matrisi göster
    mm_df = matrix_to_df(membership_matrix, U)
    print(f"\n📊 Üyelik Matrisi (İterasyon {iteration} sonrası):")
    print(mm_df.to_string())
    
    # Yeni skorlar
    scores = calculate_scores(membership_matrix, U)
    print(f"\n📊 Güncel Skorlar:")
    for u in sorted(U):
        print(f"   Eleman {u}: {float(scores[u]):.4f}")

# 5. Final Sonuçları
print("\n" + "="*80)
print("ADIM 5: FİNAL SONUÇLARI")
print("="*80)

print("\n📊 Final Üyelik Matrisi (Binary):")
print(mm_df.to_string())

print("\n🏆 Final Sıralama:")
final_scores = calculate_scores(membership_matrix, U)
sorted_scores = sorted(final_scores.items(), key=lambda x: (float(x[1]), x[0]), reverse=True)

for rank, (u, score) in enumerate(sorted_scores, 1):
    status = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
    print(f"   {status} {rank}. Eleman {u}: {float(score):.4f}")

# Optimal seçim (berabere olanları da göster)
max_score = float(sorted_scores[0][1])
optimal_elements = [u for u, s in final_scores.items() if float(s) == max_score]

print("\n" + "="*80)
print("ARAYÜZ KARŞILAŞTIRMASI İÇİN ÖZET")
print("="*80)
print(f"\n   Toplam Eleman |U| = {len(U)}")
print(f"   Toplam Parametre |E| = {len(E_named)}")
print(f"   Ortalama Skor: {np.mean([float(s) for s in final_scores.values()]):.4f}")
print(f"   Max Skor: {max_score:.4f}")
print(f"   Optimal Seçim: {', '.join(sorted(optimal_elements))}")
