import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box, Container, Typography, Button, TextField,
  Grid, Chip, Stepper, Step, StepLabel, Paper,
  FormControl, InputLabel, Select, MenuItem,
  CircularProgress, Alert, Divider, Switch, FormControlLabel,
} from '@mui/material'
import { motion } from 'framer-motion'
import PolicyIcon from '@mui/icons-material/Policy'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import BusinessIcon from '@mui/icons-material/Business'
import { apiClient } from '../api/client'

const STEPS = ['Business Identity', 'Classification', 'Financials & Ownership']

const MSME_CATEGORIES = [
  { value: 'micro', label: 'Micro — Investment ≤ ₹1Cr, Turnover ≤ ₹5Cr' },
  { value: 'small', label: 'Small — Investment ≤ ₹10Cr, Turnover ≤ ₹50Cr' },
  { value: 'medium', label: 'Medium — Investment ≤ ₹50Cr, Turnover ≤ ₹250Cr' },
]

const ENTITY_TYPES = [
  { value: 'proprietorship', label: 'Proprietorship' },
  { value: 'partnership', label: 'Partnership' },
  { value: 'llp', label: 'LLP' },
  { value: 'pvt_ltd', label: 'Private Limited' },
  { value: 'public_ltd', label: 'Public Limited' },
  { value: 'opc', label: 'One Person Company' },
]

const GUJARAT_DISTRICTS = [
  'Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar',
  'Jamnagar', 'Gandhinagar', 'Anand', 'Mehsana', 'Bharuch',
  'Navsari', 'Valsad', 'Kheda', 'Patan', 'Sabarkantha',
  'Amreli', 'Junagadh', 'Porbandar', 'Kutch',
]

const DEFAULT_FORM = {
  business_name: '',
  udyam_registration_number: '',
  gstin: '',
  msme_category: 'small',
  entity_type: 'proprietorship',
  industry_sector: '',
  is_manufacturing: true,
  is_service: false,
  state: 'Gujarat',
  district: '',
  city: '',
  investment_in_plant_machinery_lakhs: '',
  annual_turnover_lakhs: '',
  owner_gender: 'male',
  owner_caste: 'general',
  is_sc_st_owned: false,
  is_women_owned: false,
  years_in_operation: '',
  total_employees: '',
  has_bank_account: true,
  has_existing_loan: false,
  is_npa: false,
}

