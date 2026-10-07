import { useState, useEffect } from 'react'
import {
  Box, Container, Typography, Grid, Chip, Paper,
  CircularProgress, Alert, Stack, Divider, Button,
} from '@mui/material'
import { motion } from 'framer-motion'
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import NewReleasesIcon from '@mui/icons-material/NewReleases'
import EventAvailableIcon from '@mui/icons-material/EventAvailable'
import { apiClient, PolicyChange } from '../api/client'

const CHANGE_TYPE_CONFIG: Record<string, { color: string; icon: JSX.Element; label: string }> = {
  benefit_increased: { color: '#10B981', icon: <TrendingUpIcon />, label: 'Benefit Increased' },
  benefit_decreased: { color: '#EF4444', icon: <TrendingDownIcon />, label: 'Benefit Decreased' },
  eligibility_broadened: { color: '#3B82F6', icon: <TrendingUpIcon />, label: 'Eligibility Broadened' },
  eligibility_restricted: { color: '#F59E0B', icon: <TrendingDownIcon />, label: 'Eligibility Restricted' },
  scheme_launched: { color: '#6C63FF', icon: <NewReleasesIcon />, label: 'New Scheme Launched' },
  scheme_closed: { color: '#EF4444', icon: <NewReleasesIcon />, label: 'Scheme Closed' },
  deadline_extended: { color: '#10B981', icon: <EventAvailableIcon />, label: 'Deadline Extended' },
  budget_revised: { color: '#8B5CF6', icon: <TrendingUpIcon />, label: 'Budget Revised' },
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}

export default function PolicyMonitor() {
  const [changes, setChanges] = useState<PolicyChange[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    apiClient.getPolicyChanges()
      .then(res => setChanges(res.data.results || res.data as any))
      .catch(() => setError('Failed to load policy changes'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <Box sx={{ bgcolor: '#0A0F1E', minHeight: '100vh', py: 6 }}>
      <Container maxWidth="lg">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <Box sx={{ mb: 6 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <NotificationsActiveIcon sx={{ color: '#6C63FF', fontSize: 32 }} />
              <Typography variant="h3" sx={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800 }}>
                Policy Monitor
              </Typography>
            </Box>
            <Typography variant="body1" sx={{ color: 'text.secondary', maxWidth: 600 }}>
              Track government scheme changes. When policies change, UdyamNiti re-evaluates your business
              profile and surfaces new opportunities or alerts.
            </Typography>
          </Box>

          {/* Alert banner */}
          {changes.length > 0 && (
            <Box sx={{
              p: 3, mb: 4, borderRadius: 3,
              background: 'linear-gradient(135deg, rgba(108, 99, 255, 0.15) 0%, rgba(16, 185, 129, 0.08) 100%)',
              border: '1px solid rgba(108, 99, 255, 0.3)',
              display: 'flex', alignItems: 'center', gap: 3,
            }}>
              <Box sx={{
                width: 48, height: 48, borderRadius: '50%',
                background: 'linear-gradient(135deg, #6C63FF, #10B981)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
              }}>
                <Typography sx={{ fontSize: '1.4rem' }}>🔔</Typography>
              </Box>
              <Box flex={1}>
                <Typography variant="h6" sx={{ fontFamily: 'Outfit, sans-serif', mb: 0.5 }}>
                  {changes.length} Policy Change{changes.length !== 1 ? 's' : ''} Detected
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  Recent changes to Central and Gujarat MSME schemes may affect your eligibility.
                  ABC Engineering has been re-evaluated — 2 new opportunities detected.
                </Typography>
              </Box>
              <Button variant="contained" size="small" sx={{ flexShrink: 0 }} id="re-evaluate-btn">
                Re-evaluate Profile
              </Button>
            </Box>
          )}

          {loading && <CircularProgress />}
          {error && <Alert severity="error">{error}</Alert>}

          <Stack spacing={2.5}>
            {changes.map((change, i) => {
              const cfg = CHANGE_TYPE_CONFIG[change.change_type] || {
                color: '#94A3B8',
                icon: <NotificationsActiveIcon />,
                label: change.change_type,
              }
              return (
                <motion.div
                  key={change.id}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: i * 0.1 }}
                >
                  <Paper sx={{
                    p: 3, borderRadius: 3,
                    background: 'rgba(26, 34, 53, 0.8)',
                    border: `1px solid ${cfg.color}25`,
                    borderLeft: `3px solid ${cfg.color}`,
                    '&:hover': { borderColor: `${cfg.color}45` },
                  }}>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                      <Box sx={{
                        width: 40, height: 40, borderRadius: 2, flexShrink: 0,
                        bgcolor: `${cfg.color}18`,
                        border: `1px solid ${cfg.color}30`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        '& svg': { color: cfg.color, fontSize: 20 },
                      }}>
                        {cfg.icon}
                      </Box>

                      <Box flex={1}>
                        <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap', mb: 0.75, alignItems: 'center' }}>
                          <Chip
                            label={change.scheme_code}
                            size="small"
                            sx={{ bgcolor: 'rgba(108, 99, 255, 0.15)', color: '#A5B4FC', fontWeight: 700, fontSize: '0.7rem' }}
                          />
                          <Chip
                            label={cfg.label}
                            size="small"
                            sx={{ bgcolor: `${cfg.color}18`, color: cfg.color, fontWeight: 600, fontSize: '0.7rem' }}
                          />
                          <Typography variant="caption" sx={{ color: 'text.muted', ml: 'auto' }}>
                            Effective: {change.effective_date ? formatDate(change.effective_date) : 'N/A'}
                          </Typography>
                        </Box>

                        <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5, fontSize: '0.95rem' }}>
                          {change.scheme_name}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1.5, lineHeight: 1.7 }}>
                          {change.change_summary}
                        </Typography>

                        {/* Before / After */}
                        {(change.old_value || change.new_value) && (
                          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                            {change.old_value && (
                              <Box sx={{
                                px: 2, py: 1, borderRadius: 1.5,
                                bgcolor: 'rgba(239, 68, 68, 0.08)',
                                border: '1px solid rgba(239, 68, 68, 0.2)',
                              }}>
                                <Typography variant="caption" sx={{ color: '#EF4444', display: 'block', fontWeight: 600 }}>BEFORE</Typography>
                                <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.8rem' }}>
                                  {JSON.stringify(change.old_value)}
                                </Typography>
                              </Box>
                            )}
                            {change.new_value && (
                              <Box sx={{
                                px: 2, py: 1, borderRadius: 1.5,
                                bgcolor: 'rgba(16, 185, 129, 0.08)',
                                border: '1px solid rgba(16, 185, 129, 0.2)',
                              }}>
                                <Typography variant="caption" sx={{ color: '#10B981', display: 'block', fontWeight: 600 }}>AFTER</Typography>
                                <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.8rem' }}>
                                  {JSON.stringify(change.new_value)}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        )}

                        {change.source && (
                          <Typography variant="caption" sx={{ color: 'text.muted', mt: 1, display: 'block' }}>
                            Source: {change.source}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </Paper>
                </motion.div>
              )
            })}
          </Stack>

          {changes.length === 0 && !loading && !error && (
            <Box sx={{ textAlign: 'center', py: 8, color: 'text.muted' }}>
              <NotificationsActiveIcon sx={{ fontSize: 64, mb: 2, opacity: 0.3 }} />
              <Typography variant="h6">No policy changes tracked yet</Typography>
              <Typography variant="body2">Run the seed_data command to load demo policy changes.</Typography>
            </Box>
          )}
        </motion.div>
      </Container>
    </Box>
  )
}
