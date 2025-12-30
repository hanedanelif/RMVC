# 🔄 İteratif RMVC Analizi - Eşik Modu Karşılaştırması

## 📋 Analiz Özeti

**Veri Seti:** Example 1 (4 parametre × 5 eleman)  
**Eşik Değeri:** 0.50  
**Karşılaştırılan Modlar:**
- **Mixed Mod:** Eşik altındaki değerler aynı kalır
- **Binary Mod:** Eşik altındaki değerler 0'a dönüşür

---

## 📊 İterasyon 0 (Başlangıç)

### Orijinal Binary Matris
```
       1    2    3    4    5
e_1    1    1    1    0    1
e_2    0    1    0    1    1
e_3    1    0    1    1    0
e_4    1    1    0    0    1
```

### İlk Üyelik Matrisi
```
       1       2       3       4       5
e_1  1.0000  1.0000  1.0000  0.3333  1.0000
e_2  0.5556  1.0000  0.3333  1.0000  1.0000
e_3  1.0000  0.4444  1.0000  1.0000  0.4444
e_4  1.0000  1.0000  0.4444  0.3333  1.0000
```

### İlk Skorlar ve Sıralama
| Rank | Eleman | Skor   | Açıklama |
|------|--------|--------|----------|
| 1    | 1      | 3.5556 | En iyi   |
| 2    | 2      | 3.4444 |          |
| 3    | 5      | 3.4444 |          |
| 4    | 3      | 2.7778 |          |
| 5    | 4      | 2.6667 | En kötü  |

---

## 🟡 MOD 1: Mixed (Eşik Altı Aynı Kalır)

### Eşik: 0.50 | Mod: Mixed

#### Eşikleme Kuralı
- **Değer > 0.50** → **1** (Güçlü ilişki)
- **Değer ≤ 0.50** → **Aynı kalır** (Zayıf ilişki korunur)

#### İterasyon 1 - Eşiklenmiş Matris
```
       1       2       3       4       5
e_1    1       1       1    0.3333     1
e_2    1       1    0.3333     1       1
e_3    1    0.4444     1       1    0.4444
e_4    1       1    0.4444  0.3333     1
```

**Değişiklikler:**
- ✅ 16 değer 1'e dönüştü (eşik üzeri)
- 🔄 4 değer aynı kaldı (0.3333, 0.4444)

#### İterasyon 1 - Yeni Üyelik Matrisi
```
       1    2    3    4    5
e_1    1    1    1    1    1
e_2    1    1    1    1    1
e_3    1    1    1    1    1
e_4    1    1    1    1    1
```

**Sonuç:** Tüm elemanlar tüm parametrelere tam üye oldu!

#### İterasyon 1 - Yeni Skorlar
| Rank | Eleman | Eski Skor | Yeni Skor | Değişim |
|------|--------|-----------|-----------|---------|
| 1    | 1      | 3.5556    | 4.0000    | +0.4444 |
| 2    | 2      | 3.4444    | 4.0000    | +0.5556 |
| 3    | 5      | 3.4444    | 4.0000    | +0.5556 |
| 4    | 3      | 2.7778    | 4.0000    | +1.2222 |
| 5    | 4      | 2.6667    | 4.0000    | +1.3333 |

**Gözlem:** Tüm skorlar 4.0'a eşitlendi, zayıf elemanlar en çok kazandı.

#### Sıralama Değişimleri (İterasyon 0 → 1)
| Eleman | Eski Rank | Yeni Rank | Değişim | Durum       |
|--------|-----------|-----------|---------|-------------|
| 1      | 1         | 1         | =       | ⚪ Aynı     |
| 2      | 2         | 2         | =       | ⚪ Aynı     |
| 5      | 3         | 5         | ↓ -2    | 🔴 Düştü    |
| 3      | 4         | 3         | ↑ +1    | 🟢 Yükseldi |
| 4      | 5         | 4         | ↑ +1    | 🟢 Yükseldi |

**Özet:**
- 🟢 Yükselenler: 2 eleman (3, 4)
- 🔴 Düşenler: 1 eleman (5)
- ⚪ Aynı kalanlar: 2 eleman (1, 2)

---

## 🔴 MOD 2: Binary (Eşik Altı 0'a Dönüşür)

### Eşik: 0.50 | Mod: Binary

#### Eşikleme Kuralı
- **Değer > 0.50** → **1** (Güçlü ilişki)
- **Değer ≤ 0.50** → **0** (Zayıf ilişki kesilir)

