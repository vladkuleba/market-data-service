CREATE TABLE candles (
    symbol TEXT NOT NULL,
    interval VARCHAR(5)
        CHECK (interval IN
            ('1s', '1m', '3m', '5m', '15m', '30m', '1h', '2h',
             '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'))
        NOT NULL,

    open_time BIGINT NOT NULL,
    close_time BIGINT NOT NULL,

    open NUMERIC(18, 8) NOT NULL,
    high NUMERIC(18, 8) NOT NULL,
    low NUMERIC(18, 8) NOT NULL,
    close NUMERIC(18, 8) NOT NULL,

    volume NUMERIC(24, 8) NOT NULL,
    quote_volume NUMERIC(24, 8) NOT NULL,
    taker_buy_base_volume NUMERIC(24, 8) NOT NULL,
    taker_buy_quote_volume NUMERIC(24, 8) NOT NULL,

    trades INT NOT NULL,
    PRIMARY KEY (symbol, interval, open_time)
);

CREATE TABLE download_jobs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol TEXT NOT NULL,
    interval VARCHAR(5)
        CHECK (interval IN
            ('1s', '1m', '3m', '5m', '15m', '30m', '1h', '2h',
             '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'))
        NOT NULL,
    start_time BIGINT NOT NULL,
    end_time BIGINT NOT NULL,
    status TEXT
        CHECK (status IN
            ('pending', 'running', 'done', 'failed'))
        NOT NULL,
    error TEXT,

    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,

    candles_written INT NOT NULL DEFAULT 0,

    CHECK (end_time > start_time)
);

-- Claim index for: SELECT ... WHERE status = 'pending' ORDER BY id
--                  FOR UPDATE SKIP LOCKED LIMIT 1
-- Partial: finished jobs leave the index, so it stays small forever.
CREATE INDEX download_jobs_pending_idx
    ON download_jobs (id)
    WHERE status = 'pending';
