import { useState, useEffect } from 'react';
import { taskApi } from '../api/client';

const PRIORITY_CONFIG = {
  1: { label: 'Low', color: 'bg-gray-600', text: 'text-gray-400' },
  2: { label: 'Medium', color: 'bg-blue-600', text: 'text-blue-400' },
  3: { label: 'High', color: 'bg-orange-600', text: 'text-orange-400' },
  4: { label: 'Urgent', color: 'bg-red-600', text: 'text-red-400' },
};

const STATUS_CONFIG = {
  pending: { label: 'Pending', color: 'text-gray-400' },
  in_progress: { label: 'In Progress', color: 'text-blue-400' },
  completed: { label: 'Completed', color: 'text-green-400' },
};

export default function TaskCard({ task, onComplete, onEdit, onDelete, compact = false }) {
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    if (task.status !== 'completed') {
      taskApi.predict(task.id).then(setPrediction).catch(() => {});
    }
  }, [task.id, task.status]);

  const priority = PRIORITY_CONFIG[task.priority] || PRIORITY_CONFIG[2];
  const status = STATUS_CONFIG[task.status] || STATUS_CONFIG.pending;
  const isCompleted = task.status === 'completed';

  const isOverdue = task.due_date && !isCompleted && new Date(task.due_date) < new Date();

  if (compact) {
    return (
      <div className="flex items-center gap-3 p-3 bg-gray-900 rounded-lg border border-gray-800 group">
        <button
          onClick={() => onComplete(task.id)}
          className="w-5 h-5 rounded-full border-2 border-gray-600 hover:border-green-500 hover:bg-green-500/20 transition-colors flex-shrink-0"
        />
        <span className="text-sm flex-1 truncate">{task.title}</span>
        <span className={`text-xs px-2 py-0.5 rounded-full ${priority.color} text-white`}>
          {priority.label}
        </span>
        {prediction && <PredictionBadge probability={prediction.completion_probability} />}
      </div>
    );
  }

  return (
    <div className={`bg-gray-900 rounded-xl border ${isOverdue ? 'border-red-500/50' : 'border-gray-800'} p-4 group transition-colors hover:border-gray-700`}>
      <div className="flex items-start gap-3">
        {!isCompleted && (
          <button
            onClick={() => onComplete(task.id)}
            className="w-5 h-5 mt-0.5 rounded-full border-2 border-gray-600 hover:border-green-500 hover:bg-green-500/20 transition-colors flex-shrink-0"
            title="Complete task"
          />
        )}
        {isCompleted && (
          <div className="w-5 h-5 mt-0.5 rounded-full bg-green-500/20 border-2 border-green-500 flex items-center justify-center flex-shrink-0">
            <span className="text-green-500 text-xs">&#10003;</span>
          </div>
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className={`text-sm font-medium ${isCompleted ? 'line-through text-gray-500' : ''}`}>
              {task.title}
            </h4>
            <span className={`text-xs px-2 py-0.5 rounded-full ${priority.color} text-white`}>
              {priority.label}
            </span>
            <span className={`text-xs ${status.color}`}>{status.label}</span>
            {prediction && <PredictionBadge probability={prediction.completion_probability} method={prediction.method} />}
          </div>

          {task.description && (
            <p className="text-xs text-gray-500 mb-2 truncate">{task.description}</p>
          )}

          <div className="flex items-center gap-4 text-xs text-gray-600">
            {task.category && (
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: task.category.color }} />
                {task.category.name}
              </span>
            )}
            {task.due_date && (
              <span className={isOverdue ? 'text-red-400' : ''}>
                Due: {new Date(task.due_date).toLocaleDateString()}
              </span>
            )}
            {task.estimated_minutes && (
              <span>{task.estimated_minutes}m est.</span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {onEdit && !isCompleted && (
            <button
              onClick={() => onEdit(task)}
              className="text-gray-500 hover:text-gray-300 p-1 text-xs"
              title="Edit"
            >
              Edit
            </button>
          )}
          {onDelete && (
            <button
              onClick={() => onDelete(task.id)}
              className="text-gray-500 hover:text-red-400 p-1 text-xs"
              title="Delete"
            >
              Del
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function PredictionBadge({ probability, method }) {
  const pct = Math.round(probability * 100);
  let color, bg;
  if (pct >= 70) {
    color = 'text-green-400';
    bg = 'bg-green-500/10';
  } else if (pct >= 40) {
    color = 'text-yellow-400';
    bg = 'bg-yellow-500/10';
  } else {
    color = 'text-red-400';
    bg = 'bg-red-500/10';
  }

  return (
    <span className={`text-xs px-1.5 py-0.5 rounded ${bg} ${color}`} title={`${method === 'model' ? 'ML' : 'Heuristic'} prediction`}>
      {pct}%
    </span>
  );
}
