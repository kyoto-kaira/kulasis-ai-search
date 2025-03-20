from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Course(BaseModel):
    id: str
    code: str
    title: str
    department: str
    instructor: str
    semester: str
    enrollment_count: int
    rating: float
    difficulty_rating: float
    content_rating: float
    reviews: int

# Sample data
courses = [
    {
        "id": "1",
        "code": "金",
        "title": "金融リテラシー（寄附講座）",
        "department": "経済学部",
        "instructor": "藤田康範",
        "semester": "金曜4限",
        "enrollment_count": 726,
        "rating": 4,
        "difficulty_rating": 4,
        "content_rating": 4,
        "reviews": 10
    },
    {
        "id": "2",
        "code": "経",
        "title": "経済政策のミクロ分析a",
        "department": "経済学部",
        "instructor": "藤田浩範",
        "semester": "月曜1限",
        "enrollment_count": 595,
        "rating": 4,
        "difficulty_rating": 4,
        "content_rating": 4,
        "reviews": 5
    },
    {
        "id": "3",
        "code": "代",
        "title": "代謝の基礎生物学",
        "department": "環境情報学部",
        "instructor": "渡辺光博",
        "semester": "水曜4限",
        "enrollment_count": 585,
        "rating": 3,
        "difficulty_rating": 3,
        "content_rating": 3,
        "reviews": 0
    }
]

class SearchParams(BaseModel):
    year: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    semester: Optional[str] = None
    days: Optional[List[str]] = None
    periods: Optional[List[str]] = None
    course_name: Optional[str] = None
    instructor: Optional[str] = None
    campus: Optional[str] = None

@app.get("/api/courses/", response_model=List[Course])
async def get_courses():
    return courses

@app.post("/api/courses/search/", response_model=List[Course])
async def search_courses(params: SearchParams):
    filtered_courses = courses.copy()
    
    if params.course_name:
        filtered_courses = [
            course for course in filtered_courses
            if params.course_name.lower() in course["title"].lower()
        ]
    
    if params.instructor:
        filtered_courses = [
            course for course in filtered_courses
            if params.instructor.lower() in course["instructor"].lower()
        ]
    
    if params.department:
        filtered_courses = [
            course for course in filtered_courses
            if course["department"] == params.department
        ]
    
    if params.days and params.periods:
        filtered_courses = [
            course for course in filtered_courses
            if any(f"{day}曜{period}限" in course["semester"]
                  for day in params.days
                  for period in params.periods)
        ]
    elif params.days:
        filtered_courses = [
            course for course in filtered_courses
            if any(f"{day}曜" in course["semester"] for day in params.days)
        ]
    elif params.periods:
        filtered_courses = [
            course for course in filtered_courses
            if any(f"{period}限" in course["semester"] for period in params.periods)
        ]
    
    return filtered_courses

@app.get("/api/courses/popular/", response_model=List[Course])
async def get_popular_courses():
    # Sort by enrollment count and return top 3
    sorted_courses = sorted(courses, key=lambda x: x["enrollment_count"], reverse=True)
    return sorted_courses[:3]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
