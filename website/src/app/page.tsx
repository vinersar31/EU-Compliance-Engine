export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <main className="max-w-4xl mx-auto py-16 px-6 sm:px-8">
        <header className="mb-12 text-center">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-blue-900 mb-4 tracking-tight">
            EU-Compliance-Engine
          </h1>
          <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto">
            An automated compliance agent for the EU AI Act (Regulation (EU) 2024/1689).
          </p>
        </header>

        <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b pb-2">What it does</h2>
          <p className="text-gray-600 leading-relaxed mb-4">
            This project helps evaluate AI systems and software projects to determine if they classify as "Prohibited", "High-Risk" (under Annex III), or have other obligations, based on the EU AI Act standards. It automatically generates a "Conformity Assessment Report" in Markdown format.
          </p>
          <ul className="list-disc list-inside text-gray-600 space-y-2 mt-4 ml-2">
            <li>Evaluates AI systems against strict EU standards.</li>
            <li>Identifies Prohibited and High-Risk categories (Annex III).</li>
            <li>Generates detailed Conformity Assessment Reports.</li>
          </ul>
        </section>

        <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 border-b pb-2">Agentic System Integration</h2>
          <p className="text-gray-600 leading-relaxed">
            The engine is built with modern agentic workflows in mind. Exposing Pydantic schemas and structured tool interfaces, it allows seamless integration with large language models and autonomous agents via function calling.
          </p>
        </section>

        <section className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Get Started</h2>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
             <a
              href="https://github.com/vinersar31/EU-Compliance-Engine"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors shadow-sm"
            >
              View on GitHub
            </a>
          </div>
        </section>
      </main>

      <footer className="text-center py-8 text-gray-500 text-sm">
        <p>Built for the open-source community. Subject to the EU AI Act (2026 standards).</p>
      </footer>
    </div>
  );
}
