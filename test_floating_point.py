"""
FLOATING POINT PRECİSİON TEST
==============================
10x10 Tekstil anomalisindeki gerçek durumu test edelim
"""

from fractions import Fraction
import numpy as np

print("="*70)
print("TEST 1: Basit Karşılaştırma")
print("="*70)

# Tam olarak aynı değerler
a = 0.1111111111111111
b = 0.1111111111111111

print(f"a = {a}")
print(f"b = {b}")
print(f"a >= b: {a >= b}")  # Bu TRUE olmalı
print(f"a == b: {a == b}")  # Bu TRUE olmalı

print("\n" + "="*70)
print("TEST 2: Fraction → Float Dönüşümü")
print("="*70)

# 1/9'u float'a çevir
frac = Fraction(1, 9)
val = float(frac)
print(f"Fraction(1, 9) = {frac}")
print(f"float(Fraction(1, 9)) = {val}")
print(f"Decimal representation: {val:.20f}")

print("\n" + "="*70)
print("TEST 3: 6 Tane 1/9'un Ortalaması (Gerçek Tekstil Durumu)")
print("="*70)

# 6 tane 1/9 değeri
fractional_values = [float(Fraction(1, 9)) for _ in range(6)]
print(f"6 değer: {[f'{v:.20f}' for v in fractional_values[:2]]}...")  # İlk 2 tanesini göster

# Ortalama hesapla
threshold = np.mean(fractional_values)
print(f"\nOrtalama (threshold): {threshold:.20f}")

# Karşılaştır
value = float(Fraction(1, 9))
print(f"Tek değer (value):     {value:.20f}")

print(f"\nvalue >= threshold: {value >= threshold}")
print(f"value == threshold: {value == threshold}")

# FARK
diff = abs(value - threshold)
print(f"\n|value - threshold| = {diff:.30f}")

if diff < 1e-15:
    print("✅ NEREDEYSE AYNI (numerik olarak eşit)")
else:
    print("❌ FARKLI!")

print("\n" + "="*70)
print("TEST 4: SCRİPTİMİZDE OLAN DURUM")
print("="*70)

# Membership matrix benzeri (Col 4 için)
membership_values = {
    'e_1': Fraction(1, 9),
    'e_2': Fraction(1, 9),
    'e_4': Fraction(1, 9),
    'e_5': Fraction(1, 9),
    'e_7': Fraction(1, 9),
    'e_10': Fraction(1, 9)
}

# Float'a çevir ve threshold hesapla
float_values = [float(v) for v in membership_values.values()]
threshold_calculated = np.mean(float_values)

print(f"Threshold: {threshold_calculated:.20f}")

# Binary dönüşüm (SCRİPTİMİZDEKİ GİBİ)
for key, frac_val in membership_values.items():
    val = float(frac_val)
    binary = 1 if val >= threshold_calculated else 0
    print(f"{key}: {val:.20f} >= {threshold_calculated:.20f} → Binary: {binary}")

print("\n" + "="*70)
print("TEST 5: EPSILON EKLEYELİM")
print("="*70)

epsilon = 1e-9
print(f"Epsilon: {epsilon}")

for key, frac_val in membership_values.items():
    val = float(frac_val)
    binary_without_eps = 1 if val >= threshold_calculated else 0
    binary_with_eps = 1 if val >= (threshold_calculated - epsilon) else 0
    print(f"{key}: Binary (epsiz)={binary_without_eps}, Binary (eps)={binary_with_eps}")

print("\n" + "="*70)
print("SONUÇ")
print("="*70)
print("Eğer tüm binary değerler 1 ise, sorun YOK (anomali başka yerde).")
print("Eğer binary değerler 0 ise, floating point precision sorunu VAR!")
