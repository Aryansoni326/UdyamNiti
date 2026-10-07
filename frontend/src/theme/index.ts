import { createTheme, alpha } from '@mui/material/styles'
import type { Components, Theme } from '@mui/material/styles'
import { tokens } from './tokens'

// ─── Component Overrides ─────────────────────────────────────────────────────

const components: Components<Theme> = {
  MuiCssBaseline: {
    styleOverrides: {
      '*, *::before, *::after': { boxSizing: 'border-box' },
      html: { scrollBehavior: 'smooth' },
      body: {
        fontFamily: tokens.font.body,
        backgroundColor: '#F8FAFC',
        color: '#0F172A',
        WebkitFontSmoothing: 'antialiased',
        MozOsxFontSmoothing: 'grayscale',
        backgroundAttachment: 'fixed',
      },
      '::-webkit-scrollbar': { width: '6px', height: '6px' },
      '::-webkit-scrollbar-track': { background: '#F1F5F9' },
      '::-webkit-scrollbar-thumb': {
        background: '#CBD5E1',
        borderRadius: '3px',
      },
      '::-webkit-scrollbar-thumb:hover': { background: '#94A3B8' },
    },
  },
  MuiButton: {
    defaultProps: { disableElevation: true },
    styleOverrides: {
      root: {
        textTransform: 'none',
        fontWeight: tokens.fontWeight.semibold,
        fontFamily: tokens.font.body,
        borderRadius: tokens.radius.md,
        transition: tokens.transition.base,
        letterSpacing: '0.01em',
      },
      sizeLarge: { padding: '12px 28px', fontSize: '0.95rem' },
      sizeMedium: { padding: '9px 20px', fontSize: '0.875rem' },
      sizeSmall: { padding: '5px 14px', fontSize: '0.8rem' },
      containedPrimary: {
        background: 'linear-gradient(135deg, #0F2E59 0%, #1E40AF 100%)',
        color: '#FFFFFF',
        boxShadow: '0 4px 12px rgba(15, 46, 89, 0.25)',
        '&:hover': {
          background: 'linear-gradient(135deg, #0A1E3A 0%, #1E3A8A 100%)',
          boxShadow: '0 6px 18px rgba(15, 46, 89, 0.35)',
          transform: 'translateY(-1px)',
        },
        '&:active': { transform: 'translateY(0)' },
        '&.Mui-disabled': { background: '#E2E8F0', color: '#94A3B8' },
      },
      containedSecondary: {
        background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
        color: '#FFFFFF',
        boxShadow: '0 4px 12px rgba(5, 150, 105, 0.25)',
        '&:hover': {
          boxShadow: '0 6px 18px rgba(5, 150, 105, 0.35)',
          transform: 'translateY(-1px)',
        },
      },
      outlined: {
        borderColor: '#CBD5E1',
        color: '#0F2E59',
        '&:hover': { borderColor: '#0F2E59', background: 'rgba(15, 46, 89, 0.04)' },
      },
      text: {
        color: '#0F2E59',
        '&:hover': { background: 'rgba(15, 46, 89, 0.05)' },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        background: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: tokens.radius.lg,
        boxShadow: '0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)',
        transition: tokens.transition.base,
        '&:hover': {
          background: '#FFFFFF',
          borderColor: '#CBD5E1',
          transform: 'translateY(-2px)',
          boxShadow: '0 6px 16px rgba(15, 23, 42, 0.08)',
        },
      },
    },
  },
  MuiCardContent: {
    styleOverrides: {
      root: {
        padding: '24px',
        '&:last-child': { paddingBottom: '24px' },
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      root: {
        background: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: tokens.radius.lg,
        backgroundImage: 'none',
      },
      elevation1: { boxShadow: '0 1px 3px rgba(15, 23, 42, 0.06)' },
      elevation2: { boxShadow: '0 4px 12px rgba(15, 23, 42, 0.08)' },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        fontWeight: tokens.fontWeight.semibold,
        fontFamily: tokens.font.body,
        fontSize: tokens.fontSize.sm,
        borderRadius: tokens.radius.full,
        transition: tokens.transition.fast,
      },
      sizeSmall: { height: '22px', fontSize: tokens.fontSize.xs },
    },
  },
  MuiTextField: {
    defaultProps: { variant: 'outlined' },
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          backgroundColor: '#FFFFFF',
          borderRadius: tokens.radius.md,
          fontFamily: tokens.font.body,
          transition: tokens.transition.base,
          '& fieldset': { borderColor: '#CBD5E1' },
          '&:hover fieldset': { borderColor: '#94A3B8' },
          '&.Mui-focused fieldset': {
            borderColor: '#0F2E59',
            boxShadow: '0 0 0 3px rgba(15, 46, 89, 0.12)',
          },
          '&.Mui-focused': { backgroundColor: '#FFFFFF' },
        },
        '& .MuiInputLabel-root': {
          fontFamily: tokens.font.body,
          fontSize: tokens.fontSize.base,
          color: '#64748B',
        },
        '& .MuiInputLabel-root.Mui-focused': { color: '#0F2E59' },
        '& .MuiInputBase-input': { color: '#0F172A' },
        '& .MuiFormHelperText-root': {
          fontFamily: tokens.font.body,
          fontSize: tokens.fontSize.sm,
          color: tokens.color.slate[400],
          marginTop: '6px',
        },
      },
    },
  },
  MuiSelect: {
    styleOverrides: {
      root: {
        backgroundColor: tokens.color.glass.default,
        '& .MuiOutlinedInput-notchedOutline': { borderColor: tokens.color.border.default },
        '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: tokens.color.border.strong },
        '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: tokens.color.violet[500] },
      },
      icon: { color: tokens.color.slate[400] },
    },
  },
  MuiMenu: {
    styleOverrides: {
      paper: {
        background: '#FFFFFF',
        border: '1px solid #E2E8F0',
        boxShadow: '0 10px 25px -5px rgba(15, 23, 42, 0.10)',
      },
    },
  },
  MuiMenuItem: {
    styleOverrides: {
      root: {
        fontFamily: tokens.font.body,
        fontSize: tokens.fontSize.base,
        color: '#1E293B',
        '&:hover': { background: '#F1F5F9' },
        '&.Mui-selected': {
          background: 'rgba(15, 46, 89, 0.08)',
          color: '#0F2E59',
          fontWeight: 600,
          '&:hover': { background: 'rgba(15, 46, 89, 0.12)' },
        },
      },
    },
  },
  MuiTabs: {
    styleOverrides: {
      root: {
        borderBottom: '1px solid #E2E8F0',
        minHeight: '48px',
      },
      indicator: {
        background: '#0F2E59',
        height: '3px',
        borderRadius: '3px 3px 0 0',
      },
    },
  },
  MuiTab: {
    styleOverrides: {
      root: {
        textTransform: 'none',
        fontFamily: tokens.font.body,
        fontWeight: tokens.fontWeight.semibold,
        fontSize: tokens.fontSize.base,
        color: '#64748B',
        minHeight: '48px',
        padding: '12px 20px',
        transition: tokens.transition.fast,
        '&.Mui-selected': { color: '#0F2E59' },
        '&:hover': { color: '#0F2E59', background: '#F8FAFC' },
      },
    },
  },
  MuiLinearProgress: {
    styleOverrides: {
      root: {
        borderRadius: tokens.radius.full,
        backgroundColor: '#E2E8F0',
        height: '6px',
      },
      bar: { borderRadius: tokens.radius.full },
    },
  },
  MuiDivider: {
    styleOverrides: {
      root: { borderColor: '#E2E8F0' },
    },
  },
  MuiTooltip: {
    styleOverrides: {
      tooltip: {
        background: '#0F172A',
        border: '1px solid #334155',
        color: '#FFFFFF',
        fontFamily: tokens.font.body,
        fontSize: tokens.fontSize.sm,
        borderRadius: tokens.radius.md,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        padding: '8px 12px',
        maxWidth: '300px',
        lineHeight: tokens.lineHeight.relaxed,
      },
      arrow: { color: '#0F172A' },
    },
  },
  MuiAlert: {
    styleOverrides: {
      root: {
        fontFamily: tokens.font.body,
        fontSize: tokens.fontSize.base,
        borderRadius: tokens.radius.md,
        border: '1px solid',
      },
      standardError: {
        background: '#FEF2F2',
        borderColor: '#FECACA',
        color: '#991B1B',
        '& .MuiAlert-icon': { color: '#DC2626' },
      },
      standardWarning: {
        background: '#FFFBEB',
        borderColor: '#FDE68A',
        color: '#92400E',
        '& .MuiAlert-icon': { color: '#D97706' },
      },
      standardSuccess: {
        background: '#ECFDF5',
        borderColor: '#A7F3D0',
        color: '#065F46',
        '& .MuiAlert-icon': { color: '#059669' },
      },
      standardInfo: {
        background: '#EFF6FF',
        borderColor: '#BFDBFE',
        color: '#1E40AF',
        '& .MuiAlert-icon': { color: '#2563EB' },
      },
    },
  },
  MuiStepper: {
    styleOverrides: {
      root: { background: 'transparent' },
    },
  },
  MuiStepIcon: {
    styleOverrides: {
      root: {
        color: 'rgba(255,255,255,0.1)',
        '&.Mui-active': { color: tokens.color.violet[500] },
        '&.Mui-completed': { color: tokens.color.emerald[500] },
      },
      text: { fill: '#F1F5F9', fontFamily: tokens.font.body },
    },
  },
  MuiStepLabel: {
    styleOverrides: {
      label: {
        fontFamily: tokens.font.body,
        fontSize: tokens.fontSize.sm,
        color: tokens.color.slate[400],
        '&.Mui-active': { color: '#F1F5F9', fontWeight: tokens.fontWeight.semibold },
        '&.Mui-completed': { color: tokens.color.emerald[400] },
      },
    },
  },
  MuiDrawer: {
    styleOverrides: {
      paper: {
        background: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.default}`,
        borderRadius: `${tokens.radius.xl} 0 0 ${tokens.radius.xl}`,
      },
    },
  },
  MuiDialog: {
    styleOverrides: {
      paper: {
        background: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.default}`,
        borderRadius: tokens.radius.xl,
        boxShadow: tokens.shadow.lg,
      },
    },
  },
  MuiDialogTitle: {
    styleOverrides: {
      root: {
        fontFamily: tokens.font.heading,
        fontWeight: tokens.fontWeight.bold,
        fontSize: tokens.fontSize.xl,
        padding: '24px 28px 12px',
      },
    },
  },
  MuiDialogContent: {
    styleOverrides: {
      root: { padding: '12px 28px 24px' },
    },
  },
  MuiAccordion: {
    styleOverrides: {
      root: {
        background: 'transparent',
        boxShadow: 'none',
        border: `1px solid ${tokens.color.border.subtle}`,
        borderRadius: `${tokens.radius.md} !important`,
        '&:before': { display: 'none' },
        '&.Mui-expanded': { margin: 0 },
      },
    },
  },
  MuiAccordionSummary: {
    styleOverrides: {
      root: {
        padding: '0 16px',
        minHeight: '48px',
        '&.Mui-expanded': { minHeight: '48px' },
        '& .MuiAccordionSummary-expandIconWrapper': { color: tokens.color.slate[400] },
      },
      content: { margin: '12px 0', '&.Mui-expanded': { margin: '12px 0' } },
    },
  },
  MuiAccordionDetails: {
    styleOverrides: {
      root: {
        padding: '0 16px 16px',
        borderTop: `1px solid ${tokens.color.border.subtle}`,
      },
    },
  },
  MuiBadge: {
    styleOverrides: {
      badge: {
        fontFamily: tokens.font.body,
        fontWeight: tokens.fontWeight.bold,
        fontSize: '0.6rem',
        height: '18px',
        minWidth: '18px',
        padding: '0 4px',
      },
    },
  },
  MuiSkeleton: {
    styleOverrides: {
      root: {
        backgroundColor: 'rgba(255,255,255,0.06)',
        borderRadius: tokens.radius.md,
        '&::after': {
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent)',
        },
      },
    },
  },
  MuiFormControlLabel: {
    styleOverrides: {
      label: {
        fontFamily: tokens.font.body,
        fontSize: tokens.fontSize.base,
        color: tokens.color.slate[400],
      },
    },
  },
  MuiSwitch: {
    styleOverrides: {
      thumb: { boxShadow: 'none' },
    },
  },
  MuiCircularProgress: {
    styleOverrides: {
      circle: { strokeLinecap: 'round' },
    },
  },
  MuiAppBar: {
    styleOverrides: {
      root: {
        background: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        boxShadow: '0 1px 3px rgba(15, 23, 42, 0.06)',
      },
    },
  },
  MuiToolbar: {
    styleOverrides: {
      root: { padding: '0 24px', minHeight: '60px !important' },
    },
  },
}

