# OlcWave

[🇷🇺 English](README.md)

> Мост между [RemnaWave](https://github.com/remnawave) и [olcrtc-manager-panel](https://github.com/BigDaddy3334/olcrtc-manager-panel)

OlcWave работает как промежуточный слой: когда пользователь запрашивает подписку по `short_uuid`, OlcWave проверяет его аккаунт в RemnaWave, затем автоматически создаёт или находит клиента в olcrtc-manager и возвращает готовую OlcBox-подписку.

---

## Как это работает

```
Пользователь → olcwave.example.com/{short_uuid}
                  │
                  ├─ 1. Проверка подписки в RemnaWave
                  │       └─ 404 если не найден / истёк срок
                  │
                  ├─ 2. Поиск клиента в olcrtc-manager
                  │       └─ Автосоздание при отсутствии (квота берётся из даты истечения RemnaWave)
                  │
                  └─ 3. Возврат текста OlcBox-подписки
```

`short_uuid` — тот же, что используется в ссылке RemnaWave, поэтому пользователю достаточно просто сменить домен — никаких дополнительных настроек с его стороны не нужно.

---

## Требования

- Docker и Docker Compose
- Работающий инстанс [RemnaWave](https://github.com/remnawave)
- Работающий инстанс [olcrtc-manager-panel](https://github.com/BigDaddy3334/olcrtc-manager-panel)

---

## Установка

```bash
git clone https://github.com/invdevv/olcwave.git --depth=1
cd olcwave
cp .env.example .env   # заполните своими значениями
docker compose up -d
```

Сервис запускается на порту `8000` по умолчанию.

---

## Конфигурация

Все настройки загружаются из файла `.env`:

| Переменная | Описание |
|---|---|
| `BASE_HOST` | Хост для привязки сервера |
| `BASE_PORT` | Порт для привязки сервера |
| `RW_API_URL` | Базовый URL API RemnaWave |
| `RW_API_TOKEN` | Токен API RemnaWave |
| `OLCRTC_MANAGER_URL` | Базовый URL olcrtc-manager-panel |
| `OLCRTC_MANAGER_LOGIN` | Логин администратора olcrtc-manager |
| `OLCRTC_MANAGER_PASSWORD` | Пароль администратора olcrtc-manager |
| `OLCRTC_CARRIER` | Carrier по умолчанию для новых клиентов (например, `wbstream`) |
| `OLCRTC_TRANSPORT` | Transport по умолчанию (например, `datachannel`) |
| `OLCRTC_SERVER_NAME` | Отображаемое имя серверной локации |
| `OLCRTC_DNS` | DNS-сервер для новых клиентов (например, `1.1.1.1:53`) |

---

## Структура проекта

```
src/
├── main.py                  # FastAPI-приложение, единственный эндпоинт GET /{short_uuid}
├── config.py                # Pydantic-настройки (загружаются из .env)
├── rw.py                    # Обёртка над RemnaWave SDK — валидация подписки
├── olcmanager.py            # Логика olcrtc-manager — создание/получение клиента и подписки
└── olcrtc_manager_api/
    ├── client.py            # Асинхронный HTTP-клиент для REST API olcrtc-manager-panel
    └── models.py            # Pydantic-модели (State, ClientState, Quota, OlcboxURI, …)
```

---

## API

### `GET /{short_uuid}`

Возвращает OlcBox-подписку для указанного пользователя.

| Статус | Значение |
|---|---|
| `200` | Текст подписки возвращён |
| `404` | Пользователь не найден в RemnaWave |

---

## Стек

- **Python 3.13**
- **FastAPI** — HTTP-фреймворк
- **httpx** — асинхронный HTTP-клиент
- **Pydantic v2** — валидация данных и настройки
- **remnawave** — Python SDK для RemnaWave
- **uv** — управление пакетами

---

## Лицензия

[GPL-3.0](LICENSE)