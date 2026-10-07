import React, { useState } from 'react'
import {
  Box,
  Typography,
  IconButton,
  Collapse,
  Button,
  Stack,
  alpha,
} from '@mui/material'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import EventAvailableIcon from '@mui/icons-material/EventAvailable'
import VerifiedIcon from '@mui/icons-material/Verified'
import type { PolicyCitation } from '../types'
import { tokens } from '../theme/tokens'

export interface SourceCitationProps {
  citation: PolicyCitation
  initiallyExpanded?: boolean
  className?: string
}

export const SourceCitation: React.FC<SourceCitationProps> = ({
  citation,
  initiallyExpanded = false,
  className,
}) => {
  const [expanded, setExpanded] = useState(initiallyExpanded)

  return (
    <Box
      className={className}
      sx={{
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        border: `1px solid ${alpha(tokens.color.border.subtle, 0.9)}`,
        borderRadius: tokens.radius.md,
        p: 2,
        transition: tokens.transition.base,
        '&:hover': {
          borderColor: alpha(tokens.color.violet[500], 0.35),
          boxShadow: `0 4px 16px rgba(0, 0, 0, 0.25)`,
        },
      }}
    >
      {/* Header Row */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <Stack direction="row" spacing={1.5} alignItems="center" sx={{ minWidth: 0 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 32,
              height: 32,
              borderRadius: tokens.radius.sm,
              backgroundColor: alpha(tokens.color.sky[500], 0.12),
              color: tokens.color.sky[400],
              flexShrink: 0,
            }}
          >
            <MenuBookIcon sx={{ fontSize: 18 }} />
          </Box>
          <Box sx={{ minWidth: 0 }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ flexWrap: 'wrap', gap: 0.5 }}>
              <Typography
                variant="subtitle2"
                sx={{
                  color: tokens.color.slate[200],
                  fontWeight: 600,
                  fontSize: '0.85rem',
                }}
              >
                {citation.document_name}
              </Typography>
              <Box
                component="span"
                sx={{
                  backgroundColor: alpha(tokens.color.violet[500], 0.15),
                  color: tokens.color.violet[300],
                  px: 1,
                  py: 0.2,
                  borderRadius: tokens.radius.xs,
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  letterSpacing: '0.04em',
                }}
              >
                Clause {citation.clause_or_section}
              </Box>
            </Stack>
            <Stack direction="row" spacing={2} sx={{ mt: 0.3, alignItems: 'center' }}>
              {citation.effective_date && (
                <Stack direction="row" spacing={0.5} alignItems="center">
                  <EventAvailableIcon sx={{ fontSize: 13, color: tokens.color.slate[500] }} />
                  <Typography variant="caption" sx={{ color: tokens.color.slate[400], fontSize: '0.72rem' }}>
                    Effective: {citation.effective_date}
                  </Typography>
                </Stack>
              )}
              {citation.last_verified_date && (
                <Stack direction="row" spacing={0.5} alignItems="center">
                  <VerifiedIcon sx={{ fontSize: 13, color: tokens.color.emerald[400] }} />
                  <Typography variant="caption" sx={{ color: tokens.color.emerald[400], fontSize: '0.72rem' }}>
                    Verified {citation.last_verified_date}
                  </Typography>
                </Stack>
              )}
            </Stack>
          </Box>
        </Stack>

        <IconButton
          size="small"
          aria-expanded={expanded}
          aria-label="Toggle citation details"
          sx={{
            color: tokens.color.slate[400],
            transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 200ms ease',
          }}
        >
          <ExpandMoreIcon fontSize="small" />
        </IconButton>
      </Box>

      {/* Expandable Excerpt & Official Document Handoff */}
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Box sx={{ mt: 2, pt: 1.5, borderTop: `1px solid ${alpha(tokens.color.border.subtle, 0.6)}` }}>
          <Typography
            variant="body2"
            sx={{
              fontStyle: 'italic',
              color: tokens.color.slate[300],
              fontSize: '0.82rem',
              lineHeight: 1.6,
              backgroundColor: alpha(tokens.color.surface.base, 0.6),
              p: 1.5,
              borderRadius: tokens.radius.sm,
              borderLeft: `3px solid ${tokens.color.sky[500]}`,
            }}
          >
            "{citation.excerpt}"
          </Typography>

          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1.5 }}>
            <Button
              size="small"
              variant="outlined"
              href={citation.official_url}
              target="_blank"
              rel="noopener noreferrer"
              endIcon={<OpenInNewIcon sx={{ fontSize: 14 }} />}
              sx={{
                fontSize: '0.75rem',
                borderColor: tokens.color.border.subtle,
                color: tokens.color.sky[400],
                py: 0.4,
                px: 1.5,
                '&:hover': {
                  borderColor: tokens.color.sky[400],
                  backgroundColor: alpha(tokens.color.sky[500], 0.08),
                },
              }}
            >
              Verify on Official Portal
            </Button>
          </Box>
        </Box>
      </Collapse>
    </Box>
  )
}

export default SourceCitation
