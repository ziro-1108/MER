from datetime import datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: int
    request_number: str
    sample_number: str
    combined_key: str
    status: str
    image_count: int
    has_xlsx: bool
    pptx_download_url: str | None
    xlsx_download_url: str | None
    created_at: datetime

    class Config:
        from_attributes = True