#### İterasyon 1 - Eşiklenmiş Matris
```
       1    2    3    4    5
e_1    1    1    1    0    1
e_2    1    1    0    1    1
e_3    1    0    1    1    0
e_4    1    1    0    0    1
```

**Değişiklikler:**
- ✅ 16 değer 1'e dönüştü (eşik üzeri)
- ❌ 4 değer 0'a dönüştü (0.3333 → 0, 0.4444 → 0)

#### İterasyon 1 - Yeni Üyelik Matrisi
```
       1       2       3       4       5
e_1    1       1       1    0.4167     1
e_2    1       1    0.4167     1       1
e_3    1    0.5556     1       1    0.5556
e_4    1       1       1    0.4444     1
```

**Sonuç:** Yeni üyelik değerleri oluştu, tam homojenlik yok.

#### İterasyon 1 - Yeni Skorlar
| Rank | Eleman | Eski Skor | Yeni Skor | Değişim |
|------|--------|-----------|-----------|---------|
| 1    | 1      | 3.5556    | 4.0000    | +0.4444 |
| 2    | 2      | 3.4444    | 3.5556    | +0.1112 |
| 3    | 5      | 3.4444    | 3.5556    | +0.1112 |
| 4    | 3      | 2.7778    | 2.8611    | +0.0833 |
| 5    | 4      | 2.6667    | 2.8611    | +0.1944 |

**Gözlem:** Skorlar farklılaştı, sıralama korundu.

#### Sıralama Değişimleri (İterasyon 0 → 1)
| Eleman | Eski Rank | Yeni Rank | Değişim | Durum    |
|--------|-----------|-----------|---------|----------|
| 1      | 1         | 1         | =       | ⚪ Aynı  |
| 2      | 2         | 2         | =       | ⚪ Aynı  |
| 3      | 4         | 4         | =       | ⚪ Aynı  |
| 4      | 5         | 5         | =       | ⚪ Aynı  |
| 5      | 3         | 3         | =       | ⚪ Aynı  |

**Özet:**
- 🟢 Yükselenler: 0 eleman
- 🔴 Düşenler: 0 eleman
- ⚪ Aynı kalanlar: 5 eleman (TÜM ELEMANLAR)

---

## 🔬 Karşılaştırmalı Analiz

### 1. Eşikleme Etkisi

| Özellik | Mixed Mod | Binary Mod |
|---------|-----------|------------|
| **Eşik üzeri değerler** | 1'e dönüşür | 1'e dönüşür |
| **Eşik altı değerler** | Aynı kalır (0.3333, 0.4444) | 0'a dönüşür |
| **Kesilen ilişki sayısı** | 0 | 4 |
| **Korunan zayıf ilişki** | 4 | 0 |

### 2. Yeni Üyelik Matrisi

| Özellik | Mixed Mod | Binary Mod |
|---------|-----------|------------|
| **Homojenlik** | Tam homojen (hepsi 1) | Heterojen (farklı değerler) |
| **Min değer** | 1.0000 | 0.4167 |
| **Max değer** | 1.0000 | 1.0000 |
| **Ortalama** | 1.0000 | 0.8417 |
| **Std sapma** | 0.0000 | 0.2441 |

### 3. Skor Değişimleri

| Eleman | İterasyon 0 | Mixed (İter 1) | Binary (İter 1) | Mixed Δ | Binary Δ |
|--------|-------------|----------------|-----------------|---------|----------|
| 1      | 3.5556      | 4.0000         | 4.0000          | +0.4444 | +0.4444  |
| 2      | 3.4444      | 4.0000         | 3.5556          | +0.5556 | +0.1112  |
| 3      | 2.7778      | 4.0000         | 2.8611          | +1.2222 | +0.0833  |
| 4      | 2.6667      | 4.0000         | 2.8611          | +1.3333 | +0.1944  |
| 5      | 3.4444      | 4.0000         | 3.5556          | +0.5556 | +0.1112  |

**Gözlem:**
- **Mixed Mod:** Zayıf elemanlar (3, 4) en çok kazandı (+1.22, +1.33)
- **Binary Mod:** Tüm elemanlar az kazandı (+0.08 ile +0.44 arası)

### 4. Sıralama Değişimleri

| Mod | Yükselenler | Düşenler | Aynı Kalanlar |
|-----|-------------|----------|---------------|
| **Mixed** | 2 (Eleman 3, 4) | 1 (Eleman 5) | 2 (Eleman 1, 2) |
| **Binary** | 0 | 0 | 5 (TÜM ELEMANLAR) |

