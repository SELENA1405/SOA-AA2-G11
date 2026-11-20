"""Replaceable database driver; no dependencies on other project layers.

Every method uses parameterised SQL (%s placeholders). Every operation runs in
one transaction: `with psycopg.connect(...)` commits on success and rolls back
if an exception escapes. Plan operations always match BOTH plan code and
session code, so one session can never read or change another session's plan.

Mutation methods return a plain status string instead of raising domain errors
(this layer must not import other project layers):
    "ok", "plan_not_found", "equipment_not_found", "item_not_found", "duplicate"
The application layer translates these into 404 / 409 responses.
Quantity validation (whole number 1 to 15) is done in the domain layer before
these methods are called; the database CHECK constraint is the last line of defence.
"""
import psycopg
from psycopg.rows import dict_row


class PostgresData:
    def __init__(self, url: str):
        self.url = url

    def _connect(self):
        return psycopg.connect(self.url, row_factory=dict_row, connect_timeout=3)

    def _read(self, sql: str, values: tuple = ()) -> list[dict]:
        with self._connect() as connection:
            return connection.execute(sql, values).fetchall()

    @staticmethod
    def _plan_belongs_to_session(connection, plan_code: str, session_code: str) -> bool:
        row = connection.execute(
            "SELECT 1 AS owned FROM load_plans WHERE plan_code = %s AND session_code = %s",
            (plan_code, session_code),
        ).fetchone()
        return row is not None

    def health(self) -> bool:
        return self._read("SELECT 1 AS connected") == [{"connected": 1}]

    # ---- Equipment catalogue (read-only) -------------------------------

    def catalogue(self) -> list[dict]:
        """All equipment types: equipment_code, name, unit_mass_kg, handling_notes."""
        return self._read(
            "SELECT equipment_code, name, unit_mass_kg, handling_notes "
            "FROM equipment_types ORDER BY equipment_code"
        )

    def catalogue_item(self, equipment_code: str) -> dict | None:
        """One equipment type, or None if the code does not exist."""
        rows = self._read(
            "SELECT equipment_code, name, unit_mass_kg, handling_notes "
            "FROM equipment_types WHERE equipment_code = %s",
            (equipment_code,),
        )
        return rows[0] if rows else None

    # ---- Load plans (session-owned) ------------------------------------

    def create_or_get_plan(self, plan_code: str, session_code: str) -> dict:
        """Create the session's plan, or return the one it already has.

        Relies on the UNIQUE session_code. Returns
        {"plan_code": <the session's plan code>, "created": True/False}.
        `plan_code` is only used when a new plan is created.
        """
        with self._connect() as connection:
            inserted = connection.execute(
                "INSERT INTO load_plans (plan_code, session_code) VALUES (%s, %s) "
                "ON CONFLICT (session_code) DO NOTHING RETURNING plan_code",
                (plan_code, session_code),
            ).fetchone()
            if inserted is not None:
                return {"plan_code": inserted["plan_code"], "created": True}
            existing = connection.execute(
                "SELECT plan_code FROM load_plans WHERE session_code = %s",
                (session_code,),
            ).fetchone()
            return {"plan_code": existing["plan_code"], "created": False}

    def get_plan(self, plan_code: str, session_code: str) -> dict | None:
        """Saved plan, or None if the plan does not exist for this session.

        Returns {"plan_code": ..., "items": [{equipment_code, name, unit_count,
        unit_mass_kg}, ...]} ordered by equipment_code. An empty plan has
        items == []. No totals are calculated here: the domain layer does that.
        """
        rows = self._read(
            "SELECT p.plan_code, i.equipment_code, e.name, i.unit_count, e.unit_mass_kg "
            "FROM load_plans p "
            "LEFT JOIN load_plan_items i ON i.plan_code = p.plan_code "
            "LEFT JOIN equipment_types e ON e.equipment_code = i.equipment_code "
            "WHERE p.plan_code = %s AND p.session_code = %s "
            "ORDER BY i.equipment_code",
            (plan_code, session_code),
        )
        if not rows:
            return None
        items = [
            {
                "equipment_code": row["equipment_code"],
                "name": row["name"],
                "unit_count": row["unit_count"],
                "unit_mass_kg": row["unit_mass_kg"],
            }
            for row in rows
            if row["equipment_code"] is not None
        ]
        return {"plan_code": rows[0]["plan_code"], "items": items}

    def add_item(self, plan_code: str, session_code: str, equipment_code: str, unit_count: int) -> str:
        """Add an equipment type to the plan.

        "ok", "plan_not_found", "equipment_not_found" or "duplicate"
        (the equipment is already in this plan).
        """
        with self._connect() as connection:
            if not self._plan_belongs_to_session(connection, plan_code, session_code):
                return "plan_not_found"
            known = connection.execute(
                "SELECT 1 AS known FROM equipment_types WHERE equipment_code = %s",
                (equipment_code,),
            ).fetchone()
            if known is None:
                return "equipment_not_found"
            cursor = connection.execute(
                "INSERT INTO load_plan_items (plan_code, equipment_code, unit_count) "
                "VALUES (%s, %s, %s) ON CONFLICT (plan_code, equipment_code) DO NOTHING",
                (plan_code, equipment_code, unit_count),
            )
            return "ok" if cursor.rowcount == 1 else "duplicate"

    def update_item(self, plan_code: str, session_code: str, equipment_code: str, unit_count: int) -> str:
        """Change the count of an equipment type already in the plan.

        "ok", "plan_not_found" or "item_not_found" (not in this plan).
        """
        with self._connect() as connection:
            if not self._plan_belongs_to_session(connection, plan_code, session_code):
                return "plan_not_found"
            cursor = connection.execute(
                "UPDATE load_plan_items SET unit_count = %s "
                "WHERE plan_code = %s AND equipment_code = %s",
                (unit_count, plan_code, equipment_code),
            )
            return "ok" if cursor.rowcount == 1 else "item_not_found"

    def delete_item(self, plan_code: str, session_code: str, equipment_code: str) -> str:
        """Remove an entry from the plan. Never touches equipment_types.

        "ok", "plan_not_found" or "item_not_found" (not in this plan).
        """
        with self._connect() as connection:
            if not self._plan_belongs_to_session(connection, plan_code, session_code):
                return "plan_not_found"
            cursor = connection.execute(
                "DELETE FROM load_plan_items WHERE plan_code = %s AND equipment_code = %s",
                (plan_code, equipment_code),
            )
            return "ok" if cursor.rowcount == 1 else "item_not_found"