import React from 'react';

export default function AttackMatrixView({ attacks }) {
  return (
    <div className="bg-[#111726] border border-[#1f293d] rounded-xl p-5 shadow-xl">
      <h2 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
        <span>⚔️</span> Identified MITRE ATT&CK TTPs
      </h2>
      <div className="space-y-3">
        {attacks.map((item, idx) => (
          <div key={idx} className="bg-[#0a0d14] border border-[#1f293d] rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <span className="font-mono text-xs px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800">
                  {item.id}
                </span>
                <span className="ml-2 font-semibold text-slate-200">{item.name}</span>
              </div>
              <span className="text-xs text-slate-400">{item.tactic}</span>
            </div>
            {item.evidence && (
              <p className="mt-2 text-xs text-slate-400 italic bg-[#111726] p-2 rounded border border-slate-800">
                "{item.evidence}"
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
