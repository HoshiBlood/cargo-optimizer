# 🚛 CargoOpt — Оптимизатор загрузки грузового транспорта

Веб-приложение для автоматизации расчёта оптимальной 3D-загрузки грузов.

---

## О проекте

**CargoOpt** помогает логистическим компаниям планировать загрузку транспорта с учётом:
- Габаритов грузов
- Весовых ограничений
- Хрупкости и возможности штабелирования
- Максимальной эффективности объёма кузова

### Основные возможности
- ✅ CRUD справочников грузов и транспорта
- ✅ Создание задач на загрузку
- ✅ Расчёт коэффициентов эффективности
- ✅ История всех задач
- ✅ Адаптивный интерфейс

---

## Технологии

- **Backend**: Python + Flask
- **БД**: SQLAlchemy + SQLite
- **Формы**: WTForms + Bootstrap 5
- **Контейнеризация**: Docker + Docker Compose
- **Алгоритм**: Улучшенный heuristic (First-Fit + stability check)

---

## Установка и запуск

### 1. Через Docker (рекомендуется)

```bash
docker-compose up --build
Приложение будет доступно по адресу: http://localhost:5000
2. Локально
Bashcd Учебная практика
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python run.py

Структура проекта
Учебная практика/
├── run.py                 # Главный файл
├── models.py              # Модели БД
├── algorithm.py           # Алгоритм размещения
├── forms.py               # Формы
├── templates/             # HTML-шаблоны
├── static/                # CSS, JS
├── instance/              # База данных
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                   # Настройки (секретный ключ и т.д.)

Как использовать

Добавьте грузы и транспорт в справочники (Можно использовать тестовые данные: Файл seed_data.py заполняет базу данных тестовыми данными (грузы + транспорт) docker-compose exec web python seed_data.py)
Перейдите в "Новая задача"
Выберите транспорт и добавьте грузы 
Нажмите "Создать и рассчитать"
Посмотрите результат в "Задачи"


Docker
Bash# Сборка
docker-compose build

# Запуск
docker-compose up

# Остановка
docker-compose down

Разработка
Создание .env файла:
envSECRET_KEY=your-super-secret-key-here
FLASK_ENV=development
DATABASE_URI=sqlite:///instance/newflask.db
Сброс БД:
Bashrm -rf instance/*.db
docker-compose up --build

Автор: Эвелина Гирфанова
Год: 2026
