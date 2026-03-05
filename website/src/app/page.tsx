import React from 'react';
import EUFlag from '../components/EUFlag';
import LLMEvaluator from '../components/LLMEvaluator';
import { FileText, ShieldAlert, Cpu } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 font-sans selection:bg-blue-200">

      {/* Header/Nav */}
      <nav className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-6 overflow-hidden rounded shadow-sm border border-slate-200">
              <EUFlag />
            </div>
            <span className="font-bold text-lg tracking-tight text-blue-900">EU-Compliance-Engine</span>
          </div>
          <div className="flex gap-4">
             <a
              href="https://github.com/vinersar31/EU-Compliance-Engine"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </nav>

      <main>
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white py-24 sm:py-32 lg:py-40">
           <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay pointer-events-none"></div>
           <div className="absolute top-0 right-0 -mr-32 -mt-32 w-96 h-96 rounded-full bg-blue-500 blur-3xl opacity-20 pointer-events-none"></div>
           <div className="absolute bottom-0 left-0 -ml-32 -mb-32 w-96 h-96 rounded-full bg-indigo-500 blur-3xl opacity-20 pointer-events-none"></div>

           <div className="relative max-w-6xl mx-auto px-6 text-center">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight mb-8">
              Automated <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">EU AI Act</span> Compliance
            </h1>
            <p className="mt-6 text-xl leading-8 text-blue-100 max-w-3xl mx-auto mb-10 font-light">
              Evaluate software projects against the 2026 EU AI Act standards. Automatically identify High-Risk systems and generate Conformity Assessment Reports.
            </p>
            <div className="flex justify-center gap-4 flex-col sm:flex-row">
               <a
                href="#evaluator"
                className="rounded-full bg-white px-8 py-4 text-lg font-bold text-blue-900 shadow-xl hover:bg-slate-50 hover:-translate-y-1 transition-all"
              >
                Try Interactive Demo
              </a>
              <a
                href="https://github.com/vinersar31/EU-Compliance-Engine"
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-full bg-blue-800/50 border border-blue-400/30 backdrop-blur-sm px-8 py-4 text-lg font-bold text-white shadow-xl hover:bg-blue-700/50 hover:-translate-y-1 transition-all"
              >
                View Documentation
              </a>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-24 bg-white">
          <div className="max-w-6xl mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                Core Capabilities
              </h2>
              <p className="mt-4 text-lg text-slate-600">
                Designed to handle the complexities of Annex III and Prohibited AI practices.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: <ShieldAlert className="w-10 h-10 text-rose-500" />,
                  title: 'Risk Categorization',
                  description: 'Automatically maps code patterns and system descriptions to FLAG RED (Prohibited) or FLAG YELLOW (High-Risk) categories.'
                },
                {
                  icon: <FileText className="w-10 h-10 text-blue-500" />,
                  title: 'Automated Reporting',
                  description: 'Generates structured Conformity Assessment Reports in Markdown, ready for human review or regulatory submission.'
                },
                {
                  icon: <Cpu className="w-10 h-10 text-emerald-500" />,
                  title: 'Agentic Workflows',
                  description: 'Built with Pydantic schemas, perfect for integrating into larger autonomous LLM pipelines and CI/CD tools.'
                }
              ].map((feature, idx) => (
                <div key={idx} className="bg-slate-50 rounded-3xl p-8 border border-slate-100 hover:shadow-lg transition-shadow">
                  <div className="bg-white w-16 h-16 rounded-2xl flex items-center justify-center shadow-sm mb-6">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                  <p className="text-slate-600 leading-relaxed">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Interactive Demo Section */}
        <section id="evaluator" className="py-24 bg-slate-50 border-t border-slate-200">
           <div className="max-w-6xl mx-auto px-6">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                Test the Engine
              </h2>
              <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
                Use the LLM Evaluator component to see how the engine classifies different AI systems based on their descriptions.
              </p>
            </div>

            <LLMEvaluator />

          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="bg-slate-900 py-12 text-slate-400 border-t border-slate-800">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div className="flex items-center gap-4">
             <div className="w-10 h-7 overflow-hidden rounded shadow-sm opacity-50 grayscale hover:grayscale-0 transition-all">
              <EUFlag />
            </div>
            <div>
              <p className="font-semibold text-slate-200">EU-Compliance-Engine</p>
              <p className="text-sm">Preparing software for the 2026 standards.</p>
            </div>
          </div>
          <div className="text-left md:text-right text-sm">
            <p>Built for the open-source community.</p>
            <p className="mt-1">
              Not legal advice. Always consult with legal professionals regarding compliance.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
