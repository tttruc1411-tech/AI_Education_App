import os

base_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="100%" height="100%" shape-rendering="geometricPrecision">
    <!-- Core Sphere -->
    <circle cx="100" cy="100" r="52" fill="#1e3a8a" stroke="#0f172a" stroke-width="8" />
    <path d="M 105 55 Q 120 50 135 65 Q 145 80 145 95 Q 120 70 105 55 Z" fill="#3b82f6" opacity="0.6"/>

    <!-- Arms Layer -->
    <g id="arms">
        <g stroke="#0f172a" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none">
            {arm_paths}
        </g>
        <g stroke="{arm_color}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none">
            {arm_paths}
        </g>
        {arm_extras}
    </g>

    <!-- Outer Shells -->
    <g id="shells" stroke="#0f172a" stroke-width="8" stroke-linejoin="round">
        <path d="M 30 105 L 50 105 L 60 135 L 140 135 L 150 105 L 170 105 L 175 135 L 155 175 L 100 190 L 45 175 L 25 135 Z" fill="#eab308" />
        <path d="M 38 112 L 48 112 L 56 138 L 144 138 L 152 112 L 162 112 L 166 135 L 148 168 L 100 180 L 52 168 L 34 135 Z" fill="none" stroke="#fde047" stroke-width="4" opacity="0.6"/>

        <text x="100" y="167" font-family="'Courier New', monospace" font-weight="900" font-size="34" fill="#fde047" stroke="none" text-anchor="middle" opacity="0.5" letter-spacing="2">KDI</text>
        <text x="100" y="165" font-family="'Courier New', monospace" font-weight="900" font-size="34" fill="#1e3a8a" stroke="none" text-anchor="middle" letter-spacing="2">KDI</text>

        <path d="M 25 85 L 45 85 L 60 45 L 90 35 L 90 15 L 55 20 L 30 45 L 20 65 Z" fill="#eab308" />
        <path d="M 175 85 L 155 85 L 140 45 L 110 35 L 110 15 L 145 20 L 170 45 L 180 65 Z" fill="#eab308" />
    </g>

    <!-- Antenna Container -->
    <g id="antenna">
        <path d="M 100 45 L 100 10" stroke="#0f172a" stroke-width="12" stroke-linecap="round" />
        <path d="M 100 45 L 100 10" stroke="#334155" stroke-width="6" stroke-linecap="round" />
        <circle cx="100" cy="8" r="8" fill="{antenna_color}" {antenna_filter} />
    </g>
    <g id="face">
        <g fill="{eye_color}">
            {face_paths}
        </g>
    </g>
