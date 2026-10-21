-- Lumen Workspace warehouse (SQLite).
-- fact_subscription_month is one row per account per month, including the
-- month an account churns (mrr = 0). That row is what makes the bridge balance.
-- Do not count rows to count customers.

PRAGMA foreign_keys = ON;

CREATE TABLE dim_date (
  date_key INTEGER PRIMARY KEY,
  full_date TEXT NOT NULL UNIQUE,
  year INTEGER NOT NULL,
  quarter INTEGER NOT NULL,
  month INTEGER NOT NULL,
  month_name TEXT NOT NULL,
  year_month TEXT NOT NULL,
  day INTEGER NOT NULL,
  day_name TEXT NOT NULL,
  day_of_week INTEGER NOT NULL,
  week_of_year INTEGER NOT NULL,
  is_weekend INTEGER NOT NULL CHECK (is_weekend IN (0, 1))
);

CREATE TABLE dim_plan (
  plan_id INTEGER PRIMARY KEY,
  plan_name TEXT NOT NULL UNIQUE,
  monthly_price_per_seat REAL NOT NULL CHECK (monthly_price_per_seat > 0),
  tier_rank INTEGER NOT NULL UNIQUE
);

CREATE TABLE dim_channel (
  channel_id INTEGER PRIMARY KEY,
  channel_name TEXT NOT NULL UNIQUE,
  channel_group TEXT NOT NULL
);

CREATE TABLE dim_account (
  account_id INTEGER PRIMARY KEY,
  account_name TEXT NOT NULL,
  industry TEXT NOT NULL,
  region TEXT NOT NULL,
  employee_band TEXT NOT NULL,
  signup_date TEXT NOT NULL REFERENCES dim_date (full_date),
  channel_id INTEGER NOT NULL REFERENCES dim_channel (channel_id)
);

CREATE TABLE fact_subscription_month (
  subscription_month_id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL REFERENCES dim_account (account_id),
  month_start TEXT NOT NULL REFERENCES dim_date (full_date),
  plan_id INTEGER NOT NULL REFERENCES dim_plan (plan_id),
  seats INTEGER NOT NULL CHECK (seats > 0),
  mrr REAL NOT NULL CHECK (mrr >= 0),
  prior_mrr REAL NOT NULL CHECK (prior_mrr >= 0),
  movement TEXT NOT NULL CHECK (
    movement IN ('New', 'Reactivation', 'Expansion', 'Contraction', 'Churn', 'Retained')
  ),
  UNIQUE (account_id, month_start)
);

CREATE TABLE fact_usage_monthly (
  account_id INTEGER NOT NULL REFERENCES dim_account (account_id),
  month_start TEXT NOT NULL REFERENCES dim_date (full_date),
  active_users INTEGER NOT NULL CHECK (active_users >= 0),
  events INTEGER NOT NULL CHECK (events >= 0),
  adoption_score INTEGER NOT NULL CHECK (adoption_score BETWEEN 0 AND 100),
  PRIMARY KEY (account_id, month_start)
);

CREATE TABLE fact_ticket (
  ticket_id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL REFERENCES dim_account (account_id),
  opened_date TEXT NOT NULL REFERENCES dim_date (full_date),
  priority TEXT NOT NULL CHECK (priority IN ('Low', 'Medium', 'High', 'Urgent')),
  category TEXT NOT NULL,
  resolution_hours REAL NOT NULL CHECK (resolution_hours >= 0),
  csat REAL NOT NULL CHECK (csat BETWEEN 1 AND 5)
);

CREATE TABLE fact_marketing_spend (
  spend_id INTEGER PRIMARY KEY,
  month_start TEXT NOT NULL REFERENCES dim_date (full_date),
  channel_id INTEGER NOT NULL REFERENCES dim_channel (channel_id),
  spend REAL NOT NULL CHECK (spend >= 0),
  UNIQUE (month_start, channel_id)
);

CREATE INDEX idx_sub_month ON fact_subscription_month (month_start);
CREATE INDEX idx_sub_movement ON fact_subscription_month (movement);
CREATE INDEX idx_usage_month ON fact_usage_monthly (month_start);
CREATE INDEX idx_ticket_account ON fact_ticket (account_id);
CREATE INDEX idx_ticket_opened ON fact_ticket (opened_date);
