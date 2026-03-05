import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(req: Request): Promise<Response> {
  try {
    const { description } = await req.json();

    if (!description) {
      return NextResponse.json({ error: 'Description is required' }, { status: 400 });
    }

    return new Promise<Response>((resolve) => {
      const pythonScript = `
import sys
import json
import os

try:
    from eu_compliance_engine.llm_evaluator import evaluate_with_llm
    desc = sys.argv[1]
    result = evaluate_with_llm(desc)
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;

      const pythonProcess = spawn('python3', [
        '-c', pythonScript, description
      ], {
        env: {
          ...process.env,
          PYTHONPATH: path.resolve(process.cwd(), '../src')
        }
      });

      let stdoutData = '';
      let stderrData = '';

      pythonProcess.stdout.on('data', (data) => {
        stdoutData += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderrData += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error('Python script failed:', stderrData);
          resolve(NextResponse.json({ error: 'Evaluation failed', details: stderrData }, { status: 500 }));
          return;
        }

        try {
          const result = JSON.parse(stdoutData.trim());
          resolve(NextResponse.json(result));
        } catch (e) {
          console.error('Failed to parse python output:', stdoutData);
          resolve(NextResponse.json({ error: 'Failed to parse evaluation result' }, { status: 500 }));
        }
      });
    });

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
