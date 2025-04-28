import requests
from bs4 import BeautifulSoup
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import re

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

# Fungsi untuk mengunduh gambar dari URL dan menyimpannya dengan nama file sesuai judul artikel
def download_image(image_url, title):
    try:
        # Mengganti karakter yang tidak bisa digunakan pada nama file
        valid_filename = re.sub(r'[\\/*?:"<>|]', "", title)  # Menghapus karakter tidak valid
        file_name = f"{valid_filename}.jpg"  # Membuat nama file dengan ekstensi .jpg

        response = requests.get(image_url)
        response.raise_for_status()  # Memastikan tidak ada error saat mengunduh
        img = Image.open(BytesIO(response.content))

        # Menyimpan gambar dengan nama yang sesuai judul artikel
        img.save(file_name)
        print(f"Image downloaded and saved as '{file_name}'.")
        return file_name
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

# Fungsi untuk mengedit gambar (misalnya menambahkan teks) dan menyimpannya dengan nama yang sesuai judul artikel
def edit_image(img, text, file_name):
    try:
        # Menambahkan teks ke gambar
        draw = ImageDraw.Draw(img)
        
        # Menggunakan font default (bisa mengganti dengan file font lain jika perlu)
        font = ImageFont.load_default()
        
        # Menambahkan teks ke gambar di posisi tertentu
        draw.text((10, 10), text, font=font, fill="white")
        
        # Menyimpan gambar yang sudah diedit dengan nama yang sesuai judul artikel
        edited_file_name = f"edited_{file_name}"
        img.save(edited_file_name)
        print(f"Image edited and saved as '{edited_file_name}'.")
    except Exception as e:
        print(f"Error editing image: {e}")

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
                
                # Membuat link absolut jika diperlukan
                if not link.startswith("http"):
                    link = "https://www.kapanlagi.com" + link

                # Mengambil gambar dari artikel KapanLagi berdasarkan link artikel
                image_url = fetch_image_from_kapanlagi_article(link)

                if image_url:
                    # Mengunduh gambar dengan nama sesuai judul artikel
                    downloaded_file = download_image(image_url, title)
                    
                    if downloaded_file:
                        # Mengedit gambar dengan menambahkan teks (misalnya, judul artikel)
                        img = Image.open(downloaded_file)
                        edit_image(img, title, downloaded_file)
                else:
                    print(f"No image found for {title}")
                
                # Mencetak hasil
                print(f"Title: {title}")
                print(f"Link: {link}")
                print(f"Image URL: {image_url}\n")
        else:
            print("Tidak ada artikel yang ditemukan.")
    else:
        print(f"Error: {response.status_code}")

# Memanggil fungsi
get_gossip_news_from_kapanlagi()
