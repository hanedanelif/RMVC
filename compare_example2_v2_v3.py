# -*- coding: utf-8 -*-
"""
Example 2 - V2 vs V3 KARŞILAŞTIRMA
===================================
Makaledeki Example 2 için V2 ve V3 sonuçlarını karşılaştır.
"""

import pandas as pd
import numpy as np
from fractions import Fraction

print("="*80)
print("EXAMPLE 2 - V2 vs V3 KARŞILAŞTIRMA")
print("="*80)

# Veri yükle
df = pd.read_excel("Example.2..xlsx", index_col=0)
print("\n📊 Girdi Matrisi:")
print(df)
print(f"\n   Boyut: {df.shape[0]} parametre × {df.shape[1]} eleman")

# Soft Set tanımı (transpose - satırlar parametre)
df_t = df.T
U = set(df_t.index.astype(str))
E_named = {}
for col in df_t.columns:
    param_name = str(col)
    members = set(df_t.index[df_t[col] > 0].astype(str))
    E_named[param_name] = members

print(f"\n   U = {sorted(U)}")
print(f"   |U| = {len(U)}, |E| = {len(E_named)}")
print("\n   Parametre kümeleri:")
for param, members in sorted(E_named.items()):
    print(f"   Φ({param}) = {sorted(members)}")

# ============================================================
# V2 DELTA (ESKİ - TÜM KÜMELER DAHİL)
# ============================================================
def delta_v2(e_i, E_named, U):
    """V2: Tüm kümeler dahil."""
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

# ============================================================
# V3 DELTA (YENİ - KENDİ KÜMESİ HARİÇ)
# ============================================================
def delta_v3(e_i, E_named, U):
    """V3: Kendi kümesi hariç."""
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    results = {}
    for u in not_in_phi:
        delta_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            for e_j, phi_e_j in E_named.items():
                if e_j != e_i:  # KENDİ KÜMESİ HARİÇ!
                    if pair.issubset(phi_e_j):
                        delta_sum += 1
        results[u] = delta_sum
    return results

def create_membership_matrix(E_named, U, delta_func):
    """Üyelik matrisi oluştur."""
    m = len(E_named)
    membership_matrix = {}
    
    for e_i in sorted(E_named.keys()):
        phi_e_i = E_named[e_i]
        delta_results = delta_func(e_i, E_named, U)
        gamma = len(phi_e_i) * (m - 1)
        
        membership_matrix[e_i] = {}
        for u in sorted(U):
            if u in phi_e_i:
                membership_matrix[e_i][u] = Fraction(1, 1)
            else:
                if gamma > 0 and u in delta_results:
                    membership_matrix[e_i][u] = Fraction(delta_results[u], gamma)
                else:
                    membership_matrix[e_i][u] = Fraction(0, 1)
    
    return membership_matrix

def calculate_scores(membership_matrix, U):
    """Skorları hesapla."""
    scores = {}
    for u in sorted(U):
        total = Fraction(0, 1)
        for e_i in membership_matrix:
            total += membership_matrix[e_i].get(u, Fraction(0, 1))
        scores[u] = total
    return scores

def print_matrix(mm, title):
    """Matrisi yazdır."""
    print(f"\n{title}")
    print("\n        ", end="")
    for u in sorted(U):
        print(f"{u:>8}", end="")
    print()
    
    for e_i in sorted(mm.keys()):
        print(f"   {e_i}  ", end="")
        for u in sorted(U):
            val = mm[e_i][u]
            print(f"{str(val):>8}", end="")
        print()

# V2 hesapla
print("\n" + "="*80)
print("V2 SONUÇLARI (TÜM KÜMELER DAHİL)")
print("="*80)
mm_v2 = create_membership_matrix(E_named, U, delta_v2)
print_matrix(mm_v2, "📊 V2 Üyelik Matrisi (Kesirli):")

