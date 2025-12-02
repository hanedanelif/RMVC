# -*- coding: utf-8 -*-
"""
RMVC-csv.py - CSV Dosyasından RMVC Analizi
==========================================
CSV veya Excel dosyasından veri okuyarak RMVC (Rough Multi-Valued Choice) 
algoritmasını otomatik çalıştırır.

Kullanım:
    python RMVC-csv.py
    veya
    python RMVC-csv.py dosya.csv
"""

import pandas as pd
from fractions import Fraction
from io import StringIO
import sys
import os


def csv_to_soft_set(csv_data):
    """
    CSV verisini Soft Set formatına dönüştürür.
    
    CSV Formatı:
    - İlk sütun: Satır ID'leri (Firma ID vb.)
    - İlk satır: Sütun başlıkları (Ürün ID vb.)
    - Değerler: 0 = ilişki yok, >0 = ilişki var
    
    Returns:
        U: Evren kümesi (tüm satır ID'leri)
        E_named: Kriter kümeleri sözlüğü {e_1: {elemanlar}, e_2: {...}, ...}
    """
    # CSV'yi DataFrame'e oku
    if isinstance(csv_data, str):
        df = pd.read_csv(StringIO(csv_data), index_col=0)
    else:
        df = csv_data
    
    # Satır ve sütun ID'lerini al
    satir_ids = df.index.tolist()
    sutun_ids = df.columns.tolist()
    
    # U kümesi: Tüm satır ID'leri (string olarak)
    U = set(str(sid) for sid in satir_ids)
    
    # E kümeleri: Her sütun bir kriter kümesi
    E_named = {}
    for i, sutun_id in enumerate(sutun_ids):
        e_key = f"e_{i+1}"
        sutun_verisi = df[sutun_id]
        
        # Değeri > 0 olan satırları bu kümeye ekle
        alt_kume = set()
        for satir_id, deger in sutun_verisi.items():
            try:
                if pd.to_numeric(deger, errors='coerce') > 0:
                    alt_kume.add(str(satir_id))
            except:
                pass
        
        E_named[e_key] = alt_kume
    
    # Eşleştirme bilgilerini yazdır
    print("\n" + "="*60)
    print("CSV -> SOFT SET DÖNÜŞÜMÜ")
    print("="*60)
    print(f"\n📊 Evren Kümesi U ({len(U)} eleman):")
    print(f"   {sorted(U, key=lambda x: int(x) if x.isdigit() else x)}")
    
    print(f"\n📋 Kriter Kümeleri E ({len(E_named)} kriter):")
    for e_key, alt_kume in E_named.items():
        sutun_idx = int(e_key.split('_')[1]) - 1
        orijinal_ad = sutun_ids[sutun_idx]
        print(f"   {e_key} (Sütun: {orijinal_ad}): {len(alt_kume)} eleman")
    
    return U, E_named, satir_ids, sutun_ids


def delta_function(e_name, E_named, U):
    """Delta fonksiyonu: Bir kümeye ait olmayan elemanların yakınlık değerini hesaplar."""
    e_set = E_named[e_name]
    not_in_e_set = U - e_set
    results = {}
    
    for element in not_in_e_set:
        total_sum = 0
        for other_element in e_set:
            for other_e_set in E_named.values():
                if {element, other_element}.issubset(other_e_set):
                    total_sum += 1
                    break  # Her küme için sadece bir kez say
        results[element] = total_sum
    
    return results


def create_membership_matrix(E_named, U):
    """Üyelik matrisini oluşturur."""
    membership_matrix = {e_key: {} for e_key in E_named.keys()}
    m = len(E_named)  # Toplam kriter sayısı
    
    for e_key in E_named.keys():
        e_set = E_named[e_key]
        delta_results = delta_function(e_key, E_named, U)
        
        # Normalizasyon katsayısı: |e_i| × (m - 1)
        g_coeff = len(e_set) * (m - 1) if len(e_set) > 0 and m > 1 else 1
        
        for element in U:
            if element in e_set:
                membership_value = 1  # Tam üyelik
            elif element in delta_results and g_coeff > 0:
                membership_value = Fraction(delta_results[element], g_coeff)
            else:
                membership_value = 0
            
            membership_matrix[e_key][element] = membership_value
    
    return membership_matrix


