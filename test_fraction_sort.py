from fractions import Fraction

# İterasyon 0 skorları (Fraction olarak)
scores = {
    '1': Fraction(64, 18),  # 3.5556
    '2': Fraction(62, 18),  # 3.4444
    '3': Fraction(50, 18),  # 2.7778
    '4': Fraction(48, 18),  # 2.6667
    '5': Fraction(62, 18)   # 3.4444
}

print("Skorlar:")
for u, s in scores.items():
    print(f"  Eleman {u}: {s} = {float(s):.4f}")

# Sıralama 1: Doğrudan Fraction ile
sorted_direct = sorted(scores.items(), key=lambda x: x[1], reverse=True)
print("\nDoğrudan Fraction ile sıralama:")
for i, (u, s) in enumerate(sorted_direct):
    print(f"  {i}: Eleman {u} = {float(s):.4f}")

# Sıralama 2: float'a çevirip
sorted_float = sorted(scores.items(), key=lambda x: float(x[1]), reverse=True)
print("\nfloat'a çevirip sıralama:")
for i, (u, s) in enumerate(sorted_float):
    print(f"  {i}: Eleman {u} = {float(s):.4f}")

# Rank hesaplama
rank_dict = {u: i+1 for i, (u, _) in enumerate(sorted_float)}
print("\nRank sözlüğü:")
for u in sorted(rank_dict.keys()):
    print(f"  Eleman {u}: Rank {rank_dict[u]}")
