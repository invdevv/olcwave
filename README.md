# OlcWave

### панель для olcrtc управляемая через remnawave users

#### Сейчас не работает

####!!! Важно !!!
Это альфа версия которую я написал за 3 часа без ии
некоторые вещи тут пока работают костыльно или вообще не работают
завтра все допишу

Usage:
1. клиент вставляет ссылку с таким же short_uuid как в remnaWave (rw.example.com/suuid -> olcwave.example.com/suuid)
2. olcWave проверяет есть ли у клиента подписка в rw
3. если есть то отдает ему sub.md файл с подпиской

Instalation:
```bash
git clone https://github.com/invdevv/olcwave.git --depth=1
cd olcwave
docker compose up -
```

