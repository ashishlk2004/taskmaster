import { createContext, useContext, useReducer, useEffect } from 'react';
import { taskApi, categoryApi, statsApi, badgeApi } from '../api/client';

const AppContext = createContext();

const initialState = {
  tasks: [],
  categories: [],
  stats: null,
  badges: [],
  loading: true,
  notification: null,
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_TASKS':
      return { ...state, tasks: action.payload };
    case 'SET_CATEGORIES':
      return { ...state, categories: action.payload };
    case 'SET_STATS':
      return { ...state, stats: action.payload };
    case 'SET_BADGES':
      return { ...state, badges: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_NOTIFICATION':
      return { ...state, notification: action.payload };
    case 'CLEAR_NOTIFICATION':
      return { ...state, notification: null };
    default:
      return state;
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const fetchAll = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const [tasks, categories, stats, badges] = await Promise.all([
        taskApi.list(),
        categoryApi.list(),
        statsApi.get(),
        badgeApi.list(),
      ]);
      dispatch({ type: 'SET_TASKS', payload: tasks });
      dispatch({ type: 'SET_CATEGORIES', payload: categories });
      dispatch({ type: 'SET_STATS', payload: stats });
      dispatch({ type: 'SET_BADGES', payload: badges });
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
    dispatch({ type: 'SET_LOADING', payload: false });
  };

  useEffect(() => { fetchAll(); }, []);

  const notify = (message, type = 'success') => {
    dispatch({ type: 'SET_NOTIFICATION', payload: { message, type } });
    setTimeout(() => dispatch({ type: 'CLEAR_NOTIFICATION' }), 3000);
  };

  const actions = {
    fetchAll,
    createTask: async (data) => {
      const task = await taskApi.create(data);
      await fetchAll();
      notify('Task created!');
      return task;
    },
    updateTask: async (id, data) => {
      const task = await taskApi.update(id, data);
      await fetchAll();
      return task;
    },
    deleteTask: async (id) => {
      await taskApi.delete(id);
      await fetchAll();
      notify('Task deleted');
    },
    completeTask: async (id) => {
      const result = await taskApi.complete(id);
      await fetchAll();
      let msg = `+${result.points_earned} points!`;
      if (result.new_badges.length > 0) {
        msg += ` Badge earned: ${result.new_badges.map(b => `${b.icon} ${b.name}`).join(', ')}`;
      }
      notify(msg);
      return result;
    },
    createCategory: async (data) => {
      const cat = await categoryApi.create(data);
      await fetchAll();
      notify('Category created!');
      return cat;
    },
    deleteCategory: async (id) => {
      await categoryApi.delete(id);
      await fetchAll();
      notify('Category deleted');
    },
  };

  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  return useContext(AppContext);
}
