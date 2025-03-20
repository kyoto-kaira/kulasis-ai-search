import { Search } from 'lucide-react';
import React from 'react';

const Header: React.FC = () => {
  return (
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
  );
};

export default Header;
