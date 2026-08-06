# Architecture and plan

This document is the specification. It says **what** to build and **why**.
It does not say how to write it — that is the point of the project.

---

## 1. What the service does

It downloads historical candles ("klines") from Binance, stores them in
PostgreSQL, and serves them over an HTTP API.

Every request is three things: **an asset, a timeframe, and a time period.**

A separate Java application, written by a friend, is the consumer. It never
touches this code or this database. It speaks HTTP only.

---

## 2. Two processes, one repository

| Process | Runs | Job |
|---|---|---|
| **api** | always | Accepts requests, serves stored candles |
| **worker** | on demand | Downloads candles and writes them to the database |

They share one repository, one Docker image, and one database schema, but run as
two separate containers.

**Why two processes:** a download of one year of one-minute candles takes
minutes. If that ran inside the API process, every download would slow down
every request, and restarting the downloader would drop the API.

**Why one repository:** both processes use the same database tables and the same
data types. Splitting the repository would mean coordinating every schema change
across two repositories and two deployments — more work, and *more* coupling,
not less.

---

## 3. Layers and the dependency rule

This is the most important idea in the project. Learn it properly.

```
        api/            worker/          cli/
          \                |               /
           \               |              /
            +--------------+-------------+
                           |
              binance/          db/
                    \           /
                     \         /
                      domain/
```

**The rule: arrows only point down. Never up.**

| Layer | Contains | May import |
|---|---|---|
| `domain/` | Data types and pure rules. No I/O at all. | nothing from this project |
| `db/` | Reading and writing PostgreSQL | `domain/` |
| `binance/` | Talking to the Binance HTTP API | `domain/` |
| `api/` | FastAPI routes, request/response shapes | everything below |
| `worker/` | The download loop | everything below |
| `cli/` | The same actions from the terminal | everything below |

**Why this matters, concretely:** `domain/` has no database and no network. So
its tests need no setup and run in milliseconds. When you reach the testing
phase, this rule is the difference between tests that are easy to write and
tests that are impossible to write. Beginners skip this rule and then discover
their code cannot be tested at all.

Rule of thumb: if a file imports both `psycopg` and `fastapi`, something is in
the wrong layer.

---

## 4. Suggested project structure

Adjust it as you learn — but keep the dependency rule.

```
market-data-service/
├── src/marketdata/
│   ├── config.py            environment variables -> a settings object
│   ├── domain/              types and pure rules, no I/O
│   ├── db/                  connection, queries, migrations
│   ├── binance/             HTTP client for Binance
│   ├── api/                 FastAPI application and routes
│   ├── worker/              the job loop
│   └── cli.py               terminal entry point
├── tests/
│   ├── unit/                fast, no database
│   └── integration/         real PostgreSQL
├── docker/
├── .github/workflows/
├── docs/
│   ├── architecture.md      you write this, in your own words
│   └── adr/                 architecture decision records
├── .env.example
├── pyproject.toml
└── README.md
```

`src/` layout is deliberate: it stops Python from accidentally importing your
package from the working directory instead of the installed one. You will meet
this problem in the testing phase if you skip it.

---

## 5. The HTTP contract

