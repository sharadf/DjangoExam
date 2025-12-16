Для создания Django-проекта используется следующая команда.

1. Убедитесь, что Django установлен
python -m django --version


Если не установлен:
pip install django

2. Создание проекта
django-admin startproject project_name



🛠️ Установка и запуск проекта
1️⃣ Клонирование репозитория
git clone https://github.com/sharadf/DjangoExam
cd exDjango

2️⃣ Создание виртуального окружения
python -m venv venv

Windows:
venv\Scripts\activate

Linux / macOS
source venv/bin/activate

3️⃣ Установка зависимостей
pip install -r requirements.txt

🗄️ Миграции базы данных
Создание миграций
python manage.py makemigrations

Применение миграций
python manage.py migrate


🗄️ Миграции базы данных
Создание миграций:
python manage.py makemigrations

Применение миграций:
python manage.py migrate




👤 Создание пользователей через Django shell
▶️ Запуск shell:
python manage.py shell


👤 Обычный пользователь:
from users.models import User

user = User.objects.create_user(
    username="user1",
    password="password123"
)


🛡️ Администратор:
admin = User.objects.create_user(
    username="admin1",
    password="admin123",
    role="admin"
)

👑 Супер-админ:
superadmin = User.objects.create_superuser(
    username="superadmin",
    password="superadmin123"
)

superadmin.role = "superadmin"
superadmin.save()



🚫 Блокировка пользователя
user.is_active = False
user.save()


▶️ Запуск сервера
python manage.py runserver

