##Reset DOCKER #######
---

## 🔄 1. Stop and remove everything

First, stop all containers and remove volumes/networks:

```bash
./run-sea-seq.sh down
```

Also clean up anything left behind:

```bash
docker-compose down -v
```

---

## 🧹 2. Prune Docker system

This clears old images, build cache, and networks that might conflict:

```bash
docker system prune -af --volumes
```

⚠️ This will nuke unused images/volumes — which is what you want right now to guarantee a clean rebuild.

---

## 📦 3. Rebuild images fresh

Now rebuild with **no cache**:

```bash
docker-compose build --no-cache
```

This forces Docker to re-run every layer (so you know your new Dockerfile is really being used).

---

## 🚀 4. Run SEA-SEQ

* To run **both CLI + API**:

  ```bash
  ./run-sea-seq.sh both
  ```

* To run only the **CLI** (writes reports to `./reports/`):

  ```bash
  ./run-sea-seq.sh cli
  ```

* To run only the **API service** (FastAPI at [http://localhost:8000](http://localhost:8000)):

  ```bash
  ./run-sea-seq.sh api
  ```

---

## ✅ 5. Verify it worked

* Check the **CLI** container output — you should see it run test suites and create files in `./reports/`.
  Example:

  * `reports/report.html`
  * `reports/junit.xml`
  * `reports/results.json`

* Open your browser to:
  👉 [http://localhost:8000](http://localhost:8000)
  and confirm the API is running.

---

## 🛑 6. Shut down when done

```bash
./run-sea-seq.sh down
```

---

⚡ Pro tip: if things **still fail**, I’d suggest you run:

```bash
ls -R cmd
```