**Kritik Fark:** Binary modda sıralama hiç değişmedi!

### 5. Sıralama Kararlılığı

| Özellik | Mixed Mod | Binary Mod |
|---------|-----------|------------|
| **Sıralama değişimi** | Var (3 eleman etkilendi) | Yok (tüm elemanlar aynı) |
| **Rank korelasyonu** | 0.80 (orta) | 1.00 (mükemmel) |
| **Kararlılık** | Düşük | Yüksek |

---

## 💡 Sonuçlar ve Yorumlar

### Mixed Mod (Eşik Altı Aynı Kalır)

**Avantajlar:**
- ✅ Zayıf ilişkiler korunur, bilgi kaybı az
- ✅ Zayıf elemanlar şans bulur
- ✅ Sıralama değişimi gözlemlenebilir

**Dezavantajlar:**
- ❌ Aşırı homojenleşme (tüm skorlar eşitlendi)
- ❌ Ayırt edicilik kaybı
- ❌ Sıralama belirsizliği artar

**Kullanım Senaryosu:**
- Zayıf ilişkilerin de önemli olduğu durumlar
- İkinci şans vermek istediğiniz elemanlar
- Keşifsel analiz

### Binary Mod (Eşik Altı 0'a Dönüşür)

**Avantajlar:**
- ✅ Sıralama kararlılığı (hiç değişmedi)
- ✅ Net ayırım (güçlü vs zayıf)
- ✅ Gürültü temizleme

**Dezavantajlar:**
- ❌ Bilgi kaybı (zayıf ilişkiler kesildi)
- ❌ Sıralama değişimi yok (monoton)
- ❌ Zayıf elemanlar dezavantajlı

**Kullanım Senaryosu:**
- Sadece güçlü ilişkilerin önemli olduğu durumlar
- Kesin kararlar gereken durumlar
- Gürültülü veri temizleme

---

## 🎯 Öneriler

### Hangi Modu Seçmeliyim?

1. **Mixed Mod kullan eğer:**
   - Zayıf ilişkileri de değerlendirmek istiyorsan
   - Sıralama değişimlerini gözlemlemek istiyorsan
   - Keşifsel analiz yapıyorsan
   - İkinci şans vermek istiyorsan

2. **Binary Mod kullan eğer:**
   - Sadece güçlü ilişkilere odaklanmak istiyorsan
   - Kararlı sıralama istiyorsan
   - Gürültüyü temizlemek istiyorsan
   - Kesin kararlar almak istiyorsan

### Eşik Değeri Seçimi

- **Düşük eşik (0.3-0.4):** Daha az değişim, daha fazla ilişki korunur
- **Orta eşik (0.5-0.6):** Dengeli yaklaşım
- **Yüksek eşik (0.7-0.8):** Radikal değişim, sadece çok güçlü ilişkiler kalır

---

## 📈 İteratif Analiz Stratejisi

### Önerilen Yaklaşım

1. **İlk İterasyon:** Binary mod (0.5 eşik)
   - Gürültüyü temizle
   - Güçlü ilişkileri belirle

2. **İkinci İterasyon:** Mixed mod (0.6 eşik)
   - Zayıf ilişkileri değerlendir
   - Sıralama değişimlerini gözlemle

3. **Üçüncü İterasyon:** Binary mod (0.7 eşik)
   - Çok güçlü ilişkilere odaklan
   - Final kararı ver

### Karşılaştırma Metrikleri

- **Rank korelasyonu:** Sıralamaların ne kadar değiştiği
- **Skor varyansı:** Skorların ne kadar farklılaştığı
- **Homojenlik:** Değerlerin ne kadar eşitlendiği

---

## 📚 Referanslar

- **Veri:** Example 1 (4 parametre × 5 eleman)
- **Algoritma:** RMVC (Relational Membership Value Calculation)
- **Teori:** Soft Set Theory
- **Eşik Değeri:** 0.50
- **Tarih:** 30 Aralık 2025

---

## 🔗 İlgili Dosyalar

- `rmvc_app_v2.py` - Ana uygulama
- `Example.1..xlsx` - Test verisi
- `README.md` - Genel dokümantasyon

---

**Not:** Bu analiz, aynı veri seti ve aynı eşik değeri (0.50) ile iki farklı modun karşılaştırmasını içermektedir. Farklı eşik değerleri ve farklı veri setleri ile sonuçlar değişebilir.
