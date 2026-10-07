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
  Checkbox,
  FormControlLabel,
  InputAdornment,
  IconButton,
  Alert,
  Chip,
  alpha,
  Paper,
} from '@mui/material'
import Visibility from '@mui/icons-material/Visibility'
import VisibilityOff from '@mui/icons-material/VisibilityOff'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined'
import PolicyIcon from '@mui/icons-material/Policy'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import KeyOutlinedIcon from '@mui/icons-material/KeyOutlined'
import FlashOnIcon from '@mui/icons-material/FlashOn'
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
    if (!trimmed) {
      toast.error('Please enter a valid email address.')
      return
    }

    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      // If Gmail / Google Email -> 4-Digit OTP Flow
      if (trimmed.includes('@gmail.com') || trimmed.includes('@googlemail.com')) {
        setStep('GOOGLE_OTP')
        toast.info('Google account detected! A 4-digit OTP has been sent.')
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
          email,
          name: 'ABC Engineering Ltd.',
          category: 'Small Enterprise',
          udyam: 'UDYAM-GJ-01-0023456',
          loginMethod: 'manual_password',
          isLoggedIn: true,
        })
      )
      setLoading(false)
      toast.success('Welcome back, ABC Engineering! Redirecting to Dashboard...')
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
          email,
          name: email.split('@')[0].toUpperCase() + ' (Google Verified)',
          category: 'Small Enterprise',
          udyam: 'UDYAM-GJ-01-0023456',
          loginMethod: 'google_otp',
          isLoggedIn: true,
        })
      )
      setLoading(false)
      toast.success('Google OTP Verified! Redirecting to Schemes Dashboard...')
      navigate('/dashboard')
    }, 500)
  }

  // 1-Click Google Sign In Button
  const handleGoogleOneClick = () => {
    setLoading(true)
    setTimeout(() => {
      localStorage.setItem(
        'udyamniti_user',
        JSON.stringify({
          email: 'director@googlemail.com',
          name: 'Google Enterprise Member',
          category: 'Medium Enterprise',
          udyam: 'UDYAM-GJ-01-0023456',
          loginMethod: 'google_oauth',
          isLoggedIn: true,
        })
      )
      setLoading(false)
      toast.success('Google account verified! Redirecting to Dashboard...')
      navigate('/dashboard')
    }, 600)
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
        bgcolor: '#0A0F1E',
        background: `radial-gradient(ellipse at 50% 20%, ${alpha(tokens.color.violet[900], 0.25)} 0%, transparent 70%)`,
      }}
    >
      <Box sx={{ width: '100%', maxWidth: 460 }}>
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
              background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
              boxShadow: '0 4px 16px rgba(99, 102, 241, 0.35)',
              mb: 1.5,
              cursor: 'pointer',
            }}
          >
            <PolicyIcon sx={{ color: '#FFFFFF', fontSize: 26 }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 800, color: '#FFFFFF', fontSize: '1.5rem', letterSpacing: '-0.02em' }}>
            Sign in to UdyamNiti
          </Typography>
          <Typography variant="body2" sx={{ color: '#94A3B8', mt: 0.5 }}>
            Access official MSME schemes & policy intelligence
          </Typography>
        </Box>

        <Card
          sx={{
            bgcolor: '#1A2235',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            boxShadow: '0 16px 40px rgba(0, 0, 0, 0.5)',
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

            <Divider sx={{ my: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }}>
              <Typography variant="caption" sx={{ color: '#64748B', px: 1, fontWeight: 600 }}>
                OR WITH EMAIL
              </Typography>
            </Divider>

            {/* ─── STEP 1: ENTER EMAIL ONLY ─── */}
            {step === 'EMAIL_INPUT' && (
              <form onSubmit={handleEmailSubmit}>
                <Stack spacing={2.5}>
                  <Box>
                    <Typography variant="caption" sx={{ color: '#CBD5E1', fontWeight: 600, mb: 1, display: 'block' }}>
                      Enterprise or Director Email
                    </Typography>
                    <TextField
                      fullWidth
                      size="small"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      placeholder="name@company.in or name@gmail.com"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <EmailOutlinedIcon sx={{ fontSize: 18, color: '#94A3B8' }} />
                          </InputAdornment>
                        ),
                        sx: {
                          bgcolor: '#111827',
                          color: '#FFFFFF',
                          borderRadius: '8px',
                          fontSize: '0.9rem',
                        },
                      }}
                    />
                    <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mt: 0.8, fontSize: '0.74rem' }}>
                      Gmail users will receive a 4-digit OTP. Registered corporate emails use a password.
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
                    {loading ? 'Verifying Email...' : 'Continue with Email →'}
                  </Button>
                </Stack>
              </form>
            )}

            {/* ─── STEP 2A: PASSWORD AUTH (MANUAL REGISTERED EMAIL) ─── */}
            {step === 'PASSWORD_AUTH' && (
              <form onSubmit={handlePasswordSubmit}>
                <Stack spacing={2.5}>
                  {/* Selected Email Card */}
                  <Paper
                    elevation={0}
                    sx={{
                      p: 1.5,
                      bgcolor: 'rgba(16, 185, 129, 0.08)',
                      border: '1px solid rgba(16, 185, 129, 0.25)',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CheckCircleOutlineIcon sx={{ color: '#34D399', fontSize: 18 }} />
                      <Box>
                        <Typography variant="caption" sx={{ color: '#34D399', fontWeight: 700, display: 'block' }}>
                          Registered Enterprise Email
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600, fontSize: '0.85rem' }}>
                          {email}
                        </Typography>
                      </Box>
                    </Box>
                    <Button
                      size="small"
                      onClick={() => setStep('EMAIL_INPUT')}
                      sx={{ color: '#94A3B8', fontSize: '0.75rem', textTransform: 'none', p: 0.5 }}
                    >
                      Change
                    </Button>
                  </Paper>

                  <Box>
                    <Typography variant="caption" sx={{ color: '#CBD5E1', fontWeight: 600, mb: 1, display: 'block' }}>
                      Account Password
                    </Typography>
                    <TextField
                      fullWidth
                      size="small"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder="Enter your password"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LockOutlinedIcon sx={{ fontSize: 18, color: '#94A3B8' }} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              size="small"
                              onClick={() => setShowPassword(!showPassword)}
                              sx={{ color: '#94A3B8' }}
                            >
                              {showPassword ? <VisibilityOff sx={{ fontSize: 18 }} /> : <Visibility sx={{ fontSize: 18 }} />}
                            </IconButton>
                          </InputAdornment>
                        ),
                        sx: {
                          bgcolor: '#111827',
                          color: '#FFFFFF',
                          borderRadius: '8px',
                          fontSize: '0.9rem',
                        },
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
                          sx={{ color: '#64748B', '&.Mui-checked': { color: '#818CF8' } }}
                        />
                      }
                      label={<Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.8rem' }}>Remember device</Typography>}
                    />
                    <Chip
                      size="small"
                      icon={<VerifiedUserIcon sx={{ fontSize: 13, color: '#34D399' }} />}
                      label="SSL Secured"
                      sx={{
                        bgcolor: 'rgba(16, 185, 129, 0.1)',
                        color: '#34D399',
                        fontSize: '0.68rem',
                        height: 22,
                      }}
                    />
                  </Stack>

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
                    {loading ? 'Authenticating...' : 'Sign In & Go to Dashboard →'}
                  </Button>
                </Stack>
              </form>
            )}

            {/* ─── STEP 2B: 4-DIGIT OTP AUTH (GOOGLE EMAIL) ─── */}
            {step === 'GOOGLE_OTP' && (
              <form onSubmit={handleOtpSubmit}>
                <Stack spacing={2.5}>
                  {/* Google Email Detected Banner */}
                  <Paper
                    elevation={0}
                    sx={{
                      p: 1.5,
                      bgcolor: 'rgba(66, 133, 244, 0.1)',
                      border: '1px solid rgba(66, 133, 244, 0.3)',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <KeyOutlinedIcon sx={{ color: '#60A5FA', fontSize: 18 }} />
                      <Box>
                        <Typography variant="caption" sx={{ color: '#60A5FA', fontWeight: 700, display: 'block' }}>
                          Google Account Detected
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 600, fontSize: '0.85rem' }}>
                          {email}
                        </Typography>
                      </Box>
                    </Box>
                    <Button
                      size="small"
                      onClick={() => setStep('EMAIL_INPUT')}
                      sx={{ color: '#94A3B8', fontSize: '0.75rem', textTransform: 'none', p: 0.5 }}
                    >
                      Change
                    </Button>
                  </Paper>

                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="caption" sx={{ color: '#CBD5E1', fontWeight: 600, display: 'block', mb: 1 }}>
                      Enter 4-Digit Verification Code
                    </Typography>

                    {/* 4 Box Digits */}
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
                              color: '#FFFFFF',
                              padding: '12px 0',
                            },
                          }}
                          sx={{
                            width: 54,
                            bgcolor: '#111827',
                            borderRadius: '10px',
                            '& .MuiOutlinedInput-root': {
                              borderRadius: '10px',
                              '& fieldset': {
                                borderColor: otpDigits[idx] ? '#818CF8' : 'rgba(255, 255, 255, 0.15)',
                              },
                              '&:hover fieldset': {
                                borderColor: '#818CF8',
                              },
                            },
                          }}
                        />
                      ))}
                    </Stack>

                    <Chip
                      label="Demo OTP: 4829 (Or enter any 4 digits)"
                      size="small"
                      sx={{
                        bgcolor: 'rgba(245, 158, 11, 0.12)',
                        color: '#FCD34D',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        border: '1px solid rgba(245, 158, 11, 0.3)',
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
                    {loading ? 'Verifying OTP...' : 'Verify OTP & Open Dashboard →'}
                  </Button>
                </Stack>
              </form>
            )}

            <Divider sx={{ my: 3, borderColor: 'rgba(255, 255, 255, 0.1)' }}>
              <Typography variant="caption" sx={{ color: '#64748B', px: 1 }}>
                NEW TO UDYAMNITI?
              </Typography>
            </Divider>

            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/register')}
              sx={{
                borderColor: 'rgba(255, 255, 255, 0.15)',
                color: '#CBD5E1',
                py: 1,
                fontWeight: 600,
                fontSize: '0.86rem',
                borderRadius: '8px',
                textTransform: 'none',
                '&:hover': {
                  borderColor: '#818CF8',
                  bgcolor: 'rgba(255, 255, 255, 0.05)',
                },
              }}
            >
              Create New Enterprise Account
            </Button>
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}

export default LoginPage
