# Установка

## Что потребуется

* Linux-сервер (любой современный дистрибутив). Примеры ниже используют `apt` для Debian/Ubuntu.
* **Docker** и **плагин Docker Compose**.
* **Node.js 20+ / npm** - frontend собирается на хосте, а не внутри Docker.
* Рабочий экземпляр **Remnawave** и API-токен для него.
* Для production: **домен** (два имени, например `panel.example.org` и `sub.example.org`), указывающий на сервер. Caddy автоматически получает для них HTTPS-сертификаты.

API-контейнер взаимодействует с Docker daemon хоста через:

```text
/var/run/docker.sock
```

- именно так он запускает OLCRTC-контейнеры.

Это означает, что панель фактически имеет root-доступ к хосту.

Запускайте ее только на сервере, которым вы управляете.

---

# 1. Установка Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl enable --now docker
```

Проверка:

```bash
docker --version
docker compose version
```

Если вы хотите запускать `docker` без `sudo`, добавьте пользователя в группу `docker` и войдите заново:

```bash
sudo usermod -aG docker "$USER"
```

---

# 2. Установка Node.js

```bash
# Debian/Ubuntu - NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version   # v20+
```

---

# 3. Клонирование репозитория

```bash
git clone https://github.com/invdevv/olcwave.git
cd olcwave
```

---

# 4. Сборка olcrtc контейнера

```bash
cd backend/olcrtc
docker build . --tag olcrtc
cd ../..
```

---

# 5. Настройка backend

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Все переменные описаны в [configuration.md](configuration.md).

Переменные, которые **обязательно нужно изменить перед первым запуском**:

```ini
RW_API_URL=https://your-remnawave-host        # базовый URL API Remnawave
RW_API_TOKEN=...                              # API-токен Remnawave
POSTGRES_PASSWORD=<something strong>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<something strong>
JWT_SECRET_KEY=<random string>
```

> Примечание: `backend/.env` передается в API-контейнер во время запуска через `env_file` в `docker-compose.yaml` (он **не встраивается в образ** - находится в `.dockerignore`). Если позже изменить файл, достаточно перезапустить API:
>
> ```bash
> docker compose up -d api
> ```

---

# 6. Настройка frontend

```bash
cp frontend/.env.example frontend/.env
$EDITOR frontend/.env
```

```ini
# Куда браузер обращается для API backend.
# Caddy обслуживает SPA и API через один домен и удаляет префикс /api,
# поэтому здесь указывается <домен панели>/api:
VITE_API_URL=https://panel.example.org/api

# Ссылка подписки, отображаемая/копируемая в UI.
# {uuid} заменяется для каждого пользователя.
VITE_SUB_URL_TEMPLATE=https://sub.example.org/{uuid}
```

Эти значения встраиваются в собранный JavaScript во время сборки (шаг 7).

Изменили их → пересоберите frontend.

---

# 7. Сборка frontend

Caddy раздает статические файлы из:

```text
frontend/dist
```

поэтому сборка выполняется один раз на хосте:

```bash
cd frontend
npm ci
npm run build      # создает frontend/dist
cd ..
```

---

# 8. Настройка доменов в Caddy

Откройте:

```text
caddy/Caddyfile
```

и замените пример доменов на свои:

```caddyfile
panel.example.org {
    # /api/* удаляется перед проксированием:
    # /api/auth/login -> /auth/login в backend.
    handle_path /api/* {
        reverse_proxy api:8000
    }

    handle {
        root * /srv/frontend/dist
        try_files {path} /index.html
        file_server
    }
}

sub.example.org {
    handle {
        rewrite * /sub{uri}
        reverse_proxy panel.example.org
    }
}
```

* `panel.example.org` обслуживает SPA и проксирует `/api/*` в backend, удаляя префикс `/api`.

  Поэтому:

  ```text
  VITE_API_URL
  ```

  заканчивается на:

  ```text
  /api
  ```

  а backend продолжает видеть свои настоящие маршруты:

  ```text
  /auth/login
  ```

* `sub.example.org/<uuid>` переписывается в:

  ```text
  panel.example.org/sub/<uuid>
  ```

  Это публичный URL подписки.

Compose публикует порты:

```text
80
443
```

Они нужны Caddy для автоматического HTTPS на настоящих доменах.

Если нужен только обычный HTTP для быстрого тестирования, замените блок:

```caddyfile
panel.example.org { ... }
```

на:

```caddyfile
:80 {
    handle_path /api/* {
        reverse_proxy api:8000
    }

    handle {
        root * /srv/frontend/dist
        try_files {path} /index.html
        file_server
    }
}
```

В таком режиме Caddy работает через HTTP без сертификатов.

---

# 9. Запуск всего

```bash
docker compose up -d
```

Будут запущены три контейнера:

* `olcwave-postgres` - база данных
* `olcwave-api` - FastAPI backend (ждет, пока PostgreSQL станет готов)
* `olcwave-caddy` - reverse proxy + сервер статических файлов

Backend автоматически создает таблицы базы данных при первом запуске.

Отдельный шаг миграции пока не требуется.

---

# 10. Проверка

```bash
docker ps
```

Вы должны увидеть:

```text
olcwave-postgres
olcwave-api
olcwave-caddy
```

Все должны иметь статус:

```text
Up
```

Проверить логи API:

```bash
docker compose logs -f api
```

После этого откройте:

```text
https://panel.example.org
```

(или ваш хост)

и войдите используя:

```text
ADMIN_USERNAME
ADMIN_PASSWORD
```

из:

```text
backend/.env
```

---

# Локальный вариант / только HTTP

Есть файл:

```text
docker-compose-dev.yaml
```

который запускает только:

* PostgreSQL;
* API.

Без Caddy.

Для локальной разработки обычно проще запускать backend и frontend напрямую на хосте.

См. [development.md](development.md).

---

# Обновление

```bash
git pull

cd frontend && npm ci && npm run build && cd ..

docker compose up -d --build
```

Что происходит:

* frontend пересобирается, если он изменился;
* API image пересобирается;
* контейнеры перезапускаются.

Если изменился только:

```text
backend/.env
```

пересборка не нужна.

Файл читается при старте контейнера, поэтому достаточно:

```bash
docker compose up -d api
```
