from django.contrib.auth.models import User
import re


def validate_username(username):
    if User.objects.filter(username=username).exists():
        return False
    pattern = r'^[a-zA-Z0-9_]{4,20}$'
    if re.match(pattern, username):
        return True
    else:
        return False
    
def validate_email(email):
    if User.objects.filter(email=email).exists():
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False