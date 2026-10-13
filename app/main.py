from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import models
from .database import init_db
from .schemas import (
    ProjectCreate,
    ProjectOut,
    TagCreate,
    TagOut,
    TagAssociate,
    TimeEntryCreate,
    TimeEntryUpdate,
    TimeEntryOut,
)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Tock")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/projects", response_model=list[ProjectOut])
def api_list_projects():
    return models.list_projects()


@app.post("/api/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def api_create_project(payload: ProjectCreate):
    try:
        return models.create_project(payload.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_project(project_id: int):
    if not models.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return None


@app.get("/api/tags", response_model=list[TagOut])
def api_list_tags():
    return models.list_tags()


@app.post("/api/tags", response_model=TagOut, status_code=status.HTTP_201_CREATED)
def api_create_tag(payload: TagCreate):
    try:
        return models.create_tag(payload.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_tag(tag_id: int):
    if not models.delete_tag(tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")
    return None


@app.get("/api/time_entries", response_model=list[TimeEntryOut])
def api_list_time_entries():
    return models.list_time_entries()


@app.post("/api/time_entries", response_model=TimeEntryOut, status_code=status.HTTP_201_CREATED)
def api_create_time_entry(payload: TimeEntryCreate):
    started = payload.started_at or datetime.now(timezone.utc).isoformat()
    try:
        return models.create_time_entry(
            payload.project_id, payload.description, started, payload.ended_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/time_entries/{entry_id}", response_model=TimeEntryOut)
def api_get_time_entry(entry_id: int):
    entry = models.get_time_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return entry


@app.put("/api/time_entries/{entry_id}", response_model=TimeEntryOut)
def api_update_time_entry(entry_id: int, payload: TimeEntryUpdate):
    fields = payload.model_dump(exclude_unset=True)
    try:
        updated = models.update_time_entry(entry_id, fields)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    if updated is None:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return updated


@app.delete("/api/time_entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_time_entry(entry_id: int):
    if not models.delete_time_entry(entry_id):
        raise HTTPException(status_code=404, detail="Time entry not found")
    return None


class StartPayload(TimeEntryCreate):
    pass


@app.post("/api/time_entries/start", response_model=TimeEntryOut, status_code=status.HTTP_201_CREATED)
def api_start_time_entry(payload: TimeEntryCreate):
    started = datetime.now(timezone.utc).isoformat()
    try:
        return models.start_time_entry(payload.project_id, payload.description, started)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/time_entries/{entry_id}/stop", response_model=TimeEntryOut)
def api_stop_time_entry(entry_id: int):
    entry = models.get_time_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Time entry not found")
    if entry["ended_at"] is not None:
        raise HTTPException(status_code=400, detail="Time entry already stopped")
    ended = datetime.now(timezone.utc).isoformat()
    return models.stop_time_entry(entry_id, ended)


@app.post("/api/time_entries/{entry_id}/tags", response_model=TimeEntryOut)
def api_associate_tag(entry_id: int, payload: TagAssociate):
    entry = models.get_time_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Time entry not found")
    try:
        models.associate_tag(entry_id, payload.tag_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return models.get_time_entry(entry_id)


@app.delete("/api/time_entries/{entry_id}/tags/{tag_id}", response_model=TimeEntryOut)
def api_dissociate_tag(entry_id: int, tag_id: int):
    entry = models.get_time_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Time entry not found")
    models.dissociate_tag(entry_id, tag_id)
    return models.get_time_entry(entry_id)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
