# API

Бэкенд - это приложение на FastAPI. Интерактивная документация всегда доступна по адресам `/docs` (Swagger) и `/redoc` на запущенном API.

Базовый URL: то, на что указывает `VITE_API_URL` (например, `http://localhost:8000` в dev). Ниже маршруты указаны относительно него. Сам бэкенд обслуживает маршруты **без префикса `/api`** - в production Caddy публикует их под `/api/*` и удаляет префикс перед проксированием, поэтому в production `VITE_API_URL` оканчивается на `/api`.

## Auth

Все эндпоинты, кроме `POST /auth/login` и `GET /sub/{short_uuid}`, требуют bearer-токен:

```
Authorization: Bearer <token>
```

Токен - это JWT, подписанный `JWT_SECRET_KEY`, действительный в течение `JWT_EXPIRE_MINUTES`. Ответ `401` очищает токен во фронтенде и перенаправляет на страницу входа.

### `POST /auth/login`

Войти как администратор. Администратор ровно один (из `ADMIN_USERNAME` / `ADMIN_PASSWORD`).

**Запрос**

```json
{ "username": "admin", "password": "your-password" }
```

**Ответ** `200`

```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer" }
```

`401` - при неверных учетных данных.

---

## Users

Локальные записи пользователей (трафик + срок действия). `short_uuid` - это короткий UUID Remnawave.

### `GET /users/all?tag=`

Список всех пользователей. (`tag` в строке запроса обязателен по сигнатуре, но не используется - передавайте `?tag=`.)

### `GET /users/?short_uuid=<uuid>`

Один пользователь. `404`, если не найден.

**Ответ** (`UserSchema`)

```json
{
  "short_uuid": "rfWMHbDFsH_cPXRz",
  "created_at": "2026-01-01T00:00:00Z",
  "expires_at": "2026-06-01T00:00:00Z",
  "traffic_limit_bytes": 107374182400,
  "traffic_used_bytes": 1048576
}
```

### `PUT /users/?short_uuid=<uuid>&expires_at=<iso8601>`

Обновить срок действия пользователя. Параметры передаются в query string.

### `DELETE /users/?short_uuid=<uuid>`

Удалить пользователя.

### `GET /users/traffic?short_uuid=<uuid>`

Информация о трафике (`TrafficInfoSchema`).

```json
{
  "short_uuid": "rfWMHbDFsH_cPXRz",
  "limit": 107374182400,
  "used": 1048576,
  "remaining": 107373133824,
  "unlimited": false,
  "exceeded": false
}
```

### `PATCH /users/traffic?short_uuid=<uuid>`

Установить лимит трафика. `0` = безлимит.

**Запрос**

```json
{ "traffic_limit_bytes": 214748364800 }
```

Возвращает обновленный `TrafficInfoSchema`.

### `POST /users/traffic/reset?short_uuid=<uuid>`

Сбросить `used` до 0. Возвращает обновленный `TrafficInfoSchema`.

---

## Profiles

Шаблоны OLCRTC YAML. См. [profiles.md](profiles.md).

### `GET /profiles/all?tag=`

Список всех профилей. (`tag` обязателен по сигнатуре, но не используется.)

### `GET /profiles/?tag=<tag>`

Один профиль по тегу. `404`, если не найден.

### `POST /profiles/`

Создать профиль. YAML валидируется (должен корректно парситься).

**Запрос** (`ProfileSchema`)

```json
{ "name": "Germany VP8", "tag": "de-vp8", "profile": "mode: cnc\nauth:\n  provider: jitsi\n..." }
```

Возвращает `"ok"`.

### `PUT /profiles/?tag=<tag>&name=<name>&profile=<yaml>`

Обновить имя профиля и YAML. Параметры передаются в query string. **Побочный эффект:** останавливает все контейнеры, имя которых содержит `<tag>`.

### `DELETE /profiles/?tag=<tag>`

Удалить профиль. **Побочный эффект:** останавливает и удаляет все контейнеры, имя которых содержит `<tag>`.

---

## Containers

Docker-контейнеры с именами `olcwave-<config_tag>-<user_id>`.

### `GET /containers/all`

Все контейнеры панели (запущенные и остановленные).

**Ответ** (список `ContainerSchema`)

```json
[
  {
    "id": "3f2a1b...",
    "name": "olcwave-de-vp8-rfWMHbDFsH_cPXRz",
    "user_id": "rfWMHbDFsH_cPXRz",
    "config_tag": "de-vp8",
    "status": "running",
    "created": "2026-01-01T00:00:00Z",
    "image": "olcrtc"
  }
]
```

### `POST /containers/run?name=<name>`

Запустить контейнер. Возвращает `403 traffic_limit_exceeded`, если у владельца пользователя превышен лимит.

### `POST /containers/stop?name=<name>`

Остановить контейнер.

### `POST /containers/restart?name=<name>`

Перезапустить контейнер.

### `DELETE /containers/?name=<name>`

Принудительно удалить контейнер.

### `GET /containers/logs?name=<name>`

`{ "name": "...", "logs": "..." }` - stdout/stderr контейнера.

### `GET /containers/config?name=<name>`

`{ "name": "...", "config": "..." }` - `config.yaml`, с которым работает контейнер.

### `GET /containers/stats?name=<name>`

Живые счетчики байтов (`ContainerStatsSchema`).

```json
{
  "name": "olcwave-de-vp8-rfWMHbDFsH_cPXRz",
  "upload_bytes": 12345,
  "download_bytes": 67890,
  "total_bytes": 80235,
  "upload_rate_bps": 1024,
  "download_rate_bps": 4096
}
```

---

## Subscriptions (public)

### `GET /sub/{short_uuid}`

Публичный эндпоинт подписки. **Без авторизации.** Именно его запрашивает клиент подписчика.

Поведение (см. [architecture.md](architecture.md)):

* Проверяет UUID в Remnawave. `404`, если UUID неизвестен.
* При первом обращении автоматически создает локальную запись пользователя.
* Если у пользователя превышен лимит трафика → возвращает заглушку конфигурации "Traffic limit Exceeded" с HTTP `403`.
* Иначе запускает все отсутствующие контейнеры для пользователя и возвращает bundle **OLCBox v5** (JSON) со всеми его локациями.

В ответе присутствует заголовок `profile-update-interval`, чтобы клиенты знали, как часто обновляться.