export default function ProfileSetup() {
  const navigate = useNavigate()
  const location = useLocation()
  const [step, setStep] = useState(0)
  const [form, setForm] = useState({ ...DEFAULT_FORM })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const updateForm = (field: string, value: unknown) => {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    setLoading(true)
    setError('')
    try {
      await apiClient.demoLogin()
      const payload: Record<string, unknown> = { ...form }
      if (payload.investment_in_plant_machinery_lakhs === '') payload.investment_in_plant_machinery_lakhs = null
      if (payload.annual_turnover_lakhs === '') payload.annual_turnover_lakhs = null
      if (payload.years_in_operation === '') payload.years_in_operation = null
      if (payload.total_employees === '') payload.total_employees = null

      const res = await apiClient.createProfile(payload as any)
      const prefillGoal = location.state?.prefillGoal || ''
      navigate(`/goal/${res.data.id}`, { state: { prefillGoal } })
    } catch (err: any) {
      setError(err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Failed to create profile')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box sx={{
      minHeight: '100vh', bgcolor: '#0A0F1E',
      background: `radial-gradient(ellipse at 50% 0%, rgba(108, 99, 255, 0.1) 0%, transparent 60%), #0A0F1E`,
    }}>
      {/* Navbar */}
      <Box sx={{
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        py: 1.5, px: 4, display: 'flex', alignItems: 'center', gap: 1.5,
        bgcolor: 'rgba(10, 15, 30, 0.85)', backdropFilter: 'blur(12px)',
        cursor: 'pointer',
      }} onClick={() => navigate('/')}>
        <PolicyIcon sx={{ color: '#6C63FF', fontSize: 22 }} />
        <Typography sx={{
          fontFamily: 'Outfit, sans-serif', fontWeight: 800,
          background: 'linear-gradient(135deg, #6C63FF 0%, #10B981 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>
          UdyamNiti
        </Typography>
      </Box>

      <Container maxWidth="md" sx={{ py: 6 }}>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Box sx={{
              width: 56, height: 56, borderRadius: 2, mx: 'auto', mb: 2,
              background: 'linear-gradient(135deg, #6C63FF, #10B981)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <BusinessIcon sx={{ color: 'white', fontSize: 28 }} />
            </Box>
            <Typography variant="h4" sx={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, mb: 1 }}>
              Set Up Your Business Profile
            </Typography>
            <Typography variant="body1" sx={{ color: 'text.secondary' }}>
              Your profile drives the eligibility analysis. Start with self-declared facts — documents are optional.
            </Typography>
          </Box>

          <Stepper activeStep={step} sx={{ mb: 5 }}>
            {STEPS.map(label => (
              <Step key={label}>
                <StepLabel sx={{
                  '& .MuiStepLabel-label': { color: 'text.muted', fontSize: '0.85rem' },
                  '& .MuiStepLabel-label.Mui-active': { color: 'primary.light', fontWeight: 600 },
                  '& .MuiStepLabel-label.Mui-completed': { color: 'secondary.main' },
                  '& .MuiStepIcon-root': { color: 'rgba(255,255,255,0.1)' },
                  '& .MuiStepIcon-root.Mui-active': { color: 'primary.main' },
                  '& .MuiStepIcon-root.Mui-completed': { color: 'secondary.main' },
                }}>
                  {label}
                </StepLabel>
              </Step>
            ))}
          </Stepper>

          <Paper sx={{
            p: 4, borderRadius: 3,
            bgcolor: 'rgba(26, 34, 53, 0.8)',
            border: '1px solid rgba(255,255,255,0.08)',
          }}>
            {step === 0 && (
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth label="Business Name *"
                    value={form.business_name}
                    onChange={e => updateForm('business_name', e.target.value)}
                    id="profile-business-name"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth label="Udyam Registration Number"
                    value={form.udyam_registration_number}
                    onChange={e => updateForm('udyam_registration_number', e.target.value)}
                    placeholder="UDYAM-XX-00-0000000"
                    id="profile-udyam"
                    helperText="Leave blank if not registered yet"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth label="GSTIN"
                    value={form.gstin}
                    onChange={e => updateForm('gstin', e.target.value)}
                    id="profile-gstin"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>State</InputLabel>
                    <Select value={form.state} label="State" onChange={e => updateForm('state', e.target.value)} id="profile-state">
                      <MenuItem value="Gujarat">Gujarat</MenuItem>
                      <MenuItem value="Maharashtra">Maharashtra</MenuItem>
                      <MenuItem value="Rajasthan">Rajasthan</MenuItem>
                      <MenuItem value="Punjab">Punjab</MenuItem>
                      <MenuItem value="Tamil Nadu">Tamil Nadu</MenuItem>
                      <MenuItem value="Karnataka">Karnataka</MenuItem>
                      <MenuItem value="Other">Other State</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  {form.state === 'Gujarat' ? (
                    <FormControl fullWidth>
                      <InputLabel>District</InputLabel>
                      <Select value={form.district} label="District" onChange={e => updateForm('district', e.target.value)} id="profile-district">
                        {GUJARAT_DISTRICTS.map(d => (
                          <MenuItem key={d} value={d}>{d}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  ) : (
                    <TextField fullWidth label="District" value={form.district} onChange={e => updateForm('district', e.target.value)} id="profile-district-text" />
                  )}
                </Grid>
              </Grid>
            )}

            {step === 1 && (
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>MSME Category *</InputLabel>
                    <Select value={form.msme_category} label="MSME Category *" onChange={e => updateForm('msme_category', e.target.value)} id="profile-msme-cat">
                      {MSME_CATEGORIES.map(cat => (
                        <MenuItem key={cat.value} value={cat.value}>{cat.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Entity Type</InputLabel>
                    <Select value={form.entity_type} label="Entity Type" onChange={e => updateForm('entity_type', e.target.value)} id="profile-entity-type">
                      {ENTITY_TYPES.map(et => (
                        <MenuItem key={et.value} value={et.value}>{et.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth label="Industry Sector"
                    value={form.industry_sector}
                    onChange={e => updateForm('industry_sector', e.target.value)}
                    placeholder="e.g. Precision Engineering, Textiles, Food Processing"
                    id="profile-industry"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={<Switch checked={form.is_manufacturing} onChange={e => updateForm('is_manufacturing', e.target.checked)} color="primary" id="profile-is-mfg" />}
                    label="Manufacturing Enterprise"
                    sx={{ '& .MuiFormControlLabel-label': { color: 'text.secondary' } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth label="Years in Operation"
                    type="number"
                    value={form.years_in_operation}
                    onChange={e => updateForm('years_in_operation', e.target.value)}
                    id="profile-years"
                  />
                </Grid>
              </Grid>
            )}

            {step === 2 && (
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth label="Investment in Plant & Machinery (₹ Lakhs)"
                    type="number"
                    value={form.investment_in_plant_machinery_lakhs}
                    onChange={e => updateForm('investment_in_plant_machinery_lakhs', e.target.value)}
                    id="profile-investment"
                    helperText="Used to determine MSME category and subsidy limits"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth label="Annual Turnover (₹ Lakhs)"
                    type="number"
                    value={form.annual_turnover_lakhs}
                    onChange={e => updateForm('annual_turnover_lakhs', e.target.value)}
                    id="profile-turnover"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth label="Total Employees"
                    type="number"
                    value={form.total_employees}
                    onChange={e => updateForm('total_employees', e.target.value)}
                    id="profile-employees"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Divider sx={{ borderColor: 'rgba(255,255,255,0.06)', my: 1 }} />
                  <Typography variant="overline" sx={{ color: 'text.muted', letterSpacing: 1.5 }}>
                    OWNERSHIP — Unlocks additional subsidy benefits
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={<Switch checked={form.is_women_owned} onChange={e => updateForm('is_women_owned', e.target.checked)} color="secondary" id="profile-women-owned" />}
                    label="Women-Owned (>51%)"
                    sx={{ '& .MuiFormControlLabel-label': { color: 'text.secondary' } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={<Switch checked={form.is_sc_st_owned} onChange={e => updateForm('is_sc_st_owned', e.target.checked)} color="warning" id="profile-scst-owned" />}
                    label="SC/ST Owned"
                    sx={{ '& .MuiFormControlLabel-label': { color: 'text.secondary' } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={<Switch checked={form.has_bank_account} onChange={e => updateForm('has_bank_account', e.target.checked)} color="primary" id="profile-bank" />}
                    label="Has Active Bank Account"
                    sx={{ '& .MuiFormControlLabel-label': { color: 'text.secondary' } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={<Switch checked={form.is_npa} onChange={e => updateForm('is_npa', e.target.checked)} color="error" id="profile-npa" />}
                    label="Classified as NPA"
                    sx={{ '& .MuiFormControlLabel-label': { color: 'text.secondary' } }}
                  />
                </Grid>
              </Grid>
            )}

            {error && <Alert severity="error" sx={{ mt: 3 }}>{error}</Alert>}

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4, pt: 3, borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              {step > 0 ? (
                <Button
                  variant="outlined"
                  startIcon={<ArrowBackIcon />}
                  onClick={() => setStep(s => s - 1)}
                  id="profile-back-btn"
                  sx={{ borderColor: 'rgba(255,255,255,0.15)', color: 'text.secondary' }}
                >
                  Back
                </Button>
              ) : (
                <Button variant="text" onClick={() => navigate('/')} sx={{ color: 'text.muted' }}>
                  Cancel
                </Button>
              )}

              {step < STEPS.length - 1 ? (
                <Button
                  variant="contained"
                  endIcon={<ArrowForwardIcon />}
                  onClick={() => setStep(s => s + 1)}
                  disabled={step === 0 && !form.business_name}
                  id="profile-next-btn"
                >
                  Next
                </Button>
              ) : (
                <Button
                  variant="contained"
                  endIcon={loading ? <CircularProgress size={16} color="inherit" /> : <ArrowForwardIcon />}
                  onClick={handleSubmit}
                  disabled={loading || !form.business_name}
                  id="profile-submit-btn"
                  sx={{ px: 4 }}
                >
                  {loading ? 'Creating Profile...' : 'Create Profile & Set Goal'}
                </Button>
              )}
            </Box>
          </Paper>
        </motion.div>
      </Container>
    </Box>
  )
}
