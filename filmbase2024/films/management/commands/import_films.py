from django.core.management.base import BaseCommand
import json
import os
from urllib.request import urlopen
from urllib.error import HTTPError
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from films.models import Country, FilmCrew, Genre, Person, Film
from .get_films import Command as GetCommand


class Command(BaseCommand):
    help = 'Import films from json file'

    def handle(self, *args, **options):
        self.create_films()

    @staticmethod
    def get_image_by_url(url):
        img_tmp = NamedTemporaryFile()
        try:
            with urlopen(url) as uo:
                assert uo.status == 200
                img_tmp.write(uo.read())
                img_tmp.flush()
        except HTTPError:
            return None
        return File(img_tmp)

    def create_person(self, data):
        print(f"Processing PERSON «{data['name']}»")
        attrs = {"name": data['name'], "origin_name": data['enName']}
        try:
            if not data['birthday'].startswith("0000-"):
                attrs['birthday'] = data['birthday'][:10]
        except KeyError:
            pass
        try:
            photo_url = data['photo']
        except KeyError:
            photo_url = None
        person = Person.objects.update_or_create(kinopoisk_id=data['id'],
                                                 defaults=attrs)[0]
        if photo_url:
            image_file = self.get_image_by_url(photo_url)
            if image_file:
                person.photo.save(os.path.basename(photo_url), image_file)
        return person

    def create_film(self, data):
        print(f"Processing FILM «{data['name']}»")
        countries = []
        for country_data in data['countries']:
            country_name = country_data['name']
            country = Country.objects.update_or_create(name=country_name)[0]
            countries.append(country)
        genres = []
        for genre_data in data['genres']:
            genre_name = genre_data['name']
            genre = Genre.objects.update_or_create(name=genre_name)[0]
            genres.append(genre)
        people = {}
        for person_data in data['persons']:
            if not person_data['name']:
                continue
            elif not person_data['profession'] in people.keys():
                people[person_data['profession']] = [self.create_person(person_data)]
            else:
                people[person_data['profession']].append(self.create_person(person_data))
        try:
            cover_url = data['poster']['url']
        except KeyError:
            cover_url = None
        attrs = {"name": data["name"], "origin_name": data["enName"],
                 "slogan": data["slogan"], "length": data["movieLength"],
                 "description": data["description"], "year": data["year"]}
        try:
            attrs["trailer_url"] = data['videos']['trailers'][0]['url']
        except (KeyError, IndexError):
            pass

        film = Film.objects.update_or_create(kinopoisk_id=data['id'],
                                             defaults=attrs)[0]
        film.genres.set(genres)
        film.country.set(countries)
        for crew in people.keys():
            tmp = FilmCrew.objects.update_or_create(name=crew, film=film)[0]
            tmp.people.set(people[crew])

        if cover_url:
            image_file = self.get_image_by_url(cover_url)
            if image_file:
                film.cover.save(os.path.basename(cover_url), image_file)

        return film

    def create_films(self):
        with open(GetCommand.filename(), mode = 'r', encoding = "utf-8") as f:
            films_data = json.load(f)
            for film_data in films_data['docs']:
                self.create_film(film_data)
