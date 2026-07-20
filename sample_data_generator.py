import pandas as pd
import numpy as np
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_data(num_records=500):
    """
    Örnek Sayısal Loto verileri oluştur
    """
    logger.info(f"Örnek veri oluşturuluyor ({num_records} çekilişi)...")
    
    np.random.seed(42)
    
    # Tarihler oluştur (500 günlük veri)
    dates = pd.date_range(start='2023-01-01', periods=num_records, freq='D')
    
    data = []
    for i, date in enumerate(dates):
        # Gerçekçi sayılar (1-49 arasında)
        sayilar = sorted(np.random.choice(range(1, 50), 6, replace=False))
        
        data.append({
            'Cekilis_No': str(i + 1).zfill(4),
            'Cekilis_Tarihi': date.strftime('%d.%m.%Y'),
            'Sayi_1': sayilar[0],
            'Sayi_2': sayilar[1],
            'Sayi_3': sayilar[2],
            'Sayi_4': sayilar[3],
            'Sayi_5': sayilar[4],
            'Sayi_6': sayilar[5],
            'Toplam': sum(sayilar),
            'Ortalama': sum(sayilar) / 6
        })
    
    df = pd.DataFrame(data)
    
    # Data klasörünü oluştur
    os.makedirs('data', exist_ok=True)
    
    # Excel'e kaydet
    df.to_excel('data/sayisal_loto_verileri.xlsx', index=False)
    logger.info(f"Örnek veriler 'data/sayisal_loto_verileri.xlsx' dosyasına kaydedildi")
    
    # CSV'ye kaydet
    df.to_csv('data/sayisal_loto_verileri.csv', index=False, encoding='utf-8-sig')
    logger.info(f"Örnek veriler 'data/sayisal_loto_verileri.csv' dosyasına kaydedildi")
    
    logger.info(f"\n=== Örnek Veri Özeti ===")
    logger.info(f"Toplam çekilişler: {len(df)}")
    logger.info(f"Tarih aralığı: {df['Cekilis_Tarihi'].iloc[0]} - {df['Cekilis_Tarihi'].iloc[-1]}")
    logger.info(f"\nİlk 5 çekilişi:\n{df.head()}")
    
    return df


if __name__ == "__main__":
    create_sample_data()
