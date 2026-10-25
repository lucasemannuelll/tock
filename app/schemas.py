
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1)


class ProjectOut(BaseModel):
    id: int
    name: str


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1)


class TagOut(BaseModel):
    id: int
    name: str


class TimeEntryCreate(BaseModel):
    project_id: int | None = None
    description: str = Field(..., min_length=1)
    started_at: str | None = None
    ended_at: str | None = None


class TimeEntryUpdate(BaseModel):
    project_id: int | None
    description: str = None
    started_at: str | None = None
    ended_at: str | None = None


class TimeEntryOut(BaseModel):
    id: int
    project_id: int | None
    description: str
    started_at: str
    ended_at: str | None
    tags: list[TagOut] = []


class TagAssociate(BaseModel):
    tag_id: int
