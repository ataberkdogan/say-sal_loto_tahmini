import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import logging
import os
import joblib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LotteryEvaluator:
    def __init__(self):
        self.results = {}
        self.best_model = None
        self.best_score = -float('inf')

    def evaluate_model(self, model_name, model, X_test, y_test):
        """
        Modeli değerlendir
        """
        try:
            logger.info(f"\n{model_name} değerlendiriliyor...")
            
            # Tahmin yap
            y_pred = model.predict(X_test)
            
            # Hataları hesapla (her bir sayı için)
            mse_scores = []
            mae_scores = []
            r2_scores = []
            rmse_scores = []
            
            for i in range(y_test.shape[1]):
                mse = mean_squared_error(y_test.iloc[:, i], y_pred[:, i])
                mae = mean_absolute_error(y_test.iloc[:, i], y_pred[:, i])
                r2 = r2_score(y_test.iloc[:, i], y_pred[:, i])
                rmse = np.sqrt(mse)
                
                mse_scores.append(mse)
                mae_scores.append(mae)
                r2_scores.append(r2)
                rmse_scores.append(rmse)
            
            # Ortalamaları hesapla
            avg_mse = np.mean(mse_scores)
            avg_mae = np.mean(mae_scores)
            avg_r2 = np.mean(r2_scores)
            avg_rmse = np.mean(rmse_scores)
            
            self.results[model_name] = {
                'MSE': avg_mse,
                'MAE': avg_mae,
                'R2': avg_r2,
                'RMSE': avg_rmse,
                'MSE_details': mse_scores,
                'MAE_details': mae_scores,
                'R2_details': r2_scores,
                'RMSE_details': rmse_scores
            }
            
            logger.info(f"{model_name} Sonuçları:")
            logger.info(f"  MSE (Ortalama): {avg_mse:.4f}")
            logger.info(f"  MAE (Ortalama): {avg_mae:.4f}")
            logger.info(f"  R² (Ortalama): {avg_r2:.4f}")
            logger.info(f"  RMSE (Ortalama): {avg_rmse:.4f}")
            
            # En iyi modeli takip et
            if avg_r2 > self.best_score:
                self.best_score = avg_r2
                self.best_model = model_name
            
            return True
        
        except Exception as e:
            logger.error(f"{model_name} değerlendirme hatası: {e}")
            return False

    def evaluate_all_models(self, models, X_test, y_test):
        """
        Tüm modelleri değerlendir
        """
        logger.info("\n=== Tüm Modeller Değerlendiriliyor ===")
        
        for model_name, model in models.items():
            self.evaluate_model(model_name, model, X_test, y_test)
        
        return True

    def print_comparison(self):
        """
        Modelleri karşılaştır
        """
        logger.info("\n" + "="*60)
        logger.info("MODEL KARŞILAŞTIRMASI")
        logger.info("="*60)
        
        # Sonuçları DataFrame'e dönüştür
        comparison_data = {
            'Model': [],
            'MSE': [],
            'MAE': [],
            'R2': [],
            'RMSE': []
        }
        
        for model_name, metrics in self.results.items():
            comparison_data['Model'].append(model_name)
            comparison_data['MSE'].append(f"{metrics['MSE']:.4f}")
            comparison_data['MAE'].append(f"{metrics['MAE']:.4f}")
            comparison_data['R2'].append(f"{metrics['R2']:.4f}")
            comparison_data['RMSE'].append(f"{metrics['RMSE']:.4f}")
        
        df_comparison = pd.DataFrame(comparison_data)
        logger.info("\n" + df_comparison.to_string(index=False))
        
        logger.info("\n" + "="*60)
        logger.info(f"EN İYİ MODEL: {self.best_model} (R² = {self.best_score:.4f})")
        logger.info("="*60)

    def save_results(self, output_file='data/model_results.csv'):
        """
        Sonuçları CSV dosyasına kaydet
        """
        try:
            os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
            
            # Sonuçları DataFrame'e dönüştür
            results_data = []
            for model_name, metrics in self.results.items():
                results_data.append({
                    'Model': model_name,
                    'MSE': metrics['MSE'],
                    'MAE': metrics['MAE'],
                    'R2': metrics['R2'],
                    'RMSE': metrics['RMSE']
                })
            
            df_results = pd.DataFrame(results_data)
            df_results = df_results.sort_values('R2', ascending=False).reset_index(drop=True)
            
            df_results.to_csv(output_file, index=False)
            logger.info(f"\nSonuçlar {output_file} dosyasına kaydedildi")
            return True
        
        except Exception as e:
            logger.error(f"Sonuç kayıt hatası: {e}")
            return False

    def get_best_model(self):
        """
        En iyi modelin adını döndür
        """
        return self.best_model

    def get_results(self):
        """
        Tüm sonuçları döndür
        """
        return self.results


def main():
    # Eğitilmiş modelleri yükle
    model_dir = 'models/'
    
    if not os.path.exists(model_dir):
        logger.error(f"Model dizini bulunamadı: {model_dir}")
        logger.info("Lütfen önce train.py dosyasını çalıştırın")
        return
    
    # Train dosyasından test verilerini al
    from train import LotteryTrainer
    
    trainer = LotteryTrainer()
    if not trainer.prepare_data():
        logger.error("Veri hazırlama başarısız")
        return
    
    X_test, y_test = trainer.get_test_data()
    models = trainer.get_trained_models()
    
    # Modelleri değerlendir
    evaluator = LotteryEvaluator()
    evaluator.evaluate_all_models(models, X_test, y_test)
    
    # Sonuçları göster
    evaluator.print_comparison()
    
    # Sonuçları kaydet
    evaluator.save_results()


if __name__ == "__main__":
    main()
