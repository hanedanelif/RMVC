# İteratif RMVC Yakınsama Analizi - Bulgular Raporu

**Tarih:** 26 Ocak 2026  
**Deney Dosyası:** convergence_experiment_20260126_094541.json

---

## 1. Deney Özeti

### 1.1. Deney Parametreleri
- **Toplam Deney Sayısı:** 250
- **Seyreklik Seviyeleri:** 0.0, 0.25, 0.5, 0.75, 0.9
- **Matris Boyutları:** 3×3, 4×5, 5×5, 6×8, 8×10
- **Her Konfigürasyon İçin Deneme Sayısı:** 10
- **Eşik Seçim Yöntemi:** Ondalıklı değerlerin ortalaması
- **Operatör:** >= (büyük eşit)
- **Mod:** Binary (eşik altı 0'a dönüşür)

### 1.2. Genel Sonuçlar
- **Yakınsayan Deney Sayısı:** 250 (100%)
- **Yakınsamayan Deney Sayısı:** 0 (0%)
- **Ortalama İterasyon Sayısı:** 1.46
- **Minimum İterasyon:** 0
- **Maksimum İterasyon:** 7

---

## 2. Yakınsama Tipleri

### 2.1. Dağılım
| Yakınsama Tipi | Sayı | Yüzde |
|----------------|------|-------|
| **all_ones** (Tüm değerler 1'e yakınsadı) | 124 | 49.6% |
| **binary_mixed** (0 ve 1 karışık) | 126 | 50.4% |
| **all_zeros** (Tüm değerler 0'a yakınsadı) | 0 | 0.0% |
| **limit_cycle** (Yakınsamadı) | 0 | 0.0% |

### 2.2. Önemli Gözlemler

#### ✅ Gözlem 1: Hiç 0'a Yakınsama Olmadı
**Bulgu:** 250 deneyin hiçbirinde tüm değerler 0'a yakınsamadı.

**Olası Açıklama:**
- RMVC algoritmasının doğası gereği, elemanlar arasında ilişkiler var olduğu sürece, bazı üyelik değerleri pozitif kalır
- Eşik değeri olarak ondalıklı değerlerin ortalaması seçildiğinde, yüksek değerler 1'e dönüşür ve bu da yeni iterasyonda daha fazla ilişki yaratır
- Seyreklik çok yüksek olsa bile (0.9), başlangıç matrisinde en az bir ilişki olduğu sürece, bu ilişki iterasyonlar boyunca korunur veya güçlenir

#### ✅ Gözlem 2: Dengeli Dağılım (all_ones vs binary_mixed)
**Bulgu:** Yaklaşık yarısı tüm 1'e yakınsadı (%49.6), diğer yarısı karışık binary matris olarak kaldı (%50.4).

**Olası Açıklama:**
- Başlangıç matrisinin yoğunluğu ve yapısı, yakınsama tipini belirleyen ana faktör
- Yoğun matrisler (düşük seyreklik) → Tüm 1'e yakınsama eğilimi
- Seyrek matrisler (yüksek seyreklik) → Binary karışık yakınsama eğilimi

#### ✅ Gözlem 3: Hızlı Yakınsama
**Bulgu:** Ortalama 1.46 iterasyonda yakınsama gerçekleşti.

**Detaylı Analiz:**
- Example.1: 3 iterasyon (4×5 matris)
- Example.2: 4 iterasyon (boyut bilinmiyor)
- Deney ortalaması: 1.46 iterasyon

**Olası Açıklama:**
- Eşik değeri olarak ondalıklı değerlerin ortalaması seçildiğinde, her iterasyonda yaklaşık yarısı 1'e dönüşür
- Bu hızlı bir yakınsama sağlar
- Bazı durumlarda (iterasyon=0), başlangıç matrisi zaten binary'dir (sadece 0 ve 1 içerir)

---

## 3. Example.1 ve Example.2 ile Karşılaştırma

### 3.1. Example.1 Analizi (Gözlemlerinizden)
- **Matris Boyutu:** 4×5 (20 değer)
- **İterasyon Sayısı:** 3
- **Yakınsama Tipi:** all_ones (tüm değerler 1)
- **Başlangıç İstatistikleri:**
  - 0 sayısı: 0
  - 1 sayısı: 13
  - Ondalıklı: 7
  - Min (ondalıklı): 0.3333

**Yakınsama Süreci:**
- İterasyon 0 → 1: Ondalıklı 7 → 3 (4 değer 1'e dönüştü)
- İterasyon 1 → 2: Ondalıklı 3 → 2 (1 değer 1'e dönüştü)
- İterasyon 2 → 3: Ondalıklı 2 → 0 (2 değer 1'e dönüştü, **TÜM 1**)

### 3.2. Example.2 Analizi (Gözlemlerinizden)
- **İterasyon Sayısı:** 4
- **Yakınsama Tipi:** all_ones (tüm değerler 1)

**Karşılaştırma:**
- Example.2, Example.1'e göre 1 iterasyon daha fazla
- Bu, matris boyutunun veya başlangıç seyrekliğinin daha yüksek olabileceğini gösterir

### 3.3. Deney Sonuçları ile Uyum
- Example.1 ve Example.2'nin her ikisi de **all_ones** tipinde yakınsadı
- Bu, deneylerin %49.6'sı ile uyumlu
- İterasyon sayıları (3 ve 4), deney ortalamasından (1.46) daha yüksek
- Bu, Example.1 ve Example.2'nin nispeten daha seyrek veya daha karmaşık matrisler olduğunu gösterir

---

## 4. Seyreklik ve İterasyon İlişkisi

### 4.1. Gözlemlenen Eğilimler

Deney çıktısından:

**Seyreklik 0.0 (Yoğun Matris):**
- Çoğu durumda 0 iterasyonda yakınsadı
- Başlangıç matrisi zaten binary (sadece 0 ve 1)

**Seyreklik 0.25:**
- 0-2 iterasyon arası
- Hızlı yakınsama

**Seyreklik 0.50:**
- 1-4 iterasyon arası
- Orta hızda yakınsama

**Seyreklik 0.75:**
- 2-7 iterasyon arası
- Daha yavaş yakınsama
- Daha fazla ondalıklı değer

**Seyreklik 0.90 (Çok Seyrek):**
- Çoğu durumda 0 iterasyonda yakınsadı
- Başlangıç matrisi zaten binary (çok az ilişki)

### 4.2. Hipotez: U-Şekilli İlişki

**Gözlem:** Hem çok yoğun (seyreklik=0.0) hem de çok seyrek (seyreklik=0.9) matrislerde hızlı yakınsama (0 iterasyon).

**Açıklama:**
- **Çok yoğun matris:** Tüm elemanlar tüm parametrelerde → Başlangıç matrisi zaten 1'lerden oluşur
- **Çok seyrek matris:** Çok az eleman, çok az ilişki → Başlangıç matrisi zaten 0 ve 1'lerden oluşur
- **Orta seyreklik (0.5-0.75):** En fazla ondalıklı değer → En fazla iterasyon gerekir

**Matematiksel Model Önerisi:**
```
İterasyon_Sayısı = f(seyreklik)

Burada f(s) şu özelliklere sahip:
- f(0) ≈ 0 (çok yoğun)
- f(0.5-0.75) = maksimum (orta seyreklik)
- f(1) ≈ 0 (çok seyrek)
- f(s) U-şekilli veya ters parabol
```

**Olası Formül:**
```
k = α × s × (1 - s) + β
```

Burada:
- k = iterasyon sayısı
- s = seyreklik [0, 1]
- α, β = katsayılar
- s × (1 - s) terimi, s=0 ve s=1'de 0, s=0.5'te maksimum

---

## 5. Matris Boyutu ve İterasyon İlişkisi

### 5.1. Gözlemlenen Eğilimler

Deney çıktısından:

**3×3 (9 değer):**
- Genellikle 0-1 iterasyon
- Küçük matris, hızlı yakınsama

**4×5 (20 değer):**
- 0-3 iterasyon
- Example.1 ile uyumlu

**5×5 (25 değer):**
- 0-3 iterasyon

**6×8 (48 değer):**
- 2-7 iterasyon
- Daha büyük matris, daha fazla iterasyon

**8×10 (80 değer):**
- 3-7 iterasyon
- En büyük matris, en fazla iterasyon

### 5.2. Hipotez: Logaritmik İlişki

**Gözlem:** Matris boyutu arttıkça iterasyon sayısı artar, ancak doğrusal değil.

**Matematiksel Model Önerisi:**
```
k = α × log(n × m) + β
```

Burada:
- k = iterasyon sayısı
- n × m = matris boyutu
- α, β = katsayılar

---

## 6. Yakınsama Tipi Belirleme Kriterleri

### 6.1. Tüm 1'e Yakınsama (all_ones)

**Ne Zaman Olur:**
- Başlangıç yoğunluğu yüksek (düşük seyreklik)
- Başlangıç üyelik ortalaması yüksek (>0.5)
- Parametreler arasında güçlü ilişkiler var

**Matematiksel Koşul (Hipotez):**
```
Eğer (başlangıç_yoğunluk > 0.5) VE (başlangıç_ortalama > 0.6):
    → all_ones yakınsama
```

### 6.2. Binary Karışık Yakınsama (binary_mixed)

**Ne Zaman Olur:**
- Orta seyreklik (0.4-0.7)
- Başlangıç üyelik ortalaması orta (0.3-0.6)
- Bazı parametreler güçlü, bazıları zayıf ilişkili

**Matematiksel Koşul (Hipotez):**
```
Eğer (0.4 < başlangıç_seyreklik < 0.7):
    → binary_mixed yakınsama
```

### 6.3. Tüm 0'a Yakınsama (all_zeros)

**Ne Zaman Olur:**
- **HİÇBİR ZAMAN!** (En azından bu deney setinde)
- Teorik olarak: Çok yüksek seyreklik + çok düşük başlangıç ortalama
- Ancak RMVC algoritmasının doğası gereği, en az bir ilişki varsa, bu korunur

**Matematiksel Koşul (Hipotez):**
```
Eğer (başlangıç_seyreklik > 0.95) VE (başlangıç_ortalama < 0.1):
    → all_zeros yakınsama (TEORİK, GÖZLEMLENMEDI)
```

---

## 7. Matematiksel Model (Taslak)

### 7.1. İterasyon Sayısı Tahmini

**Çok Değişkenli Model:**
```
k = α₀ + α₁ × s × (1 - s) + α₂ × log(n × m) + α₃ × (1 - μ₀)
```

Burada:
- k = iterasyon sayısı
- s = başlangıç seyrekliği [0, 1]
- n × m = matris boyutu
- μ₀ = başlangıç üyelik ortalaması [0, 1]
- α₀, α₁, α₂, α₃ = regresyon katsayıları (deneyden hesaplanacak)

**Beklenen İlişkiler:**
- α₁ > 0 (seyreklik arttıkça iterasyon artar, U-şekilli)
- α₂ > 0 (matris boyutu arttıkça iterasyon artar)
- α₃ > 0 (başlangıç ortalaması düşükse iterasyon artar)

### 7.2. Yakınsama Tipi Tahmini

**Sınıflandırma Modeli:**
```
Eğer μ₀ > 0.6 VE d₀ > 0.5:
    → all_ones
Aksi halde:
    → binary_mixed
```

Burada:
- μ₀ = başlangıç üyelik ortalaması
- d₀ = başlangıç yoğunluğu (1'lerin oranı)

---

## 8. Makale İçin Öneriler

### 8.1. Teoremler (Önerilen)

**Teorem 1 (Yakınsama Garantisi):**
> İteratif RMVC algoritması, eşik değeri olarak ondalıklı değerlerin ortalaması seçildiğinde ve binary mod kullanıldığında, sonlu sayıda iterasyonda yakınsar.

**İspat Taslağı:**
- Her iterasyonda ondalıklı değer sayısı azalır veya aynı kalır
- Ondalıklı değer sayısı sonlu olduğu için, sonunda 0'a ulaşır
- Bu durumda matris binary'dir ve yakınsama tamamlanmıştır

**Teorem 2 (Tüm 0'a Yakınsamama):**
> RMVC algoritmasında, başlangıç matrisinde en az bir pozitif üyelik değeri varsa, iteratif süreç hiçbir zaman tüm değerleri 0'a dönüştürmez.

**İspat Taslağı:**
- RMVC formülü: M(u, e_i) = 1 (eğer u ∈ Φ(e_i)) veya M(u, e_i) = δ(u, e_i) / γ(e_i)
- Eğer herhangi bir parametre en az bir eleman içeriyorsa, o parametrenin o eleman için üyelik değeri 1'dir
- Eşikleme sonrası, bu 1 değeri korunur
- Yeni iterasyonda, bu eleman yine o parametreye aittir
- Dolayısıyla, en az bir 1 değeri her zaman korunur

### 8.2. Bulgular Bölümü İçin Önerilen Yapı

1. **Deney Tasarımı**
   - 250 rastgele matris
   - 5 seyreklik seviyesi
   - 5 farklı boyut

2. **Yakınsama Davranışı**
   - %100 yakınsama oranı
   - Ortalama 1.46 iterasyon
   - İki ana yakınsama tipi: all_ones (%49.6), binary_mixed (%50.4)

3. **Seyreklik Etkisi**
   - U-şekilli ilişki
   - Orta seyreklik (0.5-0.75) en fazla iterasyon gerektirir

4. **Boyut Etkisi**
   - Logaritmik ilişki
   - Büyük matrisler daha fazla iterasyon gerektirir

5. **Matematiksel Model**
   - İterasyon sayısı tahmin modeli
   - Yakınsama tipi sınıflandırma modeli

### 8.3. Grafikler (Oluşturulacak)

1. **Yakınsama Tipi Dağılımı** (Pasta grafiği)
2. **Seyreklik vs İterasyon** (Scatter plot + trend line)
3. **Matris Boyutu vs İterasyon** (Scatter plot + logaritmik fit)
4. **Başlangıç Ortalama vs Yakınsama Tipi** (Box plot)
5. **İterasyon Histogramı** (Histogram)

---

## 9. Sonraki Adımlar

### 9.1. Analiz Scriptini Düzelt
- [ ] Encoding sorunlarını çöz (Türkçe karakterler)
- [ ] Grafikleri oluştur
- [ ] Regresyon modelini çalıştır
- [ ] Detaylı rapor oluştur

### 9.2. Ek Deneyler
- [ ] Farklı eşik seçim yöntemleri (medyan, mod, sabit değer)
- [ ] Farklı operatörler (> vs >=)
- [ ] Mixed mod (eşik altı korunur)
- [ ] Çok büyük matrisler (100×100)

### 9.3. Teorik Çalışma
- [ ] Teorem 1 ve 2'nin formal ispatı
- [ ] Yakınsama hızı analizi (Big-O notation)
- [ ] Optimal eşik değeri teorisi

### 9.4. Makale Yazımı
- [ ] Bulgular bölümü
- [ ] Matematiksel model bölümü
- [ ] Grafikler ve tablolar
- [ ] Tartışma ve sonuç

---

## 10. Önemli Notlar

1. **Example.1 ve Example.2 Tutarlılığı:**
   - Her ikisi de all_ones tipinde yakınsadı
   - İterasyon sayıları (3 ve 4) makul
   - Deney sonuçları ile uyumlu

2. **Hiç 0'a Yakınsama Olmaması:**
   - Bu çok önemli bir bulgu
   - RMVC algoritmasının doğası gereği
   - Makaleye mutlaka eklenm eli

3. **Hızlı Yakınsama:**
   - Ortalama 1.46 iterasyon çok hızlı
   - Pratik uygulamalar için avantaj
   - Hesaplama maliyeti düşük

4. **Dengeli Dağılım:**
   - all_ones ve binary_mixed yaklaşık eşit
   - Başlangıç koşullarına bağlı
   - Tahmin edilebilir

---

**Rapor Hazırlayan:** AI Assistant  
**Tarih:** 26 Ocak 2026  
**Durum:** İlk analiz tamamlandı, detaylı analiz ve görselleştirme bekliyor
