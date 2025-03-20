import React from 'react';
import { Course } from '../types';
import CourseCard from './CourseCard';

interface CourseListProps {
  courses: Course[];
  isSearchResults: boolean;
}

const CourseList: React.FC<CourseListProps> = ({ courses, isSearchResults }) => {
  return (
    <>
      <h2 className="text-xl font-semibold my-8">
        検索結果
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {courses.map((course) => (
          <CourseCard key={course.id} course={course} />
        ))}
      </div>
    </>
  );
};

export default CourseList;
