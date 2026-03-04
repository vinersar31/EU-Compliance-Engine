import React from 'react';

export default function EUFlag({ className = '' }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 810 540"
      width="100%"
      height="100%"
    >
      <rect width="810" height="540" fill="#003399"/>
      <g transform="translate(405,270)">
        {Array.from({ length: 12 }).map((_, i) => (
          <g key={i} transform={`rotate(${i * 30}) translate(0,-180)`}>
            <polygon
              points="0,-27 6.06,-8.33 25.68,-8.33 9.81,3.2 15.87,21.85 0,10.32 -15.87,21.85 -9.81,3.2 -25.68,-8.33 -6.06,-8.33"
              fill="#FFCC00"
            />
          </g>
        ))}
      </g>
    </svg>
  );
}
