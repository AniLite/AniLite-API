import requests
from anime.models import Anime, Genre


def main(start, end):
    all = Anime.objects.all()
    query = all[start: end + 1]
    for anime in query:
        try:
            response = requests.get(
                f'https://kitsu.io/api/edge/anime?filter[slug]={anime.slug}')
            link_to_genres = response.json(
            )['data'][0]['relationships']['genres']['links']['related']
            res = requests.get(link_to_genres)
            slugs = [item['attributes']['slug'] for item in res.json()['data']]
            genres = [Genre.objects.get(slug__iexact=slug) for slug in slugs]
            for genre in genres:
                anime.genres.add(genre)
                print(
                    f'> {genre} added to the list of genres for the anime: {anime.name_en}')
            print(f'\n >> Added all genres for the anime {anime.name_en}!\n')
        except:
            print(
                f'\n> Something went wrong while adding the genres for the anime {anime.name_en} :/\n')
