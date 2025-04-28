import requests
import moviepy.editor as mp
import os
import time
import re
from bs4 import BeautifulSoup
import json

# Ganti dengan API key Pexels Anda
API_KEY = 'ihKVmI9533sGnIIfncdJrtZSeL9zX6xFvU7HKPCElPPHDOdE9I74qPx9'

# Fungsi untuk mengunduh video dari URL dan menyimpannya dengan nama file sesuai judul artikel
def download_video(video_url, title, duration=5):
    try:
        # Mengganti karakter yang tidak bisa digunakan pada nama file
        valid_filename = re.sub(r'[\\/*?:"<>|]', "", title)  # Menghapus karakter tidak valid
        file_name = f"{valid_filename}.mp4"  # Membuat nama file dengan ekstensi .mp4

        video_response = requests.get(video_url)
        video_response.raise_for_status()  # Memastikan tidak ada error saat mengunduh

        with open(file_name, 'wb') as f:
            f.write(video_response.content)

        print(f"Video downloaded as {file_name}")

        # Menggunakan moviepy untuk memotong durasi video menjadi 5 detik dan meresolusi ke 720x1280
        clip = mp.VideoFileClip(file_name)
        clip = clip.subclip(0, duration)  # Memotong video menjadi 5 detik

        # Menyusun ulang video agar rasio aspek menjadi 9:16 (portrait) dengan resolusi 720x1280
        clip = clip.resize(newsize=(720, 1280))  # Menentukan ukuran menjadi 720x1280 (9:16)
        clip = clip.set_fps(30)  # Set frame rate ke 30 FPS
        
        # Menyimpan video yang sudah diedit dengan codec H.264 untuk video dan AAC untuk audio
        edited_file = f"edited_{file_name}"
        clip.write_videofile(
            edited_file, 
            codec='libx264',        # Gunakan codec video libx264
            audio_codec='aac',      # Gunakan codec audio AAC
            threads=4,              # Menggunakan beberapa thread untuk mempercepat pengolahan
            preset='ultrafast',     # Pilih preset 'ultrafast' untuk kompresi yang lebih cepat
            bitrate="3000k",        # Set bitrate video agar sesuai dengan kualitas yang diinginkan (25-60 Mbps)
            audio_bitrate="128k"    # Set audio bitrate ke 128 Kbps
        )

        print(f"Video saved as {edited_file}")

        # Menutup video setelah selesai
        clip.close()

        # Menghapus file asli setelah diproses
        os.remove(file_name)
        print(f"Original video {file_name} has been deleted.")
    except Exception as e:
        print(f"Error downloading video: {e}")

# Fungsi untuk mencari video di Pexels
def search_video(query, api_key, duration=5):
    url = f'https://api.pexels.com/videos/search?query={query}&per_page=1'
    headers = {
        'Authorization': api_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['videos']:
            video_url = data['videos'][0]['video_files'][0]['link']
            print(f"Found video: {video_url}")
            download_video(video_url, query, duration)
        else:
            print("No videos found for your query.")
    else:
        print(f"Error: {response.status_code}")

# Memanggil fungsi untuk mencari video air terjun
search_video('waterfall', API_KEY)
