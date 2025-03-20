import { SearchParams } from '../types';

/**
 * バックエンドAPIから授業データを検索する
 */
export async function searchCourses(params: SearchParams) {
  try {
    const response = await fetch('/api/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    
    if (!response.ok) {
      throw new Error('Search request failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error searching courses:', error);
    throw error;
  }
}
