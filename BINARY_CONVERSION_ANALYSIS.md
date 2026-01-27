# Binary Dönüştürme Yöntemleri Analizi - Öneri Sistemleri için RMVC

**Tarih:** 27 Ocak 2026  
**Konu:** Rating verilerini binary matrise dönüştürme yöntemleri ve RMVC uygulaması

---

## 1. MEVCUT YÖNTEM: Eşik Tabanlı (Threshold-Based)

### 1.1 Uygulama

```python
# MovieLens için mevcut yöntem
binary_rating = 1 if rating >= 4 else 0
```

**Parametreler:**
- Rating aralığı: 1-5
- Eşik değeri: 4
- Sonuç: rating ∈ {4, 5} → 1, rating ∈ {1, 2, 3} → 0

### 1.2 Avantajlar ✅

1. **Basitlik:** Uygulaması çok kolay ve anlaşılır
2. **Yorumlanabilirlik:** "Kullanıcı bu filmi beğendi mi?" sorusuna net cevap
3. **Yaygın Kullanım:** Literatürde sıkça kullanılan standart yöntem
4. **Hesaplama Verimliliği:** Çok hızlı dönüşüm
5. **RMVC Uyumluluğu:** Soft set teorisi için ideal (0/1 değerleri)

### 1.3 Dezavantajlar ❌

1. **Bilgi Kaybı:** 
   - Rating 5 ile rating 4 aynı (ikisi de 1)
   - Rating 3 ile rating 1 aynı (ikisi de 0)
   - Beğeni derecesi bilgisi kaybolur

2. **Eşik Seçimi Subjektif:**
   - Neden 4? Neden 3.5 değil?
   - Farklı kullanıcılar farklı rating ölçekleri kullanabilir
   - Bazı kullanıcılar cömert, bazıları cimri puanlayabilir

3. **Sınır Durumları:**
   - Rating 3.9 → 0 (beğenmedi)
   - Rating 4.0 → 1 (beğendi)
   - Çok küçük fark büyük sonuç değişikliği

4. **Dengesiz Dağılım:**
   - MovieLens'te kullanıcılar genelde yüksek puan verir
   - Eşik 4 olunca çok fazla 1 olabilir
   - Matris çok yoğun olabilir

### 1.4 MovieLens İçin Uygunluk

**MovieLens Rating Dağılımı (Tipik):**
```
Rating 5: ~20%
Rating 4: ~35%  } → %55 pozitif (1)
Rating 3: ~25%  } → %45 negatif (0)
Rating 2: ~12%
Rating 1: ~8%
```

**Sonuç:** Eşik=4 ile yaklaşık %55 yoğunluk → Makul dengeli

---

## 2. ALTERNATİF YÖNTEMLER

### 2.1 Yöntem 1: Kullanıcı Bazlı Normalizasyon

**Fikir:** Her kullanıcının kendi ortalama rating'ine göre normalize et.

```python
# Her kullanıcı için
user_mean = ratings[user_id].mean()
binary_rating = 1 if rating > user_mean else 0
```

**Avantajlar:**
- Kullanıcılar arası rating ölçeği farklılıklarını giderir
- Cömert ve cimri puanlayıcıları dengeler
- Kişiselleştirilmiş eşik

**Dezavantajlar:**
- Her kullanıcı için farklı eşik
- Yorumlanması daha zor
- "Kullanıcının ortalamasının üstünde beğendi" anlamı

**RMVC için Uygunluk:** ⭐⭐⭐⭐ (İyi)

### 2.2 Yöntem 2: Medyan Tabanlı

**Fikir:** Tüm rating'lerin medyanını eşik olarak kullan.

```python
median_rating = all_ratings.median()  # MovieLens için ~3.5
binary_rating = 1 if rating >= median_rating else 0
```

**Avantajlar:**
- Veri odaklı eşik seçimi
- Dengeli dağılım garantisi (%50-%50)
- Outlier'lara karşı dayanıklı

**Dezavantajlar:**
- Veri setine bağımlı
- Farklı veri setlerinde farklı eşikler
- Anlamsal yorumlama zor

**RMVC için Uygunluk:** ⭐⭐⭐⭐ (İyi)

### 2.3 Yöntem 3: Üst Çeyrek (Top Quartile)

**Fikir:** En yüksek %25'lik dilimi 1 yap.

```python
threshold = ratings.quantile(0.75)  # Üst %25
binary_rating = 1 if rating >= threshold else 0
```

**Avantajlar:**
- "En çok beğenilenler" odaklı
- Seyrek matris garantisi (%25 yoğunluk)
- Öneri sistemleri için mantıklı (en iyileri öner)

**Dezavantajlar:**
- Çok seyrek matris olabilir
- Orta seviye beğeniler kaybolur
- RMVC için çok az veri

**RMVC için Uygunluk:** ⭐⭐⭐ (Orta)

