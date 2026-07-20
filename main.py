import logging
import sys
import os

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_menu():
    """
    Ana menüyü göster
    """
    print("\n" + "="*60)
    print("SAYISAL LOTO TAHMİN SİSTEMİ")
    print("="*60)
    print("\n1. Veri Çek (Web'den veya Örnek Veri)")
    print("2. Verileri Ön İşleme")
    print("3. Özellikleri Mühendislikle Çıkar")
    print("4. Modelleri Eğit")
    print("5. Modelleri Değerlendir")
    print("6. Sayıları Tahmin Et")
    print("7. Tüm İşlemleri Çalıştır (1-6)")
    print("8. İstatistiksel Analiz Yap")
    print("9. Çıkış")
    print("="*60)
    return input("\nSeçim yapınız (1-9): ").strip()

def fetch_data():
    """
    Veri çek
    """
    try:
        logger.info("Veri çekme başlıyor...")
        from scraper import LottoScraper
        
        scraper = LottoScraper()
        if scraper.scrape_with_fallback():
            scraper.save_to_excel('data/sayisal_loto_verileri.xlsx')
            scraper.save_to_csv('data/sayisal_loto_verileri.csv')
            
            df = scraper.get_data()
            logger.info(f"\n✓ Veri başarıyla çekildi ({len(df)} satır)")
            logger.info(f"Tarih aralığı: {df['Cekilis_Tarihi'].min()} - {df['Cekilis_Tarihi'].max()}")
            return True
        else:
            logger.error("✗ Veri çekme başarısız oldu!")
            return False
    except Exception as e:
        logger.error(f"✗ Veri çekme hatası: {e}")
        return False

def preprocess_data():
    """
    Verileri ön işleme
    """
    try:
        logger.info("Veri ön işleme başlıyor...")
        from preprocess import DataPreprocessor
        
        preprocessor = DataPreprocessor('data/sayisal_loto_verileri.xlsx')
        if preprocessor.load_data() is None:
            logger.error("✗ Veri yüklenemiyor!")
            return False
        
        preprocessor.clean_data()
        preprocessor.check_data_quality()
        preprocessor.remove_outliers()
        preprocessor.normalize_data()
        preprocessor.standardize_data()
        preprocessor.save_cleaned_data()
        
        logger.info("✓ Veri ön işleme tamamlandı")
        return True
    except Exception as e:
        logger.error(f"✗ Veri ön işleme hatası: {e}")
        return False

def extract_features():
    """
    Özellikleri çıkar
    """
    try:
        logger.info("Özellik mühendisliği başlıyor...")
        import pandas as pd
        from feature_engineering import FeatureEngineer
        
        df = pd.read_excel('data/sayisal_loto_temizlenmis.xlsx')
        engineer = FeatureEngineer(df)
        df_with_features, feature_cols = engineer.generate_all_features()
        
        df_with_features.to_excel('data/sayisal_loto_ozellikleri.xlsx', index=False)
        
        logger.info(f"✓ Özellik mühendisliği tamamlandı ({len(feature_cols)} özellik)")
        return True
    except Exception as e:
        logger.error(f"✗ Özellik çıkarma hatası: {e}")
        return False

def train_models():
    """
    Modelleri eğit
    """
    try:
        logger.info("Model eğitimi başlıyor...")
        from train import LotteryTrainer
        
        trainer = LotteryTrainer()
        if trainer.prepare_data():
            if trainer.train_all_models():
                trainer.save_trained_models()
                logger.info("✓ Model eğitimi tamamlandı")
                return True
        
        logger.error("✗ Model eğitimi başarısız oldu!")
        return False
    except Exception as e:
        logger.error(f"✗ Model eğitim hatası: {e}")
        return False

