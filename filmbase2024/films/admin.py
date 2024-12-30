from django.contrib import admin
from .models import Country, Film, Person, Genre

admin.site.register(Film)
admin.site.register(Person)
admin.site.register(Country)
admin.site.register(Genre)
