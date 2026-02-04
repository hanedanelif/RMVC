# -*- coding: utf-8 -*-
"""
Hocanın csvtormvc.py vs V2/V3 Karşılaştırması
"""
from fractions import Fraction

# Example 1 verisi
E_named = {
    'e_1': {'1', '2', '3', '5'},
    'e_2': {'2', '4', '5'},
    'e_3': {'1', '3', '4'},
    'e_4': {'1', '2', '5'}
}
U = {'1', '2', '3', '4', '5'}

print("="*80)
print("HOCANIN KODU vs V2 vs V3 KARŞILAŞTIRMASI")
print("="*80)

# ========================================
# HOCANIN ORİJİNAL KODU (csvtormvc.py)
# ========================================
def delta_function_hoca(e_name, E_named, U):
    """Hocanın orijinal delta fonksiyonu (csvtormvc.py satır 158-171)"""
    e_set = E_named[e_name]
    not_in_e_set = U - e_set
    results = {}
    all_sets_list = list(E_named.values())  # TÜM KÜMELERİ AL

    for element in not_in_e_set:
        total_sum = 0
        for other_element in e_set:
            pair = {element, other_element}
            count = sum(1 for s in all_sets_list if pair.issubset(s))  # BREAK YOK, TÜM KÜMELER
            total_sum += count
        results[element] = total_sum
    return results

# ========================================
# V2 DELTA FONKSIYONU
# ========================================
def delta_function_v2(e_i, E_named, U):
    """V2 delta fonksiyonu"""
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

# ========================================
# V3 DELTA FONKSIYONU
# ========================================
def delta_function_v3(e_i, E_named, U):
    """V3 delta fonksiyonu - Kendi kümesi hariç"""
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

# ========================================
# TEST: e_2 için delta(1) hesabı
# ========================================
print("\n" + "="*80)
print("TEST: Θ_e2(1) hesabı (Makalede 5/9 olmalı)")
print("="*80)

e_test = 'e_2'
u_test = '1'

delta_hoca = delta_function_hoca(e_test, E_named, U)
delta_v2 = delta_function_v2(e_test, E_named, U)
delta_v3 = delta_function_v3(e_test, E_named, U)

print(f"\nΦ(e2) = {E_named[e_test]}")
print(f"u = {u_test} (e2'de yok)")
print(f"γ = |Φ(e2)| × (m-1) = 3 × 3 = 9")

print(f"\nHOCA KODU: δ(1, e2) = {delta_hoca[u_test]}")
print(f"  → Θ_e2(1) = {delta_hoca[u_test]}/9 = {Fraction(delta_hoca[u_test], 9)}")

print(f"\nV2 KODU:   δ(1, e2) = {delta_v2[u_test]}")
print(f"  → Θ_e2(1) = {delta_v2[u_test]}/9 = {Fraction(delta_v2[u_test], 9)}")

print(f"\nV3 KODU:   δ(1, e2) = {delta_v3[u_test]}")
print(f"  → Θ_e2(1) = {delta_v3[u_test]}/9 = {Fraction(delta_v3[u_test], 9)}")

print(f"\n📌 MAKALEDEKİ DEĞER: Θ_e2(1) = 5/9")

# ========================================
# KARŞILAŞTIRMA
# ========================================
print("\n" + "="*80)
print("SONUÇ")
print("="*80)

if delta_hoca[u_test] == delta_v2[u_test]:
    print("✅ HOCANIN KODU = V2")
else:
    print("❌ HOCANIN KODU ≠ V2")

if delta_hoca[u_test] == delta_v3[u_test]:
    print("✅ HOCANIN KODU = V3")
else:
    print("❌ HOCANIN KODU ≠ V3")

makale_delta = 5  # 5/9
if delta_hoca[u_test] == makale_delta:
    print("✅ HOCANIN KODU = MAKALE")
else:
    print("❌ HOCANIN KODU ≠ MAKALE")

print("\n" + "="*80)
print("KARAR")
print("="*80)
if delta_hoca[u_test] == delta_v2[u_test]:
    print("🎯 V2 KULLANILMALI - Hocanın koduyla uyumlu")
elif delta_hoca[u_test] == delta_v3[u_test]:
    print("🎯 V3 KULLANILMALI - Hocanın koduyla uyumlu")
else:
    print("⚠️ HİÇBİRİ UYUŞMUYOR - Detaylı inceleme gerekli")
