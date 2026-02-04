import pandas as pd
from fractions import Fraction

# CSV oku
df = pd.read_csv('d:/Projects/RMVC/datasets/movielens_method1_10x10.csv', header=None)
print('='*80)
print('CSV BOYUTU:', df.shape)
print('='*80)
print('\nCSV İÇERİĞİ:')
print(df)
print()

# Soft set oluştur
E = [f'e{i+1}' for i in range(len(df))]
U_temp = [f'u{j+1}' for j in range(len(df.columns))]
U = set(U_temp)

soft_set = {}
for i, e_i in enumerate(E):
    soft_set[e_i] = set()
    for j, u in enumerate(U_temp):
        if df.iloc[i, j] == 1:
            soft_set[e_i].add(u)

print('SOFT SET:')
for e_i in sorted(soft_set.keys(), key=lambda x: int(x[1:])):
    elements = sorted(soft_set[e_i], key=lambda x: int(x[1:]))
    print(f'  Φ({e_i}) = {{{", ".join(elements) if elements else "∅"}}}')
print()

# Delta fonksiyonu (V2 - kendi kümesini dahil eder)
def delta_v2(u, phi_ei, soft_set):
    delta_sum = 0
    for v in phi_ei:
        if v == u:
            continue
        for e_j, phi_ej in soft_set.items():
            if u in phi_ej and v in phi_ej:
                delta_sum += 1
    return delta_sum

# Membership matrix
m = len(soft_set)
membership = {}

print('='*80)
print('MEMBERSHIP MATRIX HESAPLANIYOR...')
print('='*80)

for e_i, phi_ei in soft_set.items():
    membership[e_i] = {}
    gamma_ei = len(phi_ei) * (m - 1) if len(phi_ei) > 0 else 1
    
    for u in U:
        if u in phi_ei:
            membership[e_i][u] = Fraction(1, 1)
        else:
            delta_u = delta_v2(u, phi_ei, soft_set)
            membership[e_i][u] = Fraction(delta_u, gamma_ei)

# Matrisi göster
print('\nMEMBERSHIP MATRIX:')
print('SETS    ', end='')
for u in sorted(U, key=lambda x: int(x[1:])):
    print(f'{u:>10}', end='')
print()
print('-'*100)

for e_i in sorted(E, key=lambda x: int(x[1:])):
    print(f'{e_i:<8}', end='')
    for u in sorted(U, key=lambda x: int(x[1:])):
        val = float(membership[e_i][u])
        print(f'{val:>10.4f}', end='')
    print()

# Skorları hesapla
print('-'*100)
print('SUM s(x)', end='')
scores = {}
for u in sorted(U, key=lambda x: int(x[1:])):
    total = sum(float(membership[e_i][u]) for e_i in E)
    scores[u] = total
    print(f'{total:>10.4f}', end='')
print()
print('='*80)

print('\nSONUÇLAR:')
sorted_scores = sorted(scores.items(), key=lambda x: float(x[1]), reverse=True)
for rank, (u, score) in enumerate(sorted_scores, 1):
    prefix = '★' if rank == 1 else ' '
    print(f'{prefix} {rank}. {u}: {score:.4f}')
