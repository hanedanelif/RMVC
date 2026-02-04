# 📊 MovieLens Ham Ratings Analizi - Binary Dönüşüm Süreci

**Tarih:** 2026-01-29 10:15:07

---

## 1. Analiz Özeti

Bu rapor, MovieLens 100k veri setinin **ham ratings** (1-5 yıldız) halinden **binary** (0/1) formatına dönüşüm sürecini detaylı olarak göstermektedir.

### Binary Dönüşüm Kuralı

```
Rating >= 4 yıldız  →  1 (Olumlu)
Rating < 4 yıldız   →  0 (Olumsuz/İzlenmedi)
```

## 2. Yoğun Bölge Karşılaştırması

| Boyut | Ham Ort. Rating | Binary Yoğ. | Doluluk Oranı |
|-------|-----------------|-------------|---------------|
| 5x10 | 3.7233★ | %52.00 | %84.00 |
| 10x20 | 3.8220★ | %59.00 | %90.00 |
| 20x30 | 3.7937★ | %54.50 | %82.83 |
| 30x50 | 3.8774★ | %57.73 | %84.20 |
| 50x75 | 3.8199★ | %52.64 | %78.75 |

## 3. Gözlemler

- **En yüksek ortalama rating:** 30x50 (3.88★)
- **En yoğun binary bölge:** 10x20 (%59.00)

### Dönüşüm Etkisi

1. **1-3 yıldızlı ratingler:** Binary dönüşümde **kaybolur** (0'a döner)
2. **4-5 yıldızlı ratingler:** Binary'de **1** olur
3. **Yoğun bölgeler:** Genellikle yüksek ortalama rating'e sahiptir, bu yüzden binary dönüşümde de yoğun kalırlar.

## 4. Görsel Analizler

Her boyut için üç heatmap oluşturulmuştur:

1. **Ham Ratings Heatmap:** 1-5 yıldız aralığında renklendirilmiş
2. **Binary Heatmap:** 0/1 değerleri ile
3. **Kayıp Ratingler:** 1-3 yıldızlı (binary'de kaybolan) ratingler

## 5. Sonuç

- Sıralama işlemi **ham ratings** üzerinde yapılmıştır.
- En aktif kullanıcılar ve popüler filmler sol üst köşede toplanmıştır.
- Binary dönüşüm sonrası yoğunluk korunmuştur.
- Düşük ratingler (1-3★) bilgi kaybına neden olmuştur.
