from django import forms
from game.models import Game, GameScreenshot, GameBuild

class BannerUploadForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['banner']

class ScreenshotUploadForm(forms.ModelForm):
    class Meta:
        model = GameScreenshot
        fields = "__all__"

class BuildUploadForm(forms.ModelForm):
    class Meta:
        model = GameBuild
        fields = "__all__"

