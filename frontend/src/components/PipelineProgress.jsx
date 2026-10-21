import React from 'react';

export default function PipelineProgress() {
  return (
    <div className="bg-[#111726] border border-[#1f293d] rounded-xl p-4 flex items-center gap-4 animate-pulse">
      <div className="w-5 h-5 border-2 border-teal-400 border-t-transparent rounded-full animate-spin"></div>
      <p className="text-sm text-slate-300">
        Traversing LangGraph pipeline: Ingesting text &rarr; Vector Search &rarr; Neo4j D3FEND Traversal...
      </p>
    </div>
  );
}
