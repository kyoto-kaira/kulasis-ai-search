import { Star, Users } from 'lucide-react';
import React from 'react';
import { Course } from '../types';

interface CourseCardProps {
  course: Course;
}

const CourseCard: React.FC<CourseCardProps> = ({ course }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <span className="inline-block bg-gray-100 rounded px-2 py-1 text-lg font-bold mb-2">
            {course.code}
          </span>
          <h3 className="text-lg font-semibold">{course.title}</h3>
          <p className="text-gray-600">{course.department}</p>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center text-sm text-gray-600">
          <Users className="w-4 h-4 mr-2" />
          <span>履修者数：{course.enrollment_count}人</span>
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <span className="mr-2">{course.semester}</span>
          <span className="mr-2">{course.instructor}</span>
          <Star className="w-4 h-4 mr-1 text-yellow-400" />
          <span>{course.reviews}件</span>
        </div>
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span>内容充実度</span>
            <div className="flex">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < course.content_rating ? 'text-yellow-400' : 'text-gray-200'
                  }`}
                />
              ))}
            </div>
          </div>
          <div className="flex justify-between text-sm">
            <span>単位取得度</span>
            <div className="flex">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < course.difficulty_rating ? 'text-yellow-400' : 'text-gray-200'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseCard;
