import { Routes, Route, NavLink } from 'react-router-dom';
import { useApp } from './context/AppContext';
import Dashboard from './pages/Dashboard';
import TasksPage from './pages/TasksPage';
import StatsPage from './pages/StatsPage';

const navLinks = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/tasks', label: 'Tasks', icon: '📋' },
  { to: '/stats', label: 'Stats & ML', icon: '🧠' },
];

export default function App() {
  const { state } = useApp();

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-xl font-bold text-indigo-400">TaskMaster</h1>
          <p className="text-xs text-gray-500 mt-1">Gamified Task Management</p>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navLinks.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-indigo-500/20 text-indigo-400'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
                }`
              }
            >
              <span>{icon}</span>
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {state.stats && (
          <div className="p-4 border-t border-gray-800 space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Points</span>
              <span className="text-amber-400 font-bold">{state.stats.total_points}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Streak</span>
              <span className="text-orange-400 font-bold">{state.stats.current_streak} days</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Completed</span>
              <span className="text-green-400 font-bold">{state.stats.tasks_completed}</span>
            </div>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col">
        {state.notification && (
          <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-sm font-medium ${
            state.notification.type === 'success'
              ? 'bg-green-500/90 text-white'
              : 'bg-red-500/90 text-white'
          }`}>
            {state.notification.message}
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/stats" element={<StatsPage />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
