from pydantic import BaseModel, Field
from typing import Literal


class Metadata(BaseModel):
    subject: str
    category: str
    attributes: list[str]
    caption: str
    confidence: float = Field(ge=0.0, le=1.0)


class ImageCreate(Metadata):
    file_path: str


class ImageOut(ImageCreate):
    id: int


class PostCreate(BaseModel):
    subject: str
    title: str
    body: str


class PostOut(PostCreate):
    id: int


class ReviewCreate(BaseModel):
    decision: Literal["approved", "rejected"]


class ReviewOut(ReviewCreate):
    id: int
    suggestion_id: int


class SuggestionOut(BaseModel):
    id: int
    post_id: int
    image_id: int
    simularity_score: float
    guard_passed: bool
    rejection_reason: str | None
