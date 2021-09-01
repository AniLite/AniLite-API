import requests
from anime.models import Character


def add(slug):
    link = f'https://kitsu.io/api/edge/characters?filter[slug]={slug}'
    response = requests.get(link)
    if response.status_code == 200 and response.json()['data'] != []:
        name = response.json()['data'][0]['attributes']['name']
        try:
            about = response.json()['data'][0]['attributes'].get('description')
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
