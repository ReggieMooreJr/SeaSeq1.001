# 🚀 SEA-SEQ Quick Start Guide

This guide will help you set up and run **SEA-SEQ** quickly --- whether
you want to spin up supporting services or execute test suites and
generate reports.

<!-- docker build -t seaseq_runner . && docker run --rm -v $(pwd)/reports:/app/reports -v $(pwd):/app seaseq_runner ./seaseq --spec tests/examples/jsonplaceholder/suite.yaml --env tests/examples/jsonplaceholder/env.json --openapi tests/examples/jsonplaceholder/openapi.json --out reports -v --parallel 4 -->


------------------------------------------------------------------------

## 🔑 How It Works

-   **`./run.sh compose`**
    -   Builds and starts the **API/DB/Web stack** defined in
        `docker-compose.yml`.\
    -   Streams logs until you stop it (`Ctrl+C`).
-   **`./run.sh reports [suite env openapi]`**
    -   Builds the SEA-SEQ CLI Docker image.\
    -   Runs the specified test suite inside the container.\
    -   Generates reports in the `./reports/` folder.\
    -   If no arguments are passed, runs the bundled JSONPlaceholder
        demo.

------------------------------------------------------------------------

## 📂 Running SEA-SEQ

### 1. Spin up API/DB/Web services

``` bash
./run.sh compose
```

To view logs at any time:

``` bash
docker-compose logs -f --tail=100
```

To stop services:

``` bash
docker-compose down
```

To stop and remove services (containers, networks, volumes):

``` bash
docker-compose down -v
```

------------------------------------------------------------------------

### 2. Run SEA-SEQ Tests & Generate Reports

``` bash
./run.sh reports
```

This will:\
- Build the CLI image.\
- Run the default demo suite (`tests/examples/jsonplaceholder/...`).\
- Output results into `./reports/`.

Reports include:\
- `report.html` (human-readable)\
- `results.json` (raw results)\
- `junit.xml` (CI integration)\
- `coverage.json` (path/method coverage)

------------------------------------------------------------------------

### 3. Run Custom Test Suites

You can specify your own files:

``` bash
./run.sh reports path/to/suite.yaml path/to/env.json path/to/openapi.json
```

Example:

``` bash
./run.sh reports tests/mysuite.yaml configs/env.json specs/openapi.json
```

------------------------------------------------------------------------

✅ That's it --- new developers can now spin up services or run tests
with one command.
