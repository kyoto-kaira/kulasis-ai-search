export interface Course {
  id: string;
  code: string;
  title: string;
  department: string;
  instructor: string;
  semester: string;
  enrollment_count: number;
  rating: number;
  difficulty_rating: number;
  content_rating: number;
  reviews: number;
}

export interface SearchParams {
  year: string;
  department: string;
  major: string;
  semester: string;
  days: string[];
  periods: string[];
  course_name: string;
  instructor: string;
  campus: string;
}

export interface TimeSlot {
  day: string;
  period: string;
}