### 2.4 Yöntem 4: İki Eşikli (Explicit Feedback)

**Fikir:** Açıkça beğenen ve beğenmeyenleri ayır, belirsizleri çıkar.

```python
if rating >= 4:
    binary_rating = 1  # Beğendi
elif rating <= 2:
    binary_rating = 0  # Beğenmedi
else:
    # Rating 3: Belirsiz, veri setinden çıkar
    exclude = True
```

**Avantajlar:**
- Net beğeni/beğenmeme ayrımı
- Belirsiz durumları ortadan kaldırır
- Daha güvenilir veri

**Dezavantajlar:**
- Veri kaybı (%25 rating 3 olabilir)
- Matris daha seyrek olur
- RMVC için daha az veri

**RMVC için Uygunluk:** ⭐⭐⭐⭐ (İyi)

### 2.5 Yöntem 5: Ağırlıklı Binary (Soft Binary)

**Fikir:** Tam binary yerine [0, 1] aralığında değerler kullan.

```python
# Min-Max normalizasyon
normalized_rating = (rating - 1) / (5 - 1)  # [0, 1] aralığına
# Veya sigmoid
soft_binary = 1 / (1 + exp(-(rating - 3)))
```

**Avantajlar:**
- Bilgi kaybı yok
- Rating derecesi korunur
- Daha zengin veri

**Dezavantajlar:**
- Artık tam binary değil
- RMVC soft set teorisi ile uyumlu mu? (Tartışmalı)
- Yorumlanması zor

**RMVC için Uygunluk:** ⭐⭐ (Düşük - Soft set teorisi 0/1 bekler)

### 2.6 Yöntem 6: İmplicit Feedback

**Fikir:** Rating değerini görmezden gel, sadece etkileşim olup olmadığına bak.

```python
binary_rating = 1 if rating exists else 0
```

**Avantajlar:**
- En basit yöntem
- Tüm rating'ler pozitif kabul edilir
- "İzledi/izlemedi" mantığı

**Dezavantajlar:**
- Rating bilgisi tamamen kaybolur
- Kötü filmler de 1 olur
- RMVC için çok yoğun matris

**RMVC için Uygunluk:** ⭐⭐ (Düşük)

---

## 3. YÖNTEM KARŞILAŞTIRMASI

| Yöntem | Eşik | Yoğunluk | Bilgi Kaybı | Yorumlanabilirlik | RMVC Uygunluk |
|--------|------|----------|-------------|-------------------|---------------|
| **Threshold (≥4)** | Sabit (4) | ~%55 | Orta | Yüksek | ⭐⭐⭐⭐⭐ |
| **User Normalized** | Değişken | ~%50 | Düşük | Orta | ⭐⭐⭐⭐ |
| **Median** | ~3.5 | %50 | Orta | Orta | ⭐⭐⭐⭐ |
| **Top Quartile** | Değişken | %25 | Yüksek | Yüksek | ⭐⭐⭐ |
| **Two-Threshold** | 2 ve 4 | ~%40 | Orta | Yüksek | ⭐⭐⭐⭐ |
| **Soft Binary** | - | %100 | Yok | Düşük | ⭐⭐ |
| **Implicit** | - | %100 | Çok Yüksek | Orta | ⭐⭐ |

---

## 4. ÖNERİ: RMVC İÇİN EN UYGUN YÖNTEM

### 4.1 Birincil Önerim: **Threshold (≥4)** - Mevcut Yöntem ✅

**Neden?**

1. **Soft Set Teorisi ile Tam Uyumlu:**
   - RMVC soft set teorisine dayanır
   - 0/1 değerleri beklenir
   - "Parametre elemanı içeriyor mu?" sorusuna net cevap

2. **Anlamsal Açıklık:**
   - "Kullanıcı filmi beğendi mi?" → Net cevap
   - Rating 4-5: Beğendi (pozitif feedback)
   - Rating 1-3: Beğenmedi veya nötr

3. **Literatür Desteği:**
   - Öneri sistemleri araştırmalarında standart
   - Karşılaştırma için ideal
   - Yaygın kabul görmüş

4. **Dengeli Dağılım:**
   - MovieLens için ~%55 yoğunluk
   - Ne çok yoğun ne çok seyrek
   - RMVC için optimal

5. **Basitlik:**
   - Uygulaması kolay
   - Hata payı düşük
   - Tekrarlanabilir

### 4.2 İkincil Önerim: **Two-Threshold (Explicit Feedback)**

**Ne Zaman Kullanılmalı?**
- Daha net sonuçlar istiyorsanız
- Rating 3'lerin belirsizliğinden kaçınmak istiyorsanız
- Daha seyrek ama daha güvenilir veri istiyorsanız

**Uygulama:**
```python
def two_threshold_conversion(rating):
    if rating >= 4:
        return 1  # Açıkça beğendi
    elif rating <= 2:
        return 0  # Açıkça beğenmedi
    else:
        return None  # Belirsiz, çıkar
```

