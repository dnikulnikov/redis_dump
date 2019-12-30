# Утилита redis-dump.
    Предназначена для переноса данных из одного redis-хранилища в другое.

## Установка:
```bash
    cd /path/to/redis_dump
    python3.7 -m venv .env
    source .env/bin/activate
    pip install -e .
```

## Запуск:
	Перенести данные из редис host1:port1/namespace_1 в редис host2:port2/namespace_2
```bash
    redis-dump --from_host host1 --from_port port1 --from_namespace  namespace_1 --to_host host2 --to_port port2 --to_namespace namespace_2
```
