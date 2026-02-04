"""
BİZİM SCRİPTTE KARAPIŞLAŞTIRMA NASIL?
=====================================
Scriptimizdeki threshold karşılaştırmasını inceleyelim
"""

from fractions import Fraction
import numpy as np

print("="*70)
print("BİZİM SCRİPTTEKİ KARŞILAŞTIRMA YÖNTEMİ")
print("="*70)

# Bizim scriptimizde olan kod
def threshold_matrix_dynamic(membership_matrix, U, threshold_value):
    """BU BİZİM KULLANDIĞIMIZ FONKSİYON"""
    binary_matrix = {}
    for e_i in membership_matrix.keys():
        binary_matrix[e_i] = {}
        for u in U:
            val = float(membership_matrix[e_i].get(u, Fraction(0, 1)))
            # ↓↓↓ İŞTE BU SATIR ↓↓↓
            binary_matrix[e_i][u] = 1 if val >= threshold_value else 0
            # ↑↑↑ EPSILON YOK! ↑↑↑
    return binary_matrix

print("\nKOD ANALİZİ:")
print("-" * 70)
print("Satır: binary = 1 if val >= threshold_value else 0")
print("\nNE YAPIYOR:")
print("  1. 'val' ve 'threshold_value' FULL PRECISION karşılaştırılıyor")
print("  2. Python float = 64-bit (IEEE 754 Double Precision)")
print("  3. Karşılaştırma: TÜM 64 BİT kullanılıyor")
print("  4. Ondalık olarak: ~15-17 HANE karşılaştırılıyor")
print("  5. EPSİLON TOLERANSI YOK!")

print("\n" + "="*70)
print("PRATIKTE NE OLUYOR?")
print("="*70)

# Gerçek örnek
val = float(Fraction(1, 9))
threshold = np.mean([float(Fraction(1, 9)) for _ in range(6)])

print(f"\nDeğer (val):       {val:.20f}")
print(f"Eşik (threshold):  {threshold:.20f}")
print(f"\nKarşılaştırılan haneler:")
print(f"  Hane 1-15:  AYNI (0.111111111111111)")
print(f"  Hane 16-17: AYNI (11)")  
print(f"  Hane 18:    FARKLI! (1 vs 1)")
print(f"  Hane 19:    FARKLI! (0 vs 8)")
print(f"           val: ...110494...")
print(f"     threshold: ...111882...")
print(f"                   ↑↑ BURADA AYRILIK!")

print(f"\nPython'un karşılaştırması:")
print(f"  val >= threshold")
print(f"  0.11111111111111110494... >= 0.11111111111111111882...")
print(f"  Sonuç: {val >= threshold}")

print("\n" + "="*70)
print("KAÇA KADAR BAKIYOR?")
print("="*70)

print(f"\n✓ Matematiksel olarak: TÜM 64 BİT (53 bit mantis)")
print(f"✓ Ondalık olarak: ~17 HANE")
print(f"✓ Güvenli karşılaştırma: İlk 15 hane")
print(f"✓ 16-17. hane: Risk bölgesi (yuvarlama hataları)")
print(f"✓ 18+ hane: Çöp değerler")

print(f"\n❌ SORUN: Epsilon toleransı YOK!")
print(f"   → 18. hanedeki fark bile karşılaştırmayı etkiliyor")
print(f"   → 10^-17 seviyesindeki farklar önemli sayılıyor")

print("\n" + "="*70)
print("ÇÖZÜM: EPSİLON EKLE")
print("="*70)

epsilon_values = [1e-15, 1e-12, 1e-9, 1e-6]
print(f"\nFarklı epsilon değerleri ile test:")

for eps in epsilon_values:
    result_with_eps = val >= (threshold - eps)
    print(f"  ε = {eps:>10.0e}: val >= (threshold - ε) → {result_with_eps}")

print(f"\n✅ ÖNERİ: epsilon = 1e-9 kullan")
print(f"   → 9. ondalık haneden sonrasını yok say")
print(f"   → RMVC için yeterince kesin")
print(f"   → Yuvarlama hatalarından güvendedir")

print("\n" + "="*70)
