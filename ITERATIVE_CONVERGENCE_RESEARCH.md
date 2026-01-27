# İteratif RMVC Yakınsama Analizi - Araştırma Raporu

## 1. Araştırma Soruları

### Ana Sorular:
1. **Ne zaman tüm üyelik değerleri 1'e yakınsar?**
2. **Ne zaman tüm üyelik değerleri 0'a yakınsar?**
3. **Ne zaman 0 ve 1'lerden oluşan binary matris elde edilir?**
4. **İterasyon sayısı ile matris özellikleri (seyreklik, yoğunluk) arasındaki ilişki nedir?**
5. **Yakınsama hızını etkileyen faktörler nelerdir?**

## 2. İlk Gözlemler

### Example.1 Analizi (4 parametre × 5 eleman)

#### Başlangıç Üyelik Matrisi (İterasyon 0):
```
SETS    1       2       3       4       5
e_1   1.0000  1.0000  1.0000  0.3333  1.0000
e_2   0.5556  1.0000  0.3333  1.0000  1.0000
e_3   1.0000  0.4444  1.0000  1.0000  0.4444
e_4   1.0000  1.0000  0.4444  0.3333  1.0000
```

**İstatistikler:**
- Toplam değer: 20
- Min (ondalıklı): 0.3333
- Max: 1.0000
- 0 Sayısı: 0
- 1 Sayısı: 13
- Ondalıklı: 7

#### İterasyon 1 (Eşik: 0.4127, Operatör: >=, Mod: Binary):
```
Eşiklenmiş Matris: Tüm değerler 0 veya 1
Yeni Üyelik Matrisi: Hala ondalıklı değerler var (0.5833)
```

**İstatistikler:**
- Min (ondalıklı): 0.5833
- Max: 1.0000
- 0 Sayısı: 0
- 1 Sayısı: 17
- Ondalıklı: 3

**Gözlem:** Ondalıklı değer sayısı 7'den 3'e düştü. Yakınsama başladı.

#### İterasyon 2 (Eşik: 0.6667, Operatör: >=, Mod: Binary):
```
Yeni Üyelik Matrisi: Hala ondalıklı değerler var (0.6667)
```

**İstatistikler:**
- Min (ondalıklı): 0.6667
- Max: 1.0000
- 0 Sayısı: 0
- 1 Sayısı: 18
- Ondalıklı: 2

**Gözlem:** Ondalıklı değer sayısı 3'ten 2'ye düştü. Yakınsama devam ediyor.

#### İterasyon 3 (Eşik: 0.6667, Operatör: >=, Mod: Binary):
```
Yeni Üyelik Matrisi: TÜM DEĞERLER 1.0000
```

**İstatistikler:**
- Min: 1.0000
- Max: 1.0000
- 0 Sayısı: 0
- 1 Sayısı: 20
- Ondalıklı: 0

**SONUÇ:** Example.1 için 3 iterasyonda tam yakınsama (tüm değerler 1).

---

### Example.2 Analizi

**Rapor Edilen Sonuç:**
- İterasyon 4'te tüm üyelik değerleri 1'e ulaştı
- Example.1'e göre 1 iterasyon daha fazla

---

## 3. Teorik Hipotezler

### Hipotez 1: Başlangıç Seyrekliği
**Tanım:** Seyreklik = (0 değer sayısı) / (toplam değer sayısı)

**Hipotez:** 
- Düşük seyreklik (yoğun matris) → Daha hızlı 1'e yakınsama
- Yüksek seyreklik (seyrek matris) → Daha yavaş yakınsama veya 0'a yakınsama

### Hipotez 2: Başlangıç Ondalıklı Değer Dağılımı
**Gözlem:** Example.1'de başlangıçta 7 ondalıklı değer vardı.

**Hipotez:**
- Ondalıklı değerler yüksekse (>0.5) → 1'e yakınsama eğilimi
- Ondalıklı değerler düşükse (<0.5) → 0'a yakınsama eğilimi

### Hipotez 3: Eşik Değeri Seçimi
**Gözlem:** Her iterasyonda ondalıklı değerlerin ortalaması eşik olarak seçildi.