scores_v2 = calculate_scores(mm_v2, U)
print("\n🏆 V2 Skorları:")
for u, score in sorted(scores_v2.items(), key=lambda x: float(x[1]), reverse=True):
    print(f"   Eleman {u}: {float(score):.4f} ({score})")

# V3 hesapla
print("\n" + "="*80)
print("V3 SONUÇLARI (KENDİ KÜMESİ HARİÇ)")
print("="*80)
mm_v3 = create_membership_matrix(E_named, U, delta_v3)
print_matrix(mm_v3, "📊 V3 Üyelik Matrisi (Kesirli):")

scores_v3 = calculate_scores(mm_v3, U)
print("\n🏆 V3 Skorları:")
for u, score in sorted(scores_v3.items(), key=lambda x: float(x[1]), reverse=True):
    print(f"   Eleman {u}: {float(score):.4f} ({score})")

# Karşılaştırma
print("\n" + "="*80)
print("V2 vs V3 KARŞILAŞTIRMA")
print("="*80)

differences = []
for e_i in sorted(mm_v2.keys()):
    for u in sorted(U):
        v2_val = mm_v2[e_i][u]
        v3_val = mm_v3[e_i][u]
        if v2_val != v3_val:
            differences.append({
                'hücre': f"{e_i}({u})",
                'v2': str(v2_val),
                'v3': str(v3_val),
                'v2_float': float(v2_val),
                'v3_float': float(v3_val)
            })

if differences:
    print(f"\n⚠️ {len(differences)} FARKLI HÜCRE TESPİT EDİLDİ:\n")
    print(f"   {'Hücre':<12} {'V2':>10} {'V3':>10} {'Fark':>10}")
    print("   " + "-"*44)
    for d in differences:
        fark = d['v3_float'] - d['v2_float']
        print(f"   {d['hücre']:<12} {d['v2']:>10} {d['v3']:>10} {fark:>+10.4f}")
else:
    print("\n✅ V2 ve V3 AYNI SONUÇLARI VERİYOR!")

# Skor karşılaştırması
print("\n📊 SKOR KARŞILAŞTIRMASI:")
print(f"\n   {'Eleman':<8} {'V2 Skor':>12} {'V3 Skor':>12} {'Fark':>10} {'Sıralama Değ.':>15}")
print("   " + "-"*60)

# Sıralama
rank_v2 = {u: i+1 for i, (u, _) in enumerate(sorted(scores_v2.items(), key=lambda x: float(x[1]), reverse=True))}
rank_v3 = {u: i+1 for i, (u, _) in enumerate(sorted(scores_v3.items(), key=lambda x: float(x[1]), reverse=True))}

for u in sorted(U):
    v2_score = float(scores_v2[u])
    v3_score = float(scores_v3[u])
    fark = v3_score - v2_score
    rank_change = rank_v2[u] - rank_v3[u]
    
    if rank_change > 0:
        rank_str = f"↑ +{rank_change}"
    elif rank_change < 0:
        rank_str = f"↓ {rank_change}"
    else:
        rank_str = "="
    
    print(f"   {u:<8} {v2_score:>12.4f} {v3_score:>12.4f} {fark:>+10.4f} {rank_str:>15}")

# Optimal seçim
print("\n🏆 OPTİMAL SEÇİM:")
max_v2 = max(float(s) for s in scores_v2.values())
max_v3 = max(float(s) for s in scores_v3.values())
optimal_v2 = [u for u, s in scores_v2.items() if float(s) == max_v2]
optimal_v3 = [u for u, s in scores_v3.items() if float(s) == max_v3]

print(f"   V2: {', '.join(sorted(optimal_v2))} (Skor: {max_v2:.4f})")
print(f"   V3: {', '.join(sorted(optimal_v3))} (Skor: {max_v3:.4f})")

if optimal_v2 == optimal_v3:
    print("\n   ✅ AYNI OPTİMAL SEÇİM!")
else:
    print("\n   ⚠️ FARKLI OPTİMAL SEÇİM!")
