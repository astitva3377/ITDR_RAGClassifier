import React from 'react';

export default function D3fendRoadmap({ defenses }) {
  return (
    <div className="bg-[#111726] border border-[#1f293d] rounded-xl p-5 shadow-xl">
      <h2 className="text-lg font-bold text-teal-400 mb-4 flex items-center gap-2">
        <span>🛡️</span> MITRE D3FEND Countermeasures
      </h2>
      <div className="space-y-3">
        {defenses.map((item, idx) => (
          <div key={idx} className="bg-[#0a0d14] border border-[#1f293d] rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <span className="font-mono text-xs px-2 py-0.5 rounded bg-teal-950 text-teal-400 border border-teal-800">
                  {item.id}
                </span>
                <span className="ml-2 font-semibold text-slate-200">{item.name}</span>
              </div>
              <span className="text-xs text-slate-400">Counters: {item.counters_attack}</span>
            </div>
            {item.rationale && (
              <p className="mt-2 text-xs text-slate-300">
                {item.rationale}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
