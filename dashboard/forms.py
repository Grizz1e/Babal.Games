from django import forms
from game.models import Game, GameScreenshot, GameGenre

class BannerUploadForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['banner']

class ScreenshotUploadForm(forms.ModelForm):
    class Meta:
        model = GameScreenshot
        fields = "__all__"

class GenreForm(forms.ModelForm):
    class Meta:
        model = GameGenre
        fields = "__all__"