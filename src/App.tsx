import React, { useState, useEffect } from 'react';
import { Search, Star, Users } from 'lucide-react';

interface Course {
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

interface SearchParams {
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

interface TimeSlot {
  day: string;
  period: string;
}

function App() {
  const [year, setYear] = useState('2024');
  const [department, setDepartment] = useState('');
  const [major, setMajor] = useState('');
  const [semester, setSemester] = useState('');
  const [selectedTimeSlots, setSelectedTimeSlots] = useState<TimeSlot[]>([]);
  const [courseName, setCourseName] = useState('');
  const [instructor, setInstructor] = useState('');
  const [campus, setCampus] = useState('');
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const days = ['月', '火', '水', '木', '金'];
  const periods = ['1', '2', '3', '4', '5'];

  useEffect(() => {
    fetchPopularCourses();
  }, []);

  const fetchPopularCourses = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/courses/popular/');
      if (!response.ok) throw new Error('Failed to fetch popular courses');
      const data = await response.json();
      setCourses(data);
    } catch (error) {
      console.error('Error fetching popular courses:', error);
    }
  };

  const isTimeSlotSelected = (day: string, period: string) => {
    return selectedTimeSlots.some(slot => slot.day === day && slot.period === period);
  };

  const handleTimeSlotToggle = (day: string, period: string) => {
    setSelectedTimeSlots(prev => {
      const isSelected = isTimeSlotSelected(day, period);
      if (isSelected) {
        return prev.filter(slot => !(slot.day === day && slot.period === period));
      } else {
        return [...prev, { day, period }];
      }
    });
  };

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      const searchParams: SearchParams = {
        year,
        department,
        major,
        semester,
        days: [...new Set(selectedTimeSlots.map(slot => slot.day))],
        periods: [...new Set(selectedTimeSlots.map(slot => slot.period))],
        course_name: courseName,
        instructor,
        campus,
      };

      const response = await fetch('http://localhost:8000/api/courses/search/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchParams),
      });

      if (!response.ok) throw new Error('Search failed');
      
      const data = await response.json();
      setCourses(data);
    } catch (error) {
      console.error('Error searching courses:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setYear('2024');
    setDepartment('');
    setMajor('');
    setSemester('');
    setSelectedTimeSlots([]);
    setCourseName('');
    setInstructor('');
    setCampus('');
    fetchPopularCourses();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Search className="w-6 h-6 text-emerald-500" />
              <h1 className="text-xl font-bold text-gray-900">京都大学シラバスAI検索</h1>
            </div>
            <p className="text-sm text-gray-600">シラバス検索サイト</p>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h2 className="text-xl font-semibold mb-6">授業を検索</h2>
        <p className="text-gray-600 mb-6">いずれか一つの項目からでも検索が可能です。</p>

        <div className="space-y-6">
          <div className="flex flex-col lg:flex-row gap-6">
            {/* 基本情報の検索ブロック */}
            <div className="bg-white rounded-lg shadow p-6 lg:w-2/3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">基本情報</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">年度</label>
                  <select
                    value={year}
                    onChange={(e) => setYear(e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2"
                  >
                    <option value="2024">2024</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">授業名</label>
                  <input
                    type="text"
                    value={courseName}
                    onChange={(e) => setCourseName(e.target.value)}
                    placeholder="授業名を入力"
                    className="w-full rounded-md border border-gray-300 px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">教員名</label>
                  <input
                    type="text"
                    value={instructor}
                    onChange={(e) => setInstructor(e.target.value)}
                    placeholder="教員名を入力"
                    className="w-full rounded-md border border-gray-300 px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">学部</label>
                  <select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2"
                  >
                    <option value="">学部を選択</option>
                    <option value="経済学部">経済学部</option>
                    <option value="環境情報学部">環境情報学部</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">学科</label>
                  <select
                    value={major}
                    onChange={(e) => setMajor(e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2"
                  >
                    <option value="">学科を選択</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">キャンパス</label>
                  <select
                    value={campus}
                    onChange={(e) => setCampus(e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2"
                  >
                    <option value="">キャンパスを選択</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">学期</label>
                  <select
                    value={semester}
                    onChange={(e) => setSemester(e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2"
                  >
                    <option value="">学期を選択</option>
                  </select>
                </div>
              </div>
            </div>

            {/* 曜日・時限の検索ブロック */}
            <div className="bg-white rounded-lg shadow p-6 lg:w-1/3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">曜日・時限</h3>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr>
                      <th className="p-2"></th>
                      {days.map(day => (
                        <th key={day} className="p-2 text-center text-sm font-medium text-gray-700">
                          {day}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {periods.map(period => (
                      <tr key={period}>
                        <td className="p-2 text-center font-medium text-gray-700">{period}限</td>
                        {days.map(day => (
                          <td key={`${day}-${period}`} className="p-2 text-center">
                            <label className="inline-flex items-center justify-center">
                              <input
                                type="checkbox"
                                checked={isTimeSlotSelected(day, period)}
                                onChange={() => handleTimeSlotToggle(day, period)}
                                className="rounded border-gray-300 text-emerald-500 focus:ring-emerald-500"
                              />
                            </label>
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* 検索ボタン */}
          <div className="flex justify-end space-x-4">
            <button
              onClick={handleReset}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              リセット
            </button>
            <button 
              onClick={handleSearch}
              disabled={isLoading}
              className={`px-4 py-2 bg-emerald-500 text-white rounded-md hover:bg-emerald-600 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? '検索中...' : '検索する'}
            </button>
          </div>
        </div>

        <h2 className="text-xl font-semibold my-8">
          {courses.length > 0 ? '検索結果' : '人気の授業'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {courses.map((course) => (
            <div key={course.id} className="bg-white rounded-lg shadow p-6">
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
          ))}
        </div>
      </main>
    </div>
  );
}

export default App;