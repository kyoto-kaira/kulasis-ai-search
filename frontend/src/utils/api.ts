import { Course, SearchParams } from '../types';

// Define your base URL. You can also get it from an environment variable if needed.
const BASE_URL = 'http://localhost:8000';

/**
 * バックエンドAPIから授業を検索する
 */
export async function searchCourses(params: SearchParams): Promise<Course[]> {
  try {
    const response = await fetch(`${BASE_URL}/invocations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    
    if (!response.ok) {
      throw new Error('検索リクエストが失敗しました');
    }
    
    return await response.json();
  } catch (error) {
    console.error('授業の検索中にエラーが発生しました:', error);
    throw error;
  }
}
