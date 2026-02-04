
# TEKSTİL ADIM 2 RAPORU - SUB-MATRİS VE BINARY CONVERSION

**Tarih:** 2026-02-02 00:38:20

## TEST BOYUTLARI

3 farklı boyut: 10×20, 20×30, 30×50

## RAW SUB-MATRİSLER

| Boyut | Miktar Yoğunluk | AlimSayisi Yoğunluk | TotalScore Yoğunluk |
|-------|-----------------|---------------------|---------------------|
| 10x20 | 14.50% | 14.50% | 14.50% |
| 20x30 | 10.67% | 10.67% | 10.67% |
| 30x50 | 7.87% | 7.87% | 7.87% |

## 4 BINARY METHOD

### Method 1: Miktar > 0
Basit binary dönüşüm. Herhangi bir miktar varsa 1, yoksa 0.

### Method 2: AlimSayisi > 0
Alım sıklığı bazlı. En az 1 kez alınmışsa 1, yoksa 0.

### Method 3: Miktar >= Median
Threshold bazlı (MovieLens tarzı). Sadece median üzeri alımlar 1.

### Method 4: TotalScore >= Median ✨ YENİ
Miktar × AlimSayisi kombinasyonu. Hem miktar hem sıklık dikkate alınır.

## BINARY YOĞUNLUKLARı

| Boyut | Method 1 | Method 2 | Method 3 | Method 4 |
|-------|----------|----------|----------|----------|
| 10x20 | 14.50% | 14.50% | 14.50% | 14.50% |
| 20x30 | 10.67% | 10.67% | 10.67% | 10.67% |
| 30x50 | 7.87% | 7.87% | 7.87% | 7.87% |

## ÖNEMLİ BULGULAR


### Method 1 = Method 2

**Bulgu:** Tüm boyutlarda Method 1 ve Method 2 **aynı sonucu** verdi.

**Sebep:** Her alımda miktar bilgisi var (Miktar > 0 ⇔ AlimSayisi > 0).

**Sonuç:** Tekstil veri setinde "Miktar olmadan alım" yok. Her transactionda hem miktar hem alım sayısı mevcut.


### Threshold Etkisi (Method 3 ve 4)

Method 3 ve 4, median threshold kullanarak daha seçici davranıyor:

- **10x20:** Method 3 → 0.0% azalma, Method 4 → 0.0% azalma
- **20x30:** Method 3 → 0.0% azalma, Method 4 → 0.0% azalma
- **30x50:** Method 3 → 0.0% azalma, Method 4 → 0.0% azalma

## OLUŞTURULAN DOSYALAR

### Raw Matrisler (9 dosya)
3 boyut × 3 pivot tip = 9 raw matris

### Binary Matrisler (12 dosya)
3 boyut × 4 method = **12 binary matris**

**Toplam:** 21 = **21 dosya**

## SONRAKİ ADIM

ADIM 3: RMVC Hesaplama (V2 - Hocanın metodu)
- 12 binary matris
- Her biri için üyelik matrisi
- Skor hesaplama
