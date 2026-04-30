export default function BadgeDisplay({ badges, showAll = false }) {
  const displayed = showAll ? badges : badges.filter(b => b.earned);

  if (displayed.length === 0 && !showAll) {
    return <p className="text-gray-600 text-sm">No badges earned yet. Complete tasks to earn badges!</p>;
  }

  return (
    <div className="flex flex-wrap gap-3">
      {(showAll ? badges : displayed).map(badge => (
        <div
          key={badge.id}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm transition-all ${
            badge.earned
              ? 'bg-indigo-500/10 border-indigo-500/30 text-indigo-300'
              : 'bg-gray-800/50 border-gray-800 text-gray-600'
          }`}
          title={badge.description}
        >
          <span className={`text-lg ${badge.earned ? '' : 'grayscale opacity-40'}`}>{badge.icon}</span>
          <div>
            <div className="font-medium text-xs">{badge.name}</div>
            <div className="text-xs opacity-60">{badge.description}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