### 4.3 Deneysel Önerim: **User Normalized**

**Ne Zaman Kullanılmalı?**
- Kullanıcılar arası rating ölçeği farklılıkları varsa
- Daha kişiselleştirilmiş sonuçlar istiyorsanız
- Araştırma amaçlı karşılaştırma yapıyorsanız

---

## 5. UYGULAMA PLANI

### 5.1 Temel Test: Threshold (≥4)

```python
# Mevcut yöntem - değişiklik yok
df_binary = (df_ratings >= 4).astype(int)
```

**Beklenen Sonuç:**
- MovieLens 100K: ~%55 yoğunluk
- Dengeli matris
- RMVC ile uyumlu

### 5.2 Karşılaştırmalı Test: 3 Yöntem

```python
# 1. Threshold ≥4
binary_v1 = (df_ratings >= 4).astype(int)

# 2. User Normalized
user_means = df_ratings.mean(axis=1)
binary_v2 = (df_ratings.T > user_means).T.astype(int)

# 3. Two-Threshold
binary_v3 = df_ratings.copy()
binary_v3[binary_v3 >= 4] = 1
binary_v3[binary_v3 <= 2] = 0
binary_v3[(binary_v3 > 0) & (binary_v3 < 1)] = np.nan
binary_v3 = binary_v3.dropna(how='all', axis=1).dropna(how='all', axis=0)
```

**Karşılaştırma Metrikleri:**
- Matris yoğunluğu
- RMVC skorları dağılımı
- İteratif yakınsama davranışı
- Optimal seçim tutarlılığı

---

## 6. SONUÇ VE TAVSİYE

### 6.1 Kısa Vadeli (Şu An)

**Mevcut yöntemi kullanmaya devam edin: Rating ≥ 4 → 1**

**Gerekçe:**
- ✅ RMVC soft set teorisi ile tam uyumlu
- ✅ Anlamsal olarak net ve yorumlanabilir
- ✅ Literatürde yaygın kullanım
- ✅ Dengeli matris yoğunluğu
- ✅ Basit ve güvenilir

### 6.2 Orta Vadeli (Araştırma Geliştirme)

**3 yöntemi karşılaştırın:**
1. Threshold (≥4) - Baseline
2. User Normalized - Kişiselleştirilmiş
3. Two-Threshold - Explicit feedback

**Karşılaştırma Kriterleri:**
- RMVC skorlarının tutarlılığı
- İteratif yakınsama hızı
- Optimal seçim kalitesi
- Hesaplama maliyeti

### 6.3 Uzun Vadeli (Makale)

**Makalede tartışın:**
- Binary dönüşüm yöntemlerinin RMVC sonuçlarına etkisi
- Farklı eşik değerlerinin karşılaştırması
- Soft set teorisi bağlamında en uygun yöntem
- Öneri sistemleri için best practice

---

## 7. DETAYLI ÖRNEK: MovieLens 100K

### 7.1 Veri İstatistikleri

**Orijinal Rating Dağılımı:**
```
Rating 5: 21,201 (%21.2)
Rating 4: 34,174 (%34.2)  } → 55,375 (%55.4) → 1
Rating 3: 27,145 (%27.1)  } → 44,625 (%44.6) → 0
Rating 2: 11,370 (%11.4)
Rating 1:  6,110 (%6.1)
```

### 7.2 Threshold ≥4 Sonuçları

**Binary Matris:**
- Boyut: 943 kullanıcı × 1682 film
- Toplam hücre: 1,586,126
- 1'lerin sayısı: 55,375
- Yoğunluk: %3.49 (çok seyrek!)
- Seyreklik: %96.51

**Not:** Matris çok seyrek çünkü her kullanıcı az film izlemiş (ortalama ~106 film/kullanıcı).

### 7.3 Alt Küme Sonuçları

| Alt Küme | Boyut | 1'ler | Yoğunluk | Seyreklik |
|----------|-------|-------|----------|-----------|
| 10×5 | 50 | 45 | %90 | %10 |
| 20×10 | 200 | 166 | %83 | %17 |
| 30×15 | 450 | 351 | %78 | %22 |
| 50×25 | 1,250 | 862 | %69 | %31 |
| 100×50 | 5,000 | 3,017 | %60 | %40 |

**Gözlem:** En aktif kullanıcılar ve popüler filmler seçildiği için yoğunluk artıyor.

---

## 8. SONUÇ

**Mevcut yöntem (Rating ≥ 4 → 1) RMVC için uygundur ve değiştirilmesine gerek yoktur.**

**Ancak araştırma amaçlı olarak alternatif yöntemleri de test etmek faydalı olacaktır.**

---

**Hazırlayan:** Cascade AI  
**Tarih:** 27 Ocak 2026