</svg>"""

moods = {
    'neutral': {
        'arm_color': '#1e3a8a',
        'antenna_color': '#fbbf24',
        'antenna_filter': '',
        'eye_color': '#22d3ee',
        'arm_paths': '<path d="M 40 100 L 25 125 L 35 145" /> <path d="M 160 100 L 175 125 L 165 145" />',
        'arm_extras': '',
        'face_paths': '<rect x="75" y="82" width="16" height="16" rx="6" /> <rect x="109" y="82" width="16" height="16" rx="6" /> <path d="M 95 104 Q 100 108 105 104" fill="none" stroke="#22d3ee" stroke-width="4" stroke-linecap="round" />'
    },
    'happy': {
        'arm_color': '#1e3a8a',
        'antenna_color': '#22c55e',
        'antenna_filter': 'filter="drop-shadow(0 0 10px #22c55e)"',
        'eye_color': '#22d3ee',
        'arm_paths': '<path d="M 40 100 L 20 75 L 30 55" /> <path d="M 160 100 L 180 75 L 170 55" />',
        'arm_extras': '<path d="M 20 25 L 20 45 M 10 35 L 30 35" stroke="#22c55e" stroke-width="4" stroke-linecap="round" /> <path d="M 170 15 L 170 35 M 160 25 L 180 25" stroke="#22c55e" stroke-width="4" stroke-linecap="round" />',
        'face_paths': '<path d="M 72 90 Q 83 75 94 90" fill="none" stroke="#22d3ee" stroke-width="6" stroke-linecap="round" /> <path d="M 106 90 Q 117 75 128 90" fill="none" stroke="#22d3ee" stroke-width="6" stroke-linecap="round" /> <path d="M 92 102 Q 100 110 108 102" fill="none" stroke="#22d3ee" stroke-width="4" stroke-linecap="round" /> <rect x="65" y="95" width="12" height="6" rx="2" fill="#fbbf24" opacity="0.8" /> <rect x="123" y="95" width="12" height="6" rx="2" fill="#fbbf24" opacity="0.8" />'
    },
    'questioning': {
        'arm_color': '#1e3a8a',
        'antenna_color': '#a78bfa',
        'antenna_filter': '',
        'eye_color': '#22d3ee',
        'arm_paths': '<path d="M 40 100 L 25 125 L 35 145" /> <path d="M 160 100 L 145 135 L 115 125" />',
        'arm_extras': '',
        'face_paths': '<rect x="75" y="82" width="18" height="15" rx="4" /> <rect x="110" y="88" width="12" height="8" rx="3" /> <rect x="94" y="108" width="8" height="4" rx="2" /><g transform="translate(140, 15)"><path d="M 0 0 L 30 0 L 30 25 L 15 25 L 10 35 L 10 25 L 0 25 Z" fill="#0f172a" stroke="#eab308" stroke-width="3" stroke-linejoin="round"/><text x="15" y="19" font-family="\'Courier New\', monospace" font-weight="900" font-size="18" fill="#eab308" text-anchor="middle">?</text></g>'
    },
    'sad': {
        'arm_color': '#1e3a8a',
        'antenna_color': '#64748b',
        'antenna_filter': '',
        'eye_color': '#22d3ee',
        'arm_paths': '<path d="M 40 100 L 25 125 L 35 145" /> <path d="M 160 100 L 145 140 L 125 130" />',
        'arm_extras': '',
        'face_paths': '<path d="M 75 88 L 90 95" fill="none" stroke="#22d3ee" stroke-width="7" stroke-linecap="round" /> <path d="M 125 88 L 110 95" fill="none" stroke="#22d3ee" stroke-width="7" stroke-linecap="round" /> <path d="M 92 110 Q 100 102 108 110" fill="none" stroke="#22d3ee" stroke-width="4" stroke-linecap="round" /> <circle cx="85" cy="100" r="3" /> <circle cx="115" cy="100" r="3" />'
    },
    'error': {
        'arm_color': '#1e3a8a',
        'antenna_color': '#ef4444',
        'antenna_filter': 'filter="drop-shadow(0 0 10px #ef4444)"',
        'eye_color': '#22d3ee',
        'arm_paths': '<path d="M 40 100 L 15 90" /> <path d="M 160 100 L 185 90" />',
        'arm_extras': '',
        'face_paths': '<rect x="75" y="80" width="16" height="20" rx="8" /> <rect x="109" y="80" width="16" height="20" rx="8" /> <rect x="94" y="110" width="12" height="4" rx="2" /> <g transform="translate(140, 15)"><path d="M 0 0 L 30 0 L 30 25 L 15 25 L 10 35 L 10 25 L 0 25 Z" fill="#0f172a" stroke="#ef4444" stroke-width="3" stroke-linejoin="round"/><text x="15" y="19" font-family="\'Courier New\', monospace" font-weight="900" font-size="18" fill="#ef4444" stroke="none" text-anchor="middle">!</text></g>'
    }
}

out_dir = 'e:/KDI/AI_Education_App/src/modules/courses'
import os
os.makedirs(out_dir, exist_ok=True)

for mood, data in moods.items():
    content = base_svg.format(**data)
    with open(f'{out_dir}/kdi_hatchling_{mood}.svg', 'w') as f:
        f.write(content)
