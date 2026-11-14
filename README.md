# CoderRun soldier challenge

The challenge pipeline uses Celery with a local SQLite-backed broker, so no
Redis service is required. Install dependencies and prepare the database:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
```

Start the web app and a worker in separate terminals:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
.\.venv\Scripts\celery.exe -A coderrun_prob3 worker --loglevel=info --pool=threads --concurrency=8
```

Open `/simulate/` and select **Register people**. Celery registers the roster,
downloads every draft batch, follows the fight batches, stores every event, and
queues one task per fight. Revisit `/simulate/` to view the replayed events and
their remaining health. The broker can be changed with `CELERY_BROKER_URL`.
