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
        backgroundColor: tokens.color.surface.base,
        WebkitFontSmoothing: 'antialiased',
        MozOsxFontSmoothing: 'grayscale',
        backgroundImage: tokens.gradient.glow,
        backgroundAttachment: 'fixed',
      },
      '::-webkit-scrollbar': { width: '6px', height: '6px' },
      '::-webkit-scrollbar-track': { background: tokens.color.surface.base },
      '::-webkit-scrollbar-thumb': {
        background: 'rgba(108, 99, 255, 0.35)',
        borderRadius: '3px',
      },
      '::-webkit-scrollbar-thumb:hover': { background: 'rgba(108, 99, 255, 0.6)' },
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
        background: tokens.gradient.hero,
        boxShadow: `0 4px 15px ${alpha(tokens.color.violet[500], 0.3)}`,
        '&:hover': {
          background: 'linear-gradient(135deg, #7C74FF 0%, #5F57F5 100%)',
          boxShadow: `0 6px 24px ${alpha(tokens.color.violet[500], 0.45)}`,
          transform: 'translateY(-1px)',
        },
        '&:active': { transform: 'translateY(0)' },
        '&.Mui-disabled': { background: 'rgba(255,255,255,0.08)', color: 'rgba(255,255,255,0.3)' },
      },
      containedSecondary: {
        background: `linear-gradient(135deg, ${tokens.color.emerald[500]} 0%, ${tokens.color.emerald[600]} 100%)`,
        boxShadow: `0 4px 15px ${alpha(tokens.color.emerald[500], 0.3)}`,
        '&:hover': {
          boxShadow: `0 6px 24px ${alpha(tokens.color.emerald[500], 0.4)}`,
          transform: 'translateY(-1px)',
        },
      },
      outlined: {
        borderColor: tokens.color.border.default,
        '&:hover': { borderColor: tokens.color.border.strong, background: tokens.color.glass.hover },
      },
      text: {
        '&:hover': { background: tokens.color.glass.hover },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        background: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.subtle}`,
        borderRadius: tokens.radius.lg,
        boxShadow: tokens.shadow.md,
        transition: tokens.transition.base,
        '&:hover': {
          background: tokens.color.surface.cardHover,
          borderColor: tokens.color.border.default,
          transform: 'translateY(-2px)',
          boxShadow: tokens.shadow.lg,
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
        background: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.subtle}`,
        borderRadius: tokens.radius.lg,
        backgroundImage: 'none',
      },
      elevation1: { boxShadow: tokens.shadow.md },
      elevation2: { boxShadow: tokens.shadow.lg },
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
          backgroundColor: tokens.color.glass.default,
          borderRadius: tokens.radius.md,
          fontFamily: tokens.font.body,
          transition: tokens.transition.base,
          '& fieldset': { borderColor: tokens.color.border.default },
          '&:hover fieldset': { borderColor: tokens.color.border.strong },
          '&.Mui-focused fieldset': {
            borderColor: tokens.color.violet[500],
            boxShadow: `0 0 0 3px ${alpha(tokens.color.violet[500], 0.15)}`,
          },
          '&.Mui-focused': { backgroundColor: tokens.color.glass.hover },
        },
        '& .MuiInputLabel-root': {
          fontFamily: tokens.font.body,
          fontSize: tokens.fontSize.base,
          color: tokens.color.slate[400],
        },
        '& .MuiInputLabel-root.Mui-focused': { color: tokens.color.violet[400] },
        '& .MuiInputBase-input': { color: '#F1F5F9' },
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
        background: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.default}`,
        boxShadow: tokens.shadow.lg,
      },
    },
  },
  MuiMenuItem: {
    styleOverrides: {
      root: {
        fontFamily: tokens.font.body,
        fontSize: tokens.fontSize.base,
        '&:hover': { background: tokens.color.glass.hover },
        '&.Mui-selected': {
          background: alpha(tokens.color.violet[500], 0.12),
          '&:hover': { background: alpha(tokens.color.violet[500], 0.18) },
        },
      },
    },
  },
  MuiTabs: {
    styleOverrides: {
      root: {
        borderBottom: `1px solid ${tokens.color.border.subtle}`,
        minHeight: '48px',
      },
      indicator: {
        background: tokens.gradient.hero,
        height: '2px',
        borderRadius: '2px 2px 0 0',
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
        color: tokens.color.slate[400],
        minHeight: '48px',
        padding: '12px 20px',
        transition: tokens.transition.fast,
        '&.Mui-selected': { color: '#F1F5F9' },
        '&:hover': { color: '#F1F5F9', background: tokens.color.glass.hover },
      },
    },
  },
  MuiLinearProgress: {
    styleOverrides: {
      root: {
        borderRadius: tokens.radius.full,
        backgroundColor: 'rgba(255,255,255,0.08)',
        height: '6px',
      },
      bar: { borderRadius: tokens.radius.full },
    },
  },
  MuiDivider: {
    styleOverrides: {
      root: { borderColor: tokens.color.border.subtle },
    },
  },
  MuiTooltip: {
    styleOverrides: {
      tooltip: {
        background: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.default}`,
        color: '#F1F5F9',
        fontFamily: tokens.font.body,
        fontSize: tokens.fontSize.sm,
        borderRadius: tokens.radius.md,
        boxShadow: tokens.shadow.lg,
        padding: '8px 12px',
        maxWidth: '300px',
        lineHeight: tokens.lineHeight.relaxed,
      },
      arrow: { color: tokens.color.surface.card },
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
        background: 'rgba(239, 68, 68, 0.08)',
        borderColor: 'rgba(239, 68, 68, 0.25)',
        color: '#fca5a5',
        '& .MuiAlert-icon': { color: tokens.color.red[500] },
      },
      standardWarning: {
        background: 'rgba(245, 158, 11, 0.08)',
        borderColor: 'rgba(245, 158, 11, 0.25)',
        color: '#fde68a',
        '& .MuiAlert-icon': { color: tokens.color.amber[500] },
      },
      standardSuccess: {
        background: 'rgba(16, 185, 129, 0.08)',
        borderColor: 'rgba(16, 185, 129, 0.25)',
        color: '#6ee7b7',
        '& .MuiAlert-icon': { color: tokens.color.emerald[500] },
      },
      standardInfo: {
        background: 'rgba(59, 130, 246, 0.08)',
        borderColor: 'rgba(59, 130, 246, 0.25)',
        color: '#93c5fd',
        '& .MuiAlert-icon': { color: tokens.color.sky[500] },
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
        background: tokens.color.surface.overlay,
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderBottom: `1px solid ${tokens.color.border.subtle}`,
        boxShadow: 'none',
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
    mode: 'dark',
    primary: {
      main:  tokens.color.violet[500],
      dark:  tokens.color.violet[700],
      light: tokens.color.violet[300],
      contrastText: '#FFFFFF',
    },
    secondary: {
      main:  tokens.color.emerald[500],
      dark:  tokens.color.emerald[600],
      light: tokens.color.emerald[300],
      contrastText: '#FFFFFF',
    },
    warning: {
      main:  tokens.color.amber[500],
      dark:  tokens.color.amber[600],
      light: tokens.color.amber[300],
    },
    error: {
      main:  tokens.color.red[500],
      dark:  tokens.color.red[600],
      light: tokens.color.red[400],
    },
    info: {
      main:  tokens.color.sky[500],
      dark:  tokens.color.sky[600],
      light: tokens.color.sky[400],
    },
    success: {
      main:  tokens.color.emerald[500],
      dark:  tokens.color.emerald[600],
      light: tokens.color.emerald[300],
    },
    background: {
      default: tokens.color.surface.base,
      paper:   tokens.color.surface.card,
    },
    text: {
      primary:   '#F1F5F9',
      secondary: tokens.color.slate[400],
      disabled:  tokens.color.slate[600],
    },
    divider: tokens.color.border.subtle,
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
