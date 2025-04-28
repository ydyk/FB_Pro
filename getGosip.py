import requests
from bs4 import BeautifulSoup
import json

# Fungsi untuk mengambil URL gambar dari JSON di halaman artikel KapanLagi
def fetch_image_from_kapanlagi_article(link):
    try:
        # Mendapatkan halaman artikel dari KapanLagi
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Cari tag <script> yang berisi data JSON
            script_tag = soup.find('script', type='application/ld+json')
            
            if script_tag:
                # Parse JSON dari tag <script>
                json_data = json.loads(script_tag.string)
                
                # Mengambil URL gambar dari 'image' atau 'thumbnailUrl'
                if isinstance(json_data, dict) and 'image' in json_data:
                    image_url = json_data['image']
                    print(f"Image URL found: {image_url}")
                    return image_url
                elif isinstance(json_data, list):
                    for item in json_data:
                        if 'image' in item:
                            image_url = item['image']
                            print(f"Image URL found: {image_url}")
                            return image_url
            print(f"No image found in article: {link}")
            return None
        else:
            print(f"Failed to fetch article: {link}")
            return None
    except Exception as e:
        print(f"Error fetching image from article: {e}")
        return None

def get_gossip_news_from_kapanlagi():
    url = 'https://www.kapanlagi.com/showbiz/'

    # Mendapatkan halaman HTML dari URL
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")  # Memeriksa status kode HTTP

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Menemukan semua elemen <li> dengan class "tagli" yang berisi artikel
        articles = soup.find_all('li', class_='tagli')

        if articles:
            for article in articles[:5]:  # Menampilkan 5 berita teratas
                # Mengambil informasi URL dan judul
                link = article.find('a')['href'] if article.find('a') else 'No Link'
                title = article.find('img')['alt'] if article.find('img') else 'No Title'  # Mengambil title dari atribut alt
                
                # Mengambil gambar dari artikel KapanLagi berdasarkan link artikel
                image_url = fetch_image_from_kapanlagi_article(link)

                # Mencetak hasil
                print(f"Title: {title}")
                print(f"Link: {link}")
                print(f"Image: {image_url}\n")
        else:
            print("Tidak ada artikel yang ditemukan.")
    else:
        print(f"Error: {response.status_code}")

# Memanggil fungsi
get_gossip_news_from_kapanlagi()
