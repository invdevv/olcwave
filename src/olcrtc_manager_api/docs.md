# olcrtc_manager_api — документация

Асинхронный Python-клиент для REST API [olcrtc-manager-panel](https://github.com/BigDaddy3334/olcrtc-manager-panel).

**Стек:** Python 3.13 · httpx · pydantic v2

---

## Быстрый старт

```python
from olcrtc_manager_api.client import OlcrtcManager

async with OlcrtcManager("http://127.0.0.1:8888", "admin", "secret") as mgr:
    state = await mgr.get_state()
    for client in state.clients:
        print(client.client_id, client.quota.used_gb, "GB used")
```

---

## Класс `OlcrtcManager`

Основной клиент для работы с API. Используется как асинхронный контекстный менеджер.

### Инициализация

```python
OlcrtcManager(
    base_url: str,
    username: str | None = None,
    password: str | None = None,
    *,
    timeout: float = 30.0,
)
```

| Параметр | Описание |
|---|---|
| `base_url` | Базовый URL панели, например `http://127.0.0.1:8888` |
| `username` | Логин администратора (опционально) |
| `password` | Пароль администратора (опционально) |
| `timeout` | Таймаут HTTP-запросов в секундах (по умолчанию `30.0`) |

Аутентификация выполняется через HTTP Basic Auth. Если `username` и `password` не переданы, запросы отправляются без авторизации (подходит для эндпоинтов, не требующих аутентификации).

---

## Методы

### Аутентификация

---

#### `me() → AuthMeResponse`
`GET /api/auth/me`

Проверяет текущую сессию и статус первоначальной настройки.

```python
info = await mgr.me()
print(info.authenticated, info.setup_required)
```

---

#### `login(user, password) → AuthMeResponse`
`POST /api/auth/login`

Создаёт сессионную cookie. Обратите внимание: поле в теле запроса называется `user`, а не `username`.

```python
await mgr.login("admin", "secret")
```

---

#### `logout() → None`
`POST /api/auth/logout`

Инвалидирует текущую сессию.

---

#### `setup(password, user="admin") → AuthMeResponse`
`POST /api/auth/setup`

Первоначальная настройка — работает только если пароль ещё не задан. Вернёт ошибку `409` при повторном вызове. Минимальная длина пароля — 8 символов.

```python
await mgr.setup("my_secure_password")
```

---

#### `change_password(current_password, new_password) → None`
`POST /api/auth/password`

Смена пароля администратора. Требует активной сессии или Basic Auth. Минимальная длина нового пароля — 8 символов.

---

### Состояние и мониторинг

---

#### `get_state() → State`
`GET /api/state`

Возвращает полное состояние менеджера: список всех клиентов, их локации и статусы процессов. Отдельного эндпоинта для списка клиентов нет — используйте этот метод.

```python
state = await mgr.get_state()
print(state.client_count, state.running_count)
for client in state.clients:
    print(client.client_id, client.quota.expires_at)
```

---

#### `get_metrics() → Metrics`
`GET /api/metrics`

Метрики Go-рантайма, памяти и дочерних процессов.

---

#### `get_audit() → AuditResponse`
`GET /api/audit`

Последние 100 записей аудит-лога.

---

#### `get_logs(client_id, room_id, transport) → LogsResponse`
`GET /api/logs/{client_id}/{room_id}/{transport}`

Логи конкретной локации. Все три параметра обязательны — их можно получить из `LocationState` через `get_state()`.

```python
state = await mgr.get_state()
loc = state.clients[0].locations[0]
logs = await mgr.get_logs(state.clients[0].client_id, loc.room_id, loc.transport)
```

---

### Управление клиентами (CRUD)

---

#### `create_client(request) → CreateClientResponse`
`POST /api/clients`

Создаёт нового клиента. Сервер автоматически генерирует `room_id` и 32-байтный ключ.

```python
from olcrtc_manager_api.models import AddClientRequest, Quota

req = AddClientRequest(
    client_id="alice",
    carrier="wbstream",
    transport="datachannel",
    dns="1.1.1.1:53",
    quota=Quota(expires_at="2026-12-31"),
)
resp = await mgr.create_client(req)
print(resp.client_id)
```

> **Важно:** `transport` — это строка (`"datachannel"`), а не JSON-объект. Транспорт-специфичные опции передаются через поле `payload`.

Чтобы склонировать локации существующего клиента, заполните `from_client` вместо `carrier`/`transport`/`dns`.

---

#### `update_client(client_id, request) → None`
`PUT /api/clients/{client_id}`

Обновляет первую локацию клиента (carrier, transport, dns, quota, name). Поля `carrier`, `transport` и `dns` обязательны. Возвращает `204 No Content`.

```python
from olcrtc_manager_api.models import UpdateClientRequest

await mgr.update_client("alice", UpdateClientRequest(
    carrier="wbstream",
    transport="datachannel",
    dns="8.8.8.8:53",
))
```

---

#### `delete_client(client_id) → None`
`DELETE /api/clients/{client_id}`

Останавливает все процессы клиента и удаляет его из конфига. Нельзя удалить последнего оставшегося клиента.

---

#### `add_location(client_id, request) → None`
`POST /api/clients/{client_id}/locations`

Добавляет новую локацию к существующему клиенту с автоматически сгенерированным `room_id` и ключом.

---

#### `delete_location(client_id, room_id) → None`
`DELETE /api/clients/{client_id}/locations/{room_id}`

Удаляет одну локацию по `room_id`. Нельзя удалить последнюю локацию клиента.

---

### Действия

---

#### `restart_location(client_id, room_id, transport) → None`
`POST /api/actions/restart`

Перезапускает конкретный процесс локации. Все три параметра можно получить из `LocationState`.

---

#### `regenerate_room(client_id) → None`
`POST /api/actions/regenerate-room`

Генерирует новый `room_id` для всех локаций клиента, сохраняет конфиг и выполняет reload.

---

#### `rotate_key(client_id) → None`
`POST /api/actions/rotate-key`

Генерирует новый случайный 32-байтный ключ для всех локаций клиента, сохраняет конфиг и выполняет reload.

---

#### `reload() → None`
`POST /api/reload`

Горячая перезагрузка конфига — перезапускает только изменившихся клиентов. Требует аутентификации.

---

#### `reload_loopback() → None`
`POST /-/reload`

То же самое, что `reload()`, но без аутентификации — принимает запросы только с `127.0.0.1`.

---

### Подписки

---

#### `get_subscription(client_id) → str`
`GET /{client_id}/`

Возвращает текст OlcBox-подписки в виде plain-text строки. Аутентификация не требуется.

```python
raw = await mgr.get_subscription("alice")
print(raw)
# #quota-speed-mbps: 10
# #quota-traffic-gb: 100
# olcrtc://wbstream?datachannel@room-01#key%alice$Alice
```

---

#### `get_subscription_parsed(client_id) → tuple[SubscriptionMeta, list[OlcboxURI]]`

Получает и парсит текст подписки. Возвращает кортеж из метаданных квоты и списка URI.

```python
meta, uris = await mgr.get_subscription_parsed("alice")
print(meta.status)        # QuotaStatus.ACTIVE
print(meta.expires_at)    # "2026-12-31"
print(uris[0].carrier)    # "wbstream"
print(uris[0].transport)  # "datachannel"
```

---

### Вспомогательные методы

---

#### `is_first_run() → bool`

Возвращает `True`, если пароль ещё не настроен (первый запуск).

---

#### `list_clients() → list[ClientState]`

Удобный шорткат — возвращает `state.clients` из `get_state()`.

---

#### `get_uri(client_id, location_index=0) → OlcboxURI | None`

Возвращает распарсенный `OlcboxURI` для указанной локации клиента. Возвращает `None`, если клиент или локация не найдены.

---

## Исключения

### `OlcrtcManagerError`

Выбрасывается при получении не-2xx ответа от API.

```python
try:
    await mgr.delete_client("unknown")
except OlcrtcManagerError as e:
    print(e.status_code)  # например, 404
    print(e.detail)       # текст ошибки от сервера
```

---

## Модели данных

### Enums

| Класс | Значения |
|---|---|
| `Carrier` | `wbstream`, `jazz`, `telemost` |
| `TransportType` | `datachannel`, `vp8channel`, `seichannel`, `videochannel` |
| `QuotaStatus` | `active`, `expired`, `traffic_exceeded` |

> **Важно:** значения транспорта — `"vp8channel"`, `"seichannel"`, `"videochannel"`, а не `"vp8"` / `"sei"`.

---

### `Quota`

Квота трафика и скорости. Числовые поля по умолчанию равны `0` (без ограничений).

| Поле | Тип | Описание |
|---|---|---|
| `speed_mbps` | `int` | Ограничение скорости в Мбит/с (`0` = без лимита) |
| `traffic_gb` | `int` | Лимит трафика в ГБ (`0` = без лимита) |
| `used_gb` | `int` | Использовано ГБ |
| `used_bytes` | `int` | Использовано байт |
| `expires_at` | `str` | Дата истечения в формате `YYYY-MM-DD` или пустая строка |

---

### `State`

Полный ответ `GET /api/state`.

| Поле | Тип | Описание |
|---|---|---|
| `name` | `str` | Имя сервера |
| `port` | `int` | Порт |
| `client_count` | `int` | Всего клиентов |
| `running_count` | `int` | Запущенных процессов |
| `clients` | `list[ClientState]` | Список клиентов |

---

### `ClientState`

| Поле | Тип | Описание |
|---|---|---|
| `client_id` | `str` | Идентификатор клиента |
| `quota` | `Quota` | Текущая квота |
| `locations` | `list[LocationState]` | Локации клиента |

---

### `LocationState`

| Поле | Тип | Описание |
|---|---|---|
| `name` | `str` | Имя локации |
| `room_id` | `str` | Идентификатор комнаты |
| `uri` | `str` | OlcBox URI для этой локации |
| `carrier` | `str` | Carrier |
| `transport` | `str` | Тип транспорта |
| `running` | `bool` | Запущен ли процесс |
| `runtime` | `RuntimeState` | Детальный статус процесса |

---

### `OlcboxURI`

Распарсенный URI формата `olcrtc://<carrier>?<transport>@<room_id>#<key>%<client_id>$<display_name>`.

| Поле | Тип | Описание |
|---|---|---|
| `carrier` | `str` | Carrier |
| `transport` | `str` | Тип транспорта |
| `room_id` | `str` | Идентификатор комнаты |
| `key` | `str` | Ключ подключения |
| `client_id` | `str \| None` | Идентификатор клиента |
| `display_name` | `str \| None` | Отображаемое имя |
| `raw` | `str` | Исходная строка URI |

Парсинг из строки:

```python
uri = OlcboxURI.from_raw("olcrtc://wbstream?datachannel@room-01#key%alice$Alice")
print(uri.carrier)      # "wbstream"
print(uri.client_id)    # "alice"
```

---

### `SubscriptionMeta`

Метаданные квоты, извлечённые из строк `#quota-*` в тексте подписки.

| Поле | Тип | Описание |
|---|---|---|
| `speed_mbps` | `int \| None` | Скорость в Мбит/с |
| `traffic_gb` | `int \| None` | Лимит трафика в ГБ |
| `used_gb` | `float \| None` | Использовано ГБ |
| `used_bytes` | `int \| None` | Использовано байт |
| `expires_at` | `str \| None` | Дата истечения |
| `status` | `QuotaStatus \| None` | Статус квоты |