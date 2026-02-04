"""
PYTHON FLOAT PRECISION TEST
===========================
Python'un ondalıklı sayılarda kaç hane duyarlılıkta çalıştığını gösterelim
"""

import sys
import math

print("="*70)
print("PYTHON FLOAT (Double Precision) ÖZELLİKLERİ")
print("="*70)

print("\n1. TEKNİK DETAYLAR")
print("-" * 70)
print(f"Float tipi: IEEE 754 Double Precision (64-bit)")
print(f"Toplam bit: 64")
print(f"  - İşaret biti: 1 bit")
print(f"  - Üs (exponent): 11 bit")
print(f"  - Mantis (significand): 52 bit")

print("\n2. DUYARLILIK (PRECISION)")
print("-" * 70)
print(f"sys.float_info.dig: {sys.float_info.dig} ondalık basamak")
print(f"  → Bu, güvenle kullanabileceğiniz ondalık basamak sayısıdır")

print(f"\nsys.float_info.mant_dig: {sys.float_info.mant_dig} binary basamak")
print(f"  → İkili (binary) sistemde kaç basamak")

print(f"\nMachine epsilon: {sys.float_info.epsilon}")
print(f"  → 1.0 ile 1.0'dan büyük bir sonraki sayı arasındaki fark")
print(f"  → Yaklaşık: 2.22 × 10^-16")

print("\n3. ARALIK (RANGE)")
print("-" * 70)
print(f"En küçük pozitif sayı: {sys.float_info.min}")
print(f"En büyük sayı: {sys.float_info.max}")

print("\n4. PRATIK ÖRNEKLER")
print("-" * 70)

# 1/3 örneği
val = 1/3
print(f"\n1/3 = {val}")
print(f"15 hane: {val:.15f}")
print(f"20 hane: {val:.20f}")
print(f"25 hane: {val:.25f}")
print(f"  → 15. haneden sonra anlamsız!")

# 1/9 örneği (bizim durumumuz)
val = 1/9
print(f"\n1/9 = {val}")
print(f"15 hane: {val:.15f}")
print(f"20 hane: {val:.20f}")
print(f"25 hane: {val:.25f}")
print(f"  → Gerçek: 0.111111... (sonsuz)")
print(f"  → Python: 0.11111111111111110494... (16. haneden sonra çöp)")

print("\n5. YUVARLAMA HATALARI")
print("-" * 70)

# Toplama hatası
a = 0.1 + 0.2
print(f"\n0.1 + 0.2 = {a}")
print(f"20 hane: {a:.20f}")
print(f"Beklenen: 0.3")
print(f"Gerçek:   {a} ≠ 0.3")
print(f"a == 0.3: {a == 0.3}")  # False!

# Çarpma hatası
b = 0.1 * 3
print(f"\n0.1 × 3 = {b}")
print(f"20 hane: {b:.20f}")
print(f"b == 0.3: {b == 0.3}")  # False!

print("\n6. BİZİM DURUMUMUZDA")
print("-" * 70)

vals = [1/9] * 6
avg = sum(vals) / len(vals)

print(f"6 tane (1/9):")
print(f"  Tek değer: {vals[0]:.20f}")
print(f"  Ortalama:  {avg:.20f}")
print(f"  Fark:      {abs(vals[0] - avg):.25f}")
print(f"\n               ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑")
print(f"  15-16. haneden sonra FARK başlıyor!")

print("\n7. GÜVENLİ KARŞILAŞTIRMA")
print("-" * 70)

epsilon = 1e-9
print(f"\nEpsilon toleransı: {epsilon}")
print(f"Karşılaştırma: |a - b| < epsilon")

diff = abs(vals[0] - avg)
print(f"\n|değer - ortalama| = {diff}")
print(f"{diff} < {epsilon}? {diff < epsilon}")
print(f"  → EVET! Bu yüzden AYNI kabul etmeliyiz")

print("\n" + "="*70)
print("SONUÇ")
print("="*70)
print("✓ Python float: ~15-16 ondalık basamak GÜVENLİ")
print("✓ 16. haneden sonra: YUVARLAMA HATALARI başlar")
print("✓ Çözüm: Epsilon toleransı kullan (1e-9 gibi)")
print("=" * 70)
