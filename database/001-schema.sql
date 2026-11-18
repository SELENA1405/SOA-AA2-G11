-- AA-02 S18 Club Equipment Transport Planner: database schema.
-- Replaces the starter tables (catalogue_items, collections, collection_entries).

-- Seeded equipment catalogue. Read-only for users; never changed by plan operations.
CREATE TABLE equipment_types (
    equipment_code TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    unit_mass_kg   NUMERIC(6,2) NOT NULL CHECK (unit_mass_kg > 0),
    handling_notes TEXT NOT NULL
);

-- One load plan per anonymous mock session.
CREATE TABLE load_plans (
    plan_code    TEXT PRIMARY KEY,
    session_code TEXT NOT NULL UNIQUE
);

-- Saved equipment entries of a plan. Each equipment type appears at most once per plan.
CREATE TABLE load_plan_items (
    plan_code      TEXT    NOT NULL REFERENCES load_plans (plan_code),
    equipment_code TEXT    NOT NULL REFERENCES equipment_types (equipment_code),
    unit_count     INTEGER NOT NULL CHECK (unit_count BETWEEN 1 AND 15),
    PRIMARY KEY (plan_code, equipment_code)
);
-- Do not assume zero removes an entry; DELETE is separate.
