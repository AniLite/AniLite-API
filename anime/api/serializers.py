from rest_framework import serializers
from anime.models import Anime, Genre, Character


class AnimeListSerializer(serializers.ModelSerializer):

    genres = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Anime
        fields = ['id', 'type', 'name_en', 'name_jp', 'slug',
                  'about', 'started', 'is_completed', 'ended', 'rating', 'num_of_eps', 'poster_image', 'cover_image', 'studio', 'genres']

    def get_genres(self, obj):
        data = []
        for genre in obj.genres.all():
            # data.insert(0, genre.name)
            data += [{'id': genre.id, 'name': genre.name}]
        return data


class AnimeDetailSerializer(serializers.ModelSerializer):

    genres = serializers.SerializerMethodField(read_only=True)
    characters = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Anime
        fields = ['id', 'type', 'name_en', 'name_jp', 'slug',
                  'about', 'started', 'is_completed', 'ended', 'rating', 'num_of_eps', 'poster_image', 'cover_image', 'studio', 'genres', 'characters', 'episode_summary']

    def get_genres(self, obj):
        data = []
        for genre in obj.genres.all():
            # data.insert(0, genre.name)
            data += [{'id': genre.id, 'name': genre.name}]
        return data

    def get_characters(self, obj):
        data = []
        for character in obj.characters.all():
            data += [{'id': character.id,
                      'name': character.name, 'slug': character.slug, 'image': character.image}]
        return data


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug']


# class CharacterListSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Character
#         fields = ['id', 'name', 'slug']


class CharacterDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Character
        fields = ['id', 'name', 'slug', 'about', 'other_names', 'image']
