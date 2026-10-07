
import { useState, useEffect } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import {
  Box, Container, Typography, Button, TextField,
  Chip, CircularProgress, Alert, Paper, Stack, Divider,
  LinearProgress,
} from '@mui/material'
import { motion } from 'framer-motion'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import LightbulbIcon from '@mui/icons-material/Lightbulb'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import PolicyIcon from '@mui/icons-material/Policy'
import { apiClient, BusinessProfile } from '../api/client'

const EXAMPLE_GOALS = [
  "I want to purchase a ₹50 lakh CNC machine to expand our precision machining production capacity",
  "We need ₹30 lakh working capital loan to fulfill an export order",
  "I want to upgrade our factory with energy-efficient equipment and get ISO 9001 certification",
  "We want to expand our textile unit with ₹1.5 crore investment in new looms",
  "I need funding to set up a food processing unit for export to the Gulf",
]

const ANALYSIS_STEPS = [
  { label: 'Parsing your goal intent...', duration: 800 },
  { label: 'Matching against 30+ government schemes...', duration: 1200 },
  { label: 'Evaluating eligibility conditions...', duration: 1000 },
  { label: 'Analyzing cross-scheme relationships...', duration: 800 },
  { label: 'Generating strategy narrative...', duration: 600 },
  { label: 'Building your action plan...', duration: 400 },
]