def get_sum_of_column(column_element, matrix):
    """Bir elemanın toplam skorunu hesaplar."""
    total = 0
    for row in matrix.values():
        if column_element in row:
            total += float(row[column_element])
    return round(total, 4)


def create_sum_dictionary(matrix):
    """Tüm elemanların skor sözlüğünü oluşturur."""
    elements = set()
    for row in matrix.values():
        elements.update(row.keys())
    
    return {element: get_sum_of_column(element, matrix) for element in elements}


def get_best_choices(matrix):
    """En yüksek skora sahip elemanları bulur."""
    scores = create_sum_dictionary(matrix)
    if not scores:
        return [], 0
    
    max_score = max(scores.values())
    best = [elem for elem, score in scores.items() if score == max_score]
    return best, max_score


def print_results(membership_matrix, U, E_named, satir_ids, sutun_ids):
    """Sonuçları formatlanmış şekilde yazdırır."""
    
    print("\n" + "="*60)
    print("RMVC ANALİZ SONUÇLARI")
    print("="*60)
    
    # Skor hesaplama
    scores = create_sum_dictionary(membership_matrix)
    
    # Skorları sırala (yüksekten düşüğe)
    sorted_scores = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    
    print("\n📈 ELEMAN SKORLARI (Yüksekten Düşüğe):")
    print("-" * 40)
    print(f"{'Sıra':<6}{'Eleman':<15}{'Skor':<12}{'Durum'}")
    print("-" * 40)
    
    max_score = sorted_scores[0][1] if sorted_scores else 0
    
    for i, (elem, score) in enumerate(sorted_scores[:20], 1):  # İlk 20'yi göster
        status = "⭐ EN İYİ" if score == max_score else ""
        print(f"{i:<6}{elem:<15}{score:<12.4f}{status}")
    
    if len(sorted_scores) > 20:
        print(f"... ve {len(sorted_scores) - 20} eleman daha")
    
    # En iyi seçimler
    best_choices, best_score = get_best_choices(membership_matrix)
    
    print("\n" + "="*60)
    print("🏆 KARAR")
    print("="*60)
    print(f"\n✅ En Yüksek Skor: {best_score:.4f}")
    print(f"✅ Optimal Seçim(ler): {best_choices}")
    
    if len(best_choices) > 1:
        print(f"\n⚠️  {len(best_choices)} eleman eşit skora sahip.")
        print("   Ek kriterlerle aralarında seçim yapılabilir.")
    
    # İstatistikler
    print("\n📊 İSTATİSTİKLER:")
    print(f"   - Toplam eleman sayısı: {len(U)}")
    print(f"   - Toplam kriter sayısı: {len(E_named)}")
    print(f"   - Ortalama skor: {sum(scores.values())/len(scores):.4f}")
    print(f"   - Min skor: {min(scores.values()):.4f}")
    print(f"   - Max skor: {max(scores.values()):.4f}")
    
    return scores, best_choices


