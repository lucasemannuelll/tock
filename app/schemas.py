from pydantic import BaseModel, Field
from typing import Optional


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
    project_id: Optional[int] = None
    description: str = Field(..., min_length=1)
    started_at: Optional[str] = None
    ended_at: Optional[str] = None


class TimeEntryUpdate(BaseModel):
    project_id: Optional[int]
    description: str = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None


class TimeEntryOut(BaseModel):
    id: int
    project_id: Optional[int]
    description: str
    started_at: str
    ended_at: Optional[str]
    tags: list[TagOut] = []


class TagAssociate(BaseModel):
    tag_id: int
