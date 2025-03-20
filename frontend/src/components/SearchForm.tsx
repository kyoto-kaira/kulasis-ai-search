import React, { useState } from 'react';
import {
  ACADEMIC_FIELDS,
  CLASS_TYPES,
  DEPARTMENTS,
  EMPTY_OPTION,
  LANGUAGES,
  LEVELS,
  MAJORS_BY_DEPARTMENT,
  SEMESTERS
} from '../constants';
import { SearchParams, TimeSlot } from '../types';

interface SearchFormProps {
  onSearch: (params: SearchParams) => void;
  onReset: () => void;
  isLoading: boolean;
}

const SearchForm: React.FC<SearchFormProps> = ({ onSearch, onReset, isLoading }) => {
  const [year, setYear] = useState('2024');
  const [department, setDepartment] = useState('');
  const [major, setMajor] = useState('');
  const [semester, setSemester] = useState('');
  const [selectedTimeSlots, setSelectedTimeSlots] = useState<TimeSlot[]>([]);
  const [courseName, setCourseName] = useState('');
  const [instructor, setInstructor] = useState('');
  const [classType, setClassType] = useState('');
  const [language, setLanguage] = useState('');
  const [level, setLevel] = useState('');
  const [academicField, setAcademicField] = useState('');
  const [availableMajors, setAvailableMajors] = useState<string[]>([]);
  const [query, setQuery] = useState('');

  const days = ['月', '火', '水', '木', '金'];
  const periods = ['1', '2', '3', '4', '5'];

  // 学部が変更されたときに学科リストを更新
  React.useEffect(() => {
    if (department && MAJORS_BY_DEPARTMENT[department]) {
      setAvailableMajors(MAJORS_BY_DEPARTMENT[department]);
    } else {
      setAvailableMajors([]);
    }
    setMajor(''); // 学部が変更されたら学科をリセット
  }, [department]);

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

  const handleSearch = () => {
    const searchParams: SearchParams = {
      year,
      department,
      major,
      semester,
      days: [...new Set(selectedTimeSlots.map(slot => slot.day))],
      periods: [...new Set(selectedTimeSlots.map(slot => slot.period))],
      course_name: courseName,
      instructor,
      class_type: classType,
      language,
      level,
      academic_field: academicField,
      query,
    };
    onSearch(searchParams);
  };

  const handleReset = () => {
    setYear('2024');
    setDepartment('');
    setMajor('');
    setSemester('');
    setSelectedTimeSlots([]);
    setCourseName('');
    setInstructor('');
    setClassType('');
    setLanguage('');
    setLevel('');
    setAcademicField('');
    setQuery('');
    onReset();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold mb-6">授業を検索</h2>
      <p className="text-gray-600 mb-6">いずれか一つの項目からでも検索が可能です。</p>
      
      {/* 自由検索フィールド */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">自由検索</h3>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-grow">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="キーワードを入力（例：プログラミング、経済学、実験）"
              className="w-full rounded-md border border-gray-300 px-3 py-2"
            />
          </div>
        </div>
      </div>

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
                <option value="">{EMPTY_OPTION}</option>
                {DEPARTMENTS.map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">学科</label>
              <select
                value={major}
                onChange={(e) => setMajor(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2"
                disabled={availableMajors.length === 0}
              >
                <option value="">{EMPTY_OPTION}</option>
                {availableMajors.map(maj => (
                  <option key={maj} value={maj}>{maj}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">学期</label>
              <select
                value={semester}
                onChange={(e) => setSemester(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2"
              >
                <option value="">{EMPTY_OPTION}</option>
                {SEMESTERS.map(sem => (
                  <option key={sem} value={sem}>{sem}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">授業形態</label>
              <select
                value={classType}
                onChange={(e) => setClassType(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2"
              >
                <option value="">{EMPTY_OPTION}</option>
                {CLASS_TYPES.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">使用言語</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2"
              >
                <option value="">{EMPTY_OPTION}</option>
                {LANGUAGES.map(lang => (
                  <option key={lang} value={lang}>{lang}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">レベル</label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2"
              >
                <option value="">{EMPTY_OPTION}</option>
                {LEVELS.map(lvl => (
                  <option key={lvl} value={lvl}>{lvl}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">学問分野</label>
              <select
                value={academicField}
                onChange={(e) => setAcademicField(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2"
              >
                <option value="">{EMPTY_OPTION}</option>
                {ACADEMIC_FIELDS.map(field => (
                  <option key={field} value={field}>{field}</option>
                ))}
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
  );
};

export default SearchForm;
