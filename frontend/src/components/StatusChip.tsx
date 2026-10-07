import React from 'react'
import { Chip, Tooltip, Box } from '@mui/material'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import HighlightOffIcon from '@mui/icons-material/HighlightOff'
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty'
import VerifiedUserOutlinedIcon from '@mui/icons-material/VerifiedUserOutlined'
import type { MatchStatus } from '../types'
import { tokens } from '../theme/tokens'

export interface StatusChipProps {
  status: MatchStatus | string
  size?: 'small' | 'medium'
  showIcon?: boolean
  tooltipText?: string
  className?: string
  onClick?: (e: React.MouseEvent) => void
}

interface StatusConfig {
  label: string
  color: string
  bg: string
  border: string
  defaultTooltip: string
  icon: React.ReactElement
}

const STATUS_CONFIG_MAP: Record<string, StatusConfig> = {
  MATCH: {
    label: '✓ MATCH',
    color: '#10B981',
    bg: 'rgba(16, 185, 129, 0.12)',
    border: 'rgba(16, 185, 129, 0.3)',
    defaultTooltip: 'All objective and deterministic eligibility conditions are satisfied.',
    icon: <CheckCircleOutlineIcon fontSize="inherit" />,
  },
  POTENTIAL_MATCH: {
    label: '⏳ POTENTIAL MATCH',
    color: '#F59E0B',
    bg: 'rgba(245, 158, 11, 0.12)',
    border: 'rgba(245, 158, 11, 0.3)',
    defaultTooltip: 'Key criteria met; minor missing attributes or pending verification may unlock full benefits.',
    icon: <HourglassEmptyIcon fontSize="inherit" />,
  },
  UNKNOWN: {
    label: '? UNKNOWN (DATA NEEDED)',
    color: '#94A3B8',
    bg: 'rgba(148, 163, 184, 0.12)',
    border: 'rgba(148, 163, 184, 0.3)',
    defaultTooltip: 'Additional business facts needed to evaluate deterministic rules for this scheme.',
    icon: <HelpOutlineIcon fontSize="inherit" />,
  },
  DOES_NOT_MATCH: {
    label: '✕ DOES NOT MATCH',
    color: '#EF4444',
    bg: 'rgba(239, 68, 68, 0.12)',
    border: 'rgba(239, 68, 68, 0.3)',
    defaultTooltip: 'One or more mandatory eligibility requirements are not met by the current profile.',
    icon: <HighlightOffIcon fontSize="inherit" />,
  },
  REQUIRES_OFFICIAL_VERIFICATION: {
    label: '🛡️ OFFICIAL VERIFICATION',
    color: '#3B82F6',
    bg: 'rgba(59, 130, 246, 0.12)',
    border: 'rgba(59, 130, 246, 0.3)',
    defaultTooltip: 'Rule criteria met; physical inspection, bank appraisal or portal verification required.',
    icon: <VerifiedUserOutlinedIcon fontSize="inherit" />,
  },
}


export const StatusChip: React.FC<StatusChipProps> = ({
  status,
  size = 'small',
  showIcon = true,
  tooltipText,
  className,
  onClick,
}) => {
  const normalizedKey = status ? status.toUpperCase().replace(/\s+/g, '_') : 'UNKNOWN'
  const config = STATUS_CONFIG_MAP[normalizedKey] || {
    label: status ? status.replace(/_/g, ' ') : 'Status',
    color: '#CBD5E1',
    bg: '#1A2235',
    border: 'rgba(255, 255, 255, 0.06)',
    defaultTooltip: `Current evaluation state: ${status}`,
    icon: <HelpOutlineIcon fontSize="inherit" />,
  }

  const chip = (
    <Chip
      size={size}
      icon={showIcon ? React.cloneElement(config.icon, { style: { color: config.color, fontSize: size === 'small' ? '0.9rem' : '1.1rem' } }) : undefined}
      label={
        <Box component="span" sx={{ fontWeight: 700, letterSpacing: '0.04em', fontSize: size === 'small' ? '0.7rem' : '0.8rem' }}>
          {config.label}
        </Box>
      }
      onClick={onClick}
      className={className}
      sx={{
        backgroundColor: config.bg,
        color: config.color,
        border: `1px solid ${config.border}`,
        borderRadius: tokens.radius.full,
        fontWeight: tokens.fontWeight.bold,
        cursor: onClick ? 'pointer' : 'default',
        transition: tokens.transition.fast,
        '&:hover': onClick
          ? {
              filter: 'brightness(1.15)',
              transform: 'translateY(-1px)',
            }
          : undefined,
        '& .MuiChip-label': {
          px: size === 'small' ? 1 : 1.5,
        },
      }}
      aria-label={`Eligibility status: ${config.label}. ${tooltipText || config.defaultTooltip}`}
    />

  )

  return (
    <Tooltip title={tooltipText || config.defaultTooltip} arrow placement="top">
      {chip}
    </Tooltip>
  )
}

export default StatusChip
