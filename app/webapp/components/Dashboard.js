import React from 'react';

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-800 to-blue-900 flex items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-[1200px] bg-slate-900 rounded-xl shadow-2xl p-4 sm:p-8 border-2 sm:border-4 border-emerald-500">
        <header className="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4">
          <div className="flex items-center gap-4">
            <span className="material-symbols-outlined text-3xl sm:text-4xl text-emerald-400">water_drop</span>
            <h1 className="text-2xl sm:text-3xl font-bold text-emerald-400">Панель Управления DrillFlow</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <button className="flex items-center gap-2 hover:bg-emerald-800 p-2 rounded-lg transition-all">
                <span className="material-symbols-outlined text-emerald-400">notifications</span>
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">3</span>
              </button>
            </div>
            <div className="relative">
              <button className="flex items-center gap-2 hover:bg-emerald-800 p-2 rounded-lg transition-all text-emerald-400">
                <span className="material-symbols-outlined">account_circle</span>
                <span>Администратор</span>
              </button>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
          <div className="bg-emerald-900 p-4 sm:p-6 rounded-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 border-2 border-emerald-500">
            <div className="flex items-center gap-4">
              <span className="material-symbols-outlined text-2xl sm:text-3xl text-emerald-400">engineering</span>
              <div className="text-emerald-400">
                <p className="text-xl sm:text-2xl font-bold">247</p>
                <p className="text-sm sm:text-base">Активных Подрядчиков</p>
              </div>
            </div>
          </div>

          <div className="bg-blue-900 p-4 sm:p-6 rounded-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 border-2 border-emerald-500">
            <div className="flex items-center gap-4">
              <span className="material-symbols-outlined text-2xl sm:text-3xl text-emerald-400">assignment</span>
              <div className="text-emerald-400">
                <p className="text-xl sm:text-2xl font-bold">1,893</p>
                <p className="text-sm sm:text-base">Выполненных Заказов</p>
              </div>
            </div>
          </div>

          <div className="bg-emerald-900 p-4 sm:p-6 rounded-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 border-2 border-emerald-500">
            <div className="flex items-center gap-4">
              <span className="material-symbols-outlined text-2xl sm:text-3xl text-emerald-400">pending</span>
              <div className="text-emerald-400">
                <p className="text-xl sm:text-2xl font-bold">42</p>
                <p className="text-sm sm:text-base">Ожидающих Заказов</p>
              </div>
            </div>
          </div>

          <div className="bg-blue-900 p-4 sm:p-6 rounded-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 border-2 border-emerald-500">
            <div className="flex items-center gap-4">
              <span className="material-symbols-outlined text-2xl sm:text-3xl text-emerald-400">stars</span>
              <div className="text-emerald-400">
                <p className="text-xl sm:text-2xl font-bold">4.8</p>
                <p className="text-sm sm:text-base">Средний Рейтинг</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
          <div className="lg:col-span-2 bg-slate-800 rounded-xl border-2 sm:border-4 border-emerald-500 p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold mb-4 text-emerald-400">Последние Заказы</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-2 sm:p-4 hover:bg-slate-700 rounded-lg transition-all">
                <div className="flex items-center gap-4">
                  <span className="material-symbols-outlined text-emerald-400">drill</span>
                  <div className="text-emerald-400">
                    <p className="font-semibold">Бурение Скважины</p>
                    <p className="text-xs sm:text-sm text-emerald-300">ул. Главная 123, Город</p>
                  </div>
                </div>
                <button className="bg-emerald-600 text-white px-3 py-1 sm:px-4 sm:py-2 rounded-lg hover:bg-emerald-700 transition-all transform hover:scale-105 border-2 border-emerald-400 text-sm sm:text-base">
                  Назначить
                </button>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl border-2 sm:border-4 border-emerald-500 p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold mb-4 text-emerald-400">Лучшие Подрядчики</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-2 hover:bg-slate-700 rounded-lg transition-all">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-emerald-400">account_circle</span>
                  <p className="font-semibold text-emerald-400 text-sm sm:text-base">Иван Иванов</p>
                </div>
                <div className="flex items-center text-emerald-400">
                  <span className="material-symbols-outlined text-yellow-500">star</span>
                  <span className="text-sm sm:text-base">4.9</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;