import os
from dotenv import load_dotenv
import requests
from PIL import Image
import zipfile
import io
import math

load_dotenv()

API_URL = os.getenv('YANDEX_API_URL')  # используем api для скачивания с яндекс диска


def get_direct_link(public_url):
    """Получаем ссылку для скачивания"""
    response = requests.get(API_URL + public_url)
    response.raise_for_status()
    return response.json()['href']


def download_and_extract(url, extract_to):
    """Скачиваем и извлекаем"""
    direct_link = get_direct_link(url)
    response = requests.get(direct_link)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_:
        zip_.extractall(extract_to)


def get_images(directory):
    """Забираем изображения"""
    images = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg')):
                images.append(os.path.join(root, file))
    return images


def create_collage(images, output_file, image_size=(800, 800), margin=100):
    """Создаем коллаж"""
    if not images:
        raise ValueError("No images found.")

    resized_images = [img.resize(image_size) for img in images]

    image_width = max(img.width for img in resized_images)
    image_height = max(img.height for img in resized_images)

    images_per_row = 7  # количество изображений в ряду

    total_width = images_per_row * (image_width + margin) + margin
    image_background = total_width  # размер фонового изображения

    rows = math.ceil(len(resized_images) / images_per_row)
    collage_height = rows * (image_height + margin) + margin

    # фоновое изображение
    collage_image = Image.new('RGB', (image_background, collage_height), (255, 255, 255))
    x_offset, y_offset = margin, margin

    for i, img in enumerate(resized_images):
        row = i // images_per_row  # вычисляем ряд
        col = i % images_per_row  # вычисляем столбец

        offset_x = (image_width - img.width) // 2
        offset_y = (image_height - img.height) // 2

        paste_x = x_offset + col * (image_width + margin) + offset_x
        paste_y = y_offset + row * (image_height + margin) + offset_y

        collage_image.paste(img, (paste_x, paste_y))

    save_kwargs = {"compression": "jpeg"}  # Устанавливаем компрессию изображений
    collage_image.save(output_file, **save_kwargs)  # сохраняем


def run_main():
    url = input("Enter the Yandex.Disk URL: ")

    extract_to = os.getcwd()

    try:
        download_and_extract(url, extract_to)
        image_paths = get_images(extract_to)

        images = [Image.open(img_path) for img_path in image_paths]
        output_file = 'Result.tif'
        create_collage(images, output_file)
        print(f"TIFF file created successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    run_main()
