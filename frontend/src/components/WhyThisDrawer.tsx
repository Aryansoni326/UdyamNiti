import React from 'react'
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Divider,
  Stack,
  Alert,
  Button,
  alpha,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CancelIcon from '@mui/icons-material/Cancel'
import HelpIcon from '@mui/icons-material/Help'
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh'
import PolicyIcon from '@mui/icons-material/Policy'
import type { SchemeResult } from '../types'
import { StatusChip } from './StatusChip'
import { EvidenceBadge } from './EvidenceBadge'
import { SourceCitation } from './SourceCitation'
import { tokens } from '../theme/tokens'

export interface WhyThisDrawerProps {
  open: boolean
  onClose: () => void
  scheme: SchemeResult | null
  onUnlockClick?: (schemeCode: string) => void
}

export const WhyThisDrawer: React.FC<WhyThisDrawerProps> = ({
  open,
  onClose,
  scheme,
  onUnlockClick,
}) => {
  if (!scheme) return null

  const getConditionIcon = (status: 'PASS' | 'FAIL' | 'UNKNOWN') => {
    switch (status) {
      case 'PASS':
        return <CheckCircleIcon sx={{ color: tokens.color.emerald[400], fontSize: 18 }} />
      case 'FAIL':
        return <CancelIcon sx={{ color: tokens.color.red[400], fontSize: 18 }} />
      default:
        return <HelpIcon sx={{ color: tokens.color.amber[400], fontSize: 18 }} />
    }
  }

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          width: { xs: '100%', sm: 480, md: 540 },
          backgroundColor: tokens.color.surface.card,
          borderLeft: `1px solid ${tokens.color.border.subtle}`,
          boxShadow: '-8px 0 32px rgba(0, 0, 0, 0.5)',
          p: 0,
        },
      }}
    >
      {/* Drawer Header */}
      <Box
        sx={{
          p: 2.5,
          borderBottom: `1px solid ${tokens.color.border.subtle}`,
          backgroundColor: tokens.color.surface.overlay,
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: 2,
        }}
      >
        <Box sx={{ minWidth: 0 }}>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1, flexWrap: 'wrap', gap: 0.5 }}>
            <StatusChip status={scheme.status} />
            <EvidenceBadge sourceType="rule_matched" />
            <Box
              component="span"
              sx={{
                fontSize: '0.72rem',
                color: tokens.color.slate[400],
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              {scheme.level.replace('_', ' ')} • {scheme.scheme_code}
            </Box>
          </Stack>
          <Typography variant="h6" sx={{ fontWeight: 800, color: tokens.color.slate[100], lineHeight: 1.3 }}>
            Why "{scheme.name}"?
          </Typography>
          <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mt: 0.5 }}>
            Ministry: {scheme.ministry}
          </Typography>
        </Box>

        <IconButton
          onClick={onClose}
          size="small"
          aria-label="Close why this drawer"
          sx={{
            color: tokens.color.slate[400],
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            '&:hover': { backgroundColor: 'rgba(255, 255, 255, 0.1)', color: '#fff' },
          }}
        >
          <CloseIcon fontSize="small" />
        </IconButton>
      </Box>

      {/* Drawer Scrollable Body */}
      <Box sx={{ p: 3, overflowY: 'auto', flex: 1 }}>
        {/* Executive Summary */}
        <Box sx={{ mb: 3 }}>
          <Typography
            variant="overline"
            sx={{ color: tokens.color.violet[300], fontWeight: 700, letterSpacing: '0.08em' }}
          >
            Decision Rationale
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: tokens.color.slate[200],
              mt: 0.5,
              lineHeight: 1.65,
              p: 2,
              borderRadius: tokens.radius.md,
              backgroundColor: alpha(tokens.color.violet[500], 0.08),
              border: `1px solid ${alpha(tokens.color.violet[500], 0.2)}`,
            }}
          >
            {scheme.summary_explanation || scheme.description}
          </Typography>
        </Box>

        {/* Unlock Action Banner if present */}
        {(scheme.missing_info?.length > 0 || scheme.unlock_action) && (
          <Box sx={{ mb: 3 }}>
            <Alert
              severity="warning"
              icon={<AutoFixHighIcon sx={{ color: tokens.color.amber[400] }} />}
              sx={{
                backgroundColor: alpha(tokens.color.amber[500], 0.1),
                border: `1px solid ${alpha(tokens.color.amber[500], 0.3)}`,
                color: tokens.color.slate[200],
                '& .MuiAlert-message': { width: '100%' },
              }}
            >
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: tokens.color.amber[300] }}>
                Unlock Opportunity
              </Typography>
              <Typography variant="body2" sx={{ fontSize: '0.8rem', mt: 0.5 }}>
                {scheme.unlock_action ||
                  `Provide missing information (${scheme.missing_info.join(', ')}) to resolve UNKNOWN conditions and qualify.`}
              </Typography>
              {onUnlockClick && (
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => onUnlockClick(scheme.scheme_code)}
                  sx={{
                    mt: 1.5,
                    fontSize: '0.75rem',
                    backgroundColor: tokens.color.amber[500],
                    color: '#000',
                    fontWeight: 700,
                    '&:hover': { backgroundColor: tokens.color.amber[400] },
                  }}
                >
                  Resolve Missing Facts
                </Button>
              )}
            </Alert>
          </Box>
        )}

        {/* Deterministic Conditions Breakdown */}
        <Box sx={{ mb: 3 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, color: tokens.color.slate[100] }}>
              Deterministic Conditions Evaluated ({scheme.condition_results?.length || 0})
            </Typography>
          </Stack>

          <Stack spacing={1.5}>
            {scheme.condition_results?.map((cond, idx) => (
              <Box
                key={idx}
                sx={{
                  p: 1.8,
                  borderRadius: tokens.radius.md,
                  backgroundColor: alpha(tokens.color.surface.elevated, 0.5),
                  border: `1px solid ${tokens.color.border.subtle}`,
                  transition: tokens.transition.fast,
                  '&:hover': {
                    borderColor: alpha(tokens.color.slate[400], 0.3),
                  },
                }}
              >
                <Stack direction="row" spacing={1.5} alignItems="flex-start">
                  <Box sx={{ mt: 0.2, flexShrink: 0 }}>
                    {getConditionIcon(cond.status)}
                  </Box>
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap' }}>
                      <Typography variant="body2" sx={{ fontWeight: 600, color: tokens.color.slate[200] }}>
                        {cond.display_label || cond.rule_name}
                      </Typography>
                      {cond.importance === 'mandatory' && (
                        <Box
                          component="span"
                          sx={{
                            fontSize: '0.62rem',
                            fontWeight: 700,
                            color: tokens.color.red[400],
                            backgroundColor: alpha(tokens.color.red[500], 0.12),
                            px: 0.8,
                            py: 0.1,
                            borderRadius: tokens.radius.xs,
                            textTransform: 'uppercase',
                          }}
                        >
                          Mandatory
                        </Box>
                      )}
                    </Stack>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mt: 0.5 }}>
                      {cond.explanation}
                    </Typography>
                    {cond.source_clause && (
                      <Typography
                        variant="caption"
                        sx={{
                          display: 'block',
                          mt: 0.5,
                          fontSize: '0.7rem',
                          color: tokens.color.sky[400],
                        }}
                      >
                        Ref: Clause {cond.source_clause}
                      </Typography>
                    )}
                  </Box>
                </Stack>
              </Box>
            ))}

            {(!scheme.condition_results || scheme.condition_results.length === 0) && (
              <Typography variant="body2" sx={{ color: tokens.color.slate[500], fontStyle: 'italic' }}>
                No discrete conditions attached to this scheme definition.
              </Typography>
            )}
          </Stack>
        </Box>

        {/* Primary Evidence Citation */}
        {scheme.primary_citation && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, color: tokens.color.slate[100], mb: 1 }}>
              Official Evidence Source
            </Typography>
            <SourceCitation citation={scheme.primary_citation} initiallyExpanded={true} />
          </Box>
        )}

        <Divider sx={{ my: 2, borderColor: tokens.color.border.subtle }} />

        {/* Official Portal Handoff */}
        <Box sx={{ mb: 3 }}>
          <Button
            fullWidth
            variant="contained"
            href={scheme.official_portal_url}
            target="_blank"
            rel="noopener noreferrer"
            endIcon={<OpenInNewIcon />}
            sx={{
              py: 1.2,
              fontWeight: 700,
            }}
          >
            Apply on Official Scheme Portal
          </Button>
        </Box>

        {/* Trust & Legal Disclaimer */}
        <Box
          sx={{
            p: 1.5,
            borderRadius: tokens.radius.sm,
            backgroundColor: alpha(tokens.color.surface.base, 0.4),
            border: `1px dashed ${tokens.color.border.subtle}`,
            display: 'flex',
            gap: 1.2,
          }}
        >
          <PolicyIcon sx={{ color: tokens.color.slate[500], fontSize: 18, flexShrink: 0, mt: 0.3 }} />
          <Typography variant="caption" sx={{ color: tokens.color.slate[500], lineHeight: 1.5 }}>
            <strong>Trust Notice:</strong> Recommendations are derived from deterministic rules and official policy text. Official sanctioning rests with the respective ministry or nodal bank.
          </Typography>
        </Box>
      </Box>
    </Drawer>
  )
}

export default WhyThisDrawer
