# Разработка

Запуск OLcWave локально, структура проекта и правила для внесения изменений.

## Backend

Python 3.13, FastAPI, SQLAlchemy (async), управление через [uv](https://docs.astral.sh/uv/).

Вам нужен Postgres для работы. Самый простой способ - запустить только базу данных через dev compose-файл, а API запустить на своем хосте:

```bash
# запуск только Postgres (и опционально API) из dev compose
docker compose -f docker-compose-dev.yaml up -d postgres
```

Затем запустите backend:

```bash
cd backend
uv sync                      # установить зависимости из uv.lock
# убедитесь, что backend/.env содержит DB_HOST=localhost для запуска на хосте
uv run src/main.py           # запускает uvicorn на 0.0.0.0:8000
```

`uv run src/main.py` запускает приложение, определенное в `src/main.py` (uvicorn на порту 8000).

Таблицы создаются при запуске.

Миграций пока нет - схема создается напрямую из моделей.

Если вы предпочитаете uvicorn с перезагрузкой:

```bash
cd backend
uv run uvicorn --app-dir src main:app --reload --host 0.0.0.0 --port 8000
```

> `backend/.env` использует `DB_HOST=postgres` для Compose. Для запуска на хосте с локальным Postgres установите `DB_HOST=localhost`.

---

## Frontend

React 19 + Vite + TypeScript + Tailwind.

```bash
cd frontend
npm install
npm run dev        # Vite dev server на http://localhost:5173
```

Установите `frontend/.env`:

```ini
VITE_API_URL=http://localhost:8000
VITE_SUB_URL_TEMPLATE=http://localhost:8000/sub/{uuid}
```

Значения `CORS_ORIGINS` по умолчанию в backend уже разрешают:

```text
http://localhost:5173
```

поэтому dev-сервер может напрямую обращаться к API.

Другие скрипты:

```bash
npm run build      # проверка типов + production-сборка → dist/
npm run lint       # oxlint
npm run preview    # локальная раздача собранного dist/
```

---

## Структура проекта

```
backend/
  src/
    main.py            # FastAPI app, подключение роутеров, lifespan (таблицы + цикл трафика)
    config.py          # настройки env (pydantic-settings)
    database.py        # async engine, фабрика сессий, create_tables
    traffic.py         # фоновый сбор трафика + применение лимитов
    auth/              # вход администратора, JWT dependency
    users/             # локальные записи пользователей + трафик (router/service/db/models/schemas)
    profiles/          # YAML-шаблоны профилей (router/service/db/models/schemas)
    olcrtc/            # Docker SDK wrapper + сервис/схемы контейнеров
    subscriptions/     # генерация подписок, преобразование config→bundle/URI
    rw/                # Remnawave SDK wrapper
  olcrtc/              # образ OLCRTC-контейнера (Dockerfile, entrypoint, Go proxy)
  Dockerfile           # образ API
frontend/
  src/
    api/               # axios-клиенты, один файл на ресурс
    pages/             # один компонент на маршрут (Dashboard, Users, Profiles, ...)
    components/        # ui/ (примитивы), layout/, containers/, common/
    store/             # zustand auth store
    router/            # таблица маршрутов
    types/             # общие TypeScript-типы
    utils/             # форматирование + хуки
caddy/Caddyfile        # конфигурация reverse proxy
docker-compose.yaml    # prod: caddy + api + postgres
docker-compose-dev.yaml# dev: api + postgres
```

Каждый backend-модуль использует одинаковое разделение слоев:

* `router.py` - HTTP endpoints (тонкий слой, с проверкой авторизации).
* `service.py` - бизнес-логика, оркестрация.
* `db.py` - запросы к базе данных.
* `models.py` - таблицы SQLAlchemy.
* `schemas.py` - модели запросов/ответов Pydantic.

---

## Куда добавлять новые элементы

* **Новый API endpoint** → добавьте route в соответствующий `router.py`, логику разместите в `service.py`, запросы в `db.py`. Новые роутеры зарегистрируйте в `backend/src/main.py`.

* **Новая страница** → добавьте компонент в `frontend/src/pages/`, зарегистрируйте его в `frontend/src/router/index.tsx` и добавьте пункт навигации в `frontend/src/components/layout/Sidebar.tsx`.

* **Новый API-вызов из frontend** → добавьте метод в соответствующий клиент в `frontend/src/api/`, а тип - в `frontend/src/types/index.ts`.

* **Новый переиспользуемый UI-компонент** → `frontend/src/components/ui/`.

---

# Процесс разработки и правила использования AI

Это внутреннее соглашение для участников разработки OLcWave. Прочитайте его перед изменением кода.

---

## Backend

Backend должен разрабатываться **осознанно**.

**Не используйте AI coding agents для генерации реализации backend.**

Это включает всё внутри:

```text
backend/src/
```

написанное с использованием:

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* бизнес-логики
* интеграции с Docker
* внешних интеграций (Remnawave и т.д.)

**Почему:** backend содержит части, связанные с безопасностью:

* аутентификация;
* управление пользователями;
* управление контейнерами (что фактически является root-доступом к хосту через Docker socket);
* контроль трафика.

Этот код должен писаться разработчиком, который полностью понимает каждую строку

Вы **можете использовать AI для:**

* чтения документации библиотек;
* поиска решений / подходов;
* объяснения сообщений об ошибках;
* ревью уже написанного вами кода.

Вы **не можете использовать AI для генерации самой реализации backend.**

---

## Frontend - AI разрешен

AI coding agents разрешены для frontend.

**Почему:** frontend в основном представляет собой UI:

* компоненты;
* страницы;
* формы;
* таблицы;
* отображение данных.

В браузере нет секретов и привилегированных операций - backend контролирует всё.

AI можно использовать для:

* написания React-компонентов;
* стилизации (Tailwind / CSS);
* рефакторинга UI;
* генерации повторяющегося кода (таблицы, формы, списки).

**Но каждое изменение должно быть проверено разработчиком перед слиянием.**

Код, сгенерированный AI и не понятый разработчиком, не должен попадать в commit.

---

## Документация - AI разрешен

AI можно использовать для помощи с документацией.

AI подходит для:

* создания черновиков README / руководств;
* описания архитектуры;
* написания примеров;
* улучшения формулировок.

**Но документация должна проверяться вручную и соответствовать реальному состоянию кода.**

Документация, описывающая несуществующие возможности, хуже, чем отсутствие документации.

---

## Итог

| Часть проекта | AI agents | Правило                     |
| ------------- | --------- | --------------------------- |
| Backend       | Нет       | Писать вручную              |
| Frontend      | Да        | Проверять каждое изменение  |
| Documentation | Да        | Проверять соответствие коду |
