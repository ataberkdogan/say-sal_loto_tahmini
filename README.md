# Sayısal Loto Tahmin Sistemi

Makine öğrenmesi kullanarak Sayısal Loto sayılarını tahmin etmeye çalışan bir Python projesi.

## 📋 Proje Açıklaması

Bu proje, geçmiş Sayısal Loto çekilişi verilerini analiz ederek, çeşitli makine öğrenmesi algoritmalarını kullanarak bir sonraki çekilişte çıkacak sayıları tahmin etmeyi amaçlamaktadır.

### 🎯 Özellikler

- **Veri Çekme**: Millipiyango.com web sitesinden veriler çekilir, internet sorunu olursa örnek veri oluşturulur
- **Veri Temizleme**: Eksik değerler, aykırı değerler ve tutarsızlıklar temizlenir
- **Özellik Mühendisliği**: 
  - Gecikmeli (lag) özellikler
  - Hareketli ortalama (rolling) özellikler
  - İstatistiksel özellikler
  - Sıklık tabanlı özellikler
  - Zaman tabanlı özellikler
  - Fark (difference) özellikler
  - Etkileşim (interaction) özellikler
- **Makine Öğrenmesi Modelleri**:
  - Random Forest
  - XGBoost
  - CatBoost
  - LightGBM
  - Naive Bayes
- **Model Değerlendirmesi**: MSE, MAE, R², RMSE metrikleri
- **Tahmin**: Eğitilmiş modelleri kullanarak sayı tahmini

## 🚀 Başlangıç

### Gereksinimler

- Python 3.8+
- pip (Python paket yöneticisi)

### Kurulum

1. **Depoyu klonlayın:**
```bash
git clone https://github.com/ataberkdogan/say-sal_loto_tahmini.git
cd say-sal_loto_tahmini
```

2. **Sanal ortam oluşturun (opsiyonel ama önerilir):**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. **Gerekli kütüphaneleri yükleyin:**
```bash
pip install -r requirements.txt
```

## 📝 Kullanım

### Hızlı Başlangıç - Tüm Adımları Çalıştır

```bash
python main.py
```

Menüde seçenek 7'yi seçerek tüm işlemleri otomatik olarak çalıştırabilirsiniz.

### Adım Adım Kullanım

```bash
# 1. Veri çek
python scraper.py

# 2. Verileri ön işle
python preprocess.py

# 3. Özellikleri çıkar
python feature_engineering.py

# 4. Modelleri eğit
python train.py

# 5. Modelleri değerlendir
python evaluate.py

# 6. Sayıları tahmin et
python predict.py

# 7. Ana menüyü çalıştır
python main.py
```

## 📂 Proje Yapısı

```
say-sal_loto_tahmini/
├── scraper.py                  # Veri çekme
├── preprocess.py              # Veri ön işleme
├── feature_engineering.py      # Özellik mühendisliği
├── analysis.py                # İstatistiksel analiz
├── models.py                  # ML modelleri
├── train.py                   # Model eğitimi
├── evaluate.py                # Model değerlendirmesi
├── predict.py                 # Tahmin
├── main.py                    # Ana menü
├── sample_data_generator.py   # Örnek veri oluşturma
├── requirements.txt           # Gerekli kütüphaneler
├── .gitignore                 # Git'ten hariç tutulacak dosyalar
├── README.md                  # Bu dosya
└── data/                      # Veriler (Excel, CSV)
    ├── sayisal_loto_verileri.xlsx
    ├── sayisal_loto_temizlenmis.xlsx
    ├── sayisal_loto_ozellikleri.xlsx
    ├── model_results.csv
    └── predictions.txt
└── models/                    # Eğitilmiş modeller
    ├── RandomForest_model.pkl
    ├── XGBoost_model.pkl
    ├── CatBoost_model.pkl
    ├── LightGBM_model.pkl
    └── NaiveBayes_model.pkl
```

## 🔧 Modüller

### scraper.py
Web sitesinden veya örnek veri oluşturarak Sayısal Loto verilerini çeker.

**Kullanım:**
```python
from scraper import LottoScraper

scraper = LottoScraper()
scraper.scrape_with_fallback()  # API → HTML → Örnek Veri
scraper.save_to_excel('data/loto.xlsx')
```

### preprocess.py
Verileri temizler, normalize eder ve standardize eder.

**Kullanım:**
```python
from preprocess import DataPreprocessor

preprocessor = DataPreprocessor('data/loto.xlsx')
preprocessor.load_data()
preprocessor.clean_data()
preprocessor.save_cleaned_data()
```

### feature_engineering.py
Çeşitli özellikler oluşturur.

**Kullanım:**
```python
from feature_engineering import FeatureEngineer

engineer = FeatureEngineer(df)
df_with_features, feature_cols = engineer.generate_all_features()
```

### models.py
Makine öğrenmesi modellerini tanımlar.

**Kullanım:**
```python
from models import LotteryModels

models = LotteryModels()
models.create_all_models()
```

### train.py
Modelleri eğitir.

**Kullanım:**
```python
from train import LotteryTrainer

trainer = LotteryTrainer()
trainer.prepare_data()
trainer.train_all_models()
trainer.save_trained_models()
```

### evaluate.py
Modelleri değerlendirir.

**Kullanım:**
```python
from evaluate import LotteryEvaluator

evaluator = LotteryEvaluator()
evaluator.evaluate_all_models(models, X_test, y_test)
evaluator.print_comparison()
```

### predict.py
Sayıları tahmin eder.

**Kullanım:**
```python
from predict import LotteryPredictor

predictor = LotteryPredictor(model_name='XGBoost')
predictions = predictor.predict_lottery_numbers()
predictor.predict_multiple_models()
```

## 📊 Sonuçlar

Model performans metrikleri `data/model_results.csv` dosyasına kaydedilir.

Tahmin edilen sayılar `data/predictions.txt` dosyasına kaydedilir.

## ⚠️ Önemli Not

**Bu proje eğitim amaçlıdır. Sayısal Loto gibi şans oyunlarının sonuçları tamamen rastgeledir ve herhangi bir makine öğrenmesi modeli bu sonuçları güvenilir bir şekilde tahmin edemez. Bu proje herhangi bir finansal tavsiye sağlamaz.**

## 🔍 Model Performansı

Sisteme dahil edilen modeller:

| Model | Açıklama |
|-------|----------|
| Random Forest | Karar ağaçlarına dayalı topluluk yöntemi |
| XGBoost | Gradient boosting framework |
| CatBoost | Kategorik özellikleri iyi işleyen gradient boosting |
| LightGBM | Hızlı ve hafif gradient boosting |
| Naive Bayes | Probabilistik sınıflandırma |

## 📈 Gelecek Geliştirmeler

- [ ] Deep Learning modellerinin eklenmesi
- [ ] Zaman serisi analizi (ARIMA, Prophet)
- [ ] Web arayüzü (Flask/Django)
- [ ] REST API
- [ ] Gerçek zamanlı tahmin
- [ ] Başka piyango türlerine destek

## 📄 Lisans

Bu proje MIT Lisansı altında sunulmuştur.

## 👤 Yazar

[ataberkdogan](https://github.com/ataberkdogan)

## 📞 İletişim

Sorularınız veya önerileriniz için GitHub Issues'i kullanabilirsiniz.

---

**Son Güncelleme:** 2026-07-21
