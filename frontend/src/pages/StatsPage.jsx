import { useState, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { mlApi } from '../api/client';
import BadgeDisplay from '../components/BadgeDisplay';

export default function StatsPage() {
  const { state } = useApp();
  const [mlStatus, setMlStatus] = useState(null);
  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState(null);

  useEffect(() => {
    mlApi.status().then(setMlStatus).catch(() => {});
  }, []);

  const handleTrain = async () => {
    setTraining(true);
    setTrainResult(null);
    try {
      const result = await mlApi.train();
      setTrainResult(result);
      setMlStatus(result);
    } catch (err) {
      setTrainResult({ error: 'Training failed' });
    }
    setTraining(false);
  };

  if (state.loading) {
    return <div className="text-gray-500 text-center mt-20">Loading...</div>;
  }

  const { stats, tasks, badges, categories } = state;
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const completionRate = totalTasks > 0 ? ((completedTasks / totalTasks) * 100).toFixed(1) : 0;

  // Category breakdown
  const catStats = categories.map(cat => {
    const catTasks = tasks.filter(t => t.category_id === cat.id);
    const catCompleted = catTasks.filter(t => t.status === 'completed').length;
    return {
      name: cat.name,
      color: cat.color,
      total: catTasks.length,
      completed: catCompleted,
      rate: catTasks.length > 0 ? ((catCompleted / catTasks.length) * 100).toFixed(0) : 0,
    };
  });

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-1">Stats & ML Predictions</h2>
        <p className="text-gray-500 text-sm">Your performance analytics and AI insights</p>
      </div>

      {/* Overview stats */}
      <div className="grid grid-cols-5 gap-4">
        <StatBox label="Total Points" value={stats?.total_points || 0} color="text-amber-400" />
        <StatBox label="Current Streak" value={`${stats?.current_streak || 0}d`} color="text-orange-400" />
        <StatBox label="Best Streak" value={`${stats?.longest_streak || 0}d`} color="text-red-400" />
        <StatBox label="Completion Rate" value={`${completionRate}%`} color="text-green-400" />
        <StatBox label="Total Tasks" value={totalTasks} color="text-blue-400" />
      </div>

      {/* Category breakdown */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Category Breakdown</h3>
        <div className="grid grid-cols-5 gap-4">
          {catStats.map(cat => (
            <div key={cat.name} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }} />
                <span className="text-sm font-medium">{cat.name}</span>
              </div>
              <div className="text-2xl font-bold text-gray-200">{cat.completed}/{cat.total}</div>
              <div className="mt-2 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{ width: `${cat.rate}%`, backgroundColor: cat.color }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">{cat.rate}% complete</p>
            </div>
          ))}
        </div>
      </div>

      {/* Badges */}
      <div>
        <h3 className="text-lg font-semibold mb-3">All Badges</h3>
        <BadgeDisplay badges={badges} showAll />
      </div>

      {/* ML Section */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <h3 className="text-lg font-semibold mb-4">ML Completion Predictor</h3>
        <p className="text-gray-400 text-sm mb-4">
          Train a machine learning model on your task history to predict the likelihood of completing future tasks.
          The model uses features like priority, due date, category, time of day, and your current streak.
        </p>

        <div className="flex items-center gap-4 mb-4">
          <button
            onClick={handleTrain}
            disabled={training}
            className="bg-purple-500 hover:bg-purple-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            {training ? 'Training...' : 'Train Model'}
          </button>

          {mlStatus && mlStatus.trained && (
            <div className="flex items-center gap-4 text-sm">
              <span className="text-gray-400">
                Accuracy: <span className="text-green-400 font-bold">{(mlStatus.accuracy * 100).toFixed(1)}%</span>
              </span>
              <span className="text-gray-400">
                Samples: <span className="text-blue-400 font-bold">{mlStatus.sample_count}</span>
              </span>
              <span className="text-gray-400">
                Trained: <span className="text-gray-300">{new Date(mlStatus.trained_at).toLocaleDateString()}</span>
              </span>
            </div>
          )}
        </div>

        {trainResult && !trainResult.trained && trainResult.error && (
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 text-sm text-yellow-400">
            {trainResult.error}
          </div>
        )}

        {trainResult && trainResult.trained && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 text-sm text-green-400">
            Model trained successfully! Accuracy: {(trainResult.accuracy * 100).toFixed(1)}% on {trainResult.sample_count} samples.
            Predictions are now available on task cards.
          </div>
        )}

        {!mlStatus?.trained && !trainResult && (
          <div className="bg-gray-800 rounded-lg p-3 text-sm text-gray-500">
            No model trained yet. You need at least 20 completed or overdue tasks to train the model.
            Until then, predictions use a heuristic estimate.
          </div>
        )}
      </div>
    </div>
  );
}

function StatBox({ label, value, color }) {
  return (
    <div className="bg-gray-900 rounded-xl p-4 border border-gray-800 text-center">
      <p className="text-gray-500 text-xs mb-1">{label}</p>
      <p className={`text-xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
