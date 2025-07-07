pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

echo "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if username and email and password:
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(email, username, password)
" | python manage.py shell