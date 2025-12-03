# -*- coding: utf-8 -*-
import pandas as pd
from fractions import Fraction

# CSV oku
df = pd.read_csv(r"RMVC_Firma_Urun_Matrisi_10x10_Binary.csv", index_col=0)

print("CSV Sutunlari:", list(df.columns))
print("CSV Index:", list(df.index))
print()

# Hocanin yaklasimi: Satirlar=Parametreler, Sutunlar=Elemanlar
parametre_ids = df.index.tolist()
eleman_ids = [str(c) for c in df.columns.tolist()]

# U: Evrensel kume
U = set(eleman_ids)
print("U (Elemanlar):", sorted(U, key=lambda x: int(x)))
print()

# E: Parametre kumeleri
E_named = {}
for param_id in parametre_ids:
    phi_e = set()
    for col in df.columns:
        if df.loc[param_id, col] > 0:
            phi_e.add(str(col))
    E_named[str(param_id)] = phi_e
    print(f"Phi({param_id}) = {sorted(phi_e, key=lambda x: int(x)) if phi_e else 'bos'}")

print()
print("="*60)
print("DELTA VE MEMBERSHIP HESAPLAMA")
print("="*60)

# Delta fonksiyonu
def delta_function(e_name, E_named, U):
    e_set = E_named[e_name]
    not_in_e = U - e_set
    results = {}
    for u in not_in_e:
        delta_sum = 0
        for v in e_set:
            pair = {u, v}
            for other_e in E_named.values():
                if pair.issubset(other_e):
                    delta_sum += 1
        results[u] = delta_sum
    return results

# Membership matrix
m = len(E_named)
print(f"m = {m}")
print()

membership_matrix = {}
for e_key in sorted(E_named.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
    e_set = E_named[e_key]
    membership_matrix[e_key] = {}
    
    if len(e_set) == 0:
        for u in U:
            membership_matrix[e_key][u] = Fraction(0)
        continue
    
    delta_results = delta_function(e_key, E_named, U)
    gamma = len(e_set) * (m - 1)
    
    for u in U:
        if u in e_set:
            membership_matrix[e_key][u] = Fraction(1)
        else:
            delta_val = delta_results.get(u, 0)
            membership_matrix[e_key][u] = Fraction(delta_val, gamma) if gamma > 0 else Fraction(0)

# Sonuclari yazdir
print("MEMBERSHIP MATRIX:")
print()
header = "SETS    " + "".join(f"{i:>10}" for i in range(1, 11))
print(header)
print("-" * len(header))

for e_key in sorted(membership_matrix.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
    row_str = f"{e_key:<8}"
    for col in sorted(U, key=lambda x: int(x)):
        val = float(membership_matrix[e_key][col])
        row_str += f"{val:>10.4f}"
    print(row_str)

print("-" * len(header))

# SUM
print("SUM s(x)", end="")
for col in sorted(U, key=lambda x: int(x)):
    total = sum(float(membership_matrix[e_key][col]) for e_key in membership_matrix)
    print(f"{total:>10.4f}", end="")
print()
