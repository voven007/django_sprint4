## Описание

Проект блога, в котором пользовали могут создавать текстово-графические публикации и комментировать их. 

Проект реализован на фреймворке Django с использованием шаблонов.

## Установка

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/voven007/django_sprint4
```

```
cd django_sprint4
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
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

## Основные технические требования

Python==3.9 
