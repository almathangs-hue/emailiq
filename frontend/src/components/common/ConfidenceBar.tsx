function color(score: number) {
  if (score >= 70) return "bg-green-500";
  if (score >= 50) return "bg-yellow-400";
  return "bg-red-400";
}

export default function ConfidenceBar({ score }: { score: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color(score)}`}
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>
      <span className="text-xs text-gray-500">{score}</span>
    </div>
  );
}
