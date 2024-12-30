from django.core.management.base import BaseCommand
import os
import requests
import json


class Command(BaseCommand):
    help = 'Download json via https://api.kinopoisk.dev'

    def handle(self, *args, **options):
        movies = self.get_movies()
        with open(self.filename(), "w", encoding="utf-8") as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)
        print(self.filename())

    @staticmethod
    def filename():
        return "films/data/films.json"

    @staticmethod
    def headers():
        return {"X-API-KEY": os.environ.get("KINOPOISK_DEV_TOKEN")}

    def get_birthdays(self, movie_ids):
        res = {}
        params = {
            "selectFields": ["id", "birthday"],
            "notNullFields": ["birthday"],
            "limit": 250,
            "movies.id": movie_ids,
            "page": 1
        }
        while True:
            print(params["page"])
            resp = requests.get(
                "https://api.kinopoisk.dev/v1.4/person",
                headers=self.headers(), params=params)
            json = resp.json()
            for data in json['docs']:
                res[data['id']] = data['birthday']
            params["page"] += 1
            if params["page"] > json['pages']:
                break
        return res

    def get_movies(self):
        params = {
            "selectFields": ["id", "name", "enName", "year", "description",
                             "movieLength", "countries",  "genres", "persons",
                             "poster", "slogan", "videos"],
            "type": "movie",
            "lists": "top250",
            "limit": 250

        }
        resp = requests.get(
            "https://api.kinopoisk.dev/v1.4/movie",
            headers=self.headers(), params=params)
        json = resp.json()
        movie_ids = set()
        for film_data in json['docs']:
            movie_ids.add(film_data["id"])
        birthdays = self.get_birthdays(movie_ids)
        for film_data in json['docs']:
            for person_data in film_data['persons']:
                if person_data['id'] in birthdays:
                    person_data['birthday'] = birthdays[person_data['id']]
        return json
