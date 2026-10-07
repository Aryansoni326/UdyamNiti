import React from 'react'
import { Chip, Tooltip, Box } from '@mui/material'
import PersonOutlineIcon from '@mui/icons-material/PersonOutline'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import AccountBalanceOutlinedIcon from '@mui/icons-material/AccountBalanceOutlined'
import RuleOutlinedIcon from '@mui/icons-material/RuleOutlined'
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined'
import type { EvidenceSourceType } from '../types'
import { tokens } from '../theme/tokens'

export interface EvidenceBadgeProps {
  sourceType: EvidenceSourceType | string
  size?: 'small' | 'medium'
  showIcon?: boolean
  tooltipText?: string
  className?: string
}

interface EvidenceConfig {
  label: string
  color: string
  bg: string
  border: string
  defaultTooltip: string
  icon: React.ReactElement
}

const EVIDENCE_CONFIG_MAP: Record<string, EvidenceConfig> = {
  self_declared: {
    label: 'Self-declared',
    color: '#94A3B8',
    bg: 'rgba(148, 163, 184, 0.12)',
    border: 'rgba(148, 163, 184, 0.3)',
    defaultTooltip: 'Provided directly by enterprise owner during onboarding; pending document verification.',
    icon: <PersonOutlineIcon fontSize="inherit" />,
  },
  document_supported: {
    label: 'Document-supported',
    color: '#38BDF8',
    bg: 'rgba(56, 189, 248, 0.12)',
    border: 'rgba(56, 189, 248, 0.3)',
    defaultTooltip: 'Corroborated by uploaded MSME documents (e.g. Udyam cert, balance sheet, GSTIN).',
    icon: <DescriptionOutlinedIcon fontSize="inherit" />,
  },
  official_source: {
    label: 'Official source',
    color: '#10B981',
    bg: 'rgba(16, 185, 129, 0.12)',
    border: 'rgba(16, 185, 129, 0.3)',
    defaultTooltip: 'Retrieved from official Gazette Notification, Ministry Operational Guidelines, or Portal API.',
    icon: <AccountBalanceOutlinedIcon fontSize="inherit" />,
  },
  rule_matched: {
    label: 'Rule matched',
    color: '#A855F7',
    bg: 'rgba(168, 85, 247, 0.12)',
    border: 'rgba(168, 85, 247, 0.3)',
    defaultTooltip: 'Evaluated deterministically by the policy rule engine against exact numerical & categorical limits.',
    icon: <RuleOutlinedIcon fontSize="inherit" />,
  },
  ai_explanation: {
    label: 'AI explanation',
    color: '#6C63FF',
    bg: 'rgba(108, 99, 255, 0.12)',
    border: 'rgba(108, 99, 255, 0.3)',
    defaultTooltip: 'Synthesized by AI reasoning engine strictly grounded in verified policy clause evidence.',
    icon: <AutoAwesomeOutlinedIcon fontSize="inherit" />,
  },
  tier_1_gazette: {
    label: 'Tier 1: Gazette Notification',
    color: '#34D399',
    bg: 'rgba(16, 185, 129, 0.12)',
    border: 'rgba(16, 185, 129, 0.3)',
    defaultTooltip: 'Highest statutory authority: Published in the Official Gazette of India or State Gazette.',
    icon: <AccountBalanceOutlinedIcon fontSize="inherit" />,
  },
  tier_2_operational_guidelines: {
    label: 'Tier 2: Guidelines',
    color: '#38BDF8',
    bg: 'rgba(56, 189, 248, 0.12)',
    border: 'rgba(56, 189, 248, 0.3)',
    defaultTooltip: 'Operational guidelines and scheme implementation frameworks issued by the Ministry.',
    icon: <DescriptionOutlinedIcon fontSize="inherit" />,
  },
}


export const EvidenceBadge: React.FC<EvidenceBadgeProps> = ({
  sourceType,
  size = 'small',
  showIcon = true,
  tooltipText,
  className,
}) => {
  const normalizedKey = sourceType ? sourceType.toLowerCase().replace(/-/g, '_') : 'self_declared'
  const config = EVIDENCE_CONFIG_MAP[normalizedKey] || {
    label: sourceType ? sourceType.replace(/_/g, ' ') : 'Evidence',
    color: '#94A3B8',
    bg: '#1E293B',
    border: 'rgba(255, 255, 255, 0.1)',
    defaultTooltip: `Evidence provenance: ${sourceType || 'verified'}`,
    icon: <DescriptionOutlinedIcon fontSize="inherit" />,
  }

  const badge = (
    <Chip
      size={size}
      icon={showIcon ? React.cloneElement(config.icon, { style: { color: config.color, fontSize: size === 'small' ? '0.85rem' : '1rem' } }) : undefined}
      label={
        <Box component="span" sx={{ fontWeight: 600, fontSize: size === 'small' ? '0.68rem' : '0.75rem', letterSpacing: '0.02em' }}>
          {config.label}
        </Box>
      }
      className={className}
      sx={{
        backgroundColor: config.bg,
        color: config.color,
        border: `1px solid ${config.border}`,
        borderRadius: tokens.radius.sm,
        height: size === 'small' ? 22 : 28,
        '& .MuiChip-label': {
          px: 1,
        },
      }}
      aria-label={`Evidence provenance: ${config.label}`}
    />
  )

  return (
    <Tooltip title={tooltipText || config.defaultTooltip} arrow placement="top">
      {badge}
    </Tooltip>
  )
}

export default EvidenceBadge
