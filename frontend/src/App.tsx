import React, { useState } from 'react';
import CourseList from './components/CourseList';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import { Course, SearchParams } from './types';
import { searchCourses } from './utils/api';

function App() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSearchResults, setIsSearchResults] = useState(false);

  const handleSearch = async (searchParams: SearchParams) => {
    setIsLoading(true);
    try {
      const data = await searchCourses(searchParams);
      console.log(data);
      setCourses(data);
      setIsSearchResults(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setCourses([]);
    setIsSearchResults(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <SearchForm 
          onSearch={handleSearch} 
          onReset={handleReset} 
          isLoading={isLoading} 
        />
        <CourseList 
          courses={courses} 
          isSearchResults={isSearchResults} 
        />
      </main>
    </div>
  );
}

export default App;