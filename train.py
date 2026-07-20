import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import MinMaxScaler
import logging
import os
import sys

# Modelleri içe aktar
from models import LotteryModels
from preprocess import DataPreprocessor
from feature_engineering import FeatureEngineer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LotteryTrainer:
    def __init__(self):
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.scaler = MinMaxScaler()
        self.feature_names = []

    def prepare_data(self, data_path='data/sayisal_loto_verileri.xlsx'):
        """
        Verileri hazırla: yükle, temizle, özellikleri çıkar
        """
        logger.info("\n=== Veri Hazırlama ===")
        
        # Verileri yükle ve temizle
        preprocessor = DataPreprocessor(data_path)
        if preprocessor.load_data() is None:
            logger.error("Veri yüklenemiyor!")
            return False
        
        preprocessor.clean_data()
        preprocessor.check_data_quality()
        preprocessor.remove_outliers()
        preprocessor.normalize_data()
        preprocessor.standardize_data()
        
        df = preprocessor.get_processed_data()
        
        # Özellikleri çıkar
        logger.info("\n=== Özellik Mühendisliği ===")
        engineer = FeatureEngineer(df)
        df_with_features, feature_cols = engineer.generate_all_features()
        
        self.feature_names = feature_cols
        
        # Hedef değişkenleri ayarla (6 sayı)
        target_cols = ['Sayi_1', 'Sayi_2', 'Sayi_3', 'Sayi_4', 'Sayi_5', 'Sayi_6']
        
        # Feature'ları seç (eksik değerler varsa kaldır)
        feature_cols_clean = [col for col in feature_cols if col not in target_cols and col in df_with_features.columns]
        
        X = df_with_features[feature_cols_clean].fillna(0)
        y = df_with_features[target_cols].fillna(0)
        
        logger.info(f"Feature sayısı: {X.shape[1]}")
        logger.info(f"Hedef sayısı: {y.shape[1]}")
        logger.info(f"Veri satırı: {X.shape[0]}")
        
        # Train-test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info(f"\nTrain seti: {self.X_train.shape[0]} satır")
        logger.info(f"Test seti: {self.X_test.shape[0]} satır")
        
        return True

    def train_all_models(self):
        """
        Tüm modelleri eğit
        """
        if self.X_train is None:
            logger.error("Veriler hazırlanmadı!")
            return False
        
        logger.info("\n=== Modeller Eğitiliyor ===")
        
        lottery_models = LotteryModels()
        lottery_models.create_all_models()
        
        model_list = lottery_models.get_all_models()
        
        for model_name, model in model_list.items():
            try:
                logger.info(f"\n{model_name} eğitiliyor...")
                model.fit(self.X_train, self.y_train)
                self.models[model_name] = model
                logger.info(f"{model_name} başarıyla eğitildi")
            except Exception as e:
                logger.error(f"{model_name} eğitim hatası: {e}")
        
        logger.info(f"\nToplam {len(self.models)} model eğitildi")
        return len(self.models) > 0

    def save_trained_models(self, model_dir='models/'):
        """
        Eğitilmiş modelleri kaydet
        """
        try:
            os.makedirs(model_dir, exist_ok=True)
            
            import joblib
            for model_name, model in self.models.items():
                filepath = os.path.join(model_dir, f'{model_name}_model.pkl')
                joblib.dump(model, filepath)
                logger.info(f"{model_name} kaydedildi: {filepath}")
            
            return True
        except Exception as e:
            logger.error(f"Model kayıt hatası: {e}")
            return False

    def get_trained_models(self):
        """
        Eğitilmiş modelleri döndür
        """
        return self.models

    def get_test_data(self):
        """
        Test verilerini döndür
        """
        return self.X_test, self.y_test


def main():
    trainer = LotteryTrainer()
    
    # Verileri hazırla
    if trainer.prepare_data():
        # Modelleri eğit
        if trainer.train_all_models():
            # Modelleri kaydet
            trainer.save_trained_models()
            logger.info("\nEğitim tamamlandı!")
        else:
            logger.error("Model eğitimi başarısız oldu!")
    else:
        logger.error("Veri hazırlama başarısız oldu!")


if __name__ == "__main__":
    main()
