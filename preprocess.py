import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self, data_path='data/sayisal_loto_verileri.xlsx'):
        self.data_path = data_path
        self.df = None
        self.scaler = MinMaxScaler()
        self.standard_scaler = StandardScaler()

    def load_data(self):
        """
        Excel dosyasından verileri yükle
        """
        try:
            logger.info(f"Veriler {self.data_path} dosyasından yükleniyor...")
            self.df = pd.read_excel(self.data_path)
            logger.info(f"Başarıyla {len(self.df)} satır yüklendi")
            return self.df
        except Exception as e:
            logger.error(f"Veri yükleme hatası: {e}")
            return None

    def clean_data(self):
        """
        Verileri temizle: eksik değerler, duplikatlar, vb.
        """
        try:
            logger.info("Veri temizleme başlıyor...")
            
            # Duplikatları kaldır
            initial_len = len(self.df)
            self.df = self.df.drop_duplicates(subset=['Cekilis_No'])
            logger.info(f"Duplikatlar kaldırıldı: {initial_len - len(self.df)} satır")
            
            # Eksik değerleri kontrol et
            missing = self.df.isnull().sum()
            if missing.sum() > 0:
                logger.warning(f"Eksik değerler bulundu:\n{missing[missing > 0]}")
                self.df = self.df.dropna()
            
            # Tarih formatını düzenle
            self.df['Cekilis_Tarihi'] = pd.to_datetime(self.df['Cekilis_Tarihi'], format='%d.%m.%Y', errors='coerce')
            
            # Sırayla düzenle
            self.df = self.df.sort_values('Cekilis_Tarihi').reset_index(drop=True)
            
            logger.info("Veri temizleme tamamlandı")
            return self.df
        except Exception as e:
            logger.error(f"Temizleme hatası: {e}")
            return self.df

    def check_data_quality(self):
        """
        Veri kalitesini kontrol et
        """
        logger.info("\n=== Veri Kalitesi Raporu ===")
        
        # Her sayının aralığını kontrol et
        for i in range(1, 7):
            col = f'Sayi_{i}'
            if col in self.df.columns:
                min_val = self.df[col].min()
                max_val = self.df[col].max()
                logger.info(f"{col}: Min={min_val}, Max={max_val}, Ort={self.df[col].mean():.2f}")
        
        # Toplamları kontrol et
        logger.info(f"Toplam: Min={self.df['Toplam'].min()}, Max={self.df['Toplam'].max()}, Ort={self.df['Toplam'].mean():.2f}")
        
        # Her sayının kullanılma sıklığını göster
        logger.info("\n=== Sayıların Sıklığı ===")
        all_numbers = []
        for i in range(1, 7):
            col = f'Sayi_{i}'
            all_numbers.extend(self.df[col].values)
        
        number_counts = pd.Series(all_numbers).value_counts().sort_index()
        logger.info(f"En sık çıkan sayılar:\n{number_counts.head(10)}")

    def normalize_data(self, columns=None):
        """
        Verileri normalize et (0-1 aralığına)
        """
        try:
            if columns is None:
                columns = [f'Sayi_{i}' for i in range(1, 7)] + ['Toplam', 'Ortalama']
            
            logger.info(f"Normalizasyon uygulanıyor: {columns}")
            
            for col in columns:
                if col in self.df.columns:
                    self.df[f'{col}_normalized'] = self.scaler.fit_transform(self.df[[col]])
            
            return self.df
        except Exception as e:
            logger.error(f"Normalizasyon hatası: {e}")
            return self.df

    def standardize_data(self, columns=None):
        """
        Verileri standardize et (z-score)
        """
        try:
            if columns is None:
                columns = [f'Sayi_{i}' for i in range(1, 7)] + ['Toplam', 'Ortalama']
            
            logger.info(f"Standardizasyon uygulanıyor: {columns}")
            
            for col in columns:
                if col in self.df.columns:
                    self.df[f'{col}_standardized'] = self.standard_scaler.fit_transform(self.df[[col]])
            
            return self.df
        except Exception as e:
            logger.error(f"Standardizasyon hatası: {e}")
            return self.df

    def remove_outliers(self, threshold=3):
        """
        İstatistiksel yöntemle aykırı değerleri kaldır
        """
        try:
            logger.info(f"Aykırı değerler kaldırılıyor (threshold={threshold})...")
            initial_len = len(self.df)
            
            numeric_columns = [f'Sayi_{i}' for i in range(1, 7)] + ['Toplam', 'Ortalama']
            
            for col in numeric_columns:
                if col in self.df.columns:
                    mean = self.df[col].mean()
                    std = self.df[col].std()
                    self.df = self.df[(np.abs(self.df[col] - mean) <= threshold * std)]
            
            removed = initial_len - len(self.df)
            logger.info(f"Aykırı değerler kaldırıldı: {removed} satır")
            
            return self.df
        except Exception as e:
            logger.error(f"Aykırı değer kaldırma hatası: {e}")
            return self.df

    def save_cleaned_data(self, output_path='data/sayisal_loto_temizlenmis.xlsx'):
        """
        Temizlenen verileri kaydet
        """
        try:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            self.df.to_excel(output_path, index=False)
            logger.info(f"Temizlenen veriler {output_path} dosyasına kaydedildi")
            return True
        except Exception as e:
            logger.error(f"Kayıt hatası: {e}")
            return False

    def get_processed_data(self):
        """
        İşlenmiş verileri döndür
        """
        return self.df


def main():
    preprocessor = DataPreprocessor()
    
    # Verileri yükle
    if preprocessor.load_data() is not None:
        # Verileri temizle
        preprocessor.clean_data()
        
        # Veri kalitesini kontrol et
        preprocessor.check_data_quality()
        
        # Aykırı değerleri kaldır
        preprocessor.remove_outliers()
        
        # Normalizasyon ve Standardizasyon
        preprocessor.normalize_data()
        preprocessor.standardize_data()
        
        # Temizlenen verileri kaydet
        preprocessor.save_cleaned_data()
        
        logger.info("\nVeri ön işleme tamamlandı!")


if __name__ == "__main__":
    main()
