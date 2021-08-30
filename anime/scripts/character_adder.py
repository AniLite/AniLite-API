import requests
from anime.models import Character


def add(start, end):
    for i in range(start, end + 1):
        link = f'https://kitsu.io/api/edge/characters/{i}'
        response = requests.get(link)
        if response.status_code == 200 and response.json()['data'] != []:
            try:
                name = response.json()['data']['attributes']['name']
                slug = response.json()['data']['attributes']['slug']
                about = response.json()['data']['attributes']['description']

                def get_other_names():
                    lst_names = response.json(
                    )['data']['attributes']['otherNames']
                    names = ''
                    if lst_names != []:
                        for count, name in enumerate(lst_names):
                            if count == 0:
                                names += f'{name}'
                            else:
                                names += f', {name}'
                    return names

                other_names = get_other_names()
                image = response.json()[
                    'data']['attributes']['image']['original']

                Character.objects.create(
                    name=name, about=about, slug=slug, other_names=other_names, image=image)
                print(f'> Character: {name} added successfully!')
            except:
                print(
                    '\n The resource exists but couldn\'t fetch the specified attributes :/ \n')
        else:
            print(
                f'\n > Uh oh, something went wrong while fetching the information for character #{i} :/ \n')
