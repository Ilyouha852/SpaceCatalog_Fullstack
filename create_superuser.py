#!/usr/bin/env python3
"""
Utility script to create a Django superuser with fixed credentials.
Usage:
    python create_superuser.py

This will create a superuser with username 'ilyouha' and password '123'
if a user with that username does not already exist.
"""
import os
import sys

if __name__ == '__main__':
    # Ensure the project's settings are used
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    try:
        import django
        django.setup()
    except Exception as e:
        print('Failed to setup Django environment:', e)
        sys.exit(1)

    from django.contrib.auth import get_user_model

    User = get_user_model()
    username = 'ilyouha'
    password = '123'
    email = ''

    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists. No action taken.")
        sys.exit(0)

    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created with password '{password}'.")
    except Exception as e:
        print('Failed to create superuser:', e)
        sys.exit(1)
