# -*- coding: utf-8 -*-
"""
Example 2 - Makaledeki Sonuçlarla BİREBİR Karşılaştırma
=======================================================
Makaleden alınan değerler:
- Θ_e1(4) = 1/10 = 0.10
- Θ_e1(5) = 3/20 = 0.15
- Θ_e1(7) = 3/20 = 0.15

Matris (Makaleden):
1    1    1    0.10  0.15  1    0.15
0.13 1    0.33 1     0.07  1    0
1    0.2  1    0     0.2   0.27 1
0.27 0.33 1    0.07  1     1    0.13
1    0.07 0.27 0     1     0.13 1
0.27 1    1    0.13  0.13  1    0.07
"""

import pandas as pd
from fractions import Fraction

print("="*80)
print("EXAMPLE 2 - MAKALEDEKİ SONUÇLARLA BİREBİR KARŞILAŞTIRMA")
print("="*80)

# Makaledeki matris (ondalıklı)
paper_matrix_decimal = [
    [1,    1,    1,    0.10,  0.15,  1,    0.15],  # e1
    [0.13, 1,    0.33, 1,     0.07,  1,    0   ],  # e2
    [1,    0.2,  1,    0,     0.2,   0.27, 1   ],  # e3
    [0.27, 0.33, 1,    0.07,  1,     1,    0.13],  # e4
    [1,    0.07, 0.27, 0,     1,     0.13, 1   ],  # e5
    [0.27, 1,    1,    0.13,  0.13,  1,    0.07],  # e6
]

# Makaledeki skorlar
paper_scores = {
    '1': 3.67,
    '2': 3.60,
    '3': 4.60,
    '4': 1.30,
    '5': 2.55,
    '6': 4.40,
    '7': 2.35
}

# Excel'den veri yükle
df = pd.read_excel("Example.2..xlsx", index_col=0)
df_t = df.T
U = set(df_t.index.astype(str))
E_named = {}
for col in df_t.columns:
    E_named[str(col)] = set(df_t.index[df_t[col] > 0].astype(str))

# ============================================================
# V2 DELTA (BREAK YOK, TÜM KÜMELER DAHİL)
# ============================================================
def delta_v2(e_i, E_named, U):
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

def create_mm_v2(E_named, U):
    m = len(E_named)
    mm = {}
    for e_i in sorted(E_named.keys()):
        phi_e_i = E_named[e_i]
        delta_results = delta_v2(e_i, E_named, U)
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

# V2 hesapla
mm_v2 = create_mm_v2(E_named, U)

# Matrisi yazdır
print("\n" + "="*80)
print("V2 Üyelik Matrisi")
print("="*80)
print("\n        ", end="")
for u in sorted(U):
    print(f"{u:>8}", end="")
print()

for i, e_i in enumerate(sorted(E_named.keys())):
    print(f"   {e_i}  ", end="")
    for j, u in enumerate(sorted(U)):
        val = mm_v2[e_i][u]
        print(f"{float(val):>8.4f}", end="")
    print()

# Makaledeki matris
print("\n" + "="*80)
print("Makaledeki Matris")
print("="*80)
print("\n        ", end="")
for u in sorted(U):
    print(f"{u:>8}", end="")
print()

for i, e_i in enumerate(sorted(E_named.keys())):
    print(f"   {e_i}  ", end="")
    for j, val in enumerate(paper_matrix_decimal[i]):
        print(f"{val:>8.4f}", end="")
    print()

# Karşılaştırma
print("\n" + "="*80)
print("DETAYLI KARŞILAŞTIRMA")
print("="*80)

differences = []
for i, e_i in enumerate(sorted(E_named.keys())):
    for j, u in enumerate(sorted(U)):
        v2_val = float(mm_v2[e_i][u])
        paper_val = paper_matrix_decimal[i][j]
        diff = abs(v2_val - paper_val)
        if diff > 0.001:  # Tolerans
            differences.append({
                'cell': f"{e_i}({u})",
                'v2': v2_val,
                'paper': paper_val,
                'diff': diff
            })

if differences:
    print(f"\n⚠️ {len(differences)} FARKLI HÜCRE:")
    for d in differences:
        print(f"   {d['cell']}: V2={d['v2']:.4f}, Makale={d['paper']:.4f}, Fark={d['diff']:.4f}")
else:
    print("\n✅ TÜM DEĞERLER MAKALEDEKİ MATRİS İLE EŞLEŞİYOR!")

# Skorlar
scores_v2 = {}
for u in sorted(U):
    total = Fraction(0, 1)
    for e_i in mm_v2:
        total += mm_v2[e_i][u]
    scores_v2[u] = total

print("\n" + "="*80)
print("SKOR KARŞILAŞTIRMASI")
print("="*80)
print(f"\n{'Eleman':<8} {'V2 Skor':>12} {'Makale':>12} {'Fark':>10}")
print("-" * 45)

for u in sorted(U):
    v2_score = float(scores_v2[u])
    paper_score = paper_scores[u]
    diff = abs(v2_score - paper_score)
    status = "✅" if diff < 0.01 else "❌"
    print(f"{u:<8} {v2_score:>12.4f} {paper_score:>12.2f} {diff:>10.4f} {status}")

# Optimal seçim
max_v2 = max(float(s) for s in scores_v2.values())
max_paper = max(paper_scores.values())
optimal_v2 = [u for u, s in scores_v2.items() if float(s) == max_v2]
optimal_paper = [u for u, s in paper_scores.items() if s == max_paper]

print("\n" + "="*80)
print("OPTİMAL SEÇİM")
print("="*80)
print(f"V2:     {', '.join(optimal_v2)} (Skor: {max_v2:.4f})")
print(f"Makale: {', '.join(optimal_paper)} (Skor: {max_paper:.2f})")

if optimal_v2 == optimal_paper:
    print("\n✅ AYNI OPTİMAL SEÇİM!")
else:
    print("\n❌ FARKLI OPTİMAL SEÇİM!")

# Kritik değerleri kontrol et
print("\n" + "="*80)
print("KRİTİK DEĞERLER (Makaledeki örnekler)")
print("="*80)

critical_checks = [
    ('e1', '4', 0.10, '1/10'),
    ('e1', '5', 0.15, '3/20'),
    ('e1', '7', 0.15, '3/20'),
]

for e_i, u, expected, frac in critical_checks:
    v2_val = float(mm_v2[e_i][u])
    match = "✅" if abs(v2_val - expected) < 0.001 else "❌"
    print(f"Θ_{e_i}({u}): V2={v2_val:.4f}, Makale={expected} ({frac}) {match}")
