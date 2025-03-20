export interface Course {
  id: string;
  name: string;
  instructor: string;
  department: string;
  schedule: {
    day: string;
    period: string;
  }[];
  semester: string;
  class_type?: string;
  language?: string;
  level?: string;
  academic_field?: string;
  description?: string;
  credits?: number;
  url?: string;
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
  class_type?: string;
  language?: string;
  level?: string;
  academic_field?: string;
  query?: string;
}

export interface TimeSlot {
  day: string;
  period: string;
}
