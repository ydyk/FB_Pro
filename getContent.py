import requests
import random
import moviepy.editor as mp
import os
import re
from bs4 import BeautifulSoup
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
import html
from gtts import gTTS  # Import gTTS library

API_KEY = 'ihKVmI9533sGnIIfncdJrtZSeL9zX6xFvU7HKPCElPPHDOdE9I74qPx9'

# Daftar kata kunci untuk pencarian video
video_queries = [
    'white sandy beach', 'mountain cliffs', 'cool flowing water', 'beautiful forest', 'sunset over the ocean', 
    'tropical island', 'desert landscape', 'lush green hills', 'rolling meadows', 'rocky shore', 
    'calm lake', 'crystal clear water', 'snowy mountain peaks', 'waterfall in the forest', 'autumn foliage', 
    'hidden cave', 'tropical rainforest', 'volcanic island', 'blue lagoon', 'serene river', 
    'golden beach at dawn', 'desert sunset', 'deep ocean', 'high mountain pass', 'frozen lake',
    'misty morning', 'clear blue sky', 'starry night sky', 'sand dunes', 'rainforest waterfall',
    'rolling fog over hills', 'breathtaking canyon', 'peaceful pond', 'colorful coral reef', 'pristine beach',
    'sunrise over mountains', 'rocky cliffs by the sea', 'majestic glacier', 'lush jungle', 'highland lakes', 
    'desert oasis', 'tropical sunset', 'peaceful countryside', 'deep green valley', 'snow-capped mountains',
    'lush green meadows', 'ocean waves crashing', 'green rice terraces', 'flowing stream in the forest', 
    'sunset over a river', 'icy tundra', 'rolling hills of lavender', 'dense fog in the forest', 'winter wonderland',
    'hidden waterfall', 'blossoming flowers in spring', 'colorful sunset over ocean', 'clear night sky with stars',
    'snowy pine forest', 'beautiful mountain village', 'crystal clear pond', 'endless fields of wheat', 'desert rock formations',
    'misty lake', 'snowstorm in the forest', 'calm coastal cliffs', 'reflective river', 'wildflower fields', 
    'tropical beach with palm trees', 'waterfall with rainbow', 'vibrant sunset sky', 'ancient stone ruins in nature', 
    'forest clearing', 'abandoned island', 'mountain ridge view', 'mystical forest', 'secluded beach',
    'golden sand dunes', 'ocean breeze', 'majestic valley', 'stunning mountain range', 'peaceful riverbank', 
    'moonlit beach', 'remote mountain village', 'calm alpine lake', 'forest glade', 'dramatic cliffside', 
    'beautiful vineyard', 'jungle river', 'rocky desert landscape', 'peaceful meadow with flowers', 'rural countryside',
    'jungle canopy', 'sunset over farmland', 'wildlife in nature', 'mountain lake', 'winding river', 
    'serene woodland', 'colorful autumn leaves', 'desert night sky', 'tropical forest with mist', 'river through the jungle',
    'alpine forest', 'stormy beach', 'windy mountain pass', 'swimming in crystal clear water', 'sunset over sand dunes',
    'quiet rural road', 'rainforest canopy', 'snowy forest path', 'lush tropical forest', 'majestic waterfall',
    'ocean cliffs at sunrise', 'desert horizon at dusk', 'wild horse in the desert', 'iceberg in the ocean',
    'high desert plateau', 'foggy beach morning', 'hidden valley', 'bright starry sky', 'windswept beach',
    'rocky mountain lakes', 'tropical garden', 'serene coastal cliffs', 'sailboat on calm water', 'lush tropical island'
]


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
        else:
            return None
    except Exception as e:
        print(f"Error fetching image from article: {e}")
        return None

