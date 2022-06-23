# hw05_final

# yatube
### Описание
Социальная сеть блогеров(Учебный проект). </br>
Веб-сервис в котором реализована возможность вести личный блог, и просматривать записи других участников соцсети, система комментариев и подписок.

### Технологии

Python 3.9
Django 2.2.19
SQLite

### Как запустить проект на своей машине:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:ilinNE/hw05_final.git
```
Перейти в каталог с проектом 
```
cd hw05_final
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции:
```
python3 manage.py migrate
```

Запустить проект:
```
python3 manage.py runserver
```
Открыть в браузере страницу по адресу: http://127.0.0.1:8000/

### Автор

Никита Ильин
