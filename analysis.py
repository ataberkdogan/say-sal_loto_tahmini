import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LotteryAnalysis:
    def __init__(self, df):
        self.df = df.copy()
        
        # Türkçe yazı tipi ayarla
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

    def analyze_number_frequency(self):
        """
        Sayıların sıklığını analiz et
        """
        logger.info("\n=== SAYI SIKLIĞI ANALİZİ ===")
        
        all_numbers = []
        for i in range(1, 7):
            col = f'Sayi_{i}'
            all_numbers.extend(self.df[col].values)
        
        freq = pd.Series(all_numbers).value_counts().sort_index()
        
        logger.info("\nEn sık çıkan 15 sayı:")
        logger.info(freq.head(15))
        
        logger.info("\nEn az çıkan 15 sayı:")
        logger.info(freq.tail(15))
        
        return freq

    def analyze_number_distribution(self):
        """
        Sayıların dağılımını analiz et
        """
        logger.info("\n=== SAYI DAĞILIMI ANALİZİ ===")
        
        for i in range(1, 7):
            col = f'Sayi_{i}'
            logger.info(f"\n{col}:")
            logger.info(f"  Ortalama: {self.df[col].mean():.2f}")
            logger.info(f"  Medyan: {self.df[col].median():.2f}")
            logger.info(f"  Standart Sapma: {self.df[col].std():.2f}")
            logger.info(f"  Min: {self.df[col].min()}")
            logger.info(f"  Max: {self.df[col].max()}")
            logger.info(f"  Çarpıklık: {stats.skew(self.df[col]):.3f}")
            logger.info(f"  Basıklık: {stats.kurtosis(self.df[col]):.3f}")

    def analyze_sum_distribution(self):
        """
        Toplam sayıların dağılımını analiz et
        """
        logger.info("\n=== TOPLAM SAYI DAĞILIMI ANALİZİ ===")
        
        if 'Toplam' not in self.df.columns:
            self.df['Toplam'] = self.df[[f'Sayi_{i}' for i in range(1, 7)]].sum(axis=1)
        
        logger.info(f"Toplam Ortalama: {self.df['Toplam'].mean():.2f}")
        logger.info(f"Toplam Medyan: {self.df['Toplam'].median():.2f}")
        logger.info(f"Toplam Standart Sapma: {self.df['Toplam'].std():.2f}")
        logger.info(f"Toplam Min: {self.df['Toplam'].min()}")
        logger.info(f"Toplam Max: {self.df['Toplam'].max()}")

    def analyze_correlation(self):
        """
        Sayılar arasındaki korelasyonu analiz et
        """
        logger.info("\n=== KORELASYON ANALİZİ ===")
        
        numeric_cols = [f'Sayi_{i}' for i in range(1, 7)]
        correlation_matrix = self.df[numeric_cols].corr()
        
        logger.info("\nKorelasyon Matrisi:")
        logger.info(correlation_matrix)
        
        return correlation_matrix

    def analyze_patterns(self):
        """
        Desenleri analiz et
        """
        logger.info("\n=== DESEN ANALİZİ ===")
        
        # Ardışık sayılar
        logger.info("\nArdışık Sayılar Analizi:")
        consecutive_count = 0
        total_patterns = 0
        
        for idx, row in self.df.iterrows():
            numbers = sorted([row[f'Sayi_{i}'] for i in range(1, 7)])
            
            for i in range(len(numbers) - 1):
                if numbers[i+1] - numbers[i] == 1:
                    consecutive_count += 1
            
            total_patterns += 5
        
        if total_patterns > 0:
            logger.info(f"Ardışık sayı oranı: {consecutive_count/total_patterns*100:.2f}%")
        
        # Tekrar eden sayılar
        logger.info("\nTekrar Eden Sayılar Analizi:")
        repeat_count = 0
        for i in range(1, 7):
            col = f'Sayi_{i}'
            repeat_count += (self.df[col] == self.df[col].shift()).sum()
        
        logger.info(f"Tekrar eden sayı oranı: {repeat_count/(len(self.df)*6)*100:.2f}%")

    def analyze_temporal_patterns(self):
        """
        Zaman tabanlı desenleri analiz et
        """
        logger.info("\n=== ZAMANSAL DESEN ANALİZİ ===")
        
        if 'Cekilis_Tarihi' in self.df.columns or 'Tarih' in self.df.columns:
            date_col = 'Tarih' if 'Tarih' in self.df.columns else 'Cekilis_Tarihi'
            
            if pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
                self.df['Ay'] = pd.to_datetime(self.df[date_col]).dt.month
                
                logger.info("\nAylar Bazında Toplam Dağılımı:")
                month_sum = self.df.groupby('Ay')[[f'Sayi_{i}' for i in range(1, 7)]].mean().sum(axis=1)
                logger.info(month_sum)

    def calculate_statistics(self):
        """
        Genel istatistikleri hesapla
        """
        logger.info("\n=== GENEL İSTATİSTİKLER ===")
        
        logger.info(f"Toplam Çekilişler: {len(self.df)}")
        
        if 'Cekilis_Tarihi' in self.df.columns:
            try:
                dates = pd.to_datetime(self.df['Cekilis_Tarihi'], errors='coerce')
                logger.info(f"Tarih Aralığı: {dates.min()} - {dates.max()}")
                logger.info(f"Gün Sayısı: {(dates.max() - dates.min()).days}")
            except:
                pass

    def generate_statistical_report(self):
        """
        Tüm analiz raporunu oluştur
        """
        logger.info("\n" + "="*50)
        logger.info("SAYISAL LOTO İSTATİSTİKSEL ANALİZ RAPORU")
        logger.info("="*50)
        
        self.calculate_statistics()
        self.analyze_number_frequency()
        self.analyze_number_distribution()
        self.analyze_sum_distribution()
        self.analyze_correlation()
        self.analyze_patterns()
        self.analyze_temporal_patterns()
        
        logger.info("\n" + "="*50)
        logger.info("RAPOR TAMAMLANDI")
        logger.info("="*50)

    def save_analysis(self, output_path='data/analiz_raporu.txt'):
        """
        Analizi dosyaya kaydet
        """
        try:
            import io
            import sys
            
            # Çıktıyı dosyaya yönlendir
            old_stdout = sys.stdout
            f = open(output_path, 'w', encoding='utf-8')
            sys.stdout = f
            
            self.generate_statistical_report()
            
            sys.stdout = old_stdout
            f.close()
            
            logger.info(f"\nAnaliz raporu {output_path} dosyasına kaydedildi")
        except Exception as e:
            logger.error(f"Rapor kayıt hatası: {e}")


def main():
    # Temizlenen verileri yükle
    df = pd.read_excel('data/sayisal_loto_temizlenmis.xlsx')
    
    # Analizi gerçekleştir
    analyzer = LotteryAnalysis(df)
    analyzer.generate_statistical_report()
    
    # Raporu kaydet
    analyzer.save_analysis()


if __name__ == "__main__":
    main()
