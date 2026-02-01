# -*- coding: utf-8 -*-
"""
MAKALE FORMÜLÜNÜ DETAYLI ANALIZ
===============================
Makaledeki Θ_e1(4) hesabını satır satır takip et.

Makaleden:
Θ_e1(4) = 1/(4×3) × [δ_e2(4,j) + δ_e3(4,j) + δ_e4(4,j)], ∀j ∈ Φ(e1)

         = [0+1+0+1] + [1+0+1+0] + [0+0+0+0]
           ─────────────────────────────────
                       12
         = 4/12 = 1/3
"""

print("="*80)
print("MAKALE FORMÜLÜNÜ DETAYLI ANALİZ")
print("="*80)

# Tanımlar
U = {'1', '2', '3', '4', '5'}
E_named = {
    'e1': {'1', '2', '3', '5'},
    'e2': {'2', '4', '5'},
    'e3': {'1', '3', '4'},
    'e4': {'1', '2', '5'}
}

print("\n📌 Φ(e1) = {1, 2, 3, 5}")
print("📌 4 ∉ Φ(e1)")
print("📌 γ = |Φ(e1)| × (m-1) = 4 × 3 = 12")

print("\n" + "="*80)
print("MAKALE HESABI: Θ_e1(4)")
print("="*80)

print("""
Makaleden formül:
Θ_e1(4) = 1/(4×3) × [δ_e2(4,j) + δ_e3(4,j) + δ_e4(4,j)], ∀j ∈ Φ(e1)

j ∈ Φ(e1) = {1, 2, 3, 5} için:

δ_e2(4,1): {4,1} ⊆ Φ(e2)={2,4,5}? → 1∉{2,4,5} → HAYIR → 0
δ_e2(4,2): {4,2} ⊆ Φ(e2)={2,4,5}? → 2∈, 4∈ → EVET → 1
δ_e2(4,3): {4,3} ⊆ Φ(e2)={2,4,5}? → 3∉{2,4,5} → HAYIR → 0
δ_e2(4,5): {4,5} ⊆ Φ(e2)={2,4,5}? → 4∈, 5∈ → EVET → 1

δ_e3(4,1): {4,1} ⊆ Φ(e3)={1,3,4}? → 4∈, 1∈ → EVET → 1
δ_e3(4,2): {4,2} ⊆ Φ(e3)={1,3,4}? → 2∉{1,3,4} → HAYIR → 0
δ_e3(4,3): {4,3} ⊆ Φ(e3)={1,3,4}? → 4∈, 3∈ → EVET → 1
δ_e3(4,5): {4,5} ⊆ Φ(e3)={1,3,4}? → 5∉{1,3,4} → HAYIR → 0

δ_e4(4,1): {4,1} ⊆ Φ(e4)={1,2,5}? → 4∉{1,2,5} → HAYIR → 0
δ_e4(4,2): {4,2} ⊆ Φ(e4)={1,2,5}? → 4∉{1,2,5} → HAYIR → 0
δ_e4(4,3): {4,3} ⊆ Φ(e4)={1,2,5}? → 4∉{1,2,5} → HAYIR → 0
δ_e4(4,5): {4,5} ⊆ Φ(e4)={1,2,5}? → 4∉{1,2,5} → HAYIR → 0

Toplam: [0+1+0+1] + [1+0+1+0] + [0+0+0+0] = 2 + 2 + 0 = 4

Θ_e1(4) = 4/12 = 1/3 ✓

Makale de 1/3 diyor, DOĞRU!
""")

print("="*80)
print("ŞİMDİ e2(1) HESABI - MAKALE 5/9 DİYOR")
print("="*80)

print("\n📌 Φ(e2) = {2, 4, 5}")
print("📌 1 ∉ Φ(e2)")
print("📌 γ = |Φ(e2)| × (m-1) = 3 × 3 = 9")

