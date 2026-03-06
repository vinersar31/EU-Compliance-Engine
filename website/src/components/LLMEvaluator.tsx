"use client";

import React, { useState } from 'react';
import { Bot, AlertTriangle, ShieldCheck, Info } from 'lucide-react';

export default function LLMEvaluator() {
  const [description, setDescription] = useState('');
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleEvaluate = async () => {
    if (!description.trim()) return;

    setIsEvaluating(true);
    setResult(null);

    try {
      // Determine the API URL. For GitHub pages, it must point to an external Python server.
      // Defaulting to a local server for development if NEXT_PUBLIC_API_URL isn't set.
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/evaluate';

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      if (data.error && !data.risk_level) {
         setResult({
            riskLevel: 'Error',
            color: 'text-red-600',
            bgColor: 'bg-red-50',
            icon: <AlertTriangle className="w-6 h-6 text-red-600" />,
            flags: ['ERROR'],
            summary: data.error,
            obligations: []
         });
         return;
      }

      // Map backend response to UI format
      let color = 'text-gray-600';
      let bgColor = 'bg-gray-50';
      let icon = <Info className="w-6 h-6 text-gray-600" />;
      let flags: string[] = [];

      const riskLower = (data.risk_level || '').toLowerCase();

      if (riskLower.includes('minimal')) {
        color = 'text-green-600';
        bgColor = 'bg-green-50';
        icon = <ShieldCheck className="w-6 h-6 text-green-600" />;
        flags = ['FLAG GREEN'];
      } else if (riskLower.includes('unacceptable') || riskLower.includes('prohibited')) {
        color = 'text-red-600';
        bgColor = 'bg-red-50';
        icon = <AlertTriangle className="w-6 h-6 text-red-600" />;
        flags = ['FLAG RED'];
      } else if (riskLower.includes('high')) {
        color = 'text-yellow-600';
        bgColor = 'bg-yellow-50';
        icon = <AlertTriangle className="w-6 h-6 text-yellow-600" />;
        flags = ['FLAG YELLOW'];
      } else if (riskLower.includes('transparency')) {
        color = 'text-blue-600';
        bgColor = 'bg-blue-50';
        icon = <Info className="w-6 h-6 text-blue-600" />;
        flags = ['FLAG BLUE'];
      }

      setResult({
        riskLevel: data.risk_level,
        color,
        bgColor,
        icon,
        flags,
        summary: data.reasoning,
        obligations: [
          ...(data.suggested_categories ? ['Categories: ' + data.suggested_categories.join(', ')] : []),
          ...(data.suggested_features ? ['Features: ' + data.suggested_features.join(', ')] : [])
        ].filter(Boolean)
      });

    } catch (error: any) {
      console.error(error);
      setResult({
        riskLevel: 'Evaluation Failed',
        color: 'text-red-600',
        bgColor: 'bg-red-50',
        icon: <AlertTriangle className="w-6 h-6 text-red-600" />,
        flags: ['ERROR'],
        summary: error.message || 'An unexpected error occurred during evaluation. The backend server might be down.',
        obligations: []
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden max-w-3xl w-full mx-auto">
      <div className="bg-gradient-to-r from-blue-900 to-blue-800 p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Bot className="w-8 h-8 text-blue-200" />
          <h3 className="text-2xl font-bold">Interactive Evaluator</h3>
        </div>
        <p className="text-blue-100 text-sm">
          Describe an AI system below to perform an automated EU AI Act conformity assessment using the actual Python engine.
        </p>
      </div>

      <div className="p-6">
        <div className="mb-6">
          <label htmlFor="ai-description" className="block text-sm font-medium text-gray-700 mb-2">
            AI System Description
          </label>
          <textarea
            id="ai-description"
            rows={4}
            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow resize-none text-gray-800 placeholder-gray-400"
            placeholder="e.g., An AI system that filters resumes for job recruitment..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          ></textarea>
        </div>

        <button
          onClick={handleEvaluate}
          disabled={!description.trim() || isEvaluating}
          className={`w-full py-3 px-4 rounded-lg font-bold text-white transition-all flex items-center justify-center gap-2
            ${!description.trim() ? 'bg-gray-300 cursor-not-allowed' :
              isEvaluating ? 'bg-blue-400 cursor-wait' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md'}`}
        >
          {isEvaluating ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
              Evaluating Compliance...
            </>
          ) : (
            'Run Assessment'
          )}
        </button>

        {result && (
          <div className="mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h4 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">Assessment Results</h4>

            <div className={`rounded-xl p-5 mb-6 border ${result.bgColor} border-opacity-50`}>
              <div className="flex items-start gap-4">
                <div className="mt-1">
                  {result.icon}
                </div>
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <span className={`font-bold text-lg ${result.color}`}>
                      {result.riskLevel}
                    </span>
                    <div className="flex gap-2">
                      {result.flags.map((flag: string, i: number) => (
                        <span key={i} className="px-2 py-1 text-xs font-bold bg-white rounded shadow-sm border text-gray-700">
                          {flag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <p className="text-gray-700 text-sm mt-2">{result.summary}</p>
                </div>
              </div>
            </div>

            {result.obligations && result.obligations.length > 0 && (
              <div>
                <h5 className="font-medium text-gray-800 mb-3">Key Details:</h5>
                <ul className="space-y-2">
                  {result.obligations.map((obs: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                      <div className="min-w-4 mt-1 text-blue-500">•</div>
                      {obs}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
