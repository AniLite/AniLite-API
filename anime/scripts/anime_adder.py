import requests
from datetime import datetime
from anime.models import Anime


def add(start, end):
    base_url = 'https://kitsu.io/api/edge/'
    i = start
    for i in range(start, end + 1):
        anime_url = f'anime/{i}'
        response = requests.get(f"{base_url}{anime_url}")
        if response.status_code == 200 and response.json()['data'] != []:

            name_en = str(response.json()['data']
                          ['attributes']['titles'].get('en'))
            name_jp = str(response.json()['data']
                          ['attributes']['titles'].get('en_jp'))
            if name_en == 'None':
                name_en = name_jp

            slug = str(response.json()['data']['attributes'].get('slug'))
            about = str(response.json()['data']['attributes'].get('synopsis'))

            if response.json()['data']['attributes']['status'] == 'finished':
                started = datetime.strptime(
                    response.json()['data']['attributes']['startDate'], '%Y-%m-%d').date()
                ended = datetime.strptime(
                    response.json()['data']['attributes']['endDate'], '%Y-%m-%d').date()
                is_completed = True
                if response.json()['data']['attributes']['subtype'] in ('TV', 'tv'):
                    num_of_eps = response.json(
                    )['data']['attributes']['episodeCount']
                else:
                    num_of_eps = 1
            elif response.json()['data']['attributes']['status'] == 'current':
                started = datetime.strptime(
                    response.json()['data']['attributes']['startDate'], '%Y-%m-%d').date()
                ended = datetime(1111, 11, 11).date()
                is_completed = False
                num_of_eps = 0
            elif response.json()['data']['attributes']['status'] in ('tba', 'upcoming', 'unreleased'):
                started = ended = datetime(1111, 11, 11).date()
                is_completed = False
                num_of_eps = 0

            rating = response.json()['data']['attributes'].get('averageRating')
            type = "{} ({})".format(str(response.json()[
                'data'].get('type')).title(), str(response.json()['data']['attributes'].get('subtype')).upper())
            poster_image = str(response.json(
            )['data']['attributes']['posterImage'].get('original'))

            try:
                cover_image = str(response.json(
                )['data']['attributes']['coverImage'].get('original'))
            except:
                cover_image = ''

            def get_studio():
                link_one = response.json(
                )['data']['relationships']['animeProductions']['links'].get('related')
                res = requests.get(link_one + '?page%5Blimit%5D=20')
                if res.status_code == 200 and res.json()['data'] != []:
                    for item in res.json()['data']:
                        if item['attributes']['role'] == 'studio':
                            link_two = item['relationships']['producer']['links']['related']
                            res_two = requests.get(link_two)
                            if res_two.status_code == 200 and res_two.json()['data'] != []:
                                studio = res_two.json()[
                                    'data']['attributes'].get('name')
                    if 'studio' not in locals():
                        studio = 'Not Available'
                else:
                    studio = 'Not Available'
                return studio

            studio = get_studio()

            Anime.objects.create(
                name_en=name_en, name_jp=name_jp, slug=slug, about=about, started=started, ended=ended, is_completed=is_completed,
                studio=studio, cover_image=cover_image, poster_image=poster_image, type=type, rating=rating, num_of_eps=num_of_eps
            )

            print(f'> {type}: {name_en} ({name_jp}) added successfully!')

        else:
            print('The server responded with a status code of {}'.format(
                response.status_code))
