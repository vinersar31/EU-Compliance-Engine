# EU-Compliance-Engine Website

This is the frontend presentation for the EU-Compliance-Engine, built with Next.js.

It provides an interactive LLM Evaluator that directly calls the underlying Python compliance engine.

## Prerequisites

Because the interactive evaluator requires running the actual Python engine, you must have Python installed and the project dependencies set up:

```bash
# From the root of the repository
pip install -r requirements.txt
export GEMINI_API_KEY="your_api_key_here"
```

## Getting Started

First, install frontend dependencies:

```bash
cd website
npm install
```

Then, run the development server:

```bash
npm run start
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Architecture

* **Frontend**: Next.js App Router, Tailwind CSS, Lucide React icons.
* **Backend API**: The frontend uses a Next.js API Route (`src/app/api/evaluate/route.ts`) to accept evaluator requests.
* **Python Integration**: The API route uses `child_process.spawn` to execute the Python core engine (`src/eu_compliance_engine/llm_evaluator.py`) directly, ensuring the UI always uses the authentic, up-to-date compliance logic.
