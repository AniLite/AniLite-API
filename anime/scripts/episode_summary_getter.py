import requests
from anime.models import Anime


def main(start, end):

    lst_anime = Anime.objects.all()[start: end + 1]
    for anime in lst_anime:
        anime_url = f'https://kitsu.io/api/edge/anime?filter[slug]={anime.slug}'
        res = requests.get(anime_url)
        id = res.json()['data'][0]['id']
        episodes_url = f'https://kitsu.io/api/edge/anime/{id}/episodes?page%5Blimit%5D=20'

        def add_summary(link, data=[]):
            response = requests.get(link)
            for item in response.json()['data']:
                summary = item['attributes'].get('synopsis')
                title = item['attributes'].get('canonicalTitle')
                air_date = item['attributes'].get('airdate')
                try:
                    thumbnail = item['attributes']['thumbnail'].get('original')
                except:
                    thumbnail = ''
                data += [{'Summary': summary, 'Title': title,
                         'Air Date': air_date, 'Thumbnail': thumbnail}]
            if 'next' in response.json()['links'].keys():
                add_summary(response.json()['links']['next'], data)
            else:
                anime.episode_summary = data
                anime.save()
                print(f'> Added all episodes for the anime {anime.name_en}')
        add_summary(episodes_url)
