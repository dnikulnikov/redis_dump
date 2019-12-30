
Подготовка:
    python3.7 -m venv .env
    source .env/bin/activate
    pip install -e .

Использование:

	Перенести данные из редис host1:port1/namespace_1 в редис host2:port2/namespace_2
        python dump.py dump --from_host host1 --from_port port1 --from_namespace  namespace_1 --to_host host2 --to_port port2 --to_namespace namespace_2

        redis-dump --from_host dev.uis.st --from_port 6379 --from_namespace amocrm_int.0 --to_host localhost --to_port 6379 --to_namespace test_amocrm
