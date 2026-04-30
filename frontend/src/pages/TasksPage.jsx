import { useState } from 'react';
import { useApp } from '../context/AppContext';
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';

export default function TasksPage() {
  const { state, actions } = useApp();
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');

  if (state.loading) {
    return <div className="text-gray-500 text-center mt-20">Loading...</div>;
  }

  let filtered = [...state.tasks];
  if (filterStatus !== 'all') {
    filtered = filtered.filter(t => t.status === filterStatus);
  }
  if (filterCategory !== 'all') {
    filtered = filtered.filter(t => t.category_id === Number(filterCategory));
  }

  filtered.sort((a, b) => {
    if (sortBy === 'priority') return b.priority - a.priority;
    if (sortBy === 'due_date') {
      if (!a.due_date) return 1;
      if (!b.due_date) return -1;
      return new Date(a.due_date) - new Date(b.due_date);
    }
    return new Date(b.created_at) - new Date(a.created_at);
  });

  const handleEdit = (task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const handleFormSubmit = async (data) => {
    if (editingTask) {
      await actions.updateTask(editingTask.id, data);
    } else {
      await actions.createTask(data);
    }
    setShowForm(false);
    setEditingTask(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Tasks</h2>
          <p className="text-gray-500 text-sm">{filtered.length} tasks</p>
        </div>
        <button
          onClick={() => { setEditingTask(null); setShowForm(true); }}
          className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          + New Task
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 items-center">
        <select
          value={filterStatus}
          onChange={e => setFilterStatus(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>

        <select
          value={filterCategory}
          onChange={e => setFilterCategory(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300"
        >
          <option value="all">All Categories</option>
          {state.categories.map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        <select
          value={sortBy}
          onChange={e => setSortBy(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300"
        >
          <option value="created_at">Newest First</option>
          <option value="priority">Priority</option>
          <option value="due_date">Due Date</option>
        </select>
      </div>

      {/* Task list */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <p className="text-gray-600 text-center py-10">No tasks found. Create one to get started!</p>
        ) : (
          filtered.map(task => (
            <TaskCard
              key={task.id}
              task={task}
              onComplete={actions.completeTask}
              onEdit={handleEdit}
              onDelete={actions.deleteTask}
            />
          ))
        )}
      </div>

      {/* Task form modal */}
      {showForm && (
        <TaskForm
          task={editingTask}
          categories={state.categories}
          onSubmit={handleFormSubmit}
          onClose={() => { setShowForm(false); setEditingTask(null); }}
        />
      )}
    </div>
  );
}
