# -*- coding: utf-8 -*-
"""
Example 2 - Makale Sonuçlarıyla Detaylı Karşılaştırma
=====================================================
KULLANICI GERİ BİLDİRİMİ:
- Example 2'de V2 makaledeki sonuçlarla örtüşüyor
- V3 makaledeki sonuçlarla örtüşmüyor
- GitHub'taki orijinal kod (V2) doğru

Bu durumu detaylı olarak analiz ediyoruz.
"""

import pandas as pd
from fractions import Fraction

print("="*80)
print("EXAMPLE 2 - MAKALE SONUÇLARIYLA DETAYLI KARŞILAŞTIRMA")
print("="*80)

# Veri yükle
df = pd.read_excel("Example.2..xlsx", index_col=0)
print("\n📊 Girdi Matrisi:")
print(df)

# Soft Set
df_t = df.T
U = set(df_t.index.astype(str))
E_named = {}
for col in df_t.columns:
    members = set(df_t.index[df_t[col] > 0].astype(str))
    E_named[str(col)] = members

print(f"\n|U| = {len(U)}, |E| = {len(E_named)}")

# ============================================================
# GITHUB ORİJİNAL KOD MANTĞI (V2)
# ============================================================
def delta_github_original(e_i, E_named, U):
    """
    GitHub'taki orijinal kod mantığı.
    
    Makaledeki Python kodu:
    ```
    for other_e_set in E_named.values():
        if {element, other_element}.issubset(other_e_set):
            total_sum += 1
            break  # <-- BU BREAK VAR!
    ```
    
    AMA BU KOD ASLINDA:
    Her (u,v) çifti için, BULDUĞUNDAKİ İLK KÜMEYİ sayar ve break yapar.
    """
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    results = {}
    
    for u in not_in_phi:
        total_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            # İLK bulunan küme için +1 (break ile)
            for e_j, phi_e_j in E_named.items():
                if pair.issubset(phi_e_j):
                    total_sum += 1
                    break  # BREAK VAR!
        results[u] = total_sum
    return results

# ============================================================
# V2 MANTĞI (BREAK YOK, TÜM KÜMELER)
# ============================================================
def delta_v2_no_break(e_i, E_named, U):
    """V2: break yok, tüm kümeleri say."""
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    results = {}
    
    for u in not_in_phi:
        delta_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            for e_j, phi_e_j in E_named.items():
                if pair.issubset(phi_e_j):
                    delta_sum += 1  # BREAK YOK!
        results[u] = delta_sum
    return results

# ============================================================
# V3 MANTĞI (KENDİ KÜMESİ HARİÇ)
# ============================================================
def delta_v3_exclude_self(e_i, E_named, U):
    """V3: Kendi kümesi hariç, break yok."""
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

def create_membership_matrix(E_named, U, delta_func, name=""):
    """Üyelik matrisi oluştur."""
    m = len(E_named)
    mm = {}
    
    for e_i in sorted(E_named.keys()):
        phi_e_i = E_named[e_i]
        delta_results = delta_func(e_i, E_named, U)
        gamma = len(phi_e_i) * (m - 1)
        
        mm[e_i] = {}
        for u in sorted(U):
            if u in phi_e_i:
                mm[e_i][u] = Fraction(1, 1)
            else:
                if gamma > 0 and u in delta_results:
                    mm[e_i][u] = Fraction(delta_results[u], gamma)
                else:
                    mm[e_i][u] = Fraction(0, 1)
    
    return mm

# Test et
print("\n" + "="*80)
print("TEST 1: GitHub Orijinal (BREAK ile)")
print("="*80)
mm_github = create_membership_matrix(E_named, U, delta_github_original)
print("\nÜyelik Matrisi (ilk satır):")
print(f"e1: {[str(mm_github['e1'][u]) for u in sorted(U)]}")

print("\n" + "="*80)
print("TEST 2: V2 Mantığı (break YOK, tüm kümeler)")
print("="*80)
mm_v2 = create_membership_matrix(E_named, U, delta_v2_no_break)
print("\nÜyelik Matrisi (ilk satır):")
print(f"e1: {[str(mm_v2['e1'][u]) for u in sorted(U)]}")

print("\n" + "="*80)
print("TEST 3: V3 Mantığı (kendi kümesi HARİÇ)")
print("="*80)
mm_v3 = create_membership_matrix(E_named, U, delta_v3_exclude_self)
print("\nÜyelik Matrisi (ilk satır):")
print(f"e1: {[str(mm_v3['e1'][u]) for u in sorted(U)]}")

# Karşılaştırma
print("\n" + "="*80)
print("KARŞILAŞTIRMA")
print("="*80)

# e1(4) için detaylı hesap
print("\nDETAYLI HESAP: Θ_e1(4)")
print("Φ(e1) = {1, 2, 3, 6}")
print("4 ∉ Φ(e1), yani hesaplanmalı")
print("γ = 4 × 5 = 20")

print("\n(4,v) çiftleri için küme sayımı:")
print("v ∈ Φ(e1) = {1, 2, 3, 6}")

for v in ['1', '2', '3', '6']:
    pair_str = f"{{{4}, {v}}}"
    found_in = []
    for e_j, phi_e_j in E_named.items():
        if {'4', v}.issubset(phi_e_j):
            found_in.append(e_j)
    
    print(f"\n  {pair_str}:")
    print(f"    Bulunduğu kümeler: {found_in if found_in else 'HİÇBİR YERDE'}")
    print(f"    GitHub (break): {1 if found_in else 0}")
    print(f"    V2 (break yok): {len(found_in)}")
    print(f"    V3 (e1 hariç): {len([e for e in found_in if e != 'e1'])}")

# Toplamlar
github_delta = delta_github_original('e1', E_named, U).get('4', 0)
v2_delta = delta_v2_no_break('e1', E_named, U).get('4', 0)
v3_delta = delta_v3_exclude_self('e1', E_named, U).get('4', 0)

print(f"\nδ(4, e1) toplamları:")
print(f"  GitHub (break): {github_delta}")
print(f"  V2 (break yok): {v2_delta}")
print(f"  V3 (e1 hariç): {v3_delta}")

print(f"\nΘ_e1(4) sonuçları:")
print(f"  GitHub: {github_delta}/20 = {Fraction(github_delta, 20)}")
print(f"  V2: {v2_delta}/20 = {Fraction(v2_delta, 20)}")
print(f"  V3: {v3_delta}/20 = {Fraction(v3_delta, 20)}")

print("\n" + "="*80)
print("ÖNEMLİ SORU:")
print("="*80)
print("""
Kullanıcı diyor ki:
- V2 makaledeki Example 2 ile örtüşüyor
- V3 makaledeki Example 2 ile örtüşmüyor

Ama burada gördük ki:
- GitHub orijinal kodda BREAK var
- V2'de break YOK
- V3'te kendi kümesi hariç

Eğer V2 makaledeki sonuçlarla örtüşüyorsa:
→ Makale BREAK KULLANMADAN hesaplamış olabilir
→ Ya da makaledeki formül vs kod tutarsız olabilir

ÇÖZÜM: Makaledeki Example 2 Table 9'u bulmak ve karşılaştırmak gerekiyor.
""")
