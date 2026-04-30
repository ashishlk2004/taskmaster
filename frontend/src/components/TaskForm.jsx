import { useState } from 'react';

export default function TaskForm({ task, categories, onSubmit, onClose }) {
  const [form, setForm] = useState({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || 2,
    category_id: task?.category_id || '',
    due_date: task?.due_date ? task.due_date.slice(0, 16) : '',
    estimated_minutes: task?.estimated_minutes || '',
    status: task?.status || 'pending',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      ...form,
      category_id: form.category_id ? Number(form.category_id) : null,
      due_date: form.due_date || null,
      estimated_minutes: form.estimated_minutes ? Number(form.estimated_minutes) : null,
      priority: Number(form.priority),
    };
    onSubmit(data);
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-gray-900 rounded-xl border border-gray-700 p-6 w-full max-w-lg" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-semibold mb-4">{task ? 'Edit Task' : 'New Task'}</h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Title</label>
            <input
              type="text"
              required
              value={form.title}
              onChange={e => setForm({ ...form, title: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-indigo-500"
              placeholder="What needs to be done?"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">Description</label>
            <textarea
              value={form.description}
              onChange={e => setForm({ ...form, description: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-indigo-500 h-20 resize-none"
              placeholder="Add details..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Priority</label>
              <select
                value={form.priority}
                onChange={e => setForm({ ...form, priority: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200"
              >
                <option value={1}>Low</option>
                <option value={2}>Medium</option>
                <option value={3}>High</option>
                <option value={4}>Urgent</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Category</label>
              <select
                value={form.category_id}
                onChange={e => setForm({ ...form, category_id: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200"
              >
                <option value="">None</option>
                {categories.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Due Date</label>
              <input
                type="datetime-local"
                value={form.due_date}
                onChange={e => setForm({ ...form, due_date: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">Estimated Time (min)</label>
              <input
                type="number"
                value={form.estimated_minutes}
                onChange={e => setForm({ ...form, estimated_minutes: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200"
                placeholder="e.g. 30"
                min="1"
              />
            </div>
          </div>

          {task && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">Status</label>
              <select
                value={form.status}
                onChange={e => setForm({ ...form, status: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200"
              >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
              </select>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              {task ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
