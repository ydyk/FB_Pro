import requests
import moviepy.editor as mp
import os
import re
from bs4 import BeautifulSoup
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
import html

API_KEY = 'ihKVmI9533sGnIIfncdJrtZSeL9zX6xFvU7HKPCElPPHDOdE9I74qPx9'
edited_file_video = None

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

def download_video(video_url, title, duration=5):
    global edited_file_video
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
        edited_file_video = edited_file
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

def create_video_with_image(image_url, video_path, text_video, output_name):
    try:
        output_name = re.sub(r'[^\w\s]', '', output_name).replace(" ", "_")

        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        image_name = f"{output_name}_image.jpg"
        img.save(image_name)

        clip = mp.VideoFileClip(video_path)

        img_clip = mp.ImageClip(image_name).set_duration(clip.duration)
        img_width, img_height = img.size
        padding_top = 80
        padding_left_right = 50
        new_width = clip.w - 2 * padding_left_right
        new_height = int((new_width / img_width) * img_height)

        img_clip = img_clip.resize(newsize=(new_width, new_height))
        img_clip = img_clip.set_position(('center', padding_top)).set_opacity(0.7).fadein(1)

        text_image_path = f"{output_name}_text.png"
        create_combined_text_image(text_video, text_image_path)
        text_clip = mp.ImageClip(text_image_path).set_duration(clip.duration)

        text_clip = text_clip.set_position((
            ('center'),
            padding_top + new_height + 20
        ))

        final_video = mp.CompositeVideoClip([clip, img_clip, text_clip])
        final_video.write_videofile(f"{output_name}_final.mp4", codec='libx264', audio_codec='aac')

        final_video.close()
        clip.close()
        img_clip.close()
        text_clip.close()
        os.remove(image_name)
        os.remove(text_image_path)
    except Exception as e:
        print(f"Error creating video with image: {e}")

def search_video(query, api_key, image_url, title, duration=5):
    url = f'https://api.pexels.com/videos/search?query={query}&per_page=1'
    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['videos']:
            video_url = data['videos'][0]['video_files'][0]['link']
            video_path = download_video(video_url, title, duration)
            if video_path:
                create_video_with_image(image_url, video_path, title, f"{query}_image_{title}")
                try:
                    os.remove(video_path)
                except Exception as e:
                    print(f"Error removing edited video: {e}")
        else:
            print("No videos found for your query.")
    else:
        print(f"Error: {response.status_code}")

def get_gossip_news_from_kapanlagi():
    url = 'https://www.kapanlagi.com/showbiz/'
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

                if image_url:
                    search_video('beach', API_KEY, image_url, title)
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