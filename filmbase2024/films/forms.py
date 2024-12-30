from django import forms
from dal import autocomplete
from .models import Country, Genre, Film, Person, FilmCrew


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name']


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']


class FilmForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ['name', 'origin_name', 'slogan', 'length', 'year',
                  'trailer_url', 'cover', 'description', 'country', 'genres']
        widgets = {
            'genres': autocomplete.ModelSelect2Multiple(
                url='films:genres_autocomplete'),
            'country': autocomplete.ModelSelect2Multiple(
                url='films:country_autocomplete'),
        }
        
class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name', 'origin_name', 'birthday', 'photo']
        widgets = {
            "birthday": forms.DateInput(attrs={'type': 'date'},
                                        format="%Y-%m-%d")
        }

class CrewForm(forms.ModelForm):
    class Meta:
        model = FilmCrew
        fields = ['film', 'name', 'people']
        widgets = {
            'people': autocomplete.ModelSelect2Multiple(
                url='films:people_autocomplete'),
            'film' : forms.HiddenInput(),
        }