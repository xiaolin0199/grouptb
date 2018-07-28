install:

Django 1.8, MySQL-python, upyun
根据local_settings.sample.py创建local_settings.py
创建空的数据库
create database grouptb_service default charset utf8mb4;
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata grouptb
python manage.py loaddata operator
python manage.py loaddata upyungrouptb
python manage.py loaddata operatortoupyungrouptb
python manage.py loaddata dailylog
python manage.py loaddata detaillog
python manage.py runserver
