/**
 * UdyamNiti Design Tokens
 * Single source of truth for all visual decisions.
 * Referenced by both the MUI theme and CSS custom properties.
 */

export const tokens = {
  // ─── Color Primitives ──────────────────────────────────────────────────────
  color: {
    // Brand
    violet: {
      50:  '#f0efff',
      100: '#e4e2ff',
      200: '#cbc8ff',
      300: '#a8a4ff',
      400: '#8b87ff',
      500: '#6C63FF',  // primary
      600: '#5a52e8',
      700: '#4F46E5',  // primary dark
      800: '#3d35b8',
      900: '#2e278a',
    },
    emerald: {
      50:  '#ecfdf5',
      100: '#d1fae5',
      200: '#a7f3d0',
      300: '#6ee7b7',
      400: '#34d399',
      500: '#10B981',  // secondary / MATCH
      600: '#059669',  // secondary dark
      700: '#047857',
      800: '#065f46',
      900: '#064e3b',
    },
    amber: {
      50:  '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#F59E0B',  // POTENTIAL_MATCH / warning
      600: '#d97706',
      700: '#b45309',
    },
    red: {
      50:  '#fef2f2',
      100: '#fee2e2',
      400: '#f87171',
      500: '#EF4444',  // DOES_NOT_MATCH / error
      600: '#dc2626',
      700: '#b91c1c',
    },
    sky: {
      50:  '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#3B82F6',  // info / central scheme
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
    blue: {
      50:  '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
    rose: {
      50:  '#fff1f2',
      100: '#ffe4e6',
      200: '#fecdd3',
      300: '#fda4af',
      400: '#fb7185',
      500: '#f43f5e',
      600: '#e11d48',
      700: '#be123c',
      800: '#9f1239',
      900: '#881337',
    },
    slate: {
      50:  '#0F172A',  // Primary heading dark text
      100: '#1E293B',  // Strong title dark text
      200: '#334155',  // Body dark text
      300: '#475569',  // Secondary body text
      400: '#64748B',  // Muted caption text
      500: '#94A3B8',  // Subtle icons / border
      600: '#CBD5E1',  // Border default
      700: '#E2E8F0',  // Border subtle / divider
      800: '#F1F5F9',  // Elevated light background
      900: '#FFFFFF',  // Card pure white surface
    },
    // Specialty
    pink: {
      400: '#f472b6',
      500: '#EC4899',  // Gujarat state tag
    },
    purple: {
      400: '#c084fc',
      500: '#a855f7',  // sequential relationship
    },

    // ─── Semantic Surface Colors (Light Theme Government Portal) ─────────
    surface: {
      base:      '#F8FAFC',  // clean light slate page background
      raised:    '#FFFFFF',  // pure white elevated card
      elevated:  '#FFFFFF',  // pure white elevated surface
      card:      '#FFFFFF',  // card/paper background
      cardHover: '#F1F5F9',  // card hover state
      overlay:   'rgba(255, 255, 255, 0.96)',  // nav / modal backdrop
    },
    // ─── Evidence Category Badges ────────────────────────────────────────
    evidence: {
      self_declared: {
        color: '#475569',
        bg: 'rgba(71, 85, 105, 0.08)',
        border: 'rgba(71, 85, 105, 0.25)',
      },
      document_supported: {
        color: '#0284C7',
        bg: 'rgba(2, 132, 199, 0.08)',
        border: 'rgba(2, 132, 199, 0.25)',
      },
      official_source: {
        color: '#059669',
        bg: 'rgba(5, 150, 105, 0.08)',
        border: 'rgba(5, 150, 105, 0.25)',
      },
      rule_matched: {
        color: '#7C3AED',
        bg: 'rgba(124, 58, 237, 0.08)',
        border: 'rgba(124, 58, 237, 0.25)',
      },
      ai_explanation: {
        color: '#4F46E5',
        bg: 'rgba(79, 70, 229, 0.08)',
        border: 'rgba(79, 70, 229, 0.25)',
      },
    },
    // ─── Deterministic Match Status ──────────────────────────────────────
    status: {
      match: {
        color: '#059669',
        bg: 'rgba(5, 150, 105, 0.08)',
        border: 'rgba(5, 150, 105, 0.25)',
      },
      potential: {
        color: '#D97706',
        bg: 'rgba(217, 119, 6, 0.08)',
        border: 'rgba(217, 119, 6, 0.25)',
      },
      unknown: {
        color: '#64748B',
        bg: 'rgba(100, 116, 139, 0.08)',
        border: 'rgba(100, 116, 139, 0.25)',
      },
      notMatch: {
        color: '#DC2626',
        bg: 'rgba(220, 38, 38, 0.08)',
        border: 'rgba(220, 38, 38, 0.25)',
      },
      verification: {
        color: '#2563EB',
        bg: 'rgba(37, 99, 235, 0.08)',
        border: 'rgba(37, 99, 235, 0.25)',
      },
    },
    border: {
      subtle:  '#E2E8F0',
      default: '#CBD5E1',
      strong:  '#94A3B8',
    },
    glass: {
      default: 'rgba(255, 255, 255, 0.04)',
      hover:   'rgba(255, 255, 255, 0.08)',
    },
  },

  // ─── Typography ────────────────────────────────────────────────────────────
  font: {
    heading: "'Outfit', sans-serif",
    body:    "'Inter', sans-serif",
    mono:    "'JetBrains Mono', 'Fira Code', monospace",
  },
  fontSize: {
    xs:   '0.625rem',  // 10px
    sm:   '0.75rem',   // 12px
    base: '0.875rem',  // 14px
    md:   '1rem',      // 16px
    lg:   '1.125rem',  // 18px
    xl:   '1.25rem',   // 20px
    '2xl': '1.5rem',   // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
  },
  fontWeight: {
    normal:   400,
    medium:   500,
    semibold: 600,
    bold:     700,
    extrabold: 800,
    black:    900,
  },
  lineHeight: {
    tight:   1.2,
    snug:    1.4,
    normal:  1.6,
    relaxed: 1.75,
    loose:   2,
  },

  // ─── Spacing ───────────────────────────────────────────────────────────────
  space: {
    0:   '0',
    1:   '4px',
    2:   '8px',
    3:   '12px',
    4:   '16px',
    5:   '20px',
    6:   '24px',
    8:   '32px',
    10:  '40px',
    12:  '48px',
    16:  '64px',
    20:  '80px',
    24:  '96px',
  },

  // ─── Border Radius ─────────────────────────────────────────────────────────
  radius: {
    sm:   '6px',
    md:   '10px',
    lg:   '14px',
    xl:   '20px',
    '2xl': '28px',
    full: '9999px',
  },

  // ─── Shadows (Light Mode Elevation) ───────────────────────────────────────
  shadow: {
    sm:   '0 1px 3px rgba(15, 23, 42, 0.08), 0 1px 2px rgba(15, 23, 42, 0.04)',
    md:   '0 4px 12px rgba(15, 23, 42, 0.08), 0 2px 4px rgba(15, 23, 42, 0.04)',
    lg:   '0 10px 25px -5px rgba(15, 23, 42, 0.10), 0 8px 10px -6px rgba(15, 23, 42, 0.05)',
    glow: '0 0 24px rgba(15, 46, 89, 0.10)',
    glowStrong: '0 0 36px rgba(15, 46, 89, 0.16)',
  },

  // ─── Z-index ───────────────────────────────────────────────────────────────
  z: {
    base:    0,
    card:    10,
    sticky:  100,
    drawer:  200,
    modal:   300,
    toast:   400,
  },

  // ─── Transitions ───────────────────────────────────────────────────────────
  transition: {
    fast:   'all 0.15s ease',
    base:   'all 0.2s ease',
    slow:   'all 0.35s ease',
    spring: 'all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)',
  },

  // ─── Eligibility Status Palette ────────────────────────────────────────────
  status: {
    MATCH: {
      color: '#059669',
      bg:    'rgba(5, 150, 105, 0.08)',
      border:'rgba(5, 150, 105, 0.25)',
      glow:  'rgba(5, 150, 105, 0.10)',
    },
    POTENTIAL_MATCH: {
      color: '#D97706',
      bg:    'rgba(217, 119, 6, 0.08)',
      border:'rgba(217, 119, 6, 0.25)',
      glow:  'rgba(217, 119, 6, 0.10)',
    },
    UNKNOWN: {
      color: '#64748B',
      bg:    'rgba(100, 116, 139, 0.08)',
      border:'rgba(100, 116, 139, 0.20)',
      glow:  'rgba(100, 116, 139, 0.06)',
    },
    DOES_NOT_MATCH: {
      color: '#DC2626',
      bg:    'rgba(220, 38, 38, 0.08)',
      border:'rgba(220, 38, 38, 0.22)',
      glow:  'rgba(220, 38, 38, 0.08)',
    },
    REQUIRES_OFFICIAL_VERIFICATION: {
      color: '#2563EB',
      bg:    'rgba(37, 99, 235, 0.08)',
      border:'rgba(37, 99, 235, 0.22)',
      glow:  'rgba(37, 99, 235, 0.08)',
    },
  },

  // ─── Scheme Level Palette ──────────────────────────────────────────────────
  schemeLevel: {
    central:      { color: '#1E40AF', bg: 'rgba(30, 64, 175, 0.08)', label: '🇮🇳 Central' },
    state:        { color: '#7C3AED', bg: 'rgba(124, 58, 237, 0.08)', label: '🏛️ State' },
    state_gujarat:{ color: '#DB2777', bg: 'rgba(219, 39, 119, 0.08)', label: '🏴 Gujarat' },
  },

  // ─── Evidence Source Palette ───────────────────────────────────────────────
  evidence: {
    self_declared:   { color: '#64748B', label: 'Self-declared' },
    document_verified:{ color: '#059669', label: 'Document-supported' },
    official_source: { color: '#0F2E59', label: 'Official source' },
    rule_matched:    { color: '#D97706', label: 'Rule matched' },
    ai_explanation:  { color: '#2563EB', label: 'AI explanation' },
  },

  // ─── Gradients ─────────────────────────────────────────────────────────────
  gradient: {
    brand:   'linear-gradient(135deg, #0F2E59 0%, #1E40AF 50%, #059669 100%)',
    hero:    'linear-gradient(135deg, #0F2E59 0%, #1E3A8A 100%)',
    gold:    'linear-gradient(135deg, #D97706 0%, #DC2626 100%)',
    surface: 'linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)',
    glow:    'radial-gradient(ellipse at 50% 0%, rgba(15, 46, 89, 0.03) 0%, transparent 70%)',
  },
} as const

export type Tokens = typeof tokens