Four endpoints. Nothing more.

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/downloads` | Start a download. Returns a job id. |
| GET | `/v1/downloads/{id}` | Job status: pending / running / done / failed |
| GET | `/v1/candles` | Read stored candles. Cursor paginated. |
| GET | `/health` | Is the service alive |

The same actions must also work from the command line, without the API running.

### Rules that are already decided

- **Timestamps: milliseconds since Unix epoch, UTC.** No ISO strings, no local
  time zones. Binance uses this format natively; matching it removes a whole
  class of bugs.
- **Numbers are sent as strings in JSON, not as JSON numbers.** A JSON number
  becomes a floating point value on the Java side and silently loses precision.
  On money, that is unacceptable. Binance itself sends strings.
- **Cursor pagination, not offset.** Offset pagination re-scans everything it
  skips. On millions of rows it becomes unusably slow.
- **`/v1/` prefix from the first commit.** It costs nothing now and saves pain
  the first time the format changes.

---

## 6. How the friend uses it

1. He clones the repository and runs `docker compose up` on his Linux machine.
   He needs nothing else — no cloud account, no keys, no configuration beyond
   copying `.env.example` to `.env`.
2. His program calls `POST /v1/downloads` with an asset, a timeframe, and a
   period. It receives a job id.
3. It polls `GET /v1/downloads/{id}` until the status is `done`.
4. It reads the data with `GET /v1/candles`.

That is the entire contract between the two sides.

**Build the stub API first (phase 1), before the database exists.** Once it
returns fake candles in the right shape, he can build his whole side against it
and is never blocked waiting for you. This is called contract-first development,
and being able to explain why you did it is worth more in an interview than most
of the code in this repository.

---

## 7. Where the data comes from

Binance offers three ways to get data. Only two of them are useful here.

| Source | Gives you | Use it? |
|---|---|---|
| **REST API** (`/api/v3/klines`) | History, up to 1000 candles per request | **Yes — the main source** |
| **Bulk dumps** (`data.binance.vision`) | History, whole months as ZIP files | Later, as an optimisation |
| **WebSocket** | Live prices only, no history | No |

**Why not WebSocket.** REST and WebSocket differ in nature, not in speed. With
REST you ask and receive an answer — you *pull*. With WebSocket you stay
connected and the server *pushes* new events to you as they happen.

This service downloads periods that have **already happened**. You cannot ask a
WebSocket for last year — it only sends what is happening now. It is not a worse
choice here, it is an impossible one.

WebSocket would only become relevant if this service had to serve live prices.
It does not. If that ever changes, the layering already supports it: one new
module under `binance/` and one more process. That is what the dependency rule
buys you.

**Scale, so you know what you are dealing with.** One year of one-minute candles
is about 525,000 candles — roughly 526 requests at 1000 per request, a few
minutes with polite pacing. Five years is around 2,600 requests. That is the
point where bulk dumps start winning clearly, and where your measurement will
show a difference worth writing down.

**Rate limits.** Binance measures load in weight units with a per-minute budget.

- Do not hardcode limits copied from a blog post — they change. Binance returns
  your current usage in the **response headers**. Read them and slow yourself down.
- HTTP **429** means you are going too fast. The response says how long to wait.
  Respect it.
- HTTP **418** means you were temporarily IP-banned for ignoring 429s.

Handling these three properly is most of what separates a service from a script,
and it is a common interview question.

**No API key is needed.** Public market data requires no authentication. There
are no credentials in this project at all, which is why the friend can start it
with one command.

**Verify reachability on day one.** Binance applies geographic restrictions and
the main hostname is not reachable everywhere; alternative hostnames exist. Send
one request from the terminal, on your machine and on his, *before* building
three phases on the assumption that it works. Checking assumptions before
building on them is the most valuable habit in this whole project.

---

## 8. Data model

Two tables. Design them yourself; these are the requirements.

### candles

Holds one row per candle. Identified by asset + timeframe + open time — that
combination must be unique, because downloading the same period twice must not
create duplicates.

Prices and volumes must be stored as **exact decimals**, never floating point.
`0.1 + 0.2 != 0.3` in floating point, and this is money.

Think about: which column order makes range queries fast, and which index
supports "give me BTCUSDT 1m between two timestamps".

### download_jobs

One row per download request: what was asked for, the current status, when it
started and finished, how many candles were written, and the error text if it
failed.

The status must be a small fixed set of values, enforced by the database — not
free text.

**Do not add table partitioning yet.** Build the simple version first, load real
data, measure the queries, and only then decide whether partitioning helps. Then
write down the measurement in an ADR. Deciding with numbers instead of opinions
is a senior habit, and doing it in public in your repository is unusual enough
that reviewers notice.

---

## 9. How work flows through the system

**Write path**

```
POST /v1/downloads
  -> validate the request
  -> insert a job row with status "pending"
  -> immediately return the job id     (do not wait for the download)

worker loop
  -> claim one pending job             (SELECT ... FOR UPDATE SKIP LOCKED)
  -> split the period into chunks Binance will accept
  -> for each chunk: fetch, then write the candles
  -> update progress
  -> mark the job done, or failed with the error
```

`FOR UPDATE SKIP LOCKED` is how two workers can run at the same time without
ever picking up the same job. This replaces an entire message queue system with
one SQL clause. Understand it properly — it is a genuinely good interview answer.

**Read path**

```
GET /v1/candles
  -> validate the parameters
  -> query using the index
  -> return one page plus a cursor for the next page
```

### Failures you must handle, not ignore

Binance will rate-limit you. The network will drop. A download of six months
will fail after four. Decide, deliberately:

- What happens when a job fails halfway — is the partial data kept or removed?
- Can the same job be retried safely? (This is what idempotency means, and it is
  why the uniqueness rule on `candles` exists.)
- How do you avoid being banned by Binance for sending too many requests?

Handling these well is what separates a real service from a script.

---

## 10. Phases

Each phase must end with something that runs. Never start the next one before
the current one works.

| # | Phase | What you learn | Rough time |
|---|---|---|---|
| 0 | Repository, structure, dependencies, linter, first commits | project layout, git | 1 day |
| 1 | **Stub API** returning fake candles in the contract shape | HTTP, REST design, validation | 3 days |
| 2 | Database schema, PostgreSQL in Docker, migrations | SQL, data modelling | 4 days |
| 3 | Binance client: rate limits, retries, failures | HTTP clients, error handling | 4 days |
| 4 | Job queue and the worker process | transactions, concurrency | 4 days |
| 5 | Real API over real data, indexes, measurement | query performance | 3 days |
| 6 | Tests, unit and against a real database | testing strategy | 5 days |
| 7 | Dockerfile and docker-compose for everything | containers | 3 days |
| 8 | CI pipeline on GitHub Actions | automation, quality gates | 2 days |
| 9 | README, architecture doc, ADRs | explaining decisions | 2 days |

**Roughly 6–8 weeks at 40 hours per week.** Expect to overrun — everyone does,
and the estimate above already assumes you are learning each topic from zero.
Overrunning is not failure. Skipping phases to hit a date is.

Cloud and Terraform are deliberately not here. A finished, working, well
documented product beats a half-finished one with a cloud deployment bolted on.
Add it later if you want it.

---

## 11. The README is not an afterthought

Most people will spend three minutes on this repository, and most of that in the
README. Write it for a reviewer who has never met you:

1. One sentence: what this is.
2. The architecture diagram and the two processes.
3. **How to run it** — copy `.env.example`, one command, done.
4. The API contract.
5. **Why** — the decisions you made and what you rejected. This section is what
   makes the repository look like an engineer wrote it and not a tutorial
   follower.
6. What you would do next with more time. Honesty here reads as maturity.

Write it in English. Keep the sentences short. Short and clear beats long and
impressive.