export default function GoalEntry() {
  const { profileId } = useParams<{ profileId: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const [profile, setProfile] = useState<BusinessProfile | null>(null)
  const [goalText, setGoalText] = useState(location.state?.prefillGoal || '')
  const [loading, setLoading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisStep, setAnalysisStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')

  useEffect(() => {
    if (profileId) {
      apiClient.getProfile(profileId)
        .then(res => setProfile(res.data))
        .catch(() => navigate('/'))
    }
  }, [profileId])

  const runAnalysisAnimation = async () => {
    setAnalyzing(true)
    let totalMs = 0
    const total = ANALYSIS_STEPS.reduce((s, step) => s + step.duration, 0)

    for (let i = 0; i < ANALYSIS_STEPS.length; i++) {
      setAnalysisStep(i)
      await new Promise(r => setTimeout(r, ANALYSIS_STEPS[i].duration))
      totalMs += ANALYSIS_STEPS[i].duration
      setProgress(Math.round((totalMs / total) * 85))
    }
  }

  const handleSubmit = async () => {
    if (!goalText.trim() || !profileId) return
    setLoading(true)
    setError('')

    // Run animation in parallel with actual API call
    runAnalysisAnimation()

    try {
      const res = await apiClient.submitGoal(profileId, goalText.trim())
      const { strategy_id } = res.data

      setProgress(100)
      await new Promise(r => setTimeout(r, 600))

      if (strategy_id) {
        navigate(`/strategy/${strategy_id}`)
      } else {
        setError('Strategy analysis failed. Please try again.')
        setAnalyzing(false)
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to analyze goal. Please try again.')
      setAnalyzing(false)
      setLoading(false)
    }
  }

  if (!profile && profileId) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress color="primary" />
      </Box>
    )
  }

  if (analyzing) {
    return (
      <Box sx={{
        minHeight: '100vh', bgcolor: '#0A0F1E', display: 'flex',
        alignItems: 'center', justifyContent: 'center',
        background: `
          radial-gradient(ellipse at 50% 30%, rgba(108, 99, 255, 0.15) 0%, transparent 60%),
          #0A0F1E
        `,
      }}>
        <Container maxWidth="sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{
                width: 80, height: 80, borderRadius: '50%',
                background: 'linear-gradient(135deg, #6C63FF, #10B981)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                mx: 'auto', mb: 4,
                boxShadow: '0 0 40px rgba(108, 99, 255, 0.4)',
                animation: 'pulse-glow 2s ease-in-out infinite',
              }}>
                <AutoAwesomeIcon sx={{ color: 'white', fontSize: 36 }} />
              </Box>

              <Typography variant="h4" sx={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, mb: 2 }}>
                Building Your Strategy
              </Typography>
              <Typography variant="body1" sx={{ color: 'text.secondary', mb: 4 }}>
                Analyzing goal against 30+ Central and Gujarat schemes
              </Typography>

              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                  mb: 3, height: 6, borderRadius: 3,
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(90deg, #6C63FF, #10B981)',
                    borderRadius: 3,
                  },
                }}
              />

              <Stack spacing={1.5}>
                {ANALYSIS_STEPS.map((step, i) => (
                  <Box
                    key={step.label}
                    sx={{
                      display: 'flex', alignItems: 'center', gap: 2,
                      p: 1.5, borderRadius: 2,
                      bgcolor: i === analysisStep ? 'rgba(108, 99, 255, 0.1)' : 'transparent',
                      border: '1px solid',
                      borderColor: i === analysisStep ? 'rgba(108, 99, 255, 0.3)' : 'transparent',
                      transition: 'all 0.3s ease',
                    }}
                  >
                    <Box sx={{
                      width: 20, height: 20, borderRadius: '50%', flexShrink: 0,
                      bgcolor: i < analysisStep ? '#10B981' : i === analysisStep ? '#6C63FF' : 'rgba(255,255,255,0.1)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      {i === analysisStep && (
                        <CircularProgress size={12} sx={{ color: 'white' }} />
                      )}
                      {i < analysisStep && (
                        <Typography sx={{ color: 'white', fontSize: '0.7rem' }}>✓</Typography>
                      )}
                    </Box>
                    <Typography
                      variant="body2"
                      sx={{
                        color: i === analysisStep ? 'text.primary' : i < analysisStep ? '#10B981' : 'text.muted',
                        fontWeight: i === analysisStep ? 600 : 400,
                      }}
                    >
                      {step.label}
                    </Typography>
                  </Box>
                ))}
              </Stack>

              <Typography variant="caption" sx={{ color: 'text.muted', mt: 3, display: 'block' }}>
                {Math.round(progress)}% complete
              </Typography>
            </Box>
          </motion.div>
        </Container>
      </Box>
    )
  }

  return (
    <Box sx={{
      minHeight: '100vh', bgcolor: '#0A0F1E',
      background: `
        radial-gradient(ellipse at 30% 20%, rgba(108, 99, 255, 0.1) 0%, transparent 50%),
        #0A0F1E
      `,
    }}>
      {/* Navbar */}
      <Box sx={{
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        py: 1.5, px: 4, display: 'flex', alignItems: 'center', gap: 1.5,
        bgcolor: 'rgba(10, 15, 30, 0.85)', backdropFilter: 'blur(12px)',
      }}>
        <PolicyIcon sx={{ color: '#6C63FF', fontSize: 22 }} />
        <Typography sx={{
          fontFamily: 'Outfit, sans-serif', fontWeight: 800,
          background: 'linear-gradient(135deg, #6C63FF 0%, #10B981 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>
          UdyamNiti
        </Typography>
      </Box>

      <Container maxWidth="md" sx={{ py: 8 }}>
        {/* Profile summary */}
        {profile && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
            <Paper sx={{
              p: 3, mb: 5,
              background: 'rgba(26, 34, 53, 0.8)',
              border: '1px solid rgba(108, 99, 255, 0.2)',
              borderRadius: 3,
            }}>
              <Typography variant="overline" sx={{ color: 'primary.light', letterSpacing: 2 }}>
                BUSINESS PROFILE LOADED
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 1 }}>
                <Typography variant="h6" sx={{ fontFamily: 'Outfit, sans-serif', fontWeight: 700 }}>
                  {profile.business_name}
                </Typography>
                <Chip
                  label={profile.msme_category.toUpperCase()}
                  size="small"
                  sx={{ bgcolor: 'rgba(16, 185, 129, 0.15)', color: '#10B981', fontWeight: 700 }}
                />
                <Chip
                  label={`${profile.state}`}
                  size="small"
                  sx={{ bgcolor: 'rgba(255,255,255,0.08)', color: 'text.secondary' }}
                />
                <Chip
                  label={profile.industry_sector}
                  size="small"
                  sx={{ bgcolor: 'rgba(255,255,255,0.08)', color: 'text.secondary' }}
                />
              </Box>
            </Paper>
          </motion.div>
        )}

        {/* Goal input */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Typography variant="h3" sx={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, mb: 1.5 }}>
            What is your business goal?
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary', mb: 4 }}>
            Describe what you're trying to achieve in plain language. Be specific about investment amounts,
            machinery, or expansion plans if relevant.
          </Typography>

          <Box sx={{
            background: 'rgba(26, 34, 53, 0.8)',
            border: '1px solid rgba(108, 99, 255, 0.3)',
            borderRadius: 3, p: 0.5, mb: 3,
            boxShadow: '0 0 40px rgba(108, 99, 255, 0.1)',
          }}>
            <TextField
              fullWidth multiline rows={4}
              placeholder="e.g. I want to purchase a ₹50 lakh CNC machine to expand our precision machining production..."
              value={goalText}
              onChange={e => setGoalText(e.target.value)}
              id="goal-text-input"
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: 'transparent', fontSize: '1.05rem',
                  '& fieldset': { border: 'none' },
                },
              }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 1.5, pb: 1.5 }}>
              <Typography variant="caption" sx={{ color: 'text.muted' }}>
                {goalText.length}/2000 characters
              </Typography>
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={loading || !goalText.trim()}
                endIcon={loading ? <CircularProgress size={16} color="inherit" /> : <ArrowForwardIcon />}
                id="submit-goal-btn"
                sx={{
                  background: 'linear-gradient(135deg, #6C63FF 0%, #4F46E5 100%)',
                  boxShadow: '0 4px 20px rgba(108, 99, 255, 0.4)',
                  px: 3,
                }}
              >
                {loading ? 'Analyzing...' : 'Analyze & Build Strategy'}
              </Button>
            </Box>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

          {/* Example goals */}
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <LightbulbIcon sx={{ color: '#F59E0B', fontSize: 18 }} />
              <Typography variant="overline" sx={{ color: 'text.muted', letterSpacing: 1.5 }}>
                EXAMPLE GOALS - CLICK TO USE
              </Typography>
            </Box>
            <Stack spacing={1.5}>
              {EXAMPLE_GOALS.map((eg, i) => (
                <Box
                  key={i}
                  onClick={() => setGoalText(eg)}
                  sx={{
                    p: 2, borderRadius: 2, cursor: 'pointer',
                    bgcolor: goalText === eg ? 'rgba(108, 99, 255, 0.1)' : 'rgba(255,255,255,0.03)',
                    border: '1px solid',
                    borderColor: goalText === eg ? 'rgba(108, 99, 255, 0.4)' : 'rgba(255,255,255,0.06)',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      bgcolor: 'rgba(108, 99, 255, 0.08)',
                      borderColor: 'rgba(108, 99, 255, 0.3)',
                    },
                  }}
                  id={`example-goal-${i}`}
                >
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    "{eg}"
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Box>
        </motion.div>
      </Container>
    </Box>
  )
}
