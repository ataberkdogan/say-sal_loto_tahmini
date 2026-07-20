import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import logging
import os

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LottoScraper:
    def __init__(self):
        self.base_url = "https://www.millipiyangoonline.com/sayisal-loto/cekilis-sonuclari"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.data = []

    def scrape_lottery_data(self, max_pages=None):
        """
        İnternet sitesinden sayısal loto verilerini çekme
        """
        try:
            logger.info("Sayısal Loto verileri çekiliyor...")
            
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Çekiliş sonuçlarını içeren tabloyu bul
            table = soup.find('table', {'class': 'table'})
            
            if not table:
                logger.warning("Ana tablo bulunamadı, alternatif yöntem deneniyor...")
                tables = soup.find_all('table')
                if tables:
                    table = tables[0]
                else:
                    logger.error("Hiç tablo bulunamadı!")
                    return False
            
            rows = table.find_all('tr')[1:]  # Header'ı atla
            
            logger.info(f"Toplam {len(rows)} çekilişi işleniyor...")
            
            for idx, row in enumerate(rows):
                try:
                    cols = row.find_all('td')
                    
                    if len(cols) < 8:
                        continue
                    
                    # Verileri çıkar
                    cekilis_no = cols[0].text.strip()
                    cekilis_tarihi = cols[1].text.strip()
                    
                    # Çekilen sayıları al
                    sayilar = []
                    for i in range(2, 8):
                        sayi = cols[i].text.strip()
                        # Sadece sayıları al
                        sayi_clean = ''.join(filter(str.isdigit, sayi))
                        if sayi_clean:
                            sayilar.append(int(sayi_clean))
                    
                    if len(sayilar) == 6:
                        self.data.append({
                            'Cekilis_No': cekilis_no,
                            'Cekilis_Tarihi': cekilis_tarihi,
                            'Sayi_1': sayilar[0],
                            'Sayi_2': sayilar[1],
                            'Sayi_3': sayilar[2],
                            'Sayi_4': sayilar[3],
                            'Sayi_5': sayilar[4],
                            'Sayi_6': sayilar[5],
                            'Toplam': sum(sayilar),
                            'Ortalama': sum(sayilar) / 6
                        })
                    
                    if idx % 100 == 0:
                        logger.info(f"İlerleme: {idx} çekilişi işlendi")
                
                except Exception as e:
                    logger.debug(f"Satır işleme hatası: {e}")
                    continue
            
            logger.info(f"Toplam {len(self.data)} çekilişi başarıyla çekildi")
            return True
        
        except requests.exceptions.RequestException as e:
            logger.error(f"İnternet bağlantı hatası: {e}")
            return False
        except Exception as e:
            logger.error(f"Scraping hatası: {e}")
            return False

    def save_to_excel(self, filename='data/sayisal_loto_verileri.xlsx'):
        """
        Çekilen verileri Excel dosyasına kaydet
        """
        try:
            if not self.data:
                logger.error("Kaydedilecek veri yok!")
                return False
            
            # Data klasörünü oluştur
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            df = pd.DataFrame(self.data)
            df = df.sort_values('Cekilis_No', ascending=False).reset_index(drop=True)
            
            df.to_excel(filename, index=False, engine='openpyxl')
            logger.info(f"Veriler başarıyla {filename} dosyasına kaydedildi")
            return True
        
        except Exception as e:
            logger.error(f"Excel kayıt hatası: {e}")
            return False

    def get_data(self):
        """
        Çekilen verileri DataFrame olarak döndür
        """
        return pd.DataFrame(self.data)


def main():
    scraper = LottoScraper()
    
    # Verileri çek
    if scraper.scrape_lottery_data():
        # Excel'e kaydet
        scraper.save_to_excel('data/sayisal_loto_verileri.xlsx')
        
        # İstatistikleri göster
        df = scraper.get_data()
        logger.info(f"\n=== Veri Özeti ===")
        logger.info(f"\n{df.head(10)}")
        logger.info(f"\nToplam satır: {len(df)}")
        logger.info(f"Tarih aralığı: {df['Cekilis_Tarihi'].iloc[-1]} - {df['Cekilis_Tarihi'].iloc[0]}")
    else:
        logger.error("Veri çekme başarısız oldu!")


if __name__ == "__main__":
    main()
