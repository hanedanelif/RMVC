# İteratif RMVC Yakınsama Analizi - Example.1

**Tarih:** 20 Ocak 2026  
**Veri Seti:** Example.1.xlsx (4 parametre × 5 eleman)  
**Strateji:** Her iterasyonda ondalıklı değerlerin ortalamasını eşik olarak kullan (>= operatörü, Binary mod)  
**Hedef:** Tüm üyelik değerlerini 1 veya 0'a dönüştürmek (yakınsama)

---

## 📊 Özet

| Metrik | Değer |
|--------|-------|
| Toplam İterasyon Sayısı | **2** |
| Başlangıç Ondalıklı Değer Sayısı | 13 |
| Yakınsama Durumu | ✅ **Başarılı** (Tüm değerler 0 veya 1) |
| Toplam Matris Elemanı | 20 (4 parametre × 5 eleman) |

---

## 🔄 İterasyon 0 (Başlangıç)

### Genel İstatistikler
- **Toplam Değer:** 20
- **0 Sayısı:** 7
- **1 Sayısı:** 0
- **Ondalıklı Sayısı:** 13

### Ondalıklı Değerler İstatistikleri (0 ve 1 hariç)
| İstatistik | Değer |
|------------|-------|
| Min | 0.4444 |
| Max | 0.8889 |
| **Ortalama** | **0.6902** |
| Std Sapma | 0.1489 |
| Adet | 13 |

### Üyelik Matrisi

|  | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **e_1** | 0.7500 | 0.7500 | 0.5000 | 0.0000 | 0.7500 |
| **e_2** | 0.0000 | 0.7778 | 0.0000 | 0.4444 | 0.7778 |
| **e_3** | 0.6667 | 0.0000 | 0.5556 | 0.4444 | 0.0000 |
| **e_4** | 0.7778 | 0.8889 | 0.0000 | 0.0000 | 0.8889 |

### Değer Dağılımı
- **0.0000:** 7 adet (35.0%)
- **0.4444:** 2 adet (10.0%)
- **0.5000:** 1 adet (5.0%)
- **0.5556:** 1 adet (5.0%)
- **0.6667:** 1 adet (5.0%)
- **0.7500:** 3 adet (15.0%)
- **0.7778:** 3 adet (15.0%)
- **0.8889:** 2 adet (10.0%)

---

## 🔄 İterasyon 1

