import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.multioutput import MultiOutputRegressor
import logging
import joblib
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LotteryModels:
    def __init__(self):
        self.models = {}
        self.scaler = MinMaxScaler()
        self.feature_names = []

    def create_random_forest(self, n_estimators=200, max_depth=20):
        """
        Random Forest modeli oluştur
        """
        logger.info("Random Forest modeli oluşturuluyor...")
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        self.models['RandomForest'] = model
        return model

    def create_xgboost(self, n_estimators=200, max_depth=7):
        """
        XGBoost modeli oluştur
        """
        logger.info("XGBoost modeli oluşturuluyor...")
        model = XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbosity=0,
            n_jobs=-1
        )
        self.models['XGBoost'] = model
        return model

    def create_catboost(self, n_estimators=200, max_depth=7):
        """
        CatBoost modeli oluştur
        """
        logger.info("CatBoost modeli oluşturuluyor...")
        model = CatBoostRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=0.05,
            random_state=42,
            verbose=False
        )
        self.models['CatBoost'] = model
        return model

    def create_lightgbm(self, n_estimators=200, max_depth=7):
        """
        LightGBM modeli oluştur
        """
        logger.info("LightGBM modeli oluşturuluyor...")
        model = LGBMRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        self.models['LightGBM'] = model
        return model

    def create_naive_bayes(self):
        """
        Naive Bayes modeli oluştur (çoklu çıktı için)
        """
        logger.info("Naive Bayes modeli oluşturuluyor...")
        model = MultiOutputRegressor(GaussianNB())
        self.models['NaiveBayes'] = model
        return model

    def create_all_models(self):
        """
        Tüm modelleri oluştur
        """
        logger.info("\n=== Tüm Modeller Oluşturuluyor ===")
        self.create_random_forest()
        self.create_xgboost()
        self.create_catboost()
        self.create_lightgbm()
        self.create_naive_bayes()
        logger.info(f"Toplam {len(self.models)} model oluşturuldu")
        return self.models

    def get_model(self, model_name):
        """
        Belirtilen modeli al
        """
        return self.models.get(model_name)

    def get_all_models(self):
        """
        Tüm modelleri al
        """
        return self.models

    def save_model(self, model_name, filepath='models/'):
        """
        Modeli kaydet
        """
        try:
            os.makedirs(filepath, exist_ok=True)
            model = self.models.get(model_name)
            if model is None:
                logger.error(f"Model '{model_name}' bulunamadı")
                return False
            
            joblib.dump(model, f'{filepath}{model_name}_model.pkl')
            logger.info(f"Model '{model_name}' başarıyla {filepath}{model_name}_model.pkl dosyasına kaydedildi")
            return True
        except Exception as e:
            logger.error(f"Model kayıt hatası: {e}")
            return False

    def load_model(self, model_name, filepath='models/'):
        """
        Modeli yükle
        """
        try:
            model = joblib.load(f'{filepath}{model_name}_model.pkl')
            self.models[model_name] = model
            logger.info(f"Model '{model_name}' başarıyla {filepath}{model_name}_model.pkl dosyasından yüklendi")
            return model
        except Exception as e:
            logger.error(f"Model yükleme hatası: {e}")
            return None

    def save_all_models(self, filepath='models/'):
        """
        Tüm modelleri kaydet
        """
        for model_name in self.models.keys():
            self.save_model(model_name, filepath)

    def load_all_models(self, filepath='models/'):
        """
        Tüm modelleri yükle
        """
        for model_name in ['RandomForest', 'XGBoost', 'CatBoost', 'LightGBM', 'NaiveBayes']:
            self.load_model(model_name, filepath)


def main():
    # Modelleri oluştur
    lottery_models = LotteryModels()
    lottery_models.create_all_models()
    
    # Modelleri göster
    logger.info("\nOluşturulan Modeller:")
    for name, model in lottery_models.get_all_models().items():
        logger.info(f"  - {name}")


if __name__ == "__main__":
    main()
