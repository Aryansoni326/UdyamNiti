import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Grid,
  Chip,
  Button,
  Paper,
  Stack,
  Divider,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Badge,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  alpha,
} from '@mui/material'
import { motion } from 'framer-motion'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import RefreshIcon from '@mui/icons-material/Refresh'
import DescriptionIcon from '@mui/icons-material/Description'
import FactCheckIcon from '@mui/icons-material/FactCheck'
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn'
import ShieldIcon from '@mui/icons-material/Shield'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import CheckIcon from '@mui/icons-material/Check'
import SendIcon from '@mui/icons-material/Send'
import TaskAltIcon from '@mui/icons-material/TaskAlt'
import { apiClient } from '../api/client'
import { tokens } from '../theme/tokens'
import { toast } from 'sonner'

export default function ApplicationWorkspacePage() {
  const { profileId, schemeId } = useParams<{ profileId: string; schemeId: string }>()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [workspace, setWorkspace] = useState<any>(null)
  const [confirmModalOpen, setConfirmModalOpen] = useState(false)

  const fetchWorkspace = async () => {
    if (!profileId || !schemeId) return
    try {
      const res = await apiClient.getOrCreateWorkspace(profileId, schemeId)
      setWorkspace(res.data)
    } catch (err: any) {
      toast.error('Failed to load application workspace')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWorkspace()
  }, [profileId, schemeId])

  const handleRefresh = async () => {
    if (!workspace) return
    setRefreshing(true)
    try {
      const res = await apiClient.refreshWorkspace(workspace.id)
      setWorkspace(res.data)
      toast.success('Workspace refreshed against latest profile facts and documents')
    } catch (err) {
      toast.error('Could not refresh workspace')
    } finally {
      setRefreshing(false)
    }
  }

  const handleMarkApplied = async () => {
    if (!workspace) return
    try {
      await apiClient.markWorkspaceApplied(workspace.id)
      setWorkspace((prev: any) => ({ ...prev, status: 'applied_external' }))
      setConfirmModalOpen(false)
      toast.success('Status updated: Marked as applied on official portal')
    } catch (err) {
      toast.error('Could not update application status')
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress sx={{ color: tokens.colors.brandPrimary }} />
      </Box>
    )
  }

  if (!workspace) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Alert severity="error">Application Workspace could not be loaded.</Alert>
      </Container>
    )
  }

  const data = workspace.workspace_data || {}
  const knownConditions = data.known_conditions || []
  const unknownConditions = data.unknown_conditions || []
  const disqualifiers = data.disqualifiers || []
  const documents = data.required_documents || []
  const infoFields = data.required_information || []
  const tasks = data.tasks || []

  // Progress metrics calculation
  const totalItems = (workspace.documents_total_count || 1) + (workspace.info_total_count || 1)
  const readyItems = (workspace.documents_ready_count || 0) + (workspace.info_ready_count || 0)
  const readinessPercent = Math.min(100, Math.round((readyItems / totalItems) * 100))

  return (
    <Box sx={{ bgcolor: tokens.colors.background, minHeight: '100vh', color: tokens.colors.textPrimary, pb: 10 }}>
      {/* Top Banner / Navigation */}
      <Box sx={{ borderBottom: `1px solid ${tokens.colors.border}`, bgcolor: tokens.colors.surfaceCard, py: 2 }}>
        <Container maxWidth="xl">
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate(-1)}
              sx={{ color: tokens.colors.textSecondary, textTransform: 'none' }}
            >
              Back to Strategy
            </Button>
            <Stack direction="row" spacing={2} alignItems="center">
              <Button
                variant="outlined"
                size="small"
                startIcon={<RefreshIcon className={refreshing ? 'animate-spin' : ''} />}
                onClick={handleRefresh}
                sx={{
                  borderColor: tokens.colors.border,
                  color: tokens.colors.textPrimary,
                  textTransform: 'none',
                }}
              >
                Refresh Readiness
              </Button>
              <Chip
                label={workspace.status === 'ready_for_portal' ? 'Ready for Portal' : workspace.status === 'applied_external' ? 'Applied on Portal' : 'Preparation In-Progress'}
                color={workspace.status === 'ready_for_portal' ? 'success' : workspace.status === 'applied_external' ? 'info' : 'warning'}
                variant="outlined"
                sx={{ fontWeight: 600 }}
              />
            </Stack>
          </Stack>
        </Container>
      </Box>

      {/* Main Workspace Header */}
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Box>
              <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1 }}>
                <Chip
                  label={workspace.scheme_code}
                  size="small"
                  sx={{ bgcolor: alpha(tokens.colors.brandPrimary, 0.15), color: tokens.colors.brandPrimary, fontWeight: 700 }}
                />
                <Typography variant="body2" sx={{ color: tokens.colors.textSecondary }}>
                  Enterprise: <strong>{workspace.business_name}</strong>
                </Typography>
              </Stack>
              <Typography variant="h4" sx={{ fontWeight: 800, mb: 1.5 }}>
                {workspace.scheme_name}
              </Typography>
              <Typography variant="body1" sx={{ color: tokens.colors.textSecondary, mb: 3 }}>
                Application Preparation Workspace — Consolidates facts, verified documents, and statutory prerequisites before filing on the official government portal.
              </Typography>
            </Box>
          </Grid>

          {/* Call to Action: Continue to Official Portal */}
          <Grid item xs={12} lg={4}>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                bgcolor: alpha(tokens.colors.brandPrimary, 0.08),
                border: `1px solid ${alpha(tokens.colors.brandPrimary, 0.3)}`,
                borderRadius: 3,
              }}
            >
              <Stack spacing={2}>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <ShieldIcon sx={{ color: tokens.colors.brandPrimary }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                    Official Government Route
                  </Typography>
                </Stack>
                <Typography variant="body2" sx={{ color: tokens.colors.textSecondary }}>
                  Portal: <strong>{workspace.official_portal_name}</strong>
                  <br />
                  Mode: {workspace.application_mode}
                </Typography>

                <Button
                  variant="contained"
                  fullWidth
                  size="large"
                  endIcon={<OpenInNewIcon />}
                  href={workspace.official_portal_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    bgcolor: tokens.colors.brandPrimary,
                    color: '#FFF',
                    fontWeight: 700,
                    textTransform: 'none',
                    py: 1.4,
                    borderRadius: 2,
                    boxShadow: `0 8px 20px ${alpha(tokens.colors.brandPrimary, 0.3)}`,
                    '&:hover': { bgcolor: alpha(tokens.colors.brandPrimary, 0.85) },
                  }}
                >
                  Continue to Official Portal
                </Button>

                {workspace.status !== 'applied_external' ? (
                  <Button
                    variant="text"
                    size="small"
                    startIcon={<CheckIcon />}
                    onClick={() => setConfirmModalOpen(true)}
                    sx={{ color: tokens.colors.textSecondary, textTransform: 'none' }}
                  >
                    I have already submitted on portal
                  </Button>
                ) : (
                  <Typography variant="caption" sx={{ color: '#10B981', textAlign: 'center', fontWeight: 600 }}>
                    ✓ Marked as submitted on external portal
                  </Typography>
                )}
              </Stack>
            </Paper>
          </Grid>
        </Grid>

        {/* Readiness Meter Card */}
        <Paper
          elevation={0}
          sx={{
            p: 3,
            mt: 3,
            mb: 4,
            bgcolor: tokens.colors.surfaceCard,
            border: `1px solid ${tokens.colors.border}`,
            borderRadius: 3,
          }}
        >
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={3}>
              <Typography variant="caption" sx={{ color: tokens.colors.textSecondary, textTransform: 'uppercase', letterSpacing: 1 }}>
                Filing Readiness Score
              </Typography>
              <Typography variant="h3" sx={{ fontWeight: 900, color: readinessPercent >= 80 ? '#10B981' : '#F59E0B' }}>
                {readinessPercent}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={readinessPercent}
                sx={{
                  mt: 1,
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'rgba(255,255,255,0.08)',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: readinessPercent >= 80 ? '#10B981' : '#F59E0B',
                  },
                }}
              />
            </Grid>

            <Grid item xs={6} sm={3} md={2}>
              <Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>
                Documents Ready
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                {workspace.documents_ready_count} / {workspace.documents_total_count}
              </Typography>
            </Grid>

            <Grid item xs={6} sm={3} md={2}>
              <Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>
                Form Facts Prepared
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                {workspace.info_ready_count} / {workspace.info_total_count}
              </Typography>
            </Grid>

            <Grid item xs={6} sm={3} md={2}>
              <Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>
                Tasks Completed
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                {workspace.tasks_completed_count} / {workspace.tasks_total_count}
              </Typography>
            </Grid>

            <Grid item xs={6} sm={3} md={3}>
              <Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>
                Unknowns Requiring Verification
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, color: workspace.unknowns_count > 0 ? '#F59E0B' : '#10B981' }}>
                {workspace.unknowns_count} condition{workspace.unknowns_count === 1 ? '' : 's'}
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        {/* Legal Disclaimer Notice */}
        <Alert
          severity="info"
          icon={<ShieldIcon />}
          sx={{
            mb: 4,
            bgcolor: alpha('#3B82F6', 0.08),
            border: `1px solid ${alpha('#3B82F6', 0.25)}`,
            color: tokens.colors.textPrimary,
            borderRadius: 2,
            '& .MuiAlert-icon': { color: '#3B82F6' },
          }}
        >
          <strong>Statutory Filing Invariant:</strong> {workspace.disclaimer_notice}
        </Alert>

        {/* 4-Column Preparation Sections */}
        <Grid container spacing={3}>
          {/* 1. Required Documents Checklist */}
          <Grid item xs={12} md={6}>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                height: '100%',
                bgcolor: tokens.colors.surfaceCard,
                border: `1px solid ${tokens.colors.border}`,
                borderRadius: 3,
              }}
            >
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <DescriptionIcon sx={{ color: tokens.colors.brandPrimary }} />
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    Required Documents ({workspace.documents_ready_count}/{workspace.documents_total_count})
                  </Typography>
                </Stack>
                <Chip size="small" label="Tamper-Proof Verification" variant="outlined" />
              </Stack>
              <Typography variant="body2" sx={{ color: tokens.colors.textSecondary, mb: 2 }}>
                Upload official PDFs to substantiate statutory criteria before opening portal.
              </Typography>

              <List sx={{ p: 0 }}>
                {documents.map((doc: any, idx: number) => (
                  <ListItem
                    key={idx}
                    sx={{
                      mb: 1.5,
                      bgcolor: alpha('#FFFFFF', 0.02),
                      border: `1px solid ${tokens.colors.border}`,
                      borderRadius: 2,
                      px: 2,
                      py: 1.5,
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      {doc.is_available ? (
                        <CheckCircleIcon sx={{ color: '#10B981' }} />
                      ) : (
                        <WarningAmberIcon sx={{ color: '#F59E0B' }} />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {doc.label}
                          </Typography>
                          {doc.is_mandatory && (
                            <Chip label="Mandatory" size="small" sx={{ height: 18, fontSize: '0.65rem', bgcolor: alpha('#EF4444', 0.15), color: '#EF4444' }} />
                          )}
                        </Stack>
                      }
                      secondary={
                        doc.is_available ? (
                          <Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>
                            Uploaded: {doc.document_title || doc.document_type} (Verified: {doc.is_verified ? 'Yes' : 'Pending Review'})
                          </Typography>
                        ) : (
                          <Typography variant="caption" sx={{ color: '#F59E0B' }}>
                            Missing — Document not yet uploaded for this profile
                          </Typography>
                        )
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* 2. Required Form Information */}
          <Grid item xs={12} md={6}>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                height: '100%',
                bgcolor: tokens.colors.surfaceCard,
                border: `1px solid ${tokens.colors.border}`,
                borderRadius: 3,
              }}
            >
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                <FactCheckIcon sx={{ color: tokens.colors.brandPrimary }} />
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Pre-Filled Application Information ({workspace.info_ready_count}/{workspace.info_total_count})
                </Typography>
              </Stack>
              <Typography variant="body2" sx={{ color: tokens.colors.textSecondary, mb: 2 }}>
                Exact figures and registration keys required when filling out the government online form.
              </Typography>

              <List sx={{ p: 0 }}>
                {infoFields.map((field: any, idx: number) => (
                  <ListItem
                    key={idx}
                    sx={{
                      mb: 1.5,
                      bgcolor: alpha('#FFFFFF', 0.02),
                      border: `1px solid ${tokens.colors.border}`,
                      borderRadius: 2,
                      px: 2,
                      py: 1.2,
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>
                      {field.is_prepared ? (
                        <CheckCircleIcon sx={{ color: '#10B981' }} />
                      ) : (
                        <HelpOutlineIcon sx={{ color: '#F59E0B' }} />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Stack direction="row" justifyContent="space-between" alignItems="center">
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {field.label}
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 700, color: field.is_prepared ? tokens.colors.textPrimary : '#F59E0B' }}>
                            {field.value || 'Not Provided'}
                          </Typography>
                        </Stack>
                      }
                      secondary={
                        <Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>
                          Source: {field.source}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* 3. Eligibility Conditions (Known vs Unknown) */}
          <Grid item xs={12} md={6}>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                height: '100%',
                bgcolor: tokens.colors.surfaceCard,
                border: `1px solid ${tokens.colors.border}`,
                borderRadius: 3,
              }}
            >
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                <TaskAltIcon sx={{ color: tokens.colors.brandPrimary }} />
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Statutory Rule Conditions
                </Typography>
              </Stack>

              {disqualifiers.length > 0 && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  <strong>Hard Disqualifier Detected:</strong> One or more mandatory conditions are not met.
                </Alert>
              )}

              <Typography variant="caption" sx={{ color: '#10B981', fontWeight: 700, textTransform: 'uppercase' }}>
                Verified Conditions ({knownConditions.length})
              </Typography>
              <List sx={{ p: 0, mb: 2, mt: 1 }}>
                {knownConditions.map((cond: any, idx: number) => (
                  <ListItem key={idx} sx={{ py: 0.8, px: 1.5, mb: 1, bgcolor: alpha('#10B981', 0.05), borderRadius: 1.5 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <CheckCircleIcon sx={{ fontSize: 18, color: '#10B981' }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" sx={{ fontWeight: 600 }}>{cond.rule_name}</Typography>}
                      secondary={<Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>Field: {cond.field_path} ({cond.operator} {cond.expected})</Typography>}
                    />
                  </ListItem>
                ))}
              </List>

              {unknownConditions.length > 0 && (
                <>
                  <Typography variant="caption" sx={{ color: '#F59E0B', fontWeight: 700, textTransform: 'uppercase' }}>
                    Unknowns Requiring Fact Verification ({unknownConditions.length})
                  </Typography>
                  <List sx={{ p: 0, mt: 1 }}>
                    {unknownConditions.map((cond: any, idx: number) => (
                      <ListItem key={idx} sx={{ py: 0.8, px: 1.5, mb: 1, bgcolor: alpha('#F59E0B', 0.05), borderRadius: 1.5 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <HelpOutlineIcon sx={{ fontSize: 18, color: '#F59E0B' }} />
                        </ListItemIcon>
                        <ListItemText
                          primary={<Typography variant="body2" sx={{ fontWeight: 600 }}>{cond.rule_name}</Typography>}
                          secondary={<Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>Missing fact: {cond.field_path}</Typography>}
                        />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
            </Paper>
          </Grid>

          {/* 4. Action Plan Tasks */}
          <Grid item xs={12} md={6}>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                height: '100%',
                bgcolor: tokens.colors.surfaceCard,
                border: `1px solid ${tokens.colors.border}`,
                borderRadius: 3,
              }}
            >
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                <AssignmentTurnedInIcon sx={{ color: tokens.colors.brandPrimary }} />
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Preparation Tasks ({workspace.tasks_completed_count}/{workspace.tasks_total_count})
                </Typography>
              </Stack>
              <Typography variant="body2" sx={{ color: tokens.colors.textSecondary, mb: 2 }}>
                Action items that must be executed to prepare quotations, certifications, and project reports.
              </Typography>

              <List sx={{ p: 0 }}>
                {tasks.length === 0 ? (
                  <Typography variant="body2" sx={{ color: tokens.colors.textSecondary, fontStyle: 'italic' }}>
                    No pending tasks for this scheme.
                  </Typography>
                ) : (
                  tasks.map((task: any, idx: number) => (
                    <ListItem
                      key={idx}
                      sx={{
                        mb: 1.5,
                        bgcolor: alpha('#FFFFFF', 0.02),
                        border: `1px solid ${tokens.colors.border}`,
                        borderRadius: 2,
                        px: 2,
                        py: 1.5,
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        {task.is_completed ? (
                          <CheckCircleIcon sx={{ color: '#10B981' }} />
                        ) : (
                          <AssignmentTurnedInIcon sx={{ color: tokens.colors.textSecondary }} />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {task.title}
                          </Typography>
                        }
                        secondary={
                          <Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>
                            {task.rationale}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))
                )}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Confirmation Modal for Marking External Submission */}
      <Dialog
        open={confirmModalOpen}
        onClose={() => setConfirmModalOpen(false)}
        PaperProps={{
          sx: {
            bgcolor: tokens.colors.surfaceCard,
            color: tokens.colors.textPrimary,
            border: `1px solid ${tokens.colors.border}`,
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle sx={{ fontWeight: 700 }}>Confirm Portal Submission</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: tokens.colors.textSecondary, mb: 2 }}>
            Have you completed filing the application on <strong>{workspace.official_portal_name}</strong> and received an application acknowledgement / reference number?
          </Typography>
          <Typography variant="caption" sx={{ color: tokens.colors.textSecondary }}>
            Notice: Marking this as submitted updates your internal strategy tracker. It does not replace the official departmental audit.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setConfirmModalOpen(false)} sx={{ color: tokens.colors.textSecondary, textTransform: 'none' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleMarkApplied}
            sx={{ bgcolor: tokens.colors.brandPrimary, textTransform: 'none', fontWeight: 600 }}
          >
            Confirm Submission
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
