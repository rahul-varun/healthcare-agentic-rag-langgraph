-- Example health-card schema for the SQL tool. Matches the healthcare
-- vocabulary used by the knowledge graph.
CREATE TABLE IF NOT EXISTS health_plans (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    insurer TEXT NOT NULL,
    country TEXT
);

CREATE TABLE IF NOT EXISTS benefits (
    id SERIAL PRIMARY KEY,
    health_plan_id INTEGER REFERENCES health_plans(id),
    benefit TEXT NOT NULL,
    coverage_limit NUMERIC,
    waiting_period TEXT,
    source_document TEXT,
    source_page INTEGER
);

CREATE TABLE IF NOT EXISTS claims (
    id SERIAL PRIMARY KEY,
    member_id TEXT NOT NULL,
    benefit TEXT NOT NULL,
    status TEXT NOT NULL,
    amount NUMERIC,
    submitted_at TIMESTAMP,
    source_document TEXT,
    source_page INTEGER
);

INSERT INTO health_plans (name, insurer, country) VALUES ('Carewell Plus', 'Example Health', 'India')
ON CONFLICT DO NOTHING;