### Eşikleme Parametreleri
- **Eşik Değeri:** 0.6902 (Ondalıklı değerlerin ortalaması)
- **Operatör:** >= (Büyük eşit)
- **Mod:** Binary (Eşik altı 0'a dönüşür)

### Eşikleme Etkisi
- **Değer >= 0.6902 → 1:** 8 değer
- **Değer < 0.6902 → 0:** 5 değer

### Genel İstatistikler
- **Toplam Değer:** 20
- **0 Sayısı:** 12 (+5)
- **1 Sayısı:** 2 (+2)
- **Ondalıklı Sayısı:** 6 (-7)

### Ondalıklı Değerler İstatistikleri (0 ve 1 hariç)
| İstatistik | Değer | Değişim |
|------------|-------|---------|
| Min | 0.6667 | +0.2223 |
| Max | 0.8889 | 0.0000 |
| **Ortalama** | **0.8148** | **+0.1246** |
| Std Sapma | 0.1048 | -0.0441 |
| Adet | 6 | -7 |

### Üyelik Matrisi

|  | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **e_1** | 0.6667 | 0.8889 | 0.0000 | 0.0000 | 0.8889 |
| **e_2** | 0.0000 | **1.0000** | 0.0000 | 0.0000 | **1.0000** |
| **e_3** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| **e_4** | 0.6667 | 0.8889 | 0.0000 | 0.0000 | 0.8889 |

### Değer Dağılımı
- **0.0000:** 12 adet (60.0%)
- **0.6667:** 2 adet (10.0%)
- **0.8889:** 4 adet (20.0%)
- **1.0000:** 2 adet (10.0%)

### Gözlemler
- ✅ İlk kez **1.0000** değerleri ortaya çıktı (e_2 parametresinde)
- ✅ Ondalıklı değer sayısı 13'ten 6'ya düştü (%54 azalma)
- ⚠️ e_3 parametresi tamamen 0'a dönüştü (tüm elemanlarla ilişkisi kesildi)
- 📈 Ortalama 0.6902'den 0.8148'e yükseldi (daha homojen)

---

## 🔄 İterasyon 2

### Eşikleme Parametreleri
- **Eşik Değeri:** 0.8148 (Ondalıklı değerlerin ortalaması)
- **Operatör:** >= (Büyük eşit)
- **Mod:** Binary (Eşik altı 0'a dönüşür)

### Eşikleme Etkisi
- **Değer >= 0.8148 → 1:** 4 değer (0.8889 değerleri)
- **Değer < 0.8148 → 0:** 2 değer (0.6667 değerleri)

### Genel İstatistikler
- **Toplam Değer:** 20
- **0 Sayısı:** 14 (+2)
- **1 Sayısı:** 6 (+4)
- **Ondalıklı Sayısı:** 0 (-6) ✅

### Üyelik Matrisi (Final)

|  | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **e_1** | 0.0000 | **1.0000** | 0.0000 | 0.0000 | **1.0000** |
| **e_2** | 0.0000 | **1.0000** | 0.0000 | 0.0000 | **1.0000** |
| **e_3** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| **e_4** | 0.0000 | **1.0000** | 0.0000 | 0.0000 | **1.0000** |

### Değer Dağılımı
- **0.0000:** 14 adet (70.0%)
- **1.0000:** 6 adet (30.0%)

### Gözlemler
- ✅ **Yakınsama tamamlandı!** Tüm değerler 0 veya 1
- ✅ Ondalıklı değer kalmadı
- 📊 Final durumda sadece 2 ve 5 numaralı elemanlar seçildi (tüm parametrelerde)
- ⚠️ e_3 parametresi hala tamamen 0 (hiçbir elemanla ilişkisi yok)

---

## 📈 Yakınsama Grafiği

### Ondalıklı Değer Sayısı (İterasyon Bazında)

```
İterasyon 0: ████████████████████████████ 13 ondalıklı değer
İterasyon 1: ████████████ 6 ondalıklı değer (-54%)
İterasyon 2: 0 ondalıklı değer (-100%) ✅ YAKINSAMA
```

### Ortalama Değer Değişimi

```
İterasyon 0: 0.6902
İterasyon 1: 0.8148 (+18.1%)
İterasyon 2: N/A (Sadece 0 ve 1)
```

---

## 🎯 Sonuç ve Yorumlar

### Yakınsama Başarısı
✅ **2 iterasyonda yakınsama sağlandı**

Strateji olarak her iterasyonda ondalıklı değerlerin ortalamasını eşik olarak kullanmak (>= operatörü ile) başarılı oldu. Sistem hızlı bir şekilde binary duruma yakınsadı.

### Final Durum Analizi

**Seçilen Elemanlar:**
- **Eleman 2:** Tüm parametreler tarafından seçildi (e_1, e_2, e_4)
- **Eleman 5:** Tüm parametreler tarafından seçildi (e_1, e_2, e_4)

**Seçilmeyen Elemanlar:**
- **Eleman 1:** Hiçbir parametre tarafından seçilmedi
- **Eleman 3:** Hiçbir parametre tarafından seçilmedi
- **Eleman 4:** Hiçbir parametre tarafından seçilmedi

**Parametre Durumu:**
- **e_1, e_2, e_4:** Her biri 2 ve 5 numaralı elemanları seçti
- **e_3:** Hiçbir eleman seçmedi (tamamen boş küme)

### Stratejik Öneriler

1. **Hızlı Yakınsama İçin:**
   - Ondalıklı değerlerin ortalamasını eşik olarak kullanmak etkili
   - >= operatörü, eşik değerine eşit olanları da dönüştürdüğü için daha agresif yakınsama sağlar

2. **Boş Parametre Problemi:**
   - e_3 parametresi 1. iterasyonda tamamen boş kaldı
   - Bu, bazı parametrelerin çok zayıf ilişkilere sahip olduğunu gösterir
   - Gerçek uygulamalarda bu tür parametrelerin filtrelenmesi gerekebilir

3. **Eleman Konsantrasyonu:**
   - Final durumda sadece 2 eleman (2 ve 5) seçildi
   - Bu, sistemin güçlü konsensüs gösterdiği elemanları vurguladı
   - Ancak çeşitlilik azaldı (5 elemandan 2'si kaldı)

### Karşılaştırma: Farklı Stratejiler

| Strateji | İterasyon Sayısı | Final Eleman Sayısı | Boş Parametre |
|----------|------------------|---------------------|---------------|
| **Ortalama >= (Bu analiz)** | 2 | 2 | 1 |
| Sabit 0.5 >= | ? | ? | ? |
| Ortalama > | ? | ? | ? |

---

## 🔬 Teknik Detaylar

### Kullanılan Algoritma
- **RMVC (Relational Membership Value Calculation)**
- **Eşikleme:** Binary mod (eşik altı → 0, eşik üstü → 1)
- **Operatör:** >= (büyük eşit)
- **Eşik Seçimi:** Dinamik (her iterasyonda ondalıklı değerlerin ortalaması)

### Kayan Nokta Hassasiyeti
- Epsilon değeri: 1e-9
- >= operatöründe: `val >= (threshold - epsilon)`
- Bu sayede 0.6667 >= 0.6667 karşılaştırması doğru çalışır

### Veri Yapısı
- **Başlangıç:** 4×5 binary matris (0 ve 1)
- **İterasyon 0:** 4×5 üyelik matrisi (Fraction değerleri)
- **İterasyon 1-2:** Eşikleme + yeni RMVC hesaplama

---

## 📚 Referanslar

- **Veri Seti:** `Example.1.xlsx`
- **Kod:** `iterative_analysis_example1.py`
- **Sonuçlar:** `iterative_analysis_results.json`
- **GitHub:** https://github.com/hanedanelif/RMVC

---

**Analiz Tarihi:** 20 Ocak 2026  
**Analiz Eden:** Cascade AI  
**Versiyon:** v2026.01.20-stable
