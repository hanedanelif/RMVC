# -*- coding: utf-8 -*-
"""
Example 1 - MAKALE İLE BİREBİR KARŞILAŞTIRMA
=============================================
Makaledeki Example 1 ile tam karşılaştırma.

Makaleden:
U = {1, 2, 3, 4, 5}
E = {e1, e2, e3, e4}
Φ(e1) = {1, 2, 3, 5}
Φ(e2) = {2, 4, 5}
Φ(e3) = {1, 3, 4}
Φ(e4) = {1, 2, 5}
"""

import pandas as pd
import numpy as np
from fractions import Fraction

print("="*80)
print("EXAMPLE 1 - MAKALE İLE BİREBİR KARŞILAŞTIRMA")
print("="*80)

# Makaleden direkt tanımlama
U = {'1', '2', '3', '4', '5'}
E_named = {
    'e1': {'1', '2', '3', '5'},
    'e2': {'2', '4', '5'},
    'e3': {'1', '3', '4'},
    'e4': {'1', '2', '5'}
}

print("\n📌 MAKALE TANIMI:")
print(f"   U = {sorted(U)}")
print(f"   |U| = {len(U)}")
print(f"\n   Parametre kümeleri:")
for param, members in sorted(E_named.items()):
    print(f"   Φ({param}) = {sorted(members)}")

# Makaledeki delta fonksiyonu (BREAK ile!)
def delta_function_paper(e_i, E_named, U):
    """
    Makaledeki delta fonksiyonu - BREAK ile!
    Her (u,v) çifti için sadece BİR KEZ sayar.
    """
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    
    results = {}
    for u in not_in_phi:
        total_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            for e_j_name, e_j_set in E_named.items():
                if pair.issubset(e_j_set):
                    total_sum += 1
                    break  # MAKALE: BU BREAK VAR!
        results[u] = total_sum
    return results

# Benim delta fonksiyonum (BREAK yok!)
def delta_function_no_break(e_i, E_named, U):
    """
    BREAK olmadan delta fonksiyonu.
    Her (u,v) çifti için TÜM kümeleri sayar.
    """
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    
    results = {}
    for u in not_in_phi:
        total_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            for e_j_name, e_j_set in E_named.items():
                if pair.issubset(e_j_set):
                    total_sum += 1
                    # BREAK YOK!
        results[u] = total_sum
    return results

print("\n" + "="*80)
print("DELTA FONKSİYONU KARŞILAŞTIRMASI")
print("="*80)

m = len(E_named)

print("\n📊 e1 için delta hesabı:")
print(f"   Φ(e1) = {sorted(E_named['e1'])}")
print(f"   e1'de OLMAYAN: {sorted(U - E_named['e1'])}")
print(f"   γ = |Φ(e1)| × (m-1) = {len(E_named['e1'])} × {m-1} = {len(E_named['e1']) * (m-1)}")

delta_paper = delta_function_paper('e1', E_named, U)
delta_no_break = delta_function_no_break('e1', E_named, U)

print(f"\n   BREAK ile (MAKALE): δ(4, e1) = {delta_paper}")
print(f"   BREAK olmadan:      δ(4, e1) = {delta_no_break}")

# Detaylı hesap göster
print("\n   Detaylı hesap (u=4, e1 için):")
print("   v ∈ Φ(e1) için {4,v} çiftinin hangi kümelerde olduğu:")
for v in sorted(E_named['e1']):
    pair = {'4', v}
    found_in = []
    for e_j, e_j_set in sorted(E_named.items()):
        if pair.issubset(e_j_set):
            found_in.append(e_j)
    print(f"      {{4, {v}}} → {found_in if found_in else 'HİÇBİR YERDE'}")


# Üyelik matrisi oluştur
print("\n" + "="*80)
print("ÜYELİK MATRİSİ (MAKALE YÖNTEMİ - BREAK İLE)")
print("="*80)

def create_membership_matrix_paper(E_named, U):
    """Makaledeki yöntemle (break ile) üyelik matrisi."""
    m = len(E_named)
    membership_matrix = {}
    
    for e_i in sorted(E_named.keys()):
        phi_e_i = E_named[e_i]
        delta_results = delta_function_paper(e_i, E_named, U)
        
        gamma = len(phi_e_i) * (m - 1)
        
        membership_matrix[e_i] = {}
        
        for u in sorted(U):
            if u in phi_e_i:
                membership_matrix[e_i][u] = Fraction(1, 1)
            else:
                if gamma > 0 and u in delta_results:
                    delta_val = delta_results[u]
                    membership_matrix[e_i][u] = Fraction(delta_val, gamma)
                else:
                    membership_matrix[e_i][u] = Fraction(0, 1)
    
    return membership_matrix

mm_paper = create_membership_matrix_paper(E_named, U)

# Matrisi göster
print("\n📊 Hesaplanan Üyelik Matrisi (Kesirli):")
print("\n        ", end="")
for u in sorted(U):
    print(f"{u:>8}", end="")
print()

for e_i in sorted(mm_paper.keys()):
    print(f"   {e_i}  ", end="")
    for u in sorted(U):
        val = mm_paper[e_i][u]
        print(f"{str(val):>8}", end="")
    print()

# Makaledeki değerlerle karşılaştır
print("\n📌 MAKALEDEKİ TABLO 1:")
paper_values = {
    'e1': {'1': '1', '2': '1', '3': '1', '4': '1/3', '5': '1'},
    'e2': {'1': '5/9', '2': '1', '3': '1/3', '4': '1', '5': '1'},
    'e3': {'1': '1', '2': '4/9', '3': '1', '4': '1', '5': '4/9'},
    'e4': {'1': '1', '2': '1', '3': '4/9', '4': '1/3', '5': '1'}
}

print("\n        ", end="")
for u in sorted(U):
    print(f"{u:>8}", end="")
print()

for e_i in sorted(paper_values.keys()):
    print(f"   {e_i}  ", end="")
    for u in sorted(U):
        print(f"{paper_values[e_i][u]:>8}", end="")
    print()

# Karşılaştırma
print("\n📊 KARŞILAŞTIRMA (Hesaplanan vs Makale):")
all_match = True
for e_i in sorted(mm_paper.keys()):
    for u in sorted(U):
        calculated = str(mm_paper[e_i][u])
        expected = paper_values[e_i][u]
        match = "✓" if calculated == expected else "✗"
        if calculated != expected:
            all_match = False
            print(f"   {e_i}({u}): Hesaplanan={calculated}, Makale={expected} {match}")

if all_match:
    print("   ✅ TÜM DEĞERLER EŞLEŞİYOR!")

# Skorlar
print("\n" + "="*80)
print("SKORLAR")
print("="*80)

scores = {}
for u in sorted(U):
    total = Fraction(0, 1)
    for e_i in mm_paper:
        total += mm_paper[e_i][u]
    scores[u] = total

print("\n🏆 Eleman Skorları:")
for u, score in sorted(scores.items(), key=lambda x: float(x[1]), reverse=True):
    print(f"   Eleman {u}: {float(score):.4f} ({score})")

avg_score = np.mean([float(s) for s in scores.values()])
max_score = max([float(s) for s in scores.values()])

print(f"\n   Ortalama: {avg_score:.4f}")
print(f"   Max: {max_score:.4f}")

# Optimal seçimler
optimal = [u for u, s in scores.items() if float(s) == max_score]
print(f"   Optimal Seçim: {', '.join(sorted(optimal))}")
