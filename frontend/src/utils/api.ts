import { Course, SearchParams } from '../src/types';

const API_BASE_URL = 'http://localhost:8000/api';

export async function fetchPopularCourses(): Promise<Course[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/courses/popular/`);
    if (!response.ok) throw new Error('Failed to fetch popular courses');
    return await response.json();
  } catch (error) {
    console.error('Error fetching popular courses:', error);
    return [];
  }
}

export async function searchCourses(searchParams: SearchParams): Promise<Course[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/courses/search/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchParams),
    });

    if (!response.ok) throw new Error('Search failed');
    return await response.json();
  } catch (error) {
    console.error('Error searching courses:', error);
    return [];
  }
}