def evaluate_models():
    """
    Modelleri değerlendir
    """
    try:
        logger.info("Model değerlendirmesi başlıyor...")
        from evaluate import LotteryEvaluator
        from train import LotteryTrainer
        
        trainer = LotteryTrainer()
        if not trainer.prepare_data():
            logger.error("✗ Veri hazırlama başarısız!")
            return False
        
        X_test, y_test = trainer.get_test_data()
        models = trainer.get_trained_models()
        
        evaluator = LotteryEvaluator()
        evaluator.evaluate_all_models(models, X_test, y_test)
        evaluator.print_comparison()
        evaluator.save_results()
        
        logger.info("✓ Model değerlendirmesi tamamlandı")
        return True
    except Exception as e:
        logger.error(f"✗ Model değerlendirme hatası: {e}")
        return False

def predict_numbers():
    """
    Sayıları tahmin et
    """
    try:
        logger.info("Sayı tahmini başlıyor...")
        from predict import LotteryPredictor
        
        predictor = LotteryPredictor(model_name='XGBoost')
        predictions = predictor.predict_lottery_numbers()
        
        if predictions is not None:
            predictor.save_predictions(predictions)
            
            logger.info("\n" + "="*60)
            logger.info("TÜM MODELLERİN TAHMİNLERİ:")
            logger.info("="*60)
            all_predictions = predictor.predict_multiple_models()
            
            logger.info("✓ Tahmin tamamlandı")
            return True
        
        logger.error("✗ Tahmin başarısız oldu!")
        return False
    except Exception as e:
        logger.error(f"✗ Tahmin hatası: {e}")
        return False

def statistical_analysis():
    """
    İstatistiksel analiz yap
    """
    try:
        logger.info("İstatistiksel analiz başlıyor...")
        import pandas as pd
        from analysis import LotteryAnalysis
        
        df = pd.read_excel('data/sayisal_loto_temizlenmis.xlsx')
        analyzer = LotteryAnalysis(df)
        analyzer.generate_statistical_report()
        analyzer.save_analysis()
        
        logger.info("✓ İstatistiksel analiz tamamlandı")
        return True
    except Exception as e:
        logger.error(f"✗ İstatistiksel analiz hatası: {e}")
        return False

def run_all():
    """
    Tüm işlemleri çalıştır
    """
    logger.info("\n" + "="*60)
    logger.info("TÜM İŞLEMLER ÇALIŞTIRILIYÖR...")
    logger.info("="*60 + "\n")
    
    steps = [
        ("Veri Çekme", fetch_data),
        ("Veri Ön İşleme", preprocess_data),
        ("Özellik Mühendisliği", extract_features),
        ("Model Eğitimi", train_models),
        ("Model Değerlendirmesi", evaluate_models),
        ("Sayı Tahmini", predict_numbers)
    ]
    
    completed = 0
    for step_name, step_func in steps:
        logger.info(f"\nAdım: {step_name}")
        logger.info("-" * 60)
        if step_func():
            completed += 1
        else:
            logger.warning(f"⚠ {step_name} başarısız oldu, devam ediliyor...\n")
    
    logger.info("\n" + "="*60)
    logger.info(f"✓ {completed}/{len(steps)} adım tamamlandı")
    logger.info("="*60)

def main():
    """
    Ana program
    """
    logger.info("\n" + "="*60)
    logger.info("SAYISAL LOTO TAHMİN SİSTEMİ'NE HOŞ GELDİNİZ")
    logger.info("="*60)
    
    while True:
        choice = print_menu()
        
        if choice == '1':
            fetch_data()
        elif choice == '2':
            preprocess_data()
        elif choice == '3':
            extract_features()
        elif choice == '4':
            train_models()
        elif choice == '5':
            evaluate_models()
        elif choice == '6':
            predict_numbers()
        elif choice == '7':
            run_all()
        elif choice == '8':
            statistical_analysis()
        elif choice == '9':
            logger.info("\nProgramdan çıkılıyor...")
            logger.info("Hoşça kalın!")
            sys.exit(0)
        else:
            logger.warning("✗ Geçersiz seçim! Lütfen 1-9 arasında seçim yapınız.")
        
        input("\nDevam etmek için Enter tuşuna basınız...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\nProgram kullanıcı tarafından durduruldu.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n✗ Programda hata oluştu: {e}")
        sys.exit(1)
