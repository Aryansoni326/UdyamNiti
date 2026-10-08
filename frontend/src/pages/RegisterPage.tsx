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
  MenuItem,
  InputAdornment,
  IconButton,
  Grid,
  Chip,
  Paper,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import BusinessIcon from '@mui/icons-material/Business'
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined'
import PolicyIcon from '@mui/icons-material/Policy'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import Visibility from '@mui/icons-material/Visibility'
import VisibilityOff from '@mui/icons-material/VisibilityOff'
import KeyOutlinedIcon from '@mui/icons-material/KeyOutlined'
import PhoneOutlinedIcon from '@mui/icons-material/PhoneOutlined'
import PersonOutlineIcon from '@mui/icons-material/PersonOutline'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import { tokens } from '../theme/tokens'
import { toast } from 'sonner'
import { initiateGoogleSignIn } from '../utils/googleAuth'
import { apiClient } from '../api/client'

// Official Google Logo SVG
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

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState<'FORM' | 'GOOGLE_OTP'>('FORM')

  // Form Fields - Comprehensive MSME Profile Questions
  const [enterpriseName, setEnterpriseName] = useState('')
  const [constitution, setConstitution] = useState('Private Limited Company')
  const [udyam, setUdyam] = useState('')
  
  // Turnover & Investment (MSMED Act Criteria)
  const [turnover, setTurnover] = useState('1_to_5_cr')
  const [investment, setInvestment] = useState('25l_to_1cr')
  const [msmeCategory, setMsmeCategory] = useState('micro')
  const [businessAge, setBusinessAge] = useState('3')

  // Sector & Geography
  const [industry, setIndustry] = useState('Precision Engineering & Mfg')
  const [state, setState] = useState('Gujarat')
  const [district, setDistrict] = useState('Surat')

  // Special Beneficiary Criteria
  const [beneficiaryCategory, setBeneficiaryCategory] = useState('General')
  const [exportStatus, setExportStatus] = useState('IEC Holder / Active Exporter')

  // Director Credentials
  const [directorName, setDirectorName] = useState('')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  // 4-Digit OTP State
  const [otpDigits, setOtpDigits] = useState(['', '', '', ''])
  const inputRefs = [
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
  ]

  // Auto-calculate suggested MSME category based on turnover & investment
  const handleTurnoverChange = (val: string) => {
    setTurnover(val)
    if (val === 'up_to_1_cr' || val === '1_to_5_cr') {
      setMsmeCategory('micro')
    } else if (val === '5_to_50_cr') {
      setMsmeCategory('small')
    } else {
      setMsmeCategory('medium')
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!enterpriseName.trim()) {
      toast.error('Please enter enterprise legal name.')
      return
    }
    if (!email.trim() || !email.includes('@')) {
      toast.error('Please enter a valid work or director email address.')
      return
    }
    if (!password) {
      toast.error('Please create an account password.')
      return
    }

    setLoading(true)
    setTimeout(() => {
      const userData = {
        name: enterpriseName.trim(),
        directorName: directorName || 'Director',
        email: email.trim().toLowerCase(),
        phone,
        constitution,
        category:
          msmeCategory === 'micro'
            ? 'Micro Enterprise'
            : msmeCategory === 'small'
            ? 'Small Enterprise'
            : 'Medium Enterprise',
        turnover,
        investment,
        sector: industry,
        state,
        district,
        beneficiaryCategory,
        exportStatus,
        udyam: udyam || 'UDYAM-GJ-01-0023456',
        isLoggedIn: true,
        loginMethod: 'registered_form',
      }
      localStorage.setItem('udyamniti_user', JSON.stringify(userData))
      setLoading(false)
      toast.success(`Enterprise registered! Welcome, ${enterpriseName}.`)
      navigate('/dashboard')
    }, 600)
  }

  const [clientIdModalOpen, setClientIdModalOpen] = useState(false)
  const [manualClientId, setManualClientId] = useState('')

  // Real Google Sign Up (OAuth 2.0 via Google Identity Services)
  const handleGoogleOneClick = async (customId?: string) => {
    setLoading(true)
    try {
      const profile = await initiateGoogleSignIn(customId)

      // Synchronize with Django backend session
      try {
        await apiClient.googleLogin({
          email: profile.email,
          name: profile.name,
          picture: profile.picture,
          google_id: profile.sub,
        })
      } catch (backendErr) {
        console.warn('Backend registration note:', backendErr)
      }

      // Store authentic verified Google user in localStorage
      const googleUser = {
        name: profile.name || profile.email.split('@')[0],
        directorName: profile.name,
        email: profile.email,
        phone: '+91 98250 12345',
        constitution: 'Private Limited Company',
        category: 'Small Enterprise',
        turnover: '5_to_50_cr',
        investment: '1cr_to_10cr',
        sector: 'Precision Engineering & Mfg',
        state: 'Gujarat',
        district: 'Surat',
        beneficiaryCategory: 'General',
        exportStatus: 'IEC Holder / Active Exporter',
        udyam: 'UDYAM-GJ-01-0023456',
        isLoggedIn: true,
        loginMethod: 'google_oauth',
        picture: profile.picture,
        googleId: profile.sub,
      }
      localStorage.setItem('udyamniti_user', JSON.stringify(googleUser))
      toast.success(`Google verification successful! Welcome, ${profile.name}.`)
      navigate('/dashboard')
    } catch (err: any) {
      if (err?.message === 'MISSING_CLIENT_ID') {
        setClientIdModalOpen(true)
      } else {
        toast.error(err?.message || 'Google sign-up was cancelled or encountered an error.')
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

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) value = value.slice(-1)
    const newDigits = [...otpDigits]
    newDigits[index] = value
    setOtpDigits(newDigits)
    if (value && index < 3) {
      inputRefs[index + 1].current?.focus()
    }
  }

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otpDigits[index] && index > 0) {
      inputRefs[index - 1].current?.focus()
    }
  }

  const handleOtpSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => {
      handleGoogleOneClick()
    }, 400)
  }

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 120px)',
        bgcolor: '#F8FAFC',
        py: { xs: 4, md: 7 },
        px: 2,
      }}
    >
      <Container maxWidth="md">
        {/* Top Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
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
              fontSize: { xs: '1.6rem', md: '2rem' },
              letterSpacing: '-0.02em',
            }}
          >
            Create Your Enterprise Account
          </Typography>
          <Typography variant="body2" sx={{ color: '#64748B', mt: 0.5 }}>
            Provide your business profile to receive personalized Central & Gujarat State scheme matches
          </Typography>
        </Box>

        <Card
          sx={{
            bgcolor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '16px',
            boxShadow: '0 4px 20px rgba(15, 23, 42, 0.06)',
            overflow: 'visible',
          }}
        >
          <CardContent sx={{ p: { xs: 3, sm: 4, md: 5 } }}>
            {/* ─── GOOGLE SIGN UP BUTTON (PERFECTLY MATCHING UI) ─── */}
            <Button
              fullWidth
              variant="outlined"
              onClick={handleGoogleOneClick}
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
              Sign up with Google (Fast Verification)
            </Button>

            <Divider sx={{ my: 3.5, borderColor: '#E2E8F0' }}>
              <Typography variant="caption" sx={{ color: '#64748B', px: 1, fontWeight: 700, letterSpacing: '0.04em' }}>
                OR FILL OFFICIAL MSME QUESTIONNAIRE
              </Typography>
            </Divider>

            {step === 'FORM' && (
              <form onSubmit={handleSubmit}>
                <Stack spacing={3.5}>
                  {/* PART 1: Legal Identification */}
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <BusinessIcon sx={{ fontSize: 18, color: '#0F2E59' }} /> 1. Enterprise Legal Identification
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={8}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Enterprise Registered Legal Name *
                        </Typography>
                        <TextField
                          fullWidth
                          size="small"
                          required
                          value={enterpriseName}
                          onChange={(e) => setEnterpriseName(e.target.value)}
                          placeholder="e.g. Apex Precision Engineering Pvt. Ltd."
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        />
                      </Grid>

                      <Grid item xs={12} sm={4}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Constitution / Type *
                        </Typography>
                        <TextField
                          select
                          fullWidth
                          size="small"
                          value={constitution}
                          onChange={(e) => setConstitution(e.target.value)}
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        >
                          <MenuItem value="Proprietorship">Proprietorship</MenuItem>
                          <MenuItem value="Partnership">Partnership Firm</MenuItem>
                          <MenuItem value="Private Limited Company">Private Limited Company</MenuItem>
                          <MenuItem value="LLP">Limited Liability Partnership (LLP)</MenuItem>
                          <MenuItem value="Cooperative Society">Cooperative Society / Trust</MenuItem>
                        </TextField>
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Udyam Registration Number (Optional / Pending)
                        </Typography>
                        <TextField
                          fullWidth
                          size="small"
                          value={udyam}
                          onChange={(e) => setUdyam(e.target.value)}
                          placeholder="UDYAM-GJ-01-0023456"
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        />
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Business Age / Year of Incorporation *
                        </Typography>
                        <TextField
                          select
                          fullWidth
                          size="small"
                          value={businessAge}
                          onChange={(e) => setBusinessAge(e.target.value)}
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        >
                          <MenuItem value="0">New Unit / Startup (&lt;1 Year)</MenuItem>
                          <MenuItem value="1">1 to 3 Years</MenuItem>
                          <MenuItem value="3">3 to 5 Years</MenuItem>
                          <MenuItem value="5">5 to 10 Years</MenuItem>
                          <MenuItem value="10">10+ Years Established</MenuItem>
                        </TextField>
                      </Grid>
                    </Grid>
                  </Box>

                  {/* PART 2: MSMED Act Criteria (Turnover & Plant/Machinery) */}
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <AccountBalanceIcon sx={{ fontSize: 18, color: '#059669' }} /> 2. Turnover & Investment Classification (Statutory MSME Rules)
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Expected Annual Turnover *
                        </Typography>
                        <TextField
                          select
                          fullWidth
                          size="small"
                          value={turnover}
                          onChange={(e) => handleTurnoverChange(e.target.value)}
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        >
                          <MenuItem value="up_to_1_cr">Up to ₹1.00 Crore</MenuItem>
                          <MenuItem value="1_to_5_cr">₹1.00 Cr to ₹5.00 Crore</MenuItem>
                          <MenuItem value="5_to_50_cr">₹5.00 Cr to ₹50.00 Crore</MenuItem>
                          <MenuItem value="50_to_250_cr">₹50.00 Cr to ₹250.00 Crore</MenuItem>
                          <MenuItem value="above_250_cr">Above ₹250.00 Crore</MenuItem>
                        </TextField>
                      </Grid>

                      <Grid item xs={12} sm={4}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Plant & Machinery Investment *
                        </Typography>
                        <TextField
                          select
                          fullWidth
                          size="small"
                          value={investment}
                          onChange={(e) => setInvestment(e.target.value)}
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        >
                          <MenuItem value="up_to_25l">Up to ₹25 Lakh</MenuItem>
                          <MenuItem value="25l_to_1cr">₹25 Lakh to ₹1 Crore</MenuItem>
                          <MenuItem value="1cr_to_10cr">₹1 Crore to ₹10 Crore</MenuItem>
                          <MenuItem value="10cr_to_50cr">₹10 Crore to ₹50 Crore</MenuItem>
                        </TextField>
                      </Grid>

                      <Grid item xs={12} sm={4}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          MSME Category *
                        </Typography>
                        <TextField
                          select
                          fullWidth
                          size="small"
                          value={msmeCategory}
                          onChange={(e) => setMsmeCategory(e.target.value)}
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        >
                          <MenuItem value="micro">Micro Enterprise (&le; ₹5 Cr Turn)</MenuItem>
                          <MenuItem value="small">Small Enterprise (&le; ₹50 Cr Turn)</MenuItem>
                          <MenuItem value="medium">Medium Enterprise (&le; ₹250 Cr Turn)</MenuItem>
                        </TextField>
                      </Grid>
                    </Grid>
                  </Box>

                  {/* PART 3: Sector & State */}
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LocationOnOutlinedIcon sx={{ fontSize: 18, color: '#2563EB' }} /> 3. Sector & Operational Location
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Industry / Focus Sector *
                        </Typography>
                        <TextField
                          select
                          fullWidth
                          size="small"
                          value={industry}
                          onChange={(e) => setIndustry(e.target.value)}
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        >
                          <MenuItem value="Precision Engineering & Mfg">Precision Engineering & Machinery</MenuItem>
                          <MenuItem value="Textiles & Apparel">Textiles, Garments & Technical Fabrics</MenuItem>
                          <MenuItem value="Agro & Food Processing">Agro & Food Processing</MenuItem>
                          <MenuItem value="Chemicals & Petrochemicals">Chemicals & Allied Products</MenuItem>
                          <MenuItem value="Coir & Natural Fibres">Coir, Jute & Natural Fibres</MenuItem>
                          <MenuItem value="Renewable Energy & EV">Renewable Energy, Solar & Clean Tech</MenuItem>
                          <MenuItem value="Services & IT Solutions">IT, Software & Professional Services</MenuItem>
                          <MenuItem value="Handicrafts & Traditional Artisans">Handicrafts & Traditional Clusters</MenuItem>
                        </TextField>
                      </Grid>

                      <Grid item xs={12} sm={3}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          State *
                        </Typography>
                        <TextField
                          select
                          fullWidth
                          size="small"
                          value={state}
                          onChange={(e) => setState(e.target.value)}
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        >
                          <MenuItem value="Gujarat">Gujarat (SER / GIDC)</MenuItem>
                          <MenuItem value="Maharashtra">Maharashtra</MenuItem>
                          <MenuItem value="Tamil Nadu">Tamil Nadu</MenuItem>
                          <MenuItem value="Karnataka">Karnataka</MenuItem>
                          <MenuItem value="Uttar Pradesh">Uttar Pradesh</MenuItem>
                          <MenuItem value="All India">All-India / Central</MenuItem>
                        </TextField>
                      </Grid>

                      <Grid item xs={12} sm={3}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          District / Hub
                        </Typography>
                        <TextField
                          fullWidth
                          size="small"
                          value={district}
                          onChange={(e) => setDistrict(e.target.value)}
                          placeholder="e.g. Surat, Ahmedabad"
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        />
                      </Grid>
                    </Grid>
                  </Box>

                  {/* PART 4: Special Beneficiary Category & Exports */}
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <VerifiedUserIcon sx={{ fontSize: 18, color: '#D97706' }} /> 4. Beneficiary Category & Export Activity (Subsidy Booster)
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Special Entrepreneur Category *
                        </Typography>
                        <TextField
                          select
                          fullWidth
                          size="small"
                          value={beneficiaryCategory}
                          onChange={(e) => setBeneficiaryCategory(e.target.value)}
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        >
                          <MenuItem value="General">General Category</MenuItem>
                          <MenuItem value="Women-Led Enterprise (51%+)">Women-Led Enterprise (51%+ Shareholding)</MenuItem>
                          <MenuItem value="SC/ST Entrepreneur">SC / ST Entrepreneur (NSSH Covered)</MenuItem>
                          <MenuItem value="Divyangjan / PwD">Divyangjan / PwD Entrepreneur</MenuItem>
                          <MenuItem value="North East / Border District">North East / Border Region</MenuItem>
                        </TextField>
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Export Activity & IEC Status *
                        </Typography>
                        <TextField
                          select
                          fullWidth
                          size="small"
                          value={exportStatus}
                          onChange={(e) => setExportStatus(e.target.value)}
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        >
                          <MenuItem value="IEC Holder / Active Exporter">IEC Code Holder / Active Exporter (EPM Eligible)</MenuItem>
                          <MenuItem value="Planning to Export">Planning to Export / First Time Exporter</MenuItem>
                          <MenuItem value="Domestic Only">Domestic Indian Market Only</MenuItem>
                        </TextField>
                      </Grid>
                    </Grid>
                  </Box>

                  {/* PART 5: Director Login Credentials */}
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <PersonOutlineIcon sx={{ fontSize: 18, color: '#7C3AED' }} /> 5. Director / Authorized Signatory Credentials
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Director / Contact Person Name *
                        </Typography>
                        <TextField
                          fullWidth
                          size="small"
                          required
                          value={directorName}
                          onChange={(e) => setDirectorName(e.target.value)}
                          placeholder="e.g. Rajesh Patel"
                          InputProps={{ sx: { bgcolor: '#F8FAFC', borderRadius: '8px' } }}
                        />
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Mobile Number *
                        </Typography>
                        <TextField
                          fullWidth
                          size="small"
                          value={phone}
                          onChange={(e) => setPhone(e.target.value)}
                          placeholder="+91 98250 12345"
                          InputProps={{
                            startAdornment: (
                              <InputAdornment position="start">
                                <PhoneOutlinedIcon sx={{ fontSize: 18, color: '#64748B' }} />
                              </InputAdornment>
                            ),
                            sx: { bgcolor: '#F8FAFC', borderRadius: '8px' },
                          }}
                        />
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Official Email Address *
                        </Typography>
                        <TextField
                          fullWidth
                          size="small"
                          type="email"
                          required
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="director@company.in"
                          InputProps={{
                            startAdornment: (
                              <InputAdornment position="start">
                                <EmailOutlinedIcon sx={{ fontSize: 18, color: '#64748B' }} />
                              </InputAdornment>
                            ),
                            sx: { bgcolor: '#F8FAFC', borderRadius: '8px' },
                          }}
                        />
                      </Grid>

                      <Grid item xs={12} sm={6}>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 700, mb: 0.5, display: 'block' }}>
                          Create Password *
                        </Typography>
                        <TextField
                          fullWidth
                          size="small"
                          type={showPassword ? 'text' : 'password'}
                          required
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="Create strong account password"
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
                            sx: { bgcolor: '#F8FAFC', borderRadius: '8px' },
                          }}
                        />
                      </Grid>
                    </Grid>
                  </Box>

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size="large"
                    disabled={loading}
                    endIcon={<ArrowForwardIcon />}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      py: 1.4,
                      fontWeight: 800,
                      fontSize: '0.96rem',
                      borderRadius: '8px',
                      textTransform: 'none',
                      boxShadow: '0 4px 14px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {loading ? 'Creating Enterprise Account...' : 'Complete Registration & Open Dashboard →'}
                  </Button>
                </Stack>
              </form>
            )}

            <Divider sx={{ my: 3, borderColor: '#E2E8F0' }}>
              <Typography variant="caption" sx={{ color: '#64748B', px: 1 }}>
                ALREADY REGISTERED?
              </Typography>
            </Divider>

            <Button
              fullWidth
              variant="outlined"
              onClick={() => navigate('/login')}
              sx={{
                borderColor: '#CBD5E1',
                color: '#0F2E59',
                py: 1.1,
                fontWeight: 700,
                fontSize: '0.9rem',
                borderRadius: '8px',
                textTransform: 'none',
                '&:hover': { bgcolor: '#F8FAFC', borderColor: '#0F2E59' },
              }}
            >
              Sign In with Existing Account
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
            To activate Google Sign-Up, please paste your <b>Client ID</b> from Google Cloud Console.
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

export default RegisterPage