print("""
j ∈ Φ(e2) = {2, 4, 5} için:

δ_e1(1,2): {1,2} ⊆ Φ(e1)={1,2,3,5}? → EVET → 1
δ_e1(1,4): {1,4} ⊆ Φ(e1)={1,2,3,5}? → 4∉ → HAYIR → 0
δ_e1(1,5): {1,5} ⊆ Φ(e1)={1,2,3,5}? → EVET → 1

δ_e3(1,2): {1,2} ⊆ Φ(e3)={1,3,4}? → 2∉ → HAYIR → 0
δ_e3(1,4): {1,4} ⊆ Φ(e3)={1,3,4}? → EVET → 1
δ_e3(1,5): {1,5} ⊆ Φ(e3)={1,3,4}? → 5∉ → HAYIR → 0

δ_e4(1,2): {1,2} ⊆ Φ(e4)={1,2,5}? → EVET → 1
δ_e4(1,4): {1,4} ⊆ Φ(e4)={1,2,5}? → 4∉ → HAYIR → 0
δ_e4(1,5): {1,5} ⊆ Φ(e4)={1,2,5}? → EVET → 1

Toplam: [1+0+1] + [0+1+0] + [1+0+1] = 2 + 1 + 2 = 5

Θ_e2(1) = 5/9 ✓

AMA BENİM KODUM 1/3 = 3/9 VERİYOR!?
""")

print("="*80)
print("SORUN: BREAK KULLANIMI!")
print("="*80)

print("""
Makaledeki KOD:

    for other_e_set in E_named.values():
        if {element, other_element}.issubset(other_e_set):
            total_sum += 1
            break  # <-- BU BREAK HER ÇİFT İÇİN SADECE 1 KEZ SAYAR

AMA FORMÜL farklı hesaplıyor!

Formülde:
δ(u, e_i) = Σ_{v ∈ Φ(e_i)} |{e_j ∈ E : {u, v} ⊆ Φ(e_j)}|

Her (u,v) çifti için, TÜM KÜMELERİ sayar!

Yani BREAK OLMAMALI!
""")

# Doğru delta - BREAK olmadan
def delta_function_correct(e_i, E_named, U):
    """BREAK olmadan - makaledeki FORMÜLE göre."""
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    
    results = {}
    for u in not_in_phi:
        total_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            count = 0
            for e_j_name, e_j_set in E_named.items():
                if e_j_name != e_i:  # KENDİ KÜMESİ HARİÇ!
                    if pair.issubset(e_j_set):
                        count += 1
            total_sum += count
        results[u] = total_sum
    return results

print("\n" + "="*80)
print("DÜZELTME: KENDİ KÜMESİ HARİÇ TÜM KÜMELERİ SAY")
print("="*80)

# e2 için test
print("\ne2(1) için düzeltilmiş delta:")
delta_result = delta_function_correct('e2', E_named, U)
print(f"   δ = {delta_result}")
print(f"   γ = 3 × 3 = 9")
print(f"   Θ_e2(1) = {delta_result['1']}/9")

# Tam üyelik matrisi
from fractions import Fraction

def create_membership_matrix_correct(E_named, U):
    m = len(E_named)
    membership_matrix = {}
    
    for e_i in sorted(E_named.keys()):
        phi_e_i = E_named[e_i]
        delta_results = delta_function_correct(e_i, E_named, U)
        
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

mm_correct = create_membership_matrix_correct(E_named, U)

print("\n📊 DÜZELTİLMİŞ Üyelik Matrisi (Kesirli):")
print("\n        ", end="")
for u in sorted(U):
    print(f"{u:>8}", end="")
print()

for e_i in sorted(mm_correct.keys()):
    print(f"   {e_i}  ", end="")
    for u in sorted(U):
        val = mm_correct[e_i][u]
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
print("\n📊 KARŞILAŞTIRMA:")
all_match = True
for e_i in sorted(mm_correct.keys()):
    for u in sorted(U):
        calculated = str(mm_correct[e_i][u])
        expected = paper_values[e_i][u]
        if calculated != expected:
            all_match = False
            print(f"   ✗ {e_i}({u}): Hesaplanan={calculated}, Makale={expected}")

if all_match:
    print("   ✅ TÜM DEĞERLER MAKALE İLE EŞLEŞİYOR!")
