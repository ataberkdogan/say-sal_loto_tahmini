import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import logging
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.data = []
        self.session = self._create_session()

    def _create_session(self):
        """
        Retry mekanizması ile session oluştur
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def scrape_lottery_data_api(self):
        """
        API endpoint'i kullanarak sayısal loto verilerini çek (daha hızlı)
        """
        try:
            logger.info("Sayısal Loto API'den veriler çekiliyor...")
            
            # Millipiyango.com API endpoint
            api_url = "https://www.millipiyangoonline.com/api/cekilis-sonuclari?tip=sayisal-loto&page=1&limit=1000"
            
            response = self.session.get(api_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"API'den {len(data.get('data', []))} çekilişi alındı")
            
            if 'data' in data:
                for item in data['data']:
                    try:
                        sayilar = [
                            item.get('sayi1'),
                            item.get('sayi2'),
                            item.get('sayi3'),
                            item.get('sayi4'),
                            item.get('sayi5'),
                            item.get('sayi6')
                        ]
                        
                        if all(isinstance(s, int) for s in sayilar):
                            self.data.append({
                                'Cekilis_No': item.get('cekilisNo', ''),
                                'Cekilis_Tarihi': item.get('cekilisArihi', item.get('tarih', '')),
                                'Sayi_1': sayilar[0],
                                'Sayi_2': sayilar[1],
                                'Sayi_3': sayilar[2],
                                'Sayi_4': sayilar[3],
                                'Sayi_5': sayilar[4],
                                'Sayi_6': sayilar[5],
                                'Toplam': sum(sayilar),
                                'Ortalama': sum(sayilar) / 6
                            })
                    except Exception as e:
                        logger.debug(f"API item işleme hatası: {e}")
                        continue
            
            return True
        except Exception as e:
            logger.warning(f"API çekme başarısız, HTML scraping'e geçiliyor: {e}")
            return False

    def scrape_lottery_data_html(self):
        """
        HTML scraping ile sayısal loto verilerini çek
        """
        try:
            logger.info("HTML scraping ile Sayısal Loto verileri çekiliyor...")
            
            response = self.session.get(self.base_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Çekiliş sonuçlarını içeren tabloyu bul
            table = soup.find('table', {'class': ['table', 'table-striped', 'result-table']})
            
            if not table:
                logger.warning("Spesifik tablo bulunamadı, tüm tabloları kontrol ediliyor...")
                tables = soup.find_all('table')
                logger.info(f"Toplam {len(tables)} tablo bulundu")
                if tables:
                    table = tables[0]
            
            if not table:
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
                            try:
                                sayilar.append(int(sayi_clean))
                            except ValueError:
                                continue
                    
                    if len(sayilar) == 6 and all(1 <= s <= 49 for s in sayilar):
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
                    
                    if idx % 50 == 0 and idx > 0:
                        logger.info(f"İlerleme: {idx} satır işlendi")
                
                except Exception as e:
                    logger.debug(f"Satır işleme hatası: {e}")
                    continue
            
            logger.info(f"Toplam {len(self.data)} çekilişi başarıyla çekildi")
            return len(self.data) > 0
        
        except requests.exceptions.Timeout:
            logger.error("Timeout hatası: İnternet bağlantısı çok yavaş. Lütfen sonra tekrar deneyin.")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Bağlantı hatası: {e}")
            return False
        except Exception as e:
            logger.error(f"Scraping hatası: {e}")
            return False

    def scrape_with_fallback(self):
        """
        Fallback stratejisi: API başarısız olursa HTML'yi dene
        """
        if not self.scrape_lottery_data_api():
            self.data = []  # API başarısız olursa, yeniden başla
            return self.scrape_lottery_data_html()
        return True

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
            
            # Tarih formatını düzenle (eğer yapılmadıysa)
            try:
                df['Cekilis_Tarihi'] = pd.to_datetime(df['Cekilis_Tarihi'], format='%d.%m.%Y', errors='coerce')
            except:
                pass
            
            df = df.sort_values('Cekilis_No', ascending=False).reset_index(drop=True)
            
            df.to_excel(filename, index=False, engine='openpyxl')
            logger.info(f"Veriler başarıyla {filename} dosyasına kaydedildi ({len(df)} satır)")
            return True
        
        except Exception as e:
            logger.error(f"Excel kayıt hatası: {e}")
            return False

    def save_to_csv(self, filename='data/sayisal_loto_verileri.csv'):
        """
        Çekilen verileri CSV dosyasına kaydet
        """
        try:
            if not self.data:
                logger.error("Kaydedilecek veri yok!")
                return False
            
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            df = pd.DataFrame(self.data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"Veriler başarıyla {filename} dosyasına kaydedildi")
            return True
        
        except Exception as e:
            logger.error(f"CSV kayıt hatası: {e}")
            return False

    def get_data(self):
        """
        Çekilen verileri DataFrame olarak döndür
        """
        return pd.DataFrame(self.data)


def main():
    scraper = LottoScraper()
    
    # Verileri çek (API veya HTML fallback)
    logger.info("=== Sayısal Loto Veri Çekme Başlıyor ===")
    if scraper.scrape_with_fallback():
        # Excel'e kaydet
        scraper.save_to_excel('data/sayisal_loto_verileri.xlsx')
        # CSV'ye de kaydet
        scraper.save_to_csv('data/sayisal_loto_verileri.csv')
        
        # İstatistikleri göster
        df = scraper.get_data()
        logger.info(f"\n=== Veri Özeti ===")
        logger.info(f"\n{df.head(10)}")
        logger.info(f"\nToplam satır: {len(df)}")
        if len(df) > 0:
            try:
                logger.info(f"Tarih aralığı: {df['Cekilis_Tarihi'].min()} - {df['Cekilis_Tarihi'].max()}")
            except:
                pass
    else:
        logger.error("Veri çekme başarısız oldu!")
        logger.info("Lütfen internet bağlantınızı kontrol edin ve bir süre sonra tekrar deneyin.")


if __name__ == "__main__":
    main()
