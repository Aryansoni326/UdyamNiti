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
      50:  '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94A3B8',  // UNKNOWN / text-secondary
      500: '#64748B',  // text-muted
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
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

    // ─── Semantic Surface Colors ─────────────────────────────────────────
    surface: {
      base:      '#0A0F1E',  // page background
      raised:    '#0D1526',  // slightly elevated
      elevated:  '#1E293B',  // elevated surface
      card:      '#1A2235',  // card/paper
      cardHover: '#1E2A42',  // card hover
      overlay:   'rgba(10, 15, 30, 0.85)',  // nav / modal backdrop
    },
    // ─── Evidence Category Badges ────────────────────────────────────────
    evidence: {
      self_declared: {
        color: '#94A3B8',
        bg: 'rgba(148, 163, 184, 0.12)',
        border: 'rgba(148, 163, 184, 0.3)',
      },
      document_supported: {
        color: '#38BDF8',
        bg: 'rgba(56, 189, 248, 0.12)',
        border: 'rgba(56, 189, 248, 0.3)',
      },
      official_source: {
        color: '#10B981',
        bg: 'rgba(16, 185, 129, 0.12)',
        border: 'rgba(16, 185, 129, 0.3)',
      },
      rule_matched: {
        color: '#A855F7',
        bg: 'rgba(168, 85, 247, 0.12)',
        border: 'rgba(168, 85, 247, 0.3)',
      },
      ai_explanation: {
        color: '#6C63FF',
        bg: 'rgba(108, 99, 255, 0.12)',
        border: 'rgba(108, 99, 255, 0.3)',
      },
    },
    // ─── Deterministic Match Status ──────────────────────────────────────
    status: {
      match: {
        color: '#10B981',
        bg: 'rgba(16, 185, 129, 0.12)',
        border: 'rgba(16, 185, 129, 0.3)',
      },
      potential: {
        color: '#F59E0B',
        bg: 'rgba(245, 158, 11, 0.12)',
        border: 'rgba(245, 158, 11, 0.3)',
      },
      unknown: {
        color: '#94A3B8',
        bg: 'rgba(148, 163, 184, 0.12)',
        border: 'rgba(148, 163, 184, 0.3)',
      },
      notMatch: {
        color: '#EF4444',
        bg: 'rgba(239, 68, 68, 0.12)',
        border: 'rgba(239, 68, 68, 0.3)',
      },
      verification: {
        color: '#3B82F6',
        bg: 'rgba(59, 130, 246, 0.12)',
        border: 'rgba(59, 130, 246, 0.3)',
      },
    },
    border: {
      subtle:  'rgba(255, 255, 255, 0.06)',
      default: 'rgba(255, 255, 255, 0.10)',
      strong:  'rgba(255, 255, 255, 0.20)',
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

  // ─── Shadows ───────────────────────────────────────────────────────────────
  shadow: {
    sm:   '0 2px 8px rgba(0, 0, 0, 0.3)',
    md:   '0 4px 16px rgba(0, 0, 0, 0.35)',
    lg:   '0 8px 32px rgba(0, 0, 0, 0.4)',
    glow: '0 0 40px rgba(108, 99, 255, 0.2)',
    glowStrong: '0 0 60px rgba(108, 99, 255, 0.4)',
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
      color: '#10B981',
      bg:    'rgba(16, 185, 129, 0.12)',
      border:'rgba(16, 185, 129, 0.25)',
      glow:  'rgba(16, 185, 129, 0.15)',
    },
    POTENTIAL_MATCH: {
      color: '#F59E0B',
      bg:    'rgba(245, 158, 11, 0.12)',
      border:'rgba(245, 158, 11, 0.25)',
      glow:  'rgba(245, 158, 11, 0.15)',
    },
    UNKNOWN: {
      color: '#94A3B8',
      bg:    'rgba(148, 163, 184, 0.10)',
      border:'rgba(148, 163, 184, 0.20)',
      glow:  'rgba(148, 163, 184, 0.08)',
    },
    DOES_NOT_MATCH: {
      color: '#EF4444',
      bg:    'rgba(239, 68, 68, 0.10)',
      border:'rgba(239, 68, 68, 0.22)',
      glow:  'rgba(239, 68, 68, 0.12)',
    },
    REQUIRES_OFFICIAL_VERIFICATION: {
      color: '#3B82F6',
      bg:    'rgba(59, 130, 246, 0.10)',
      border:'rgba(59, 130, 246, 0.22)',
      glow:  'rgba(59, 130, 246, 0.12)',
    },
  },

  // ─── Scheme Level Palette ──────────────────────────────────────────────────
  schemeLevel: {
    central:      { color: '#3B82F6', bg: 'rgba(59, 130, 246, 0.12)', label: '🇮🇳 Central' },
    state:        { color: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.12)', label: '🏛️ State' },
    state_gujarat:{ color: '#EC4899', bg: 'rgba(236, 72, 153, 0.12)', label: '🏴 Gujarat' },
  },

  // ─── Evidence Source Palette ───────────────────────────────────────────────
  evidence: {
    self_declared:   { color: '#94A3B8', label: 'Self-declared' },
    document_verified:{ color: '#10B981', label: 'Document-supported' },
    official_source: { color: '#6C63FF', label: 'Official source' },
    rule_matched:    { color: '#F59E0B', label: 'Rule matched' },
    ai_explanation:  { color: '#3B82F6', label: 'AI explanation' },
  },

  // ─── Gradients ─────────────────────────────────────────────────────────────
  gradient: {
    brand:   'linear-gradient(135deg, #6C63FF 0%, #3B82F6 50%, #10B981 100%)',
    hero:    'linear-gradient(135deg, #6C63FF 0%, #4F46E5 100%)',
    gold:    'linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)',
    surface: 'linear-gradient(135deg, #1A2235 0%, #0D1526 100%)',
    glow:    'radial-gradient(ellipse at 50% 0%, rgba(108, 99, 255, 0.15) 0%, transparent 70%)',
  },
} as const

export type Tokens = typeof tokens
