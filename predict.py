import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging
import joblib
import os

# Modülleri içe aktar
from feature_engineering import FeatureEngineer
from preprocess import DataPreprocessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LotteryPredictor:
    def __init__(self, model_name='XGBoost', model_dir='models/'):
        self.model_name = model_name
        self.model_dir = model_dir
        self.model = None
        self.scaler = MinMaxScaler()
        self.feature_names = []
        self.load_model()

    def load_model(self):
        """
        Eğitilmiş modeli yükle
        """
        try:
            model_path = os.path.join(self.model_dir, f'{self.model_name}_model.pkl')
            self.model = joblib.load(model_path)
            logger.info(f"Model '{self.model_name}' başarıyla yüklendi: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Model yükleme hatası: {e}")
            return False

    def prepare_features(self, data_path='data/sayisal_loto_verileri.xlsx'):
        """
        Tahmin için özellikleri hazırla
        """
        try:
            # Verileri yükle ve temizle
            preprocessor = DataPreprocessor(data_path)
            if preprocessor.load_data() is None:
                logger.error("Veri yüklenemiyor!")
                return None
            
            preprocessor.clean_data()
            preprocessor.normalize_data()
            preprocessor.standardize_data()
            
            df = preprocessor.get_processed_data()
            
            # Son satırı al (en yeni çekilişi)
            df_latest = df.iloc[-1:].copy()
            
            # Özellikleri çıkar
            engineer = FeatureEngineer(df)
            df_with_features, feature_cols = engineer.generate_all_features()
            
            self.feature_names = feature_cols
            
            # En son satırın özelliklerini al
            target_cols = ['Sayi_1', 'Sayi_2', 'Sayi_3', 'Sayi_4', 'Sayi_5', 'Sayi_6']
            feature_cols_clean = [col for col in feature_cols if col not in target_cols and col in df_with_features.columns]
            
            X_latest = df_with_features[feature_cols_clean].iloc[-1:].fillna(0)
            
            logger.info(f"Özellikler hazırlandı: {X_latest.shape[1]} feature")
            
            return X_latest
        
        except Exception as e:
            logger.error(f"Özellik hazırlama hatası: {e}")
            return None

    def predict_lottery_numbers(self, features=None):
        """
        Sayısal Loto sayılarını tahmin et
        """
        try:
            if self.model is None:
                logger.error("Model yüklenmedi!")
                return None
            
            if features is None:
                features = self.prepare_features()
            
            if features is None:
                logger.error("Özellikler hazırlanamadı!")
                return None
            
            # Tahmin yap
            logger.info(f"\n{self.model_name} modeli ile tahmin yapılıyor...")
            predictions = self.model.predict(features)
            
            # Tahminleri tamsayıya dönüştür ve sırayla düzenle
            predicted_numbers = np.round(predictions[0]).astype(int)
            predicted_numbers = np.clip(predicted_numbers, 1, 49)  # 1-49 aralığına sıkıştır
            predicted_numbers = sorted(predicted_numbers)
            
            logger.info(f"\n{'='*50}")
            logger.info(f"TAHMİN EDILEN SAYILAR ({self.model_name}):")
            logger.info(f"{'='*50}")
            logger.info(f"{' '.join(map(str, predicted_numbers))}")
            logger.info(f"Toplam: {sum(predicted_numbers)}")
            logger.info(f"Ortalama: {sum(predicted_numbers) / 6:.2f}")
            logger.info(f"{'='*50}")
            
            return predicted_numbers
        
        except Exception as e:
            logger.error(f"Tahmin hatası: {e}")
            return None

    def predict_with_confidence(self, features=None):
        """
        Güven skoru ile tahmin yap
        """
        try:
            predictions = self.model.predict(features if features is not None else self.prepare_features())
            
            # Tahminleri tamsayıya dönüştür
            predicted_numbers = np.round(predictions[0]).astype(int)
            predicted_numbers = np.clip(predicted_numbers, 1, 49)
            predicted_numbers = sorted(predicted_numbers)
            
            # Güven skoru (tahminlerin varyasyonu azsa güven yüksek)
            confidence = 1.0 / (1.0 + np.std(predictions[0]))
            
            logger.info(f"\nGüven Skoru: {confidence:.4f}")
            
            return predicted_numbers, confidence
        
        except Exception as e:
            logger.error(f"Güven skorlu tahmin hatası: {e}")
            return None, 0

    def predict_multiple_models(self, model_names=None):
        """
        Birden fazla modelle tahmin yap ve sonuçları karşılaştır
        """
        try:
            if model_names is None:
                model_names = ['RandomForest', 'XGBoost', 'CatBoost', 'LightGBM']
            
            features = self.prepare_features()
            if features is None:
                logger.error("Özellikler hazırlanamadı!")
                return None
            
            logger.info(f"\n{'='*60}")
            logger.info("TÜYÜN MODELLER İLE TAHMİN")
            logger.info(f"{'='*60}\n")
            
            all_predictions = {}
            
            for model_name in model_names:
                try:
                    model_path = os.path.join(self.model_dir, f'{model_name}_model.pkl')
                    if not os.path.exists(model_path):
                        logger.warning(f"Model bulunamadı: {model_path}")
                        continue
                    
                    model = joblib.load(model_path)
                    predictions = model.predict(features)
                    predicted_numbers = np.round(predictions[0]).astype(int)
                    predicted_numbers = np.clip(predicted_numbers, 1, 49)
                    predicted_numbers = sorted(predicted_numbers)
                    
                    all_predictions[model_name] = predicted_numbers
                    
                    logger.info(f"{model_name}: {' '.join(map(str, predicted_numbers))}")
                
                except Exception as e:
                    logger.warning(f"{model_name} tahmin hatası: {e}")
            
            logger.info(f"\n{'='*60}")
            
            return all_predictions
        
        except Exception as e:
            logger.error(f"Çoklu model tahmin hatası: {e}")
            return None

    def save_predictions(self, predicted_numbers, output_file='data/predictions.txt'):
        """
        Tahminleri dosyaya kaydet
        """
        try:
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Tahmin Edilen Sayılar ({self.model_name}):\n")
                f.write(f"{'='*50}\n")
                f.write(f"{' '.join(map(str, predicted_numbers))}\n")
                f.write(f"\nToplam: {sum(predicted_numbers)}\n")
                f.write(f"Ortalama: {sum(predicted_numbers) / 6:.2f}\n")
                f.write(f"{'='*50}\n")
            
            logger.info(f"Tahminler {output_file} dosyasına kaydedildi")
            return True
        
        except Exception as e:
            logger.error(f"Tahmin kayıt hatası: {e}")
            return False


def main():
    # Tahminciyi oluştur
    predictor = LotteryPredictor(model_name='XGBoost')
    
    # Tek modelle tahmin yap
    predictions = predictor.predict_lottery_numbers()
    
    if predictions is not None:
        # Tahminleri kaydet
        predictor.save_predictions(predictions)
        
        # Tüm modelleri dene
        logger.info("\n\nTÜM MODELLERİN TAHMİNLERİ:")
        all_predictions = predictor.predict_multiple_models()


if __name__ == "__main__":
    main()
