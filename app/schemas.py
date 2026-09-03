from pydantic import BaseModel, Field

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