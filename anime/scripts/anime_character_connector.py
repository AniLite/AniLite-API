import requests
from anime.models import Anime, Character


def main():

    lst_anime = Anime.objects.all()[11: 51]
    for anime in lst_anime:
        anime_url = f'https://kitsu.io/api/edge/anime?filter[slug]={anime.slug}'
        res = requests.get(anime_url)
        id = res.json()['data'][0]['id']
        characters_url = f'https://kitsu.io/api/edge/anime/{id}/characters?page%5Blimit%5D=20'

        def add_characters(link):
            response = requests.get(link)
            for item in response.json()['data']:
                slug_link = f"https://kitsu.io/api/edge/media-characters/{item['id']}/character"
                r = requests.get(slug_link)
                slug = r.json()['data']['attributes']['slug']
                name = r.json()['data']['attributes']['name']
                try:
                    character = Character.objects.get(slug__iexact=slug)
                    anime.characters.add(character)
                    print(
                        f'> Added character: {name} to anime: {anime.name_en}')
                except:
                    print(f'\n!> {name} doesn\'t exist in the database\n')
            if 'next' in response.json()['links'].keys():
                add_characters(response.json()['links']['next'])
            else:
                return 0
        add_characters(characters_url)
        print(
            f'\n  > Added all the available characters for {anime.name_en} successfully!\n')
