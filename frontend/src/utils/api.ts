import { Course, SearchParams } from '../types';

const API_BASE_URL = 'http://localhost:8000';

export async function searchCourses(searchParams: SearchParams): Promise<Course[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/invocations/`, {
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
