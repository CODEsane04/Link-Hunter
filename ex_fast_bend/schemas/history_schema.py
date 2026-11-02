from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

""""    is_valid" : True,
        "rejection_reason" : None,
        "search_query" : generated_sq_object["search_query"],
        "total_results" : len(semantically_filtered_tutorial),
        "final_list" : semantically_filtered_tutorial
        """
class TutorialItem(BaseModel):
    title: str
    link: str
    duration: str
    views: str
    publishedTime: int
    score: float
    cosine_score: float

class store_history_schema(BaseModel):
    email: str
    image_url: str
    search_query: str
    total_results: int
    final_list: List[TutorialItem]  # 👈 Strictly typed list
    created_at: datetime