def run_rmvc_from_csv(csv_source):
    """
    CSV kaynağından RMVC analizi çalıştırır.
    
    Args:
        csv_source: Dosya yolu (str) veya CSV içeriği (str)
    """
    # CSV'yi oku
    if os.path.isfile(csv_source):
        print(f"\n📁 Dosya okunuyor: {csv_source}")
        df = pd.read_csv(csv_source, index_col=0)
    elif csv_source.endswith('.xlsx') or csv_source.endswith('.xls'):
        print(f"\n📁 Excel dosyası okunuyor: {csv_source}")
        df = pd.read_excel(csv_source, index_col=0)
    else:
        # String olarak CSV içeriği
        df = pd.read_csv(StringIO(csv_source), index_col=0)
    
    # Soft Set'e dönüştür
    U, E_named, satir_ids, sutun_ids = csv_to_soft_set(df)
    
    # Boş kümeleri filtrele (opsiyonel)
    E_named_filtered = {k: v for k, v in E_named.items() if len(v) > 0}
    
    if len(E_named_filtered) < 2:
        print("\n❌ HATA: En az 2 boş olmayan kriter kümesi gerekli!")
        print(f"   Mevcut boş olmayan küme sayısı: {len(E_named_filtered)}")
        return None, None
    
    print(f"\n⚙️  {len(E_named_filtered)} kriter ile RMVC hesaplanıyor...")
    
    # Üyelik matrisini hesapla
    membership_matrix = create_membership_matrix(E_named_filtered, U)
    
    # Sonuçları yazdır
    scores, best_choices = print_results(
        membership_matrix, U, E_named_filtered, satir_ids, sutun_ids
    )
    
    return scores, best_choices


# ============================================================
# ANA ÇALIŞTIRMA BLOĞU
# ============================================================

if __name__ == "__main__":
    
    # Komut satırından dosya adı verilmişse onu kullan
    if len(sys.argv) > 1:
        dosya_yolu = sys.argv[1]
        if os.path.isfile(dosya_yolu):
            run_rmvc_from_csv(dosya_yolu)
        else:
            print(f"❌ Dosya bulunamadı: {dosya_yolu}")
    
    else:
        # Varsayılan: Örnek veri ile çalıştır
        print("\n" + "="*60)
        print("RMVC-CSV: CSV'den Otomatik RMVC Analizi")
        print("="*60)
        print("\nKullanım:")
        print("  python RMVC-csv.py dosya.csv")
        print("  python RMVC-csv.py dosya.xlsx")
        print("\nŞimdi örnek veri ile çalıştırılıyor...")
        
        # Örnek CSV verisi (hocanızın verdiği)
        ornek_csv = """FirmaID,52757,88109,3350,64670,120333,105628,61375,24349,117567,118605,107321,113309,73320,3347,40640,17226,78845,93712,3190,119476
6567,0,0,0,0,0,0,9800,0,0,0,0,0,0,0,0,0,0,0,0,0
5871,0,24700,0,0,0,24590,1600,0,4260,0,0,2170,0,0,0,0,2850,0,0,0
4775,0,0,3400,17450,0,0,0,0,6250,0,0,0,0,0,0,0,0,0,370150,0
8179,13900,0,0,0,0,0,0,26850,0,0,2000,1000,0,0,0,0,0,0,0,0
974,0,1100,0,4500,0,0,0,0,0,0,1500,0,0,0,0,0,0,3645,0,2907
713,0,0,0,0,0,0,0,0,0,0,1375,0,0,0,0,0,0,0,0,0
3797,28500,0,0,0,0,0,0,0,0,0,1000,1200,0,0,0,0,1200,18500,0,500
5096,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
5815,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
897,100903,0,0,0,55000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
2027,0,23570,0,500,0,0,0,4900,1200,0,0,0,0,0,0,0,0,0,17465,0
3008,0,0,16000,0,0,0,0,0,0,1900,0,0,0,0,0,0,0,0,0,0
872,0,0,0,0,0,0,1200,0,0,5950,0,0,0,0,1300,0,0,0,0,0
9975,5500,0,0,0,0,1500,0,0,0,600,0,0,0,0,0,0,0,0,0,0
2537,0,0,0,4800,0,0,0,75425,0,0,0,0,0,0,0,0,0,0,0,0
2842,4000,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,19550,0,0
5336,0,0,0,0,0,0,112750,0,0,0,0,0,0,0,0,0,4100,0,0,0
6885,0,1600,6000,0,0,0,443279,0,0,0,0,0,0,0,0,0,0,0,0,0
9206,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
6372,0,7450,0,0,0,0,0,5500,0,0,0,0,0,6100,0,0,0,0,1000,0"""
        
        run_rmvc_from_csv(ornek_csv)
