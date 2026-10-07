import React, { useState, useRef } from 'react'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Stack,
  Divider,
  MenuItem,
  InputAdornment,
  IconButton,
  Grid,
  Alert,
  Chip,
  alpha,
  Paper,
} from '@mui/material'
import BusinessIcon from '@mui/icons-material/Business'
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined'
import PolicyIcon from '@mui/icons-material/Policy'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import Visibility from '@mui/icons-material/Visibility'
import VisibilityOff from '@mui/icons-material/VisibilityOff'
import FlashOnIcon from '@mui/icons-material/FlashOn'
import KeyOutlinedIcon from '@mui/icons-material/KeyOutlined'
import { tokens } from '../theme/tokens'
import { toast } from 'sonner'

// Official Google Logo SVG
const GoogleIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" style={{ marginRight: 8, display: 'inline-block', verticalAlign: 'middle' }}>
    <path
      fill="#4285F4"
      d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17Z"
    />
    <path
      fill="#34A853"
      d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24Z"
    />
    <path
      fill="#FBBC05"
      d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 10.03 0 12s.45 3.82 1.25 5.42l4.03-3.15Z"
    />
    <path
      fill="#EA4335"
      d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98Z"
    />
  </svg>
)

type RegisterStep = 'EMAIL_INPUT' | 'MANUAL_FORM' | 'GOOGLE_OTP'

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState<RegisterStep>('EMAIL_INPUT')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [enterpriseName, setEnterpriseName] = useState('')
  const [msmeCategory, setMsmeCategory] = useState('small')
  const [sector, setSector] = useState('manufacturing')
  const [state, setState] = useState('Gujarat')
  const [udyam, setUdyam] = useState('')
  const [loading, setLoading] = useState(false)

  // 4-Digit OTP State for Google Emails
  const [otpDigits, setOtpDigits] = useState(['', '', '', ''])
  const inputRefs = [
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
  ]

  // Step 1: Submit Email
  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = email.trim().toLowerCase()
    if (!trimmed || !trimmed.includes('@')) {
      toast.error('Please enter a valid work or director email address.')
      return
    }

    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      // If Gmail / Google Email -> 4-Digit OTP flow
      if (trimmed.includes('@gmail.com') || trimmed.includes('@googlemail.com')) {
        setStep('GOOGLE_OTP')
        toast.info('Google email detected! We have dispatched a 4-digit OTP.')
      } else {
        // Manual Corporate / Enterprise email -> Password & details form
        setStep('MANUAL_FORM')
        toast.info('Manual enterprise email recognized. Please set your password & enterprise profile.')
      }
    }, 400)
  }

  // Step 2A: Manual Registration Submit
  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!password) {
      toast.error('Please provide a password for your account.')
      return
    }
    setLoading(true)
    setTimeout(() => {
      localStorage.setItem(
        'udyamniti_user',
        JSON.stringify({
          email,
          name: enterpriseName || 'Enterprise Member',
          category:
            msmeCategory === 'micro'
              ? 'Micro Enterprise'
              : msmeCategory === 'small'
              ? 'Small Enterprise'
              : 'Medium Enterprise',
          udyam: udyam || 'UDYAM-REG-2026-PENDING',
          sector,
          state,
          loginMethod: 'manual_registered',
          isLoggedIn: true,
        })
      )
      setLoading(false)
      toast.success('Registration successful! Redirecting to your Schemes Dashboard...')
      navigate('/dashboard')
    }, 600)
  }

  // Step 2B: OTP Digit change
  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) {
      value = value.slice(-1)
    }
    const newDigits = [...otpDigits]
    newDigits[index] = value
    setOtpDigits(newDigits)

    // Auto-focus next input
    if (value && index < 3) {
      inputRefs[index + 1].current?.focus()
    }
  }

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otpDigits[index] && index > 0) {
      inputRefs[index - 1].current?.focus()
    }
  }

  // Step 2B: OTP Submit (Google Email flow)
  const handleOtpSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const enteredOtp = otpDigits.join('')
    if (enteredOtp.length < 4) {
      toast.error('Please enter all 4 digits of the OTP.')
      return
    }

    setLoading(true)
    setTimeout(() => {
      const derivedName = email.split('@')[0].replace(/[._-]/g, ' ')
      localStorage.setItem(
        'udyamniti_user',
        JSON.stringify({
          email,
          name: enterpriseName || `${derivedName.toUpperCase()} Enterprises`,
          category: 'Small Enterprise',
          udyam: udyam || 'UDYAM-GJ-01-0023456',
          sector: sector || 'manufacturing',
          state: state || 'Gujarat',
          loginMethod: 'google_otp',
          isLoggedIn: true,
        })
      )
      setLoading(false)
      toast.success('Google OTP verified! Your enterprise account is active. Redirecting to Dashboard...')
      navigate('/dashboard')
    }, 500)
  }

  // 1-Click Google Sign In / Registration
  const handleGoogleOneClick = () => {
    setLoading(true)
    setTimeout(() => {
      localStorage.setItem(
        'udyamniti_user',
        JSON.stringify({
          email: 'director.msme@gmail.com',
          name: 'Verified MSME Director',
          category: 'Small Enterprise',
          udyam: 'UDYAM-GJ-01-0023456',
          sector: 'manufacturing',
          state: 'Gujarat',
          loginMethod: 'google_oauth',
          isLoggedIn: true,
        })
      )
      setLoading(false)
      toast.success('Google account verified! Redirecting to Dashboard...')
      navigate('/dashboard')
    }, 600)
  }

  const handleDemoFill = () => {
    setEnterpriseName('ABC Engineering & Exports Pvt. Ltd.')
    setMsmeCategory('small')
    setSector('manufacturing')
    setState('Gujarat')
    setUdyam('UDYAM-GJ-01-0023456')
    setEmail('contact@abcengineering.in')
    setPassword('demo1234')
    setStep('MANUAL_FORM')
    toast.info('Sample enterprise details populated.')
  }

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 120px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        px: 2,
        py: 6,
        background: `radial-gradient(ellipse at 50% 15%, ${alpha(tokens.color.violet[900], 0.22)} 0%, transparent 70%)`,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: step === 'MANUAL_FORM' ? 580 : 460 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 3.5 }}>
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 48,
              height: 48,
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
              boxShadow: '0 4px 16px rgba(99, 102, 241, 0.35)',
              mb: 1.5,
            }}
          >
            <PolicyIcon sx={{ color: '#FFFFFF', fontSize: 26 }} />
          </Box>
          <Typography
            variant="h5"
            sx={{
              fontWeight: 800,
              letterSpacing: '-0.02em',
              color: tokens.color.slate[50],
              fontSize: '1.45rem',
            }}
          >
            Create Your Enterprise Account
          </Typography>
          <Typography
            variant="body2"
            sx={{
              color: tokens.color.slate[400],
              mt: 0.5,
              fontSize: '0.875rem',
            }}
          >
            Instant access to verified Central & State Government incentives & RAG search
          </Typography>
        </Box>

        <Card
          sx={{
            bgcolor: tokens.color.surface.card,
            border: `1px solid ${tokens.color.border.subtle}`,
            borderRadius: '16px',
            boxShadow: '0 16px 40px rgba(0, 0, 0, 0.45)',
          }}
        >
          <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
            {/* ─── GOOGLE SIGN IN BUTTON ─── */}
            <Button
              fullWidth
              variant="outlined"
              onClick={handleGoogleOneClick}
              disabled={loading}
              sx={{
                bgcolor: '#FFFFFF',
                color: '#1E293B',
                borderColor: '#E2E8F0',
                py: 1.2,
                fontWeight: 600,
                fontSize: '0.9rem',
                borderRadius: '8px',
                textTransform: 'none',
                boxShadow: '0 2px 6px rgba(0, 0, 0, 0.08)',
                '&:hover': {
                  bgcolor: '#F8FAFC',
                  borderColor: '#CBD5E1',
                },
              }}
            >
              <GoogleIcon />
              Continue with Google
            </Button>

            <Divider sx={{ my: 3, borderColor: tokens.color.border.subtle }}>
              <Typography variant="caption" sx={{ color: tokens.color.slate[400], px: 1, fontWeight: 600 }}>
                OR REGISTER WITH EMAIL
              </Typography>
            </Divider>

            {/* ─── STEP 1: ENTER EMAIL ONLY ─── */}
            {step === 'EMAIL_INPUT' && (
              <form onSubmit={handleEmailSubmit}>
                <Stack spacing={2.5}>
                  <Box>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[300], fontWeight: 600, mb: 1, display: 'block' }}>
                      Enter Work or Director Email *
                    </Typography>
                    <TextField
                      fullWidth
                      size="small"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      placeholder="e.g. director@company.in or name@gmail.com"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <EmailOutlinedIcon sx={{ fontSize: 18, color: tokens.color.slate[400] }} />
                          </InputAdornment>
                        ),
                        sx: {
                          bgcolor: tokens.color.surface.elevated,
                          color: '#FFFFFF',
                          borderRadius: '8px',
                          fontSize: '0.9rem',
                        },
                      }}
                    />
                    <Typography variant="caption" sx={{ color: tokens.color.slate[500], display: 'block', mt: 0.8, fontSize: '0.74rem' }}>
                      Gmail addresses receive a 4-digit OTP. Manual/corporate emails unlock password setup.
                    </Typography>
                  </Box>

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading}
                    endIcon={<ArrowForwardIcon />}
                    sx={{
                      background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                      color: '#FFFFFF',
                      py: 1.25,
                      fontWeight: 700,
                      fontSize: '0.92rem',
                      borderRadius: '8px',
                      textTransform: 'none',
                      boxShadow: '0 4px 14px rgba(99, 102, 241, 0.4)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)',
                      },
                    }}
                  >
                    {loading ? 'Validating...' : 'Continue with Email →'}
                  </Button>
                </Stack>
              </form>
            )}

            {/* ─── STEP 2A: MANUAL REGISTERED EMAIL (PASSWORD & PROFILE) ─── */}
            {step === 'MANUAL_FORM' && (
              <form onSubmit={handleManualSubmit}>
                {/* Email Chip with Change Action */}
                <Paper
                  elevation={0}
                  sx={{
                    p: 1.5,
                    bgcolor: 'rgba(99, 102, 241, 0.08)',
                    border: '1px solid rgba(99, 102, 241, 0.25)',
                    borderRadius: '8px',
                    mb: 2.5,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <Stack direction="row" spacing={1} alignItems="center">
                    <EmailOutlinedIcon sx={{ fontSize: 18, color: '#818CF8' }} />
                    <Box>
                      <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', fontSize: '0.72rem' }}>
                        Enterprise Email
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600, fontSize: '0.85rem' }}>
                        {email}
                      </Typography>
                    </Box>
                  </Stack>
                  <Button
                    size="small"
                    onClick={() => setStep('EMAIL_INPUT')}
                    startIcon={<ArrowBackIcon sx={{ fontSize: 14 }} />}
                    sx={{ color: '#818CF8', fontSize: '0.75rem', textTransform: 'none', p: 0.5 }}
                  >
                    Change
                  </Button>
                </Paper>

                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[300], fontWeight: 600, mb: 0.5, display: 'block' }}>
                      Enterprise Legal Name *
                    </Typography>
                    <TextField
                      fullWidth
                      size="small"
                      value={enterpriseName}
                      onChange={(e) => setEnterpriseName(e.target.value)}
                      required
                      placeholder="e.g. Apex Precision Engineering Pvt. Ltd."
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <BusinessIcon sx={{ fontSize: 18, color: tokens.color.slate[400] }} />
                          </InputAdornment>
                        ),
                        sx: { bgcolor: tokens.color.surface.elevated, borderRadius: '8px', fontSize: '0.88rem' },
                      }}
                    />
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[300], fontWeight: 600, mb: 0.5, display: 'block' }}>
                      MSME Category *
                    </Typography>
                    <TextField
                      select
                      fullWidth
                      size="small"
                      value={msmeCategory}
                      onChange={(e) => setMsmeCategory(e.target.value)}
                      InputProps={{
                        sx: { bgcolor: tokens.color.surface.elevated, borderRadius: '8px', fontSize: '0.88rem' },
                      }}
                    >
                      <MenuItem value="micro">Micro (Turnover &le; ₹5 Cr)</MenuItem>
                      <MenuItem value="small">Small (Turnover &le; ₹50 Cr)</MenuItem>
                      <MenuItem value="medium">Medium (Turnover &le; ₹250 Cr)</MenuItem>
                    </TextField>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[300], fontWeight: 600, mb: 0.5, display: 'block' }}>
                      Sector / Focus *
                    </Typography>
                    <TextField
                      select
                      fullWidth
                      size="small"
                      value={sector}
                      onChange={(e) => setSector(e.target.value)}
                      InputProps={{
                        sx: { bgcolor: tokens.color.surface.elevated, borderRadius: '8px', fontSize: '0.88rem' },
                      }}
                    >
                      <MenuItem value="manufacturing">Precision Engineering & Mfg</MenuItem>
                      <MenuItem value="textiles">Textiles & Apparel (Surat Hub)</MenuItem>
                      <MenuItem value="export">Export & Foreign Trade (EPM)</MenuItem>
                      <MenuItem value="coir">Agro, Coir & Natural Fibres</MenuItem>
                      <MenuItem value="services">Services & IT Solutions</MenuItem>
                    </TextField>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[300], fontWeight: 600, mb: 0.5, display: 'block' }}>
                      Operational State *
                    </Typography>
                    <TextField
                      select
                      fullWidth
                      size="small"
                      value={state}
                      onChange={(e) => setState(e.target.value)}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LocationOnOutlinedIcon sx={{ fontSize: 18, color: tokens.color.slate[400] }} />
                          </InputAdornment>
                        ),
                        sx: { bgcolor: tokens.color.surface.elevated, borderRadius: '8px', fontSize: '0.88rem' },
                      }}
                    >
                      <MenuItem value="Gujarat">Gujarat (SER / GIDC)</MenuItem>
                      <MenuItem value="Maharashtra">Maharashtra</MenuItem>
                      <MenuItem value="Tamil Nadu">Tamil Nadu</MenuItem>
                      <MenuItem value="Karnataka">Karnataka</MenuItem>
                      <MenuItem value="Uttar Pradesh">Uttar Pradesh</MenuItem>
                      <MenuItem value="All India">All-India / Central Only</MenuItem>
                    </TextField>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[300], fontWeight: 600, mb: 0.5, display: 'block' }}>
                      Udyam Reg. Number (Optional)
                    </Typography>
                    <TextField
                      fullWidth
                      size="small"
                      value={udyam}
                      onChange={(e) => setUdyam(e.target.value)}
                      placeholder="UDYAM-XX-00-0000000"
                      InputProps={{
                        sx: { bgcolor: tokens.color.surface.elevated, borderRadius: '8px', fontSize: '0.88rem' },
                      }}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[300], fontWeight: 600, mb: 0.5, display: 'block' }}>
                      Account Password *
                    </Typography>
                    <TextField
                      fullWidth
                      size="small"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder="Create a strong account password"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LockOutlinedIcon sx={{ fontSize: 18, color: tokens.color.slate[400] }} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              size="small"
                              onClick={() => setShowPassword(!showPassword)}
                              edge="end"
                              sx={{ color: tokens.color.slate[400] }}
                            >
                              {showPassword ? <VisibilityOff sx={{ fontSize: 18 }} /> : <Visibility sx={{ fontSize: 18 }} />}
                            </IconButton>
                          </InputAdornment>
                        ),
                        sx: { bgcolor: tokens.color.surface.elevated, borderRadius: '8px', fontSize: '0.88rem' },
                      }}
                    />
                  </Grid>

                  <Grid item xs={12} sx={{ mt: 1 }}>
                    <Button
                      type="submit"
                      fullWidth
                      variant="contained"
                      disabled={loading}
                      endIcon={<ArrowForwardIcon />}
                      sx={{
                        background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                        color: '#FFFFFF',
                        py: 1.25,
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        borderRadius: '8px',
                        textTransform: 'none',
                        boxShadow: '0 4px 14px rgba(99, 102, 241, 0.4)',
                        '&:hover': { background: 'linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)' },
                      }}
                    >
                      {loading ? 'Creating Enterprise Account...' : 'Register & Launch Dashboard →'}
                    </Button>
                  </Grid>
                </Grid>
              </form>
            )}

            {/* ─── STEP 2B: GOOGLE EMAIL 4-DIGIT OTP VERIFICATION ─── */}
            {step === 'GOOGLE_OTP' && (
              <form onSubmit={handleOtpSubmit}>
                <Stack spacing={2.5}>
                  {/* Google Verified Banner */}
                  <Paper
                    elevation={0}
                    sx={{
                      p: 1.5,
                      bgcolor: 'rgba(66, 133, 244, 0.08)',
                      border: '1px solid rgba(66, 133, 244, 0.25)',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Stack direction="row" spacing={1} alignItems="center">
                      <GoogleIcon />
                      <Box>
                        <Typography variant="caption" sx={{ color: '#93C5FD', display: 'block', fontSize: '0.72rem' }}>
                          Google Account Detected
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600, fontSize: '0.85rem' }}>
                          {email}
                        </Typography>
                      </Box>
                    </Stack>
                    <Button
                      size="small"
                      onClick={() => setStep('EMAIL_INPUT')}
                      startIcon={<ArrowBackIcon sx={{ fontSize: 14 }} />}
                      sx={{ color: '#93C5FD', fontSize: '0.75rem', textTransform: 'none', p: 0.5 }}
                    >
                      Change
                    </Button>
                  </Paper>

                  <Box sx={{ textAlign: 'center' }}>
                    <KeyOutlinedIcon sx={{ color: '#818CF8', fontSize: 32, mb: 1 }} />
                    <Typography variant="subtitle1" sx={{ color: '#FFFFFF', fontWeight: 700 }}>
                      Enter 4-Digit Security OTP
                    </Typography>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mt: 0.5 }}>
                      A 4-digit verification code was sent to your Google mailbox.
                    </Typography>
                  </Box>

                  {/* 4 Digit Boxes */}
                  <Stack direction="row" spacing={2} justifyContent="center" sx={{ my: 1 }}>
                    {otpDigits.map((digit, index) => (
                      <Box
                        key={index}
                        component="input"
                        ref={inputRefs[index]}
                        type="text"
                        maxLength={1}
                        value={digit}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleOtpChange(index, e.target.value)}
                        onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => handleOtpKeyDown(index, e)}
                        autoFocus={index === 0}
                        sx={{
                          width: 54,
                          height: 58,
                          textAlign: 'center',
                          fontSize: '1.5rem',
                          fontWeight: 700,
                          color: '#FFFFFF',
                          bgcolor: tokens.color.surface.elevated,
                          border: digit ? '2px solid #6366F1' : '1px solid rgba(255, 255, 255, 0.15)',
                          borderRadius: '10px',
                          outline: 'none',
                          boxShadow: digit ? '0 0 12px rgba(99, 102, 241, 0.35)' : 'none',
                          transition: 'all 0.2s',
                          '&:focus': {
                            borderColor: '#818CF8',
                            boxShadow: '0 0 16px rgba(129, 140, 248, 0.45)',
                          },
                        }}
                      />
                    ))}
                  </Stack>

                  {/* Demo helper */}
                  <Stack direction="row" justifyContent="center" alignItems="center" spacing={1}>
                    <Chip
                      icon={<FlashOnIcon sx={{ fontSize: '14px !important', color: '#F59E0B !important' }} />}
                      label="Demo OTP: 4829"
                      size="small"
                      onClick={() => setOtpDigits(['4', '8', '2', '9'])}
                      sx={{
                        bgcolor: 'rgba(245, 158, 11, 0.1)',
                        color: '#FCD34D',
                        border: '1px solid rgba(245, 158, 11, 0.25)',
                        cursor: 'pointer',
                        fontSize: '0.75rem',
                        '&:hover': { bgcolor: 'rgba(245, 158, 11, 0.2)' },
                      }}
                    />
                  </Stack>

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading}
                    endIcon={<CheckCircleOutlineIcon />}
                    sx={{
                      background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                      color: '#FFFFFF',
                      py: 1.25,
                      fontWeight: 700,
                      fontSize: '0.92rem',
                      borderRadius: '8px',
                      textTransform: 'none',
                      boxShadow: '0 4px 14px rgba(16, 185, 129, 0.4)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                      },
                    }}
                  >
                    {loading ? 'Verifying OTP...' : 'Verify OTP & Launch Dashboard →'}
                  </Button>
                </Stack>
              </form>
            )}

            <Divider sx={{ my: 3, borderColor: tokens.color.border.subtle }}>
              <Typography variant="caption" sx={{ color: tokens.color.slate[500], px: 1 }}>
                ALREADY REGISTERED?
              </Typography>
            </Divider>

            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/login')}
              sx={{
                borderColor: tokens.color.border.subtle,
                color: tokens.color.slate[200],
                py: 0.9,
                fontWeight: 600,
                fontSize: '0.85rem',
                borderRadius: '8px',
                textTransform: 'none',
                '&:hover': {
                  borderColor: tokens.color.slate[500],
                  bgcolor: alpha(tokens.color.slate[700], 0.2),
                },
              }}
            >
              Sign In with Existing Account
            </Button>
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}

export default RegisterPage
