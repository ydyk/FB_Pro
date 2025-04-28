import requests
import moviepy.editor as mp
import os
import re
from bs4 import BeautifulSoup
import json
from PIL import Image
from io import BytesIO

# Ganti dengan API key Pexels Anda
API_KEY = 'ihKVmI9533sGnIIfncdJrtZSeL9zX6xFvU7HKPCElPPHDOdE9I74qPx9'
edited_file_video = ""

# Fungsi untuk mengambil URL gambar dari JSON di halaman artikel KapanLagi
def fetch_image_from_kapanlagi_article(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            script_tag = soup.find('script', type='application/ld+json')

            if script_tag:
                json_data = json.loads(script_tag.string)
                if isinstance(json_data, dict) and 'image' in json_data:
                    return json_data['image']
                elif isinstance(json_data, list):
                    for item in json_data:
                        if 'image' in item:
                            return item['image']
            return None
    except Exception as e:
        print(f"Error fetching image: {e}")
        return None

# Fungsi untuk mengambil gambar-gambar dari artikel gossip
def get_gossip_images():
    url = 'https://www.kapanlagi.com/showbiz/'
    response = requests.get(url)
    images = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('li', class_='tagli')

        for article in articles[:5]:  # Get top 5 articles
            link = article.find('a')['href'] if article.find('a') else None
            if link and not link.startswith("http"):
                link = "https://www.kapanlagi.com" + link

            image_url = fetch_image_from_kapanlagi_article(link)
            if image_url:
                image_name = re.sub(r'[\\/*?:"<>|]', "", article.find('img')['alt']) + '.jpg'
                images.append((image_url, image_name))
    return images


# Fungsi untuk mengunduh video dari URL dan menyimpannya dengan nama file sesuai judul artikel
def download_video(video_url, title, duration=5):
    global edited_file_video  # Menambahkan global agar bisa mengubah variabel global
    try:
        valid_filename = re.sub(r'[\\/*?:"<>|]', "", title)
        file_name = f"{valid_filename}.mp4"
        video_response = requests.get(video_url)
        video_response.raise_for_status()

        with open(file_name, 'wb') as f:
            f.write(video_response.content)

        clip = mp.VideoFileClip(file_name)
        clip = clip.subclip(0, duration)
        clip = clip.resize(newsize=(720, 1280))
        clip = clip.set_fps(30)

        # Set variabel global edited_file_video dengan nama file video yang sudah diedit
        edited_file = f"edited_{file_name}"
        edited_file_video = edited_file  # Menyimpan path file yang akan dihapus nanti
        clip.write_videofile(edited_file, codec='libx264', audio_codec='aac', threads=4, preset='ultrafast', bitrate="3000k", audio_bitrate="128k")

        clip.close()
        os.remove(file_name)
        return edited_file
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

# Fungsi untuk membuat video terpisah dengan gambar sebagai overlay di atas video
def create_video_with_image(image_url, video_path, output_name):
    try:
        # Mengunduh gambar
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        image_name = f"{output_name}.jpg"
        img.save(image_name)
        
        # Membuka video latar belakang
        clip = mp.VideoFileClip(video_path)
        
        # Menyesuaikan ukuran gambar untuk 1/4 bagian atas
        img_clip = mp.ImageClip(image_name).set_duration(clip.duration)  # Gambar tampil selama durasi video
        img_clip = img_clip.resize(width=clip.w)  # Sesuaikan lebar gambar agar tidak melebihi lebar video
        img_clip = img_clip.set_position(('center', 'top'))  # Tempatkan gambar di bagian atas
        img_clip = img_clip.set_opacity(0.7)  # Menambahkan transparansi sedikit

        # Membuat video akhir dengan overlay gambar
        final_video = mp.CompositeVideoClip([clip, img_clip])  # Gabungkan video dan gambar sebagai overlay
        final_video.write_videofile(f"{output_name}_final.mp4", codec='libx264', audio_codec='aac')
        final_video.close()

        # Hapus gambar setelah selesai
        os.remove(image_name)

    except Exception as e:
        print(f"Error creating video with image: {e}")

# Fungsi untuk mencari video di Pexels dan mengunduhnya
def search_video(query, api_key, duration=5):
    url = f'https://api.pexels.com/videos/search?query={query}&per_page=1'
    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['videos']:
            video_url = data['videos'][0]['video_files'][0]['link']
            print(f"Found video: {video_url}")
            video_path = download_video(video_url, query, duration)
            if video_path:
                images = get_gossip_images()
                for i, (image_url, image_name) in enumerate(images):
                    create_video_with_image(image_url, video_path, f"{query}_image_{i+1}")
        else:
            print("No videos found for your query.")
    else:
        print(f"Error: {response.status_code}")

    # Menghapus video yang telah diunduh setelah digunakan
    if edited_file_video:
        os.remove(edited_file_video)
        print(f"Removed edited video: {edited_file_video}")

# Memanggil fungsi untuk mencari video dan membuat video terpisah dengan gambar
search_video('beach', API_KEY)
