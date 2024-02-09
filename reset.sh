# delete database
rm -f "db.sqlite3"

# make migrations and run them
python manage.py makemigrations
python manage.py migrate

# create superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@abc.com', '1234')" | python manage.py shell