**Hipotez:**
- Eşik = ortalama → Dengeli yakınsama
- Eşik > ortalama → Daha fazla 0, daha yavaş yakınsama
- Eşik < ortalama → Daha fazla 1, daha hızlı yakınsama

### Hipotez 4: Matris Boyutu
**Gözlem:**
- Example.1: 4×5 = 20 değer, 3 iterasyon
- Example.2: Boyut bilinmiyor, 4 iterasyon

**Hipotez:**
- Daha büyük matris → Daha fazla iterasyon gerekebilir

### Hipotez 5: Parametre-Eleman İlişkisi
**Tanım:** 
- m = parametre sayısı
- n = eleman sayısı
- Oran = m/n

**Hipotez:**
- m ≈ n → Dengeli yakınsama
- m >> n → Farklı yakınsama davranışı
- m << n → Farklı yakınsama davranışı

---

## 4. Deney Tasarımı

### 4.1. Test Matrisleri Oluşturma

**Sabit Tutulacak Değişkenler:**
- Eşik seçim yöntemi: Ondalıklı değerlerin ortalaması
- Operatör: >= (eşite eşit ve büyük)
- Mod: Binary

**Değiştirilecek Parametreler:**

1. **Seyreklik Seviyeleri:**
   - %0 (tam yoğun)
   - %25 (düşük seyrek)
   - %50 (orta seyrek)
   - %75 (yüksek seyrek)
   - %90 (çok seyrek)

2. **Matris Boyutları:**
   - 3×3 (9 değer)
   - 4×5 (20 değer) - Example.1
   - 5×5 (25 değer)
   - 6×8 (48 değer)
   - 10×10 (100 değer)

3. **Parametre/Eleman Oranı:**
   - m < n (daha az parametre)
   - m = n (eşit)
   - m > n (daha fazla parametre)

### 4.2. Her Test İçin Ölçülecek Metrikler

1. **Yakınsama Tipi:**
   - Tüm 1'e yakınsama
   - Tüm 0'a yakınsama
   - Karışık (0 ve 1)
   - Yakınsamama (limit cycle)

2. **İterasyon Sayısı:**
   - Yakınsama için gereken iterasyon sayısı

3. **Yakınsama Hızı:**
   - Her iterasyonda ondalıklı değer sayısındaki azalma

4. **Başlangıç Özellikleri:**
   - Başlangıç seyrekliği
   - Başlangıç ondalıklı değer ortalaması
   - Başlangıç 1 oranı

---

## 5. Beklenen Matematiksel Model

### Model Formu (Taslak):

```
İterasyon_Sayısı = f(seyreklik, boyut, m/n_oranı, başlangıç_ortalama)
```

**Olası Formül:**
```
k = α × log(n×m) + β × seyreklik + γ × (1 - başlangıç_ortalama) + δ
```

Burada:
- k = iterasyon sayısı
- α, β, γ, δ = regresyon katsayıları
- n×m = matris boyutu
- seyreklik = [0, 1] aralığında
- başlangıç_ortalama = başlangıç üyelik değerlerinin ortalaması

---

## 6. Sonraki Adımlar

### Adım 1: Otomatik Test Scripti
- Rastgele matris oluşturucu
- İteratif RMVC çalıştırıcı
- Sonuç kaydedici

### Adım 2: Kapsamlı Deney Seti
- Her seyreklik seviyesi için 10 rastgele matris
- Her boyut için 10 rastgele matris
- Toplam: ~500 test

### Adım 3: İstatistiksel Analiz
- Korelasyon analizi
- Regresyon modeli
- Görselleştirme

### Adım 4: Makale Yazımı
- Bulgular bölümü
- Matematiksel model
- Teoremler ve ispatlar (varsa)

---

## 7. Notlar

- Example.1 ve Example.2'nin tam verilerini kaydet
- Her iterasyonda hangi değerlerin nasıl değiştiğini takip et
- Limit cycle durumlarını özel olarak incele
- Epsilon değerinin (1e-4) etkisini değerlendir

---

**Tarih:** 26 Ocak 2026
**Durum:** Araştırma planı oluşturuldu, deneyler başlatılacak
