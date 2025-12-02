# -*- coding: utf-8 -*-
"""
Example 1 Test - Makaledeki değerlerle karşılaştırma
"""

import pandas as pd
from fractions import Fraction

# Excel dosyasını oku ve TRANSPOSE et
df_raw = pd.read_excel(r'C:\Users\user\Downloads\RMVC\Example.1..xlsx', index_col=0)
df = df_raw.T  # Transpose: Satırlar=Elemanlar, Sütunlar=Parametreler

print('=== GİRDİ MATRİSİ (Transpose edilmiş) ===')
print(df)
print()

# Soft Set'e dönüştür
U = set(str(idx) for idx in df.index.tolist())
E_named = {}

for i, col in enumerate(df.columns):
    e_key = f'e_{i+1}'
    phi = set()
    for idx, val in df[col].items():
        if pd.to_numeric(val, errors='coerce') > 0:
            phi.add(str(idx))
    E_named[e_key] = phi

print('=== SOFT SET ===')
print(f'U = {sorted(U, key=lambda x: int(x) if x.isdigit() else x)}')
for e, phi in sorted(E_named.items(), key=lambda x: int(x[0].split("_")[1])):
    print(f'Φ({e}) = {sorted(phi, key=lambda x: int(x) if x.isdigit() else x)}')
print()

# Delta fonksiyonu - DÜZELTİLMİŞ
def delta_function(e_i, E_named, U):
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    results = {}
    
    for u in not_in_phi:
        delta_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            # TÜM kümelerde say (break YOK)
            for e_j, phi_e_j in E_named.items():
                if pair.issubset(phi_e_j):
                    delta_sum += 1
        results[u] = delta_sum
    return results

# Üyelik matrisi hesapla
m = len(E_named)
membership_matrix = {}

print('=== HESAPLAMA DETAYLARI ===')
for e_i in sorted(E_named.keys(), key=lambda x: int(x.split('_')[1])):
    phi_e_i = E_named[e_i]
    delta_results = delta_function(e_i, E_named, U)
    gamma = len(phi_e_i) * (m - 1)
    
    print(f'{e_i}: |Φ| = {len(phi_e_i)}, γ = {len(phi_e_i)} × {m-1} = {gamma}')
    
    membership_matrix[e_i] = {}
    for u in U:
        if u in phi_e_i:
            membership_matrix[e_i][u] = Fraction(1, 1)
        elif gamma > 0 and u in delta_results:
            membership_matrix[e_i][u] = Fraction(delta_results[u], gamma)
            if delta_results[u] > 0:
                print(f'  δ({u}, {e_i}) = {delta_results[u]} → M = {delta_results[u]}/{gamma} = {float(Fraction(delta_results[u], gamma)):.4f}')
        else:
            membership_matrix[e_i][u] = Fraction(0, 1)

print()

# Sonuçları yazdır
print('=== ÜYELİK MATRİSİ ===')
sorted_U = sorted(U, key=lambda x: int(x) if x.isdigit() else x)
header = 'Param'.ljust(8)
for u in sorted_U:
    header += str(u).rjust(12)
print(header)
print('-' * 70)

for e_i in sorted(membership_matrix.keys(), key=lambda x: int(x.split('_')[1])):
    row = e_i.ljust(8)
    for u in sorted_U:
        val = membership_matrix[e_i][u]
        row += f'{float(val):.4f}'.rjust(12)
    print(row)
print()

# Makaledeki değerlerle karşılaştır
print('=== DOĞRULAMA (Makaledeki Değerler) ===')
checks = [
    ('e_1', '4', Fraction(1, 3), '1/3 ≈ 0.333'),
    ('e_2', '1', Fraction(5, 9), '5/9 ≈ 0.556'),
    ('e_2', '3', Fraction(1, 3), '1/3 ≈ 0.333'),
    ('e_3', '2', Fraction(4, 9), '4/9 ≈ 0.444'),
    ('e_3', '5', Fraction(4, 9), '4/9 ≈ 0.444'),
    ('e_4', '3', Fraction(4, 9), '4/9 ≈ 0.444'),
    ('e_4', '4', Fraction(1, 3), '1/3 ≈ 0.333'),
]

all_pass = True
for e_i, u, expected, desc in checks:
    actual = membership_matrix[e_i][u]
    if actual == expected:
        print(f'✅ M({u}, {e_i}) = {float(actual):.4f} ({actual}) = {desc}')
    else:
        all_pass = False
        print(f'❌ M({u}, {e_i}) = {float(actual):.4f} ({actual}) - Beklenen: {desc}')

print()
if all_pass:
    print('🎉 TÜM DEĞERLER MAKALE İLE UYUŞUYOR!')
else:
    print('⚠️ Bazı değerler uyuşmuyor')

# Skorları hesapla
print()
print('=== SKORLAR (Sütun Toplamları) ===')
scores = {}
for u in U:
    total = sum(membership_matrix[e_i][u] for e_i in membership_matrix)
    scores[u] = total

max_score = max(float(v) for v in scores.values())
for u, s in sorted(scores.items(), key=lambda x: -float(x[1])):
    status = '⭐ EN İYİ' if float(s) == max_score else ''
    print(f'S({u}) = {float(s):.4f} ({s}) {status}')
