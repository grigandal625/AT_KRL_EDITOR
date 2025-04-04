## Установка

С помощью `poetry`

```bash
poetry add git+https://github.com/grigandal625/AT_KRL_EDITOR@master
```

## Запуск сервера

```bash
python -m at_krl_editor
```

### Параметры запуска

> **Примечание**
Если параметр запуска не указан, значение берется из соответствующей переменной среды. Если переменная среды не задана, используется значение по умолчанию.

1. **`-u`, `--url`** - URL для подключения к RabbitMQ.
   - Соответствующая переменная среды: `RABBIT_MQ_URL`
   - Значение по умолчанию: `None`

2. **`-H`, `--host`** - Хост для подключения к RabbitMQ.
   - Соответствующая переменная среды: `RABBIT_MQ_HOST`
   - Значение по умолчанию: `"localhost"`

3. **`-p`, `--port`** - Порт для подключения к RabbitMQ.
   - Соответствующая переменная среды: `RABBIT_MQ_PORT`
   - Значение по умолчанию: `5672`

4. **`-L`, `--login`, `-U`, `--user`, `--user-name`, `--username`, `--user_name`** - Логин для подключения к RabbitMQ.
   - Соответствующая переменная среды: `RABBIT_MQ_USER`
   - Значение по умолчанию: `"guest"`

5. **`-P`, `--password`** - Пароль для подключения к RabbitMQ.
   - Соответствующая переменная среды: `RABBIT_MQ_PASS`
   - Значение по умолчанию: `"guest"`

6. **`-v`, `--virtualhost`, `--virtual-host`, `--virtual_host`** - Виртуальный хост для подключения к RabbitMQ.
   - Соответствующая переменная среды: `RABBIT_MQ_VIRTUALHOST`
   - Значение по умолчанию: `"/"`

7. **`-sh`, `--server-host`** - Хост сервера.
   - Соответствующая переменная среды: `AT_KRL_EDITOR_HOST`
   - Значение по умолчанию: `"localhost"`

8. **`-sp`, `--server-port`** - Порт сервера.
   - Соответствующая переменная среды: `AT_KRL_EDITOR_PORT`
   - Значение по умолчанию: `8000`

9. **`-rh`, `--redis-host`** - Хост Redis.
   - Соответствующая переменная среды: `REDIS_HOST`
   - Значение по умолчанию: `"redis"`

10. **`-rp`, `--redis-port`** - Порт Redis.
    - Соответствующая переменная среды: `REDIS_PORT`
    - Значение по умолчанию: `6379`

11. **`-rpass`, `--redis-pass`** - Пароль Redis.
    - Соответствующая переменная среды: `REDIS_PASS`
    - Значение по умолчанию: `None`

12. **`-db`, `--db-engine`** - Тип СУБД.
    - Соответствующая переменная среды: `DB_ENGINE`
    - Значение по умолчанию: `"postgres"`
    - Допустимые значения: `["postgres", "sqlite"]`

13. **`-dbname`, `--db-name`** - Имя базы данных (или путь к файлу базы данных для SQLite).
    - Соответствующая переменная среды: `DB_NAME`
    - Значение по умолчанию: `"at_krl_editor"`
    - В случае если указан тип СУБД `"sqlite"`, создастся файл БД по указанному пути. Если путь не абсолютный, то файл создастя относительно рабочей директории.

14. **`-dbuser`, `--db-user`** - Пользователь базы данных (для типа СУБД `"postgres"`).
    - Соответствующая переменная среды: `DB_USER`
    - Значение по умолчанию: `"at_krl"`

15. **`-dbpass`, `--db-password`** - Пароль базы данных (для типа СУБД `"postgres"`).
    - Соответствующая переменная среды: `DB_PASS`
    - Значение по умолчанию: `None`

16. **`-dbh`, `--db-host`** - Хост базы данных (для типа СУБД `"postgres"`).
    - Соответствующая переменная среды: `DB_HOST`
    - Значение по умолчанию: `"postgres"`

17. **`-dbpt`, `--db-port`** - Порт базы данных (для типа СУБД `"postgres"`).
    - Соответствующая переменная среды: `DB_PORT`
    - Значение по умолчанию: `5432`

18. **`-nw`, `--no-worker`** - Флаг, указывающий на запуск только сервера без Celery воркера, обрабатывающего загружаемые файлы.
    - Соответствующая переменная среды: `NO_WORKER`
    - Значение по умолчанию: `False`

---
