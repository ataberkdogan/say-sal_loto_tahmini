import pandas as pd
import numpy as np
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self, df):
        self.df = df.copy()
        self.feature_columns = []

    def create_lag_features(self, lags=[1, 2, 3, 5, 7]):
        """
        Gecikmeli (lag) özellikleri oluştur
        """
        logger.info(f"Lag özellikleri oluşturuluyor (lags={lags})...")
        
        for lag in lags:
            for i in range(1, 7):
                col = f'Sayi_{i}'
                self.df[f'{col}_lag_{lag}'] = self.df[col].shift(lag)
                self.feature_columns.append(f'{col}_lag_{lag}')
        
        logger.info(f"{len(lags) * 6} lag özelliği oluşturuldu")
        return self.df

    def create_rolling_features(self, windows=[3, 5, 7, 10]):
        """
        Hareketli ortalama (rolling) özellikleri oluştur
        """
        logger.info(f"Rolling özellikleri oluşturuluyor (windows={windows})...")
        
        for window in windows:
            for i in range(1, 7):
                col = f'Sayi_{i}'
                
                # Hareketli ortalama
                self.df[f'{col}_rolling_mean_{window}'] = self.df[col].rolling(window=window, min_periods=1).mean()
                self.feature_columns.append(f'{col}_rolling_mean_{window}')
                
                # Hareketli standart sapma
                self.df[f'{col}_rolling_std_{window}'] = self.df[col].rolling(window=window, min_periods=1).std()
                self.feature_columns.append(f'{col}_rolling_std_{window}')
                
                # Hareketli min
                self.df[f'{col}_rolling_min_{window}'] = self.df[col].rolling(window=window, min_periods=1).min()
                self.feature_columns.append(f'{col}_rolling_min_{window}')
                
                # Hareketli max
                self.df[f'{col}_rolling_max_{window}'] = self.df[col].rolling(window=window, min_periods=1).max()
                self.feature_columns.append(f'{col}_rolling_max_{window}')
        
        logger.info(f"{len(windows) * 6 * 4} rolling özelliği oluşturuldu")
        return self.df

    def create_statistical_features(self):
        """
        İstatistiksel özellikler oluştur
        """
        logger.info("İstatistiksel özellikler oluşturuluyor...")
        
        # Toplam
        self.df['Sum'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].sum(axis=1)
        self.feature_columns.append('Sum')
        
        # Ortalama
        self.df['Mean'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].mean(axis=1)
        self.feature_columns.append('Mean')
        
        # Medyan
        self.df['Median'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].median(axis=1)
        self.feature_columns.append('Median')
        
        # Standart sapma
        self.df['Std'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].std(axis=1)
        self.feature_columns.append('Std')
        
        # Varyans
        self.df['Variance'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].var(axis=1)
        self.feature_columns.append('Variance')
        
        # Min
        self.df['Min'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].min(axis=1)
        self.feature_columns.append('Min')
        
        # Max
        self.df['Max'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].max(axis=1)
        self.feature_columns.append('Max')
        
        # Range (Max - Min)
        self.df['Range'] = self.df['Max'] - self.df['Min']
        self.feature_columns.append('Range')
        
        # Çeyrekler arası aralık (IQR)
        q1 = self.df[[f'Sayi_{i}' for i in range(1, 7)]].quantile(0.25, axis=1)
        q3 = self.df[[f'Sayi_{i}' for i in range(1, 7)]].quantile(0.75, axis=1)
        self.df['IQR'] = q3 - q1
        self.feature_columns.append('IQR')
        
        # Çarpıklık (Skewness)
        self.df['Skewness'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].skew(axis=1)
        self.feature_columns.append('Skewness')
        
        # Basıklık (Kurtosis)
        self.df['Kurtosis'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].kurtosis(axis=1)
        self.feature_columns.append('Kurtosis')
        
        logger.info("10 istatistiksel özellik oluşturuldu")
        return self.df

    def create_frequency_features(self):
        """
        Sıklık tabanlı özellikler oluştur
        """
        logger.info("Sıklık özellikleri oluşturuluyor...")
        
        # Son 10 çekilişte kaç kez çıktığı
        for i in range(1, 7):
            col = f'Sayi_{i}'
            self.df[f'{col}_freq_10'] = self.df[col].rolling(window=10, min_periods=1).apply(
                lambda x: (x == x.iloc[-1]).sum() - 1 if len(x) > 0 else 0
            )
            self.feature_columns.append(f'{col}_freq_10')
        
        # Son 30 çekilişte kaç kez çıktığı
        for i in range(1, 7):
            col = f'Sayi_{i}'
            self.df[f'{col}_freq_30'] = self.df[col].rolling(window=30, min_periods=1).apply(
                lambda x: (x == x.iloc[-1]).sum() - 1 if len(x) > 0 else 0
            )
            self.feature_columns.append(f'{col}_freq_30')
        
        logger.info("12 sıklık özelliği oluşturuldu")
        return self.df

    def create_time_features(self):
        """
        Zaman tabanlı özellikler oluştur
        """
        logger.info("Zaman özellikleri oluşturuluyor...")
        
        if 'Cekilis_Tarihi' in self.df.columns:
            self.df['Tarih'] = pd.to_datetime(self.df['Cekilis_Tarihi'], errors='coerce')
            
            # Gün
            self.df['Gun'] = self.df['Tarih'].dt.day
            self.feature_columns.append('Gun')
            
            # Ay
            self.df['Ay'] = self.df['Tarih'].dt.month
            self.feature_columns.append('Ay')
            
            # Yıl
            self.df['Yil'] = self.df['Tarih'].dt.year
            self.feature_columns.append('Yil')
            
            # Haftanın günü
            self.df['Haftanin_Gunu'] = self.df['Tarih'].dt.dayofweek
            self.feature_columns.append('Haftanin_Gunu')
            
            # Yılın günü
            self.df['Yilin_Gunu'] = self.df['Tarih'].dt.dayofyear
            self.feature_columns.append('Yilin_Gunu')
            
            # Haftanın numarası
            self.df['Hafta_No'] = self.df['Tarih'].dt.isocalendar().week
            self.feature_columns.append('Hafta_No')
            
            logger.info("6 zaman özelliği oluşturuldu")
        
        return self.df

    def create_difference_features(self):
        """
        Fark (difference) özellikleri oluştur
        """
        logger.info("Fark özellikleri oluşturuluyor...")
        
        for i in range(1, 7):
            col = f'Sayi_{i}'
            self.df[f'{col}_diff_1'] = self.df[col].diff()
            self.feature_columns.append(f'{col}_diff_1')
            
            self.df[f'{col}_diff_2'] = self.df[col].diff().diff()
            self.feature_columns.append(f'{col}_diff_2')
        
        logger.info("12 fark özelliği oluşturuldu")
        return self.df

    def create_interaction_features(self):
        """
        Etkileşim (interaction) özellikleri oluştur
        """
        logger.info("Etkileşim özellikleri oluşturuluyor...")
        
        # Sayılar arasındaki fark
        self.df['Sayi_Max_Min_Diff'] = self.df['Sayi_6'] - self.df['Sayi_1']
        self.feature_columns.append('Sayi_Max_Min_Diff')
        
        # Çift/Tek sayı oranı
        odd_count = (self.df[[f'Sayi_{i}' for i in range(1, 7)]] % 2 == 1).sum(axis=1)
        self.df['Odd_Count'] = odd_count
        self.feature_columns.append('Odd_Count')
        
        even_count = (self.df[[f'Sayi_{i}' for i in range(1, 7)]] % 2 == 0).sum(axis=1)
        self.df['Even_Count'] = even_count
        self.feature_columns.append('Even_Count')
        
        # 50'den büyük sayı sayısı
        large_count = (self.df[[f'Sayi_{i}' for i in range(1, 7)]] > 45).sum(axis=1)
        self.df['Large_Count'] = large_count
        self.feature_columns.append('Large_Count')
        
        # 50'den küçük sayı sayısı
        small_count = (self.df[[f'Sayi_{i}' for i in range(1, 7)]] <= 45).sum(axis=1)
        self.df['Small_Count'] = small_count
        self.feature_columns.append('Small_Count')
        
        logger.info("5 etkileşim özelliği oluşturuldu")
        return self.df

    def handle_missing_values(self):
        """
        Eksik değerleri işle
        """
        logger.info("Eksik değerler işleniyor...")
        
        # NaN değerleri ileriye doldur, sonra geriye doldur
        self.df = self.df.fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        logger.info("Eksik değerler işlendi")
        return self.df

    def get_engineered_features(self):
        """
        Mühendislik yapılmış özellikleri döndür
        """
        return self.df, self.feature_columns

    def generate_all_features(self):
        """
        Tüm özelikleri oluştur
        """
        logger.info("\n=== Tüm Özellikler Oluşturuluyor ===")
        
        self.create_lag_features()
        self.create_rolling_features()
        self.create_statistical_features()
        self.create_frequency_features()
        self.create_time_features()
        self.create_difference_features()
        self.create_interaction_features()
        self.handle_missing_values()
        
        logger.info(f"\nToplam {len(self.feature_columns)} özellik oluşturuldu")
        
        return self.df, self.feature_columns


def main():
    # Temizlenen verileri yükle
    df = pd.read_excel('data/sayisal_loto_temizlenmis.xlsx')
    
    # Özellikler oluştur
    engineer = FeatureEngineer(df)
    df_with_features, feature_cols = engineer.generate_all_features()
    
    # Sonuçları kaydet
    df_with_features.to_excel('data/sayisal_loto_ozellikleri.xlsx', index=False)
    
    logger.info(f"\nÖzelliklerle birlikte veriler {len(df_with_features)} satır, {len(df_with_features.columns)} sütunla kaydedildi")
    logger.info(f"Kullanılan özellikler: {feature_cols[:10]}... (ve {len(feature_cols) - 10} daha)")


if __name__ == "__main__":
    main()
