import requests
import time
from datetime import datetime
from anime.models import Anime, Character, Genre


def add(start, end):

    base_url = 'https://kitsu.io/api/edge/'
    i = start
    for i in range(start, end + 1):

        anime_url = f'anime/{i}'

        response = requests.get(f"{base_url}{anime_url}")

        # skipping the anime if it doesn't exist in the database (response.json()['data'] = []) or status code is not 200 (OK)
        if response.status_code == 200 and response.json()['data'] != []:

            # getting the English and Japanese names, and setting them to be the same in case there is no Japanese name provided, i.e. they're same
            name_en = str(response.json()['data']
                          ['attributes']['titles'].get('en'))
            name_jp = str(response.json()['data']
                          ['attributes']['titles'].get('en_jp'))
            if name_en == 'None':
                name_en = name_jp

            print(f'   >>> Working on the anime {name_en}')

            # getting slug and description without any checks as these are present for all anime
            slug = str(response.json()['data']['attributes'].get('slug'))
            about = str(response.json()['data']['attributes'].get('synopsis'))

            # checking if the anime is finished, then and only then fetching the date it ended
            if response.json()['data']['attributes']['status'] == 'finished':
                started = datetime.strptime(
                    response.json()['data']['attributes']['startDate'], '%Y-%m-%d').date()
                ended = datetime.strptime(
                    response.json()['data']['attributes']['endDate'], '%Y-%m-%d').date()
                is_completed = True

                # if it's a series, then and only then fetching the number of episodes, otherwise setting equal to one for movies and OVAs/ONAs
                if response.json()['data']['attributes']['subtype'] in ('TV', 'tv'):
                    num_of_eps = response.json(
                    )['data']['attributes']['episodeCount']
                else:
                    num_of_eps = 1
            # not trying to get the finishing date in case it's ongoing, but because the database accepts only a date object, assigning 11-11-1111
            elif response.json()['data']['attributes']['status'] == 'current':
                started = datetime.strptime(
                    response.json()['data']['attributes']['startDate'], '%Y-%m-%d').date()
                ended = datetime(1111, 11, 11).date()
                is_completed = False
                num_of_eps = 0

            # if the anime hasn't even started airing yet, then setting 11-11-1111 for both start and end dates
            elif response.json()['data']['attributes']['status'] in ('tba', 'upcoming', 'unreleased'):
                started = ended = datetime(1111, 11, 11).date()
                is_completed = False
                num_of_eps = 0

            # getting the rating and type as these are always there
            rating = response.json()['data']['attributes'].get('averageRating')
            type = "{} ({})".format(str(response.json()[
                'data'].get('type')).title(), str(response.json()['data']['attributes'].get('subtype')).upper())

            # trying to get the poster and cover image, setting to empty string if not available
            try:
                poster_image = str(response.json(
                )['data']['attributes']['posterImage'].get('original'))
            except:
                poster_image = ''
            try:
                cover_image = str(response.json(
                )['data']['attributes']['coverImage'].get('original'))
            except:
                cover_image = ''

            # fetching the name of the studio, setting to 'Not Available' if that's the case
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

            # creating the object using the object manager Django provides on every model
            anime = Anime.objects.create(
                name_en=name_en, name_jp=name_jp, slug=slug, about=about, started=started, ended=ended, is_completed=is_completed,
                studio=studio, cover_image=cover_image, poster_image=poster_image, type=type, rating=rating, num_of_eps=num_of_eps
            )
            anime.save()

            # printing a little confirmation message if everything goes fine
            print(
                f'\n    >> {type}: {name_en} ({name_jp}) added to the database successfully ^w^\n')

            # function to first make a list of all the genres of the anime, and then fetch these Genre objects from the database and bind them to the Anime object under consideration
            def genre_adder(anime, response):
                link_to_genres = response.json(
                )['data']['relationships']['genres']['links']['related']
                res = requests.get(link_to_genres)
                slugs = [item['attributes']['slug']
                         for item in res.json()['data']]
                genres = [Genre.objects.get(slug__iexact=slug)
                          for slug in slugs]
                for genre in genres:
                    anime.genres.add(genre)
                    print(
                        f'> {genre} added to the list of genres for the anime: {anime.name_en}')
                print(
                    f'\n    >> Added all genres for the anime {anime.name_en} ^_^\n')

            # adding the genres using the function defined above
            genre_adder(anime, response)

            def create_character(slug):
                link = f'https://kitsu.io/api/edge/characters?filter[slug]={slug}'
                response = requests.get(link)
                if response.status_code == 200 and response.json()['data'] != []:
                    name = response.json()['data'][0]['attributes']['name']
                    try:
                        about = response.json()['data'][0]['attributes'].get(
                            'description')
                    except:
                        about = 'Not Available'

                    def get_other_names():
                        lst_names = response.json(
                        )['data'][0]['attributes']['otherNames']
                        names = ''
                        if lst_names != []:
                            for count, name in enumerate(lst_names):
                                if count == 0:
                                    names += f'{name}'
                                else:
                                    names += f', {name}'
                        else:
                            names = ''
                        return names

                    other_names = get_other_names()

                    try:
                        image = response.json()[
                            'data'][0]['attributes']['image']['original']
                    except:
                        image = ''

                    character = Character.objects.create(
                        name=name, about=about, slug=slug, other_names=other_names, image=image)

                    return character

                else:

                    return None

            def character_adder(anime, response):
                id = response.json()['data']['id']

                characters_url = f'https://kitsu.io/api/edge/anime/{id}/characters?page%5Blimit%5D=20'

                def add_characters(link):
                    response = requests.get(link)
                    for item in response.json()['data']:
                        slug_link = f"https://kitsu.io/api/edge/media-characters/{item['id']}/character"
                        r = requests.get(slug_link)
                        slug = r.json()['data']['attributes']['slug']
                        name = r.json()['data']['attributes']['name']
                        try:
                            character = Character.objects.get(
                                slug__iexact=slug)
                            anime.characters.add(character)
                            print(
                                f'> Connected character: {name} to anime: {anime.name_en}')
                        except:
                            char = create_character(slug)
                            if char == None:
                                print(
                                    f'\n    > Uh oh, something went wrong while fetching the information for character {name} :/ \n')
                            else:
                                anime.characters.add(char)
                                print(
                                    f'> Character: {name} added to the database and connected to {anime.name_en} successfully!')

                    if 'next' in response.json()['links'].keys():
                        add_characters(response.json()['links']['next'])
                    else:
                        return 0

                add_characters(characters_url)

            character_adder(anime, response)
            print(
                f'\n    >> Added all characters to the anime: {anime.name_en} ＾▽＾')

            print(
                f'\n    >>> Added the anime {anime.name_en} and it\'s related genres and characters successfully! ＼(~o~)／ \n')

            print('\n-----------------------------------------------------------------------------------------------------\n')
            time.sleep(3)

        # in case the details of the anime could not be fetched
        else:
            print(' >> The server responded with a status code of {}\n'.format(
                response.status_code))
            print('\n-----------------------------------------------------------------------------------------------------\n')
            time.sleep(3)
