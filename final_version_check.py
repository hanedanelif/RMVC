# -*- coding: utf-8 -*-
"""
FINAL KARŞILAŞTIRMA: Hocanın Kodu vs Arayüz V2
"""
from fractions import Fraction

# Example 1 verisi
E_named = {
    'e_1': {'1', '2', '3', '5'},
    'e_2': {'2', '4', '5'},
    'e_3': {'1', '3', '4'},
    'e_4': {'1', '2', '5'}
}
U = {'1', '2', '3', '4', '5'}

print("="*100)
print("HOCANIN csvtormvc.py KODU")
print("="*100)
print("""
def delta_function(e_name, E_named, U):
    e_set = E_named[e_name]
    not_in_e_set = U - e_set
    results = {}
    all_sets_list = list(E_named.values())  # TÜM KÜMELERİN VALUE'LERİ

    for element in not_in_e_set:
        total_sum = 0
        for other_element in e_set:
            pair = {element, other_element}
            count = sum(1 for s in all_sets_list if pair.issubset(s))  # TÜM SETLERDE SAY
            total_sum += count
        results[element] = total_sum
    return results
""")

print("ÖZELLİKLER:")
print("  ✅ all_sets_list = list(E_named.values()) → Sadece VALUE'ler (setler)")
print("  ✅ Kendi kümesinin KEY'i (e_name) dahil değil ama VALUE'si dahil!")
print("  ✅ Break YOK")
print("  ❓ Kendi kümesinin VALUE'si sayılıyor mu? EVET!")

print("\n" + "="*100)
print("V2 ARAYÜZ rmvc_app_v2.py DELTA FONKSİYONU")
print("="*100)
print("""
def delta_function(e_i, E_named, U):
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    results = {}
    
    for u in not_in_phi:
        delta_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            for e_j, phi_e_j in E_named.items():  # KEY ve VALUE ikisi de döner
                if pair.issubset(phi_e_j):
                    delta_sum += 1
        results[u] = delta_sum
    return results
""")

print("ÖZELLİKLER:")
print("  ✅ E_named.items() → (KEY, VALUE) çiftleri döner")
print("  ✅ e_j kontrolü YOK → Kendi kümesi dahil!")
print("  ✅ Break YOK")
print("  ❓ Kendi kümesi sayılıyor mu? EVET!")

print("\n" + "="*100)
print("MANTIKSAL KARŞILAŞTIRMA")
print("="*100)

# Hocanın kodu
def delta_hoca(e_name, E_named, U):
    e_set = E_named[e_name]
    not_in_e_set = U - e_set
    results = {}
    all_sets_list = list(E_named.values())

    for element in not_in_e_set:
        total_sum = 0
        for other_element in e_set:
            pair = {element, other_element}
            count = sum(1 for s in all_sets_list if pair.issubset(s))
            total_sum += count
        results[element] = total_sum
    return results

# V2 arayüz kodu
def delta_v2_ui(e_i, E_named, U):
    phi_e_i = E_named[e_i]
    not_in_phi = U - phi_e_i
    results = {}
    
    for u in not_in_phi:
        delta_sum = 0
        for v in phi_e_i:
            pair = {u, v}
            for e_j, phi_e_j in E_named.items():
                if pair.issubset(phi_e_j):
                    delta_sum += 1
        results[u] = delta_sum
    return results

# Test
e_test = 'e_2'
delta_h = delta_hoca(e_test, E_named, U)
delta_v2 = delta_v2_ui(e_test, E_named, U)

print(f"\nTEST: e_2 için delta hesabı")
print(f"Hocanın kodu: {delta_h}")
print(f"V2 arayüz:    {delta_v2}")

if delta_h == delta_v2:
    print("\n✅✅✅ İKİSİ DE AYNI SONUCU VERİYOR! ✅✅✅")
    print("\nSonuç: HOCANIN KODU = V2 ARAYÜZ")
    print("Kararı: V2 ile devam et!")
else:
    print("\n❌ FARKLI SONUÇLAR!")
    print(f"Hocanın: {delta_h}")
    print(f"V2:      {delta_v2}")

print("\n" + "="*100)
print("KRİTİK NOKTA ANALİZİ")
print("="*100)
print("""
HOCANIN KODU:
  all_sets_list = list(E_named.values())
  → Sadece VALUE'ler: [{'1','2','3','5'}, {'2','4','5'}, {'1','3','4'}, {'1','2','5'}]
  → e_2'nin kendisi bu listede VAR (çünkü value olarak)
  → Kendi kümesini SAYIYOR!

V2 ARAYÜZ:
  for e_j, phi_e_j in E_named.items():
  → (KEY, VALUE) çiftleri: [('e_1',set), ('e_2',set), ('e_3',set), ('e_4',set)]
  → e_j kontrolü yok
  → phi_e_j kullanılıyor (VALUE)
  → Kendi kümesini SAYIYOR!

SONUÇ: İKİSİ DE KENDİ KÜMESİNİ SAYIYOR, AYNI SONUÇLAR!
""")

print("\n" + "="*100)
print("FİNAL KARAR")
print("="*100)
print("""
✅ HOCANIN ORİJİNAL KODU (csvtormvc.py) = V2 ARAYÜZ (rmvc_app_v2.py)
✅ İkisi de kendi kümesini sayıyor
✅ İkisi de break kullanmıyor
✅ İkisi de aynı sonuçları veriyor

🎯 KARAR: V2 İLE DEVAM ET!
   - Port: 8515
   - Dosya: rmvc_app_v2.py
   - Hocanın orijinal metodolojisine uygun
   - GitHub'da zaten var
""")
