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

    // Simulate API call and evaluation time
    setTimeout(() => {
      let mockResult = {
        riskLevel: 'Minimal Risk',
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        icon: <ShieldCheck className="w-6 h-6 text-green-600" />,
        flags: ['FLAG GREEN'],
        summary: 'Based on the description, this system poses minimal risk to citizens\' rights and safety.',
        obligations: [
          'No mandatory obligations under the EU AI Act.',
          'Voluntary codes of conduct are encouraged.'
        ]
      };

      const lowerDesc = description.toLowerCase();

      // Simple mock logic for demonstration
      if (lowerDesc.includes('biometric') || lowerDesc.includes('facial recognition') || lowerDesc.includes('law enforcement')) {
        mockResult = {
          riskLevel: 'Unacceptable Risk',
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          icon: <AlertTriangle className="w-6 h-6 text-red-600" />,
          flags: ['FLAG RED'],
          summary: 'This system likely falls under the Prohibited AI practices of the EU AI Act.',
          obligations: [
            'Prohibited from being placed on the market or put into service in the EU.',
            'Exceptions apply only in very narrow, strictly defined circumstances (e.g., targeted search for missing persons).'
          ]
        };
      } else if (lowerDesc.includes('recruitment') || lowerDesc.includes('employment') || lowerDesc.includes('education') || lowerDesc.includes('credit')) {
         mockResult = {
          riskLevel: 'High Risk',
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          icon: <AlertTriangle className="w-6 h-6 text-yellow-600" />,
          flags: ['FLAG YELLOW'],
          summary: 'This system likely classifies as High-Risk under Annex III of the EU AI Act.',
          obligations: [
            'Mandatory Conformity Assessment required.',
            'Implementation of a Risk Management System.',
            'Data governance and quality requirements.',
            'Human oversight measures must be in place.'
          ]
        };
      } else if (lowerDesc.includes('chatbot') || lowerDesc.includes('deepfake') || lowerDesc.includes('generate')) {
         mockResult = {
          riskLevel: 'Transparency Risk',
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          icon: <Info className="w-6 h-6 text-blue-600" />,
          flags: ['FLAG BLUE'],
          summary: 'This system must comply with specific transparency obligations under Article 50.',
          obligations: [
            'Users must be informed they are interacting with an AI system.',
            'Generated content (like deepfakes) must be clearly labeled as artificially generated.'
          ]
        };
      }

      setResult(mockResult);
      setIsEvaluating(false);
    }, 1500);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden max-w-3xl w-full mx-auto">
      <div className="bg-gradient-to-r from-blue-900 to-blue-800 p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Bot className="w-8 h-8 text-blue-200" />
          <h3 className="text-2xl font-bold">Interactive Evaluator</h3>
        </div>
        <p className="text-blue-100 text-sm">
          Describe an AI system below to simulate an automated EU AI Act conformity assessment.
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

            <div>
              <h5 className="font-medium text-gray-800 mb-3">Key Obligations:</h5>
              <ul className="space-y-2">
                {result.obligations.map((obs: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                    <div className="min-w-4 mt-1 text-blue-500">•</div>
                    {obs}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
