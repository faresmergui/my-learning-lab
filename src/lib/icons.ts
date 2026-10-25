// Hand-drawn logos for some modules (inline SVG, color inherited from the module
// via currentColor). A module missing from this list shows its `code` field.
const attrs = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true"';

export const moduleIcons: Record<string, string> = {
  // Two playing cards; the front one bears an inverted pyramid.
  yugioh: `<svg ${attrs}>
    <rect x="3.2" y="4.6" width="10.5" height="15" rx="1.6" transform="rotate(-12 8.45 12.1)" opacity=".45"/>
    <rect x="9.3" y="3.5" width="11" height="16" rx="1.7"/>
    <path d="M11.8 7.6h6l-3 6.2z"/>
    <circle cx="14.8" cy="9.7" r=".9" fill="currentColor" stroke="none"/>
    <path d="M11.8 16.6h6"/>
  </svg>`,
  // A crosshair with the spike (diamond) in the middle.
  valorant: `<svg ${attrs}>
    <circle cx="12" cy="12" r="7.3"/>
    <path d="M12 2.4v4.2M12 17.4v4.2M2.4 12h4.2M17.4 12h4.2"/>
    <path d="M12 9.5l2.5 2.5-2.5 2.5-2.5-2.5z" fill="currentColor"/>
  </svg>`,
  // One keyboard octave: seven white keys and five black ones.
  piano: `<svg ${attrs}>
    <rect x="2.5" y="5" width="19" height="14" rx="1.6"/>
    <path d="M5.2 12.6V19M7.9 12.6V19M10.6 12.6V19M13.4 12.6V19M16.1 12.6V19M18.8 12.6V19"/>
    <path d="M4.6 5h1.3v7.6H4.6zM7.3 5h1.3v7.6H7.3zM12.7 5h1.3v7.6h-1.3zM15.4 5h1.3v7.6h-1.3zM18.1 5h1.3v7.6h-1.3z" fill="currentColor" stroke-width="1"/>
  </svg>`,
  // A rising curve above bars: savings that grow.
  finance: `<svg ${attrs}>
    <path d="M3 20.5h18"/>
    <path d="M6 20.5v-4M10 20.5v-6M14 20.5v-5M18 20.5v-8.5"/>
    <path d="M4 12.5l5-4.5 4 3 6.5-6.5"/>
    <path d="M15.5 4.5h4v4"/>
  </svg>`,
  // A knight's head.
  echecs: `<svg ${attrs}>
    <path d="M7 20.5h10.5"/>
    <path d="M8.5 20.5c0-3.2 1.6-4.8 3.6-6.6-1.6.3-3 .9-4.4 2.1L6 14.2c.5-2.6 2-5.1 4.3-6.7L10 4.5l2.2 1.6c3.6-.2 6.3 2.6 6.3 6.6v7.8"/>
    <circle cx="12.6" cy="9.2" r=".8" fill="currentColor" stroke="none"/>
  </svg>`,
};