def download_video(video_url, title, duration):
    try:
        valid_filename = re.sub(r'[\\/*?:"<>|]', "", title)
        file_name = f"{valid_filename}.mp4"
        video_response = requests.get(video_url)
        video_response.raise_for_status()

        with open(file_name, 'wb') as f:
            f.write(video_response.content)

        clip = mp.VideoFileClip(file_name)
        clip = clip.subclip(0, duration)
        clip = clip.resize(newsize=(720, 1280)).set_fps(30)

        edited_file = f"edited_{file_name}"
        clip.write_videofile(edited_file, codec='libx264', audio_codec='aac', threads=4, preset='ultrafast', bitrate="3000k", audio_bitrate="128k")
        clip.close()
        os.remove(file_name)
        return edited_file
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def create_text_block(text, font, line_spacing=10, highlight_padding=10, radius=10):
    lines = []
    for paragraph in text.split('\n'):
        wrapped = textwrap.wrap(paragraph, width=30)
        lines.extend(wrapped)

    draw_dummy = ImageDraw.Draw(Image.new('RGB', (1000, 100)))
    line_sizes = [draw_dummy.textsize(line, font=font) for line in lines]
    img_width = max(w for w, h in line_sizes) + highlight_padding * 2
    img_height = sum(h for w, h in line_sizes) + (len(lines) - 1) * line_spacing + highlight_padding * 2

    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    y = highlight_padding
    for line, (line_width, line_height) in zip(lines, line_sizes):
        x = (img_width - line_width) // 2
        # Draw rounded highlight background behind text
        draw.rounded_rectangle([x - highlight_padding//2, y - highlight_padding//2, x + line_width + highlight_padding//2, y + line_height + highlight_padding//2], radius=radius, fill=(255,255,255,255))
        draw.text((x, y), line, fill="black", font=font)
        y += line_height + line_spacing

    return img

def create_combined_text_image(text, output_path, font_size=40, spacing_between_blocks=20):
    font_path = "arial.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    text_blocks = text.split('\n\n')
    block_images = [create_text_block(block.strip(), font) for block in text_blocks if block.strip()]

    total_height = sum(img.height for img in block_images) + spacing_between_blocks * (len(block_images) - 1)
    max_width = max(img.width for img in block_images)

    combined_img = Image.new('RGBA', (max_width, total_height), (0, 0, 0, 0))

    y_offset = 0
    for img in block_images:
        combined_img.paste(img, ((max_width - img.width) // 2, y_offset), mask=img)
        y_offset += img.height + spacing_between_blocks

    combined_img.save(output_path)

def create_video_with_image(image_url, video_path, text_video, audio_path, output_name):
    try:
        output_name = re.sub(r'[^\w\s]', '', output_name).replace(" ", "_")

        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        image_name = f"{output_name}_image.jpg"
        img.save(image_name)

        clip = mp.VideoFileClip(video_path)

        img_clip = mp.ImageClip(image_name).set_duration(clip.duration)
        img_width, img_height = img.size
        padding_top = 120
        padding_left_right = 50
        new_width = clip.w - 2 * padding_left_right
        new_height = int((new_width / img_width) * img_height)

        img_clip = img_clip.resize(newsize=(new_width, new_height))
        img_clip = img_clip.set_position(('center', padding_top))

        text_image_path = f"{output_name}_text.png"
        create_combined_text_image(text_video, text_image_path)
        text_clip = mp.ImageClip(text_image_path).set_duration(clip.duration)

        text_clip = text_clip.set_position((
            ('center'),
            padding_top + new_height + 20
        ))
        
        audio_clip = mp.AudioFileClip(audio_path)
        final_video = mp.CompositeVideoClip([clip, img_clip, text_clip])
        final_video = final_video.set_audio(audio_clip)

        final_video.write_videofile(f"{output_name}_final.mp4", codec='libx264', audio_codec='aac')

        final_video.close()
        clip.close()
        img_clip.close()
        text_clip.close()
        os.remove(image_name)
        os.remove(text_image_path)
        os.remove(audio_path)
    except Exception as e:
        print(f"Error creating video with image: {e}")

def search_video(query, api_key, image_url, title):
    url = f'https://api.pexels.com/videos/search?query={query}&per_page=1'
    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['videos']:
            video_url = data['videos'][0]['video_files'][0]['link']
            
            # Generate audio with gTTS
            output_name = title
            output_name = re.sub(r'[^\w\s]', '', output_name).replace(" ", "_")
            audio_path = f"{output_name}_audio.mp3"
            tts = gTTS(title, lang='id')  # 'id' for Bahasa Indonesia
            tts.save(audio_path)
            audio_duration = 5
            # Check if the audio file exists
            if os.path.exists(audio_path):
                print(f"Audio file saved successfully at: {audio_path}")
                audio_clip = mp.AudioFileClip(audio_path)
                audio_duration = audio_clip.duration  # Get duration of the audio
                audio_clip.close()
                print(f"Audio duration: {audio_duration} seconds")
            else:
                print(f"Audio file not found: {audio_path}")
                return
            
            # Download video and adjust the duration based on the audio duration
            video_path = download_video(video_url, title, audio_duration)
            if video_path:
                create_video_with_image(image_url, video_path, title, audio_path, f"{query}_image_{title}")
                try:
                    os.remove(video_path)
                except Exception as e:
                    print(f"Error removing edited video: {e}")
        else:
            print("No videos found for your query.")
    else:
        print(f"Error: {response.status_code}")

def get_gossip_news_from_kapanlagi():
    url = 'https://www.kapanlagi.com/trending/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('li', class_='tagli')

        if articles:
            for article in articles[:5]:
                link = article.find('a')['href'] if article.find('a') else 'No Link'
                title = article.find('img')['alt'] if article.find('img') else 'No Title'
                title = html.unescape(title)

                if not link.startswith("http"):
                    link = "https://www.kapanlagi.com" + link

                image_url = fetch_image_from_kapanlagi_article(link)

                # Choose a random query from the list
                query = random.choice(video_queries)

                if image_url:
                    search_video(query, API_KEY, image_url, title)
                else:
                    print(f"No image found for {title}")

                print(f"Title: {title}")
                print(f"Link: {link}")
                print(f"Image URL: {image_url}\n")
        else:
            print("Tidak ada artikel yang ditemukan.")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    get_gossip_news_from_kapanlagi()
