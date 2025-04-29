import requests
import json

# API Key Gemini
api_key = "AIzaSyDOltdythGzcfMH4cqKPsJEz7813keq5nw"

# Judul Berita yang akan digunakan (ganti sesuai dengan berita yang ingin Anda buat teksnya)
judul_berita = "Teknologi AI Membantu Pengembangan Industri Kreatif"

# URL endpoint untuk model Gemini
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent?key={api_key}"

# Data yang akan dikirim dalam permintaan POST, dengan prompt yang lebih lengkap
payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": f"Tuliskan teks singkat dan menarik untuk video Reel berdasarkan judul berita berikut:\n\n{judul_berita}\n\nTeks harus mencakup:\n1. Ringkasan singkat tentang inti berita.\n2. Poin penting yang menjelaskan cerita lebih lanjut.\n3. Elemen yang membangkitkan rasa penasaran audiens.\n4. Gunakan gaya bahasa yang menarik dan cocok untuk platform sosial media seperti Facebook, Instagram, atau Twitter.\n5. Batasi teks agar tetap singkat dan padat (maksimal 120 karakter).\n6. Sertakan ajakan untuk berinteraksi atau membagikan konten, seperti 'Ceritakan pendapatmu di komentar!' atau 'Jangan lupa bagikan!'.\n7. Jangan sertakan hashtag.\n8. Jangan mengandung kata-kata yang dilarang di facebook."
                }
            ]
        }
    ]
}

# Header yang diperlukan
headers = {
    "Content-Type": "application/json"
}

# Mengirim permintaan POST
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Mengecek status dan mencetak respons
if response.status_code == 200:
    # Mengambil hanya teks dari respons
    generated_text = response.json()['candidates'][0]['content']['parts'][0]['text']
    print("Generated text:", generated_text)
else:
    print(f"Error: {response.status_code}, {response.text}")
