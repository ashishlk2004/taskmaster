import { useApp } from '../context/AppContext';
import BadgeDisplay from '../components/BadgeDisplay';
import TaskCard from '../components/TaskCard';

const PRIORITY_LABELS = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' };

export default function Dashboard() {
  const { state, actions } = useApp();
  const { tasks, stats, badges } = state;

  if (state.loading) {
    return <div className="text-gray-500 text-center mt-20">Loading...</div>;
  }

  const pendingTasks = tasks.filter(t => t.status !== 'completed');
  const recentCompleted = tasks
    .filter(t => t.status === 'completed')
    .slice(0, 5);

  const urgentTasks = pendingTasks
    .filter(t => t.priority >= 3)
    .sort((a, b) => b.priority - a.priority)
    .slice(0, 5);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-1">Dashboard</h2>
        <p className="text-gray-500 text-sm">Your task overview at a glance</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Points" value={stats?.total_points || 0} color="text-amber-400" bg="bg-amber-500/10" />
        <StatCard label="Current Streak" value={`${stats?.current_streak || 0}d`} color="text-orange-400" bg="bg-orange-500/10" />
        <StatCard label="Tasks Pending" value={pendingTasks.length} color="text-blue-400" bg="bg-blue-500/10" />
        <StatCard label="Completed" value={stats?.tasks_completed || 0} color="text-green-400" bg="bg-green-500/10" />
      </div>

      {/* Badges */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Badges</h3>
        <BadgeDisplay badges={badges} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Urgent tasks */}
        <div>
          <h3 className="text-lg font-semibold mb-3">High Priority Tasks</h3>
          {urgentTasks.length === 0 ? (
            <p className="text-gray-600 text-sm">No urgent tasks. Nice!</p>
          ) : (
            <div className="space-y-2">
              {urgentTasks.map(task => (
                <TaskCard key={task.id} task={task} onComplete={actions.completeTask} compact />
              ))}
            </div>
          )}
        </div>

        {/* Recent completions */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Recently Completed</h3>
          {recentCompleted.length === 0 ? (
            <p className="text-gray-600 text-sm">No completed tasks yet.</p>
          ) : (
            <div className="space-y-2">
              {recentCompleted.map(task => (
                <div key={task.id} className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg border border-gray-800">
                  <span className="text-green-500">&#10003;</span>
                  <span className="text-sm text-gray-400 line-through">{task.title}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color, bg }) {
  return (
    <div className={`${bg} rounded-xl p-5 border border-gray-800`}>
      <p className="text-gray-500 text-xs mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
