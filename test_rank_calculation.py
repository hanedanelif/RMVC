from fractions import Fraction

# İterasyon 0 skorları (Example 1)
scores_old = {
    '1': Fraction(64, 18),  # 3.5556
    '2': Fraction(62, 18),  # 3.4444
    '3': Fraction(50, 18),  # 2.7778
    '4': Fraction(48, 18),  # 2.6667
    '5': Fraction(62, 18)   # 3.4444
}

# Sıralama
sorted_old = sorted(scores_old.items(), key=lambda x: float(x[1]), reverse=True)

print("Sıralanmış skorlar (büyükten küçüğe):")
for i, (u, score) in enumerate(sorted_old):
    print(f"  i={i}, Eleman {u}: {float(score):.4f} → Rank = {i+1}")

# Rank sözlüğü
rank_old = {u: i+1 for i, (u, _) in enumerate(sorted_old)}

print("\nRank sözlüğü:")
for u in sorted(rank_old.keys()):
    print(f"  Eleman {u}: Rank {rank_old[u]}")
