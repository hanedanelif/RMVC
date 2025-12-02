# 🚀 GitHub'a Yükleme Talimatları

Bu dosya, RMVC projesini GitHub'a nasıl yükleyeceğinizi adım adım açıklar.

---

## 📋 Ön Hazırlık

### 1. GitHub Hesabı
- https://github.com adresinde bir hesabınız olmalı
- Giriş yapın

### 2. Git Kurulumu
Git yüklü değilse: https://git-scm.com/download/win

Kontrol:
```bash
git --version
```

---

## 📁 Yüklenecek Dosyalar

| Dosya | Açıklama | Yüklenecek mi? |
|-------|----------|----------------|
| `rmvc_app_v2.py` | Ana web uygulaması | ✅ EVET |
| `RMVC-git.py` | Orijinal konsol uygulaması | ✅ EVET |
| `RMVC-csv.py` | CSV entegreli versiyon | ✅ EVET |
| `test_example1.py` | Doğrulama testi | ✅ EVET |
| `Example.1..xlsx` | Örnek veri | ✅ EVET |
| `README.md` | Ana açıklama | ✅ EVET |
| `KULLANIM_KILAVUZU.md` | Türkçe kılavuz | ✅ EVET |
| `RMVC-git-ACIKLAMA.md` | Detaylı açıklama | ✅ EVET |
| `requirements.txt` | Bağımlılıklar | ✅ EVET |
| `LICENSE` | Lisans | ✅ EVET |
| `.gitignore` | Git ignore | ✅ EVET |
| `rmvc_app.py` | Eski versiyon | ❌ HAYIR (silinebilir) |
| `csv_softset_converter.py` | Eski dosya | ❌ HAYIR (silinebilir) |
| `mathematics-13-02693-v3.pdf` | Makale (telif) | ❌ HAYIR |
| `GITHUB_YUKLEME.md` | Bu dosya | ❌ HAYIR |

---

## 🔧 Adım Adım Yükleme

### Adım 1: GitHub'da Yeni Repository Oluşturun

1. https://github.com/new adresine gidin
2. **Repository name:** `RMVC` yazın
3. **Description:** `Rough Multi-Valued Choice - Decision Support System` yazın
4. **Public** seçin (veya Private)
5. ❌ "Add a README file" işaretlemeyin (zaten var)
6. **Create repository** butonuna tıklayın

### Adım 2: Terminal/Komut İstemi Açın

Windows:
```
Win + R → cmd → Enter
```

### Adım 3: RMVC Klasörüne Gidin

```bash
cd C:\Users\user\Downloads\RMVC
```

### Adım 4: Gereksiz Dosyaları Silin (Opsiyonel)

```bash
del rmvc_app.py
del csv_softset_converter.py
del mathematics-13-02693-v3.pdf
del GITHUB_YUKLEME.md
```

### Adım 5: Git Repository Başlatın

```bash
git init
```

### Adım 6: Kullanıcı Bilgilerini Ayarlayın (İlk kez ise)

```bash
git config user.name "KULLANICI_ADINIZ"
git config user.email "EMAIL_ADRESINIZ@example.com"
```

### Adım 7: Dosyaları Ekleyin

```bash
git add .
```

### Adım 8: İlk Commit

```bash
git commit -m "Initial commit: RMVC Decision Support System"
```

### Adım 9: Ana Branch'i Ayarlayın

```bash
git branch -M main
```

### Adım 10: Remote Repository Ekleyin

```bash
git remote add origin https://github.com/KULLANICI_ADINIZ/RMVC.git
```

> ⚠️ `KULLANICI_ADINIZ` yerine GitHub kullanıcı adınızı yazın!

### Adım 11: GitHub'a Push Edin

```bash
git push -u origin main
```

> 📝 GitHub kullanıcı adı ve şifre/token istenebilir.

---

## 🔑 GitHub Token Oluşturma (Şifre Yerine)

GitHub artık şifre ile push'a izin vermiyor. Token oluşturmanız gerekiyor:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token (classic)** tıklayın
3. **Note:** `RMVC push` yazın
4. **Expiration:** 90 days (veya istediğiniz süre)
5. **Scopes:** `repo` işaretleyin
6. **Generate token** tıklayın
7. Token'ı kopyalayın (bir daha göremezsiniz!)

Push sırasında:
- Username: GitHub kullanıcı adınız
- Password: Oluşturduğunuz token

---

## ✅ Kontrol

Yükleme başarılı ise:
```
https://github.com/KULLANICI_ADINIZ/RMVC
```

adresinde projenizi görebilirsiniz.

---

## 📝 Sonraki Güncellemeler

Değişiklik yaptıktan sonra:

```bash
cd C:\Users\user\Downloads\RMVC
git add .
git commit -m "Açıklama: Ne değişti"
git push
```

---

## 🆘 Sorun Giderme

### "fatal: not a git repository"
```bash
git init
```

### "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/KULLANICI_ADINIZ/RMVC.git
```

### "failed to push some refs"
```bash
git pull origin main --allow-unrelated-histories
git push
```

### "Authentication failed"
- Token'ınızı kontrol edin
- Yeni token oluşturun

---

## 🎉 Tebrikler!

Projeniz artık GitHub'da! 

README.md otomatik olarak ana sayfada görünecektir.

---

## 📌 Önerilen Sonraki Adımlar

1. **About** bölümünü düzenleyin (sağ üstteki ⚙️)
2. **Topics** ekleyin: `python`, `decision-making`, `rough-set`, `streamlit`
3. **Releases** oluşturun: v1.0.0
4. Projeyi paylaşın! 🚀
