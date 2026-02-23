import React from 'react';

export const ScaleLogo = ({ size = 28, className = '' }) => (
    <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        xmlns="http://www.w3.org/2000/svg"
        className={className}
        style={{ borderRadius: '50%', backgroundColor: '#fff', padding: '2px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}
    >
        <g transform="scale(0.8) translate(12.5, 12.5)">
            {/* Stand Base */}
            <path d="M 30 85 L 70 85 L 65 75 L 35 75 Z" fill="#111" />
            {/* Stand Pillar */}
            <rect x="44" y="25" width="12" height="50" fill="#111" />
            <rect x="41" y="70" width="18" height="5" fill="#111" />
            {/* Top Beam */}
            <path d="M 15 25 L 85 25 L 85 30 L 15 30 Z" fill="#111" />
            <path d="M 40 20 L 60 20 L 60 25 L 40 25 Z" fill="#111" />

            {/* Center Pivot */}
            <circle cx="50" cy="27.5" r="5" fill="#eab308" />
            <circle cx="50" cy="27.5" r="2" fill="#111" />

            {/* Left Strings */}
            <line x1="20" y1="30" x2="10" y2="60" stroke="#111" strokeWidth="2" />
            <line x1="20" y1="30" x2="30" y2="60" stroke="#111" strokeWidth="2" />
            {/* Right Strings */}
            <line x1="80" y1="30" x2="70" y2="60" stroke="#111" strokeWidth="2" />
            <line x1="80" y1="30" x2="90" y2="60" stroke="#111" strokeWidth="2" />

            {/* Left Pan */}
            <path d="M 5 60 Q 20 75 35 60 Z" fill="#eab308" stroke="#111" strokeWidth="2.5" />
            <rect x="5" y="58" width="30" height="2" fill="#111" />

            {/* Right Pan */}
            <path d="M 65 60 Q 80 75 95 60 Z" fill="#eab308" stroke="#111" strokeWidth="2.5" />
            <rect x="65" y="58" width="30" height="2" fill="#111" />
        </g>
    </svg>
);

export default ScaleLogo;
