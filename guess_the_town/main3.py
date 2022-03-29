import os
import sys
import pygame
import requests
import pprint
from functions import find_spn
from random import shuffle

cities = ['Нью-йорк', 'Санкт-Петербург', 'Арзамас', 'Вена', 'Стамбул', 'Киев']
list1 = []
for toponym_to_find in cities:
    # python search.py Москва, ул. Ак. Королева, 12
    # Тогда запрос к геокодеру формируется следующим образом:
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    a, b = find_spn(json_response)

    map_params = {
        'spn': f"{a},{b}",
        # "l": "sat,trf,skl", с ответами
        "l": "sat,trf",
        "ll": toponym['Point']['pos'].replace(' ', ',')
    }
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_api_server)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = f"map{len(list1) + 1}.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    a = pygame.image.load(map_file)
    list1.append(a)
shuffle(list1)
image = list1[0]
number = 1
time_to_switch = 0
# Инициализируем pygame
FPS = 60
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((600, 450))

font = pygame.font.Font(None, 20)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    Mouse_x, Mouse_y = pygame.mouse.get_pos()
    text = font.render(f'x={Mouse_x}, y={Mouse_y}', True, (0, 0, 0))
    if time_to_switch == FPS * 4:
        time_to_switch = -1
        number += 1
        if number > len(list1):
            number = 1
        image = list1[number - 1]
    screen.blit(image, (0, 0))
    screen.blit(text, (0, 0))
    pygame.display.flip()
    time_to_switch += 1
    clock.tick(FPS)
pygame.quit()

# Удаляем за собой файл с изображением.
for i in range(len(list1)):
    os.remove(f"map{i + 1}.png")