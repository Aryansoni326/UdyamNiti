import React from 'react'
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Skeleton,
  Stack,
  Card,
  CardContent,
  alpha,
} from '@mui/material'
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline'
import InboxIcon from '@mui/icons-material/Inbox'
import RefreshIcon from '@mui/icons-material/Refresh'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import { tokens } from '../theme/tokens'

// ─── Loading State ────────────────────────────────────────────────────────────

export interface LoadingStateProps {
  message?: string
  submessage?: string
  progressSteps?: string[]
  currentStepIndex?: number
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Analyzing MSME Policy Landscape...',
  submessage = 'Evaluating deterministic eligibility conditions and cross-scheme relationships.',
  progressSteps,
  currentStepIndex = 0,
}) => {
  return (
    <Box
      sx={{
        py: 8,
        px: 3,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
      }}
    >
      <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
        <CircularProgress
          size={56}
          thickness={4}
          sx={{
            color: tokens.color.violet[500],
            animationDuration: '1.2s',
          }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <AutoAwesomeIcon sx={{ fontSize: 22, color: tokens.color.emerald[400] }} />
        </Box>
      </Box>

      <Typography variant="h6" sx={{ fontWeight: 700, color: tokens.color.slate[100], mb: 1 }}>
        {message}
      </Typography>
      <Typography variant="body2" sx={{ color: tokens.color.slate[400], maxWidth: 480, mb: 3 }}>
        {submessage}
      </Typography>

      {progressSteps && progressSteps.length > 0 && (
        <Stack spacing={1} sx={{ width: '100%', maxWidth: 360, textAlign: 'left' }}>
          {progressSteps.map((step, idx) => {
            const isCompleted = idx < currentStepIndex
            const isCurrent = idx === currentStepIndex
            return (
              <Box
                key={idx}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                  fontSize: '0.8rem',
                  color: isCompleted
                    ? tokens.color.emerald[400]
                    : isCurrent
                    ? tokens.color.violet[300]
                    : tokens.color.slate[600],
                  fontWeight: isCurrent ? 600 : 400,
                }}
              >
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: isCompleted
                      ? tokens.color.emerald[400]
                      : isCurrent
                      ? tokens.color.violet[400]
                      : tokens.color.slate[700],
                  }}
                />
                {step}
              </Box>
            )
          })}
        </Stack>
      )}
    </Box>
  )
}

// ─── Skeleton Card Loader ─────────────────────────────────────────────────────

export const SchemeCardSkeleton: React.FC = () => {
  return (
    <Card
      sx={{
        backgroundColor: tokens.color.surface.card,
        border: `1px solid ${tokens.color.border.subtle}`,
        borderRadius: tokens.radius.lg,
        p: 2.5,
      }}
    >
      <CardContent sx={{ p: 0 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
          <Box sx={{ width: '60%' }}>
            <Skeleton variant="text" width="90%" height={28} sx={{ bgcolor: 'rgba(255,255,255,0.06)' }} />
            <Skeleton variant="text" width="40%" height={18} sx={{ bgcolor: 'rgba(255,255,255,0.04)' }} />
          </Box>
          <Skeleton variant="rounded" width={80} height={24} sx={{ bgcolor: 'rgba(255,255,255,0.06)', borderRadius: tokens.radius.full }} />
        </Stack>
        <Skeleton variant="rounded" width="100%" height={56} sx={{ bgcolor: 'rgba(255,255,255,0.04)', mb: 2, borderRadius: tokens.radius.sm }} />
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Skeleton variant="rounded" width={110} height={22} sx={{ bgcolor: 'rgba(255,255,255,0.04)', borderRadius: tokens.radius.sm }} />
          <Skeleton variant="rounded" width={110} height={22} sx={{ bgcolor: 'rgba(255,255,255,0.04)', borderRadius: tokens.radius.sm }} />
        </Stack>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Skeleton variant="text" width={140} height={24} sx={{ bgcolor: 'rgba(255,255,255,0.06)' }} />
          <Skeleton variant="rounded" width={100} height={32} sx={{ bgcolor: 'rgba(255,255,255,0.06)', borderRadius: tokens.radius.sm }} />
        </Stack>
      </CardContent>
    </Card>
  )
}

// ─── Error State ──────────────────────────────────────────────────────────────

export interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  retryLabel?: string
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Unable to Load Data',
  message = 'An unexpected error occurred while communicating with the decision engine. Please verify connectivity or retry.',
  onRetry,
  retryLabel = 'Retry Request',
}) => {
  return (
    <Box
      sx={{
        py: 8,
        px: 3,
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <Box
        sx={{
          width: 56,
          height: 56,
          borderRadius: tokens.radius.full,
          backgroundColor: alpha(tokens.color.red[500], 0.12),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: tokens.color.red[400],
          mb: 2.5,
        }}
      >
        <ErrorOutlineIcon sx={{ fontSize: 32 }} />
      </Box>

      <Typography variant="h6" sx={{ fontWeight: 700, color: tokens.color.slate[100], mb: 1 }}>
        {title}
      </Typography>
      <Typography variant="body2" sx={{ color: tokens.color.slate[400], maxWidth: 440, mb: 3, lineHeight: 1.6 }}>
        {message}
      </Typography>

      {onRetry && (
        <Button
          variant="outlined"
          onClick={onRetry}
          startIcon={<RefreshIcon />}
          sx={{
            borderColor: tokens.color.border.subtle,
            color: tokens.color.slate[200],
            '&:hover': {
              borderColor: tokens.color.slate[300],
              backgroundColor: 'rgba(255,255,255,0.05)',
            },
          }}
        >
          {retryLabel}
        </Button>
      )}
    </Box>
  )
}

// ─── Empty State ──────────────────────────────────────────────────────────────

export interface EmptyStateProps {
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
  icon?: React.ReactElement
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  onAction,
  icon,
}) => {
  return (
    <Box
      sx={{
        py: 8,
        px: 3,
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        backgroundColor: alpha(tokens.color.surface.card, 0.4),
        border: `1px dashed ${tokens.color.border.subtle}`,
        borderRadius: tokens.radius.lg,
      }}
    >
      <Box
        sx={{
          width: 52,
          height: 52,
          borderRadius: tokens.radius.full,
          backgroundColor: 'rgba(255, 255, 255, 0.04)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: tokens.color.slate[500],
          mb: 2,
        }}
      >
        {icon || <InboxIcon sx={{ fontSize: 28 }} />}
      </Box>

      <Typography variant="subtitle1" sx={{ fontWeight: 700, color: tokens.color.slate[200], mb: 0.5 }}>
        {title}
      </Typography>
      <Typography variant="body2" sx={{ color: tokens.color.slate[400], maxWidth: 400, mb: actionLabel ? 2.5 : 0, lineHeight: 1.6 }}>
        {description}
      </Typography>

      {actionLabel && onAction && (
        <Button
          variant="contained"
          size="small"
          onClick={onAction}
          sx={{ fontWeight: 600, fontSize: '0.8rem' }}
        >
          {actionLabel}
        </Button>
      )}
    </Box>
  )
}
