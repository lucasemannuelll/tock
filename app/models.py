from typing import Any, Optional
from .database import get_connection


def list_projects() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, name FROM projects ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_project(name: str) -> dict[str, Any]:
    conn = get_connection()
    try:
        cur = conn.execute("INSERT INTO projects (name) VALUES (?)", (name,))
        conn.commit()
        return {"id": cur.lastrowid, "name": name}
    finally:
        conn.close()


def delete_project(project_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def list_tags() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, name FROM tags ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def create_tag(name: str) -> dict[str, Any]:
    conn = get_connection()
    try:
        cur = conn.execute("INSERT INTO tags (name) VALUES (?)", (name,))
        conn.commit()
        return {"id": cur.lastrowid, "name": name}
    finally:
        conn.close()


def delete_tag(tag_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def _tags_for_entry(conn, entry_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT t.id, t.name
        FROM tags t
        JOIN time_entry_tags tet ON tet.tag_id = t.id
        WHERE tet.time_entry_id = ?
        ORDER BY t.id
        """,
        (entry_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def list_time_entries() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, project_id, description, started_at, ended_at
            FROM time_entries
            ORDER BY id DESC
            """
        ).fetchall()
        result = []
        for r in rows:
            entry = dict(r)
            entry["tags"] = _tags_for_entry(conn, entry["id"])
            result.append(entry)
        return result
    finally:
        conn.close()


def get_time_entry(entry_id: int) -> Optional[dict[str, Any]]:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT id, project_id, description, started_at, ended_at
            FROM time_entries WHERE id = ?
            """,
            (entry_id,),
        ).fetchone()
        if row is None:
            return None
        entry = dict(row)
        entry["tags"] = _tags_for_entry(conn, entry["id"])
        return entry
    finally:
        conn.close()


def create_time_entry(
    project_id: Optional[int],
    description: str,
    started_at: str,
    ended_at: Optional[str],
) -> dict[str, Any]:

    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO time_entries (project_id, description, started_at, ended_at)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, description, started_at, ended_at),
        )
        conn.commit()
        return get_time_entry(cur.lastrowid)
    finally:
        conn.close()


def update_time_entry(
    entry_id: int, fields: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
    if not fields:
        return get_time_entry(entry_id)
    conn = get_connection()
    try:
        cols = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [entry_id]
        cur = conn.execute(f"UPDATE time_entries SET {cols} WHERE id = ?", values)
        conn.commit()
        if cur.rowcount == 0:
            return None
        return get_time_entry(entry_id)
    finally:
        conn.close()


def delete_time_entry(entry_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def start_time_entry(
    project_id: Optional[int], description: str, started_at: str
) -> dict[str, Any]:
    return create_time_entry(project_id, description, started_at, None)


def stop_time_entry(entry_id: int, ended_at: str) -> Optional[dict[str, Any]]:
    return update_time_entry(entry_id, {"ended_at": ended_at})


def associate_tag(entry_id: int, tag_id: int) -> bool:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO time_entry_tags (time_entry_id, tag_id) VALUES (?, ?)",
            (entry_id, tag_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def dissociate_tag(entry_id: int, tag_id: int) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM time_entry_tags WHERE time_entry_id = ? AND tag_id = ?",
            (entry_id, tag_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
