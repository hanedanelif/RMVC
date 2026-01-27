import pandas as pd
from rmvc_app_v2 import csv_to_soft_set, create_membership_matrix, calculate_scores
from fractions import Fraction

# Excel'i oku
df = pd.read_excel('Example.1..xlsx', index_col=0)
print('=== GIRDI MATRISI ===')
print(df)
print()

# Soft set'e dönüştür (rows_are_params=True)
U, E_named, E_info, eleman_ids, parametre_ids = csv_to_soft_set(df, rows_are_params=True)

print('=== SOFT SET ===')
print(f'U (Elemanlar): {sorted(U, key=lambda x: int(x))}')
print()
for e_key in sorted(E_named.keys(), key=lambda x: int(x.split('_')[1])):
    print(f'{e_key}: {sorted(E_named[e_key], key=lambda x: int(x))}')
print()

# Üyelik matrisi hesapla
membership_matrix = create_membership_matrix(E_named, U)

print('=== MEMBERSHIP MATRIX ===')
sorted_u = sorted(U, key=lambda x: int(x))
print('       ', end='')
for u in sorted_u:
    print(f'{u:>8}', end='')
print()

sorted_e = sorted(membership_matrix.keys(), key=lambda x: int(x.split('_')[1]))
for e_key in sorted_e:
    print(f'{e_key:6}', end=' ')
    for u in sorted_u:
        val = membership_matrix[e_key].get(u, Fraction(0, 1))
        print(f'{float(val):8.4f}', end='')
    print()
print()

# Skorları hesapla
scores = calculate_scores(membership_matrix, U)

print('=== SKORLAR (SUM s(x)) ===')
print('Eleman  Skor')
for u in sorted_u:
    print(f'{u:>6}  {float(scores[u]):8.4f}')
print()

print('=== SIRALAMA ===')
sorted_scores = sorted(scores.items(), key=lambda x: (-float(x[1]), int(x[0])))
for rank, (u, score) in enumerate(sorted_scores, 1):
    print(f'{rank}. Eleman {u}: {float(score):.4f}')
