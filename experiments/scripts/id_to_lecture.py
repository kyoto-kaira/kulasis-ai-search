import json

PATH_TO_COURSES = "data/courses.json"

with open(PATH_TO_COURSES, mode="r", encoding="utf-8") as f:
    courses = json.load(f)

id_to_lecture = {}

for department, sections in courses.items():
    for section, classes in sections.items():
        for class_ in classes:
            id_to_lecture[class_["lecture_no"]] = {
                "lecture_name": class_["lecture_name"],
                "url": class_["url"],
                "department": department,
                "section": section,
            }

with open("data/id_to_lecture.json", mode="w", encoding="utf-8") as f:
    json.dump(id_to_lecture, f, ensure_ascii=False, indent=4)