// ─── Theme ────────────────────────────────────────────────────────────────────

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main:  '#0F2E59', // Indian Navy Blue
      dark:  '#0A1E3A',
      light: '#1E40AF',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main:  '#059669', // India Emerald Green
      dark:  '#047857',
      light: '#10B981',
      contrastText: '#FFFFFF',
    },
    warning: {
      main:  '#D97706',
      dark:  '#B45309',
      light: '#F59E0B',
    },
    error: {
      main:  '#DC2626',
      dark:  '#991B1B',
      light: '#EF4444',
    },
    info: {
      main:  '#2563EB',
      dark:  '#1D4ED8',
      light: '#3B82F6',
    },
    success: {
      main:  '#059669',
      dark:  '#047857',
      light: '#10B981',
    },
    background: {
      default: '#F8FAFC',
      paper:   '#FFFFFF',
    },
    text: {
      primary:   '#0F172A',
      secondary: '#475569',
      disabled:  '#94A3B8',
    },
    divider: '#E2E8F0',
  },
  typography: {
    fontFamily: tokens.font.body,
    h1: { fontFamily: tokens.font.heading, fontWeight: 900, lineHeight: 1.1 },
    h2: { fontFamily: tokens.font.heading, fontWeight: 800, lineHeight: 1.15 },
    h3: { fontFamily: tokens.font.heading, fontWeight: 700, lineHeight: 1.2 },
    h4: { fontFamily: tokens.font.heading, fontWeight: 700, lineHeight: 1.25 },
    h5: { fontFamily: tokens.font.heading, fontWeight: 600, lineHeight: 1.3 },
    h6: { fontFamily: tokens.font.heading, fontWeight: 600, lineHeight: 1.35 },
    subtitle1: { fontWeight: 500, lineHeight: 1.5 },
    subtitle2: { fontWeight: 500, fontSize: '0.8rem', lineHeight: 1.5 },
    body1: { lineHeight: 1.7 },
    body2: { lineHeight: 1.65, fontSize: '0.875rem' },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.5,
      color: tokens.color.slate[400],
    },
    overline: {
      fontSize: '0.65rem',
      fontWeight: 700,
      letterSpacing: '0.1em',
      lineHeight: 1.5,
    },
    button: {
      fontWeight: 600,
      letterSpacing: '0.01em',
    },
  },
  shape: { borderRadius: 12 },
  spacing: 4, // 1 unit = 4px
  breakpoints: {
    values: { xs: 0, sm: 600, md: 900, lg: 1200, xl: 1536 },
  },
  components,
})

export default theme
