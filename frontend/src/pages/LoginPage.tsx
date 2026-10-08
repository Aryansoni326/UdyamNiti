import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Stack,
  Divider,
  Checkbox,
  FormControlLabel,
  InputAdornment,
  IconButton,
  Chip,
  Paper,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import Visibility from '@mui/icons-material/Visibility'
import VisibilityOff from '@mui/icons-material/VisibilityOff'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined'
import PolicyIcon from '@mui/icons-material/Policy'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import KeyOutlinedIcon from '@mui/icons-material/KeyOutlined'
import FlashOnIcon from '@mui/icons-material/FlashOn'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import { tokens } from '../theme/tokens'
import { toast } from 'sonner'
import { initiateGoogleSignIn, getGoogleClientId } from '../utils/googleAuth'
import { apiClient } from '../api/client'

// Official Google Logo SVG matching RegisterPage
const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" style={{ marginRight: 10, display: 'inline-block', verticalAlign: 'middle' }}>
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

type LoginStep = 'EMAIL_INPUT' | 'PASSWORD_AUTH' | 'GOOGLE_OTP'

export const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const [step, setStep] = useState<LoginStep>('EMAIL_INPUT')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(true)
  const [loading, setLoading] = useState(false)

  // 4-Digit OTP State
  const [otpDigits, setOtpDigits] = useState(['', '', '', ''])
  const inputRefs = [
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
  ]

  // Step 1: Check Email
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
      // If Gmail / Google Email -> 4-Digit OTP Flow
      if (trimmed.includes('@gmail.com') || trimmed.includes('@googlemail.com')) {
        setStep('GOOGLE_OTP')
        toast.info('Google email recognized! Enter the 4-digit verification code.')
      } else {
        // Manually registered corporate email -> Password Flow
        setStep('PASSWORD_AUTH')
        toast.info('Registered enterprise email recognized. Enter your password.')
      }
    }, 400)
  }

  // Step 2A: Password Submit (Manual Flow)
  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!password) {
      toast.error('Please enter your account password.')
      return
    }
    setLoading(true)
    setTimeout(() => {
      localStorage.setItem(
        'udyamniti_user',
        JSON.stringify({
          email: email.trim().toLowerCase(),
          name: 'ABC Precision Engineering Pvt. Ltd.',
          directorName: 'Rajesh Patel',
          category: 'Small Enterprise',
          sector: 'Precision Engineering & Mfg',
          state: 'Gujarat',
          udyam: 'UDYAM-GJ-01-0023456',
          loginMethod: 'manual_password',
          isLoggedIn: true,
        })
      )
      setLoading(false)
      toast.success('Welcome back! Redirecting to Dashboard...')
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

  // Step 2B: OTP Submit (Google Email Flow)
  const handleOtpSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const enteredOtp = otpDigits.join('')
    if (enteredOtp.length < 4) {
      toast.error('Please enter all 4 digits of the OTP.')
      return
    }

    setLoading(true)
    setTimeout(() => {
      localStorage.setItem(
        'udyamniti_user',
        JSON.stringify({
          email: email.trim().toLowerCase(),
          name: email.split('@')[0].toUpperCase() + ' (Google Verified)',
          directorName: 'Authorized Signatory',
          category: 'Small Enterprise',
          sector: 'Precision Engineering & Mfg',
          state: 'Gujarat',
          udyam: 'UDYAM-GJ-01-0023456',
          loginMethod: 'google_otp',
          isLoggedIn: true,
        })
      )
      setLoading(false)
      toast.success('Google OTP Verified! Redirecting to Dashboard...')
      navigate('/dashboard')
    }, 500)
  }

  const [clientIdModalOpen, setClientIdModalOpen] = useState(false)
  const [manualClientId, setManualClientId] = useState(() => getGoogleClientId())

  // Real Google Sign In (OAuth 2.0 via Google Identity Services)
  const handleGoogleOneClick = async (customId?: unknown) => {
    setLoading(true)
    try {
      const cleanId = typeof customId === 'string' && customId.trim() ? customId.trim() : undefined
      const profile = await initiateGoogleSignIn(cleanId)

      // Synchronize with Django backend session
      try {
        await apiClient.googleLogin({
          email: profile.email,
          name: profile.name,
          picture: profile.picture,
          google_id: profile.sub,
        })
      } catch (backendErr) {
        console.warn('Backend session note:', backendErr)
      }

      // Store authentic verified Google user in localStorage
      const userData = {
        email: profile.email,
        name: profile.name || profile.email.split('@')[0],
        directorName: profile.name,
        picture: profile.picture,
        googleId: profile.sub,
        category: 'Small Enterprise',
        sector: 'Precision Engineering & Mfg',
        state: 'Gujarat',
        udyam: 'UDYAM-GJ-01-0023456',
        loginMethod: 'google_oauth',
        isLoggedIn: true,
      }
      localStorage.setItem('udyamniti_user', JSON.stringify(userData))
      toast.success(`Welcome, ${profile.name}! Signed in with Google.`)
      navigate('/dashboard')
    } catch (err: any) {
      if (err?.message === 'MISSING_CLIENT_ID') {
        setClientIdModalOpen(true)
      } else {
        toast.error(err?.message || 'Google sign-in was cancelled or encountered an error.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleSaveManualClientId = () => {
    if (!manualClientId.trim()) {
      toast.error('Please paste your Google Client ID.')
      return
    }
    localStorage.setItem('udyamniti_google_client_id', manualClientId.trim())
    setClientIdModalOpen(false)
    handleGoogleOneClick(manualClientId.trim())
  }

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 120px)',
        bgcolor: '#F8FAFC',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        px: 2,
        py: { xs: 5, md: 8 },
      }}
    >
      <Container maxWidth="xs" disableGutters>
        {/* Header Logo */}
        <Box sx={{ textAlign: 'center', mb: 3.5 }}>
          <Box
            onClick={() => navigate('/')}
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 48,
              height: 48,
              borderRadius: '12px',
              bgcolor: '#0F2E59',
              boxShadow: '0 4px 14px rgba(15, 46, 89, 0.25)',
              mb: 1.5,
              cursor: 'pointer',
            }}
          >
            <PolicyIcon sx={{ color: '#FFFFFF', fontSize: 26 }} />
          </Box>
          <Typography
            variant="h4"
            sx={{
              fontFamily: tokens.font.heading,
              fontWeight: 800,
              color: '#0F2E59',
              fontSize: '1.65rem',
              letterSpacing: '-0.02em',
            }}
          >
            Sign in to UdyamNiti
          </Typography>
          <Typography variant="body2" sx={{ color: '#64748B', mt: 0.5 }}>
            Access official MSME schemes & policy intelligence
          </Typography>
        </Box>

        <Card
          sx={{
            bgcolor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '16px',
            boxShadow: '0 4px 20px rgba(15, 23, 42, 0.06)',
          }}
        >
          <CardContent sx={{ p: { xs: 3, sm: 4 } }}>
            {/* ─── GOOGLE SIGN IN BUTTON (MATCHING UI) ─── */}
            <Button
              fullWidth
              variant="outlined"
              onClick={() => handleGoogleOneClick()}
              disabled={loading}
              sx={{
                bgcolor: '#FFFFFF',
                color: '#1E293B',
                borderColor: '#CBD5E1',
                py: 1.3,
                fontWeight: 700,
                fontSize: '0.92rem',
                borderRadius: '8px',
                textTransform: 'none',
                boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
                transition: 'all 0.15s ease',
                '&:hover': {
                  bgcolor: '#F8FAFC',
                  borderColor: '#0F2E59',
                  boxShadow: '0 3px 8px rgba(0, 0, 0, 0.08)',
                },
              }}
            >
              <GoogleIcon />
              Sign in with Google
            </Button>

            <Divider sx={{ my: 3, borderColor: '#E2E8F0' }}>
              <Typography variant="caption" sx={{ color: '#64748B', px: 1, fontWeight: 700, letterSpacing: '0.04em' }}>
                OR WITH WORK EMAIL
              </Typography>
            </Divider>

            {/* ─── STEP 1: ENTER EMAIL ONLY ─── */}
            {step === 'EMAIL_INPUT' && (
              <form onSubmit={handleEmailSubmit}>
                <Stack spacing={2.5}>
                  <Box>
                    <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.8, display: 'block' }}>
                      Enterprise or Director Email
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
                            <EmailOutlinedIcon sx={{ fontSize: 18, color: '#64748B' }} />
                          </InputAdornment>
                        ),
                        sx: { bgcolor: '#F8FAFC', borderRadius: '8px', fontSize: '0.9rem' },
                      }}
                    />
                    <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mt: 0.8, fontSize: '0.74rem' }}>
                      Gmail users receive a 4-digit OTP. Registered corporate emails use password.
                    </Typography>
                  </Box>

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading}
                    endIcon={<ArrowForwardIcon />}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      py: 1.25,
                      fontWeight: 800,
                      fontSize: '0.92rem',
                      borderRadius: '8px',
                      textTransform: 'none',
                      boxShadow: '0 4px 14px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {loading ? 'Verifying...' : 'Continue with Email →'}
                  </Button>
                </Stack>
              </form>
            )}

            {/* ─── STEP 2A: PASSWORD AUTH ─── */}
            {step === 'PASSWORD_AUTH' && (
              <form onSubmit={handlePasswordSubmit}>
                <Stack spacing={2.5}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 1.5,
                      bgcolor: '#ECFDF5',
                      border: '1px solid #A7F3D0',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CheckCircleOutlineIcon sx={{ color: '#059669', fontSize: 18 }} />
                      <Box>
                        <Typography variant="caption" sx={{ color: '#065F46', fontWeight: 700, display: 'block' }}>
                          Registered Enterprise Email
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#0F2E59', fontWeight: 700, fontSize: '0.85rem' }}>
                          {email}
                        </Typography>
                      </Box>
                    </Box>
                    <Button
                      size="small"
                      onClick={() => setStep('EMAIL_INPUT')}
                      sx={{ color: '#64748B', fontSize: '0.75rem', textTransform: 'none', p: 0.5 }}
                    >
                      Change
                    </Button>
                  </Paper>

                  <Box>
                    <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.8, display: 'block' }}>
                      Account Password
                    </Typography>
                    <TextField
                      fullWidth
                      size="small"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder="Enter your account password"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LockOutlinedIcon sx={{ fontSize: 18, color: '#64748B' }} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton size="small" onClick={() => setShowPassword(!showPassword)}>
                              {showPassword ? <VisibilityOff sx={{ fontSize: 18 }} /> : <Visibility sx={{ fontSize: 18 }} />}
                            </IconButton>
                          </InputAdornment>
                        ),
                        sx: { bgcolor: '#F8FAFC', borderRadius: '8px', fontSize: '0.9rem' },
                      }}
                    />
                  </Box>

                  <Stack direction="row" alignItems="center" justifyContent="space-between">
                    <FormControlLabel
                      control={
                        <Checkbox
                          size="small"
                          checked={rememberMe}
                          onChange={(e) => setRememberMe(e.target.checked)}
                          sx={{ color: '#64748B', '&.Mui-checked': { color: '#0F2E59' } }}
                        />
                      }
                      label={<Typography variant="caption" sx={{ color: '#64748B', fontSize: '0.8rem' }}>Remember device</Typography>}
                    />
                    <Chip
                      size="small"
                      icon={<VerifiedUserIcon sx={{ fontSize: 13, color: '#059669' }} />}
                      label="SSL Secured"
                      sx={{ bgcolor: '#ECFDF5', color: '#065F46', fontSize: '0.68rem', height: 22 }}
                    />
                  </Stack>

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading}
                    endIcon={<ArrowForwardIcon />}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      py: 1.25,
                      fontWeight: 800,
                      fontSize: '0.92rem',
                      borderRadius: '8px',
                      textTransform: 'none',
                      boxShadow: '0 4px 14px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {loading ? 'Authenticating...' : 'Sign In & Go to Dashboard →'}
                  </Button>
                </Stack>
              </form>
            )}

            {/* ─── STEP 2B: 4-DIGIT OTP AUTH ─── */}
            {step === 'GOOGLE_OTP' && (
              <form onSubmit={handleOtpSubmit}>
                <Stack spacing={2.5}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 1.5,
                      bgcolor: '#EFF6FF',
                      border: '1px solid #BFDBFE',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <KeyOutlinedIcon sx={{ color: '#2563EB', fontSize: 18 }} />
                      <Box>
                        <Typography variant="caption" sx={{ color: '#1D4ED8', fontWeight: 700, display: 'block' }}>
                          Google Account Detected
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#0F2E59', fontWeight: 700, fontSize: '0.85rem' }}>
                          {email}
                        </Typography>
                      </Box>
                    </Box>
                    <Button
                      size="small"
                      onClick={() => setStep('EMAIL_INPUT')}
                      sx={{ color: '#64748B', fontSize: '0.75rem', textTransform: 'none', p: 0.5 }}
                    >
                      Change
                    </Button>
                  </Paper>

                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, display: 'block', mb: 1 }}>
                      Enter 4-Digit Security Code
                    </Typography>

                    <Stack direction="row" spacing={1.5} justifyContent="center" sx={{ my: 1.5 }}>
                      {[0, 1, 2, 3].map((idx) => (
                        <TextField
                          key={idx}
                          inputRef={inputRefs[idx]}
                          value={otpDigits[idx]}
                          onChange={(e) => handleOtpChange(idx, e.target.value)}
                          onKeyDown={(e) => handleOtpKeyDown(idx, e as any)}
                          type="text"
                          inputProps={{
                            maxLength: 1,
                            style: {
                              textAlign: 'center',
                              fontSize: '1.4rem',
                              fontWeight: 800,
                              color: '#0F2E59',
                              padding: '12px 0',
                            },
                          }}
                          sx={{
                            width: 54,
                            bgcolor: '#F8FAFC',
                            borderRadius: '10px',
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '10px',
                              '& fieldset': {
                                borderColor: otpDigits[idx] ? '#0F2E59' : '#CBD5E1',
                              },
                            },
                          }}
                        />
                      ))}
                    </Stack>

                    <Chip
                      icon={<FlashOnIcon sx={{ fontSize: '13px !important', color: '#D97706 !important' }} />}
                      label="Demo OTP: 4829 (Or any 4 digits)"
                      size="small"
                      onClick={() => setOtpDigits(['4', '8', '2', '9'])}
                      sx={{
                        bgcolor: '#FEF3C7',
                        color: '#B45309',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        mt: 0.5,
                      }}
                    />
                  </Box>

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={loading}
                    endIcon={<ArrowForwardIcon />}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      py: 1.25,
                      fontWeight: 800,
                      fontSize: '0.92rem',
                      borderRadius: '8px',
                      textTransform: 'none',
                      boxShadow: '0 4px 14px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {loading ? 'Verifying OTP...' : 'Verify & Open Dashboard →'}
                  </Button>
                </Stack>
              </form>
            )}

            <Divider sx={{ my: 3, borderColor: '#E2E8F0' }}>
              <Typography variant="caption" sx={{ color: '#64748B', px: 1 }}>
                NEW TO UDYAMNITI?
              </Typography>
            </Divider>

            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/register')}
              sx={{
                borderColor: '#CBD5E1',
                color: '#0F2E59',
                py: 1.1,
                fontWeight: 700,
                fontSize: '0.88rem',
                borderRadius: '8px',
                textTransform: 'none',
                '&:hover': {
                  borderColor: '#0F2E59',
                  bgcolor: '#F8FAFC',
                },
              }}
            >
              Create New Enterprise Account
            </Button>
          </CardContent>
        </Card>
      </Container>

      {/* Google Client ID Modal if not yet loaded from .env */}
      <Dialog
        open={clientIdModalOpen}
        onClose={() => setClientIdModalOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { borderRadius: '14px', p: 1 } }}
      >
        <DialogTitle sx={{ fontWeight: 800, color: '#0F2E59', pb: 1 }}>
          Connect Google OAuth Client ID
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: '#64748B', mb: 2 }}>
            To activate Google Sign-In, please paste your <b>Client ID</b> from Google Cloud Console.
            (You can also save it in <code>frontend/.env</code> as <code>VITE_GOOGLE_CLIENT_ID</code>).
          </Typography>
          <TextField
            fullWidth
            size="small"
            autoFocus
            label="Google Client ID"
            placeholder="e.g. 1234567890-abcdefg.apps.googleusercontent.com"
            value={manualClientId}
            onChange={(e) => setManualClientId(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setClientIdModalOpen(false)} sx={{ color: '#64748B' }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSaveManualClientId}
            sx={{ bgcolor: '#0F2E59', fontWeight: 700, borderRadius: '8px', px: 2.5, '&:hover': { bgcolor: '#0A1E3A' } }}
          >
            Save & Connect Google
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default LoginPage
