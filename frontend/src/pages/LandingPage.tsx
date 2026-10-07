import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  Stack,
  Paper,
  Divider,
  TextField,
  MenuItem,
  InputAdornment,
  LinearProgress,
} from '@mui/material'
import PolicyIcon from '@mui/icons-material/Policy'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import SearchIcon from '@mui/icons-material/Search'
import FactCheckOutlinedIcon from '@mui/icons-material/FactCheckOutlined'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import TrackChangesOutlinedIcon from '@mui/icons-material/TrackChangesOutlined'
import MonetizationOnOutlinedIcon from '@mui/icons-material/MonetizationOnOutlined'
import BuildCircleOutlinedIcon from '@mui/icons-material/BuildCircleOutlined'
import FlightTakeoffOutlinedIcon from '@mui/icons-material/FlightTakeoffOutlined'
import StorefrontOutlinedIcon from '@mui/icons-material/StorefrontOutlined'
import SchoolOutlinedIcon from '@mui/icons-material/SchoolOutlined'
import RocketLaunchOutlinedIcon from '@mui/icons-material/RocketLaunchOutlined'
import LightbulbOutlinedIcon from '@mui/icons-material/LightbulbOutlined'
import ApartmentOutlinedIcon from '@mui/icons-material/ApartmentOutlined'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import NotificationsActiveOutlinedIcon from '@mui/icons-material/NotificationsActiveOutlined'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import { tokens } from '../theme/tokens'
import { useLanguage } from '../i18n'
import { toast } from 'sonner'

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()
  const { t } = useLanguage()

  // Section 3: "Tell Us About Your Business" Profiler State
  const [industry, setIndustry] = useState('manufacturing')
  const [state, setState] = useState('Gujarat')
  const [enterpriseSize, setEnterpriseSize] = useState('micro')
  const [businessAge, setBusinessAge] = useState('3')
  const [turnover, setTurnover] = useState('1_to_5_cr')
  const [profileSubmitted, setProfileSubmitted] = useState(false)

  // Section 7: AI Assistant Query State
  const [aiQuestion, setAiQuestion] = useState('')

  // Section 10: Selected Persona Filter
  const [selectedPersona, setSelectedPersona] = useState<string>('all')

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setProfileSubmitted(true)
    toast.success('Business profile updated! Recommended benefits re-calculated.')
    const el = document.getElementById('recommended-benefits')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const handleAskAI = (sampleQuery?: string) => {
    const q = sampleQuery || aiQuestion
    if (!q.trim()) {
      toast.info('Please enter a question for MSME AI.')
      return
    }
    navigate(`/dashboard?mode=ai&q=${encodeURIComponent(q.trim())}`)
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F8FAFC', color: '#0F172A' }}>
      {/* ─── SECTION 1: HERO ─── */}
      <Box
        sx={{
          bgcolor: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          pt: { xs: 7, md: 10 },
          pb: { xs: 8, md: 11 },
          background: 'radial-gradient(ellipse at 50% 0%, #F1F5F9 0%, #FFFFFF 75%)',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: 860, mx: 'auto' }}>
            {/* Top Verified Badge */}
            <Chip
              icon={<VerifiedUserIcon sx={{ fontSize: '15px !important', color: '#059669 !important' }} />}
              label="Official Central & Gujarat State MSME Scheme Intelligence"
              sx={{
                mb: 3,
                bgcolor: '#ECFDF5',
                color: '#065F46',
                border: '1px solid #A7F3D0',
                fontWeight: 700,
                fontSize: '0.82rem',
                py: 2,
                px: 1.5,
              }}
            />

            {/* Main Headline */}
            <Typography
              variant="h1"
              sx={{
                fontFamily: tokens.font.heading,
                fontWeight: 800,
                fontSize: { xs: '2.2rem', sm: '3.1rem', md: '3.8rem' },
                lineHeight: 1.15,
                letterSpacing: '-0.03em',
                color: '#0F2E59',
                mb: 2.5,
              }}
            >
              Government Benefits.{' '}
              <Box
                component="span"
                sx={{
                  color: '#E65100',
                  borderBottom: '4px solid #E65100',
                  display: 'inline-block',
                }}
              >
                Matched to Your Business.
              </Box>
            </Typography>

            {/* Subtitle */}
            <Typography
              variant="body1"
              sx={{
                color: '#475569',
                fontSize: { xs: '1.05rem', md: '1.25rem' },
                lineHeight: 1.65,
                maxWidth: 720,
                mx: 'auto',
                mb: 4.5,
                fontWeight: 500,
              }}
            >
              Discover schemes, subsidies, grants, credit support, tax incentives and growth opportunities verified from official government sources.
            </Typography>

            {/* Hero CTAs */}
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
              alignItems="center"
              sx={{ mb: 4 }}
            >
              <Button
                variant="contained"
                size="large"
                startIcon={<AutoAwesomeIcon sx={{ color: '#FEF08A' }} />}
                endIcon={<ArrowForwardIcon />}
                onClick={() => {
                  const el = document.getElementById('business-profiler')
                  if (el) el.scrollIntoView({ behavior: 'smooth' })
                }}
                sx={{
                  background: 'linear-gradient(135deg, #E65100 0%, #EA580C 100%)',
                  color: '#FFFFFF',
                  fontWeight: 800,
                  fontSize: '1.02rem',
                  px: 4,
                  py: 1.6,
                  borderRadius: '10px',
                  textTransform: 'none',
                  boxShadow: '0 6px 20px rgba(230, 81, 0, 0.35)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #C2410C 0%, #9A3412 100%)',
                    boxShadow: '0 8px 25px rgba(230, 81, 0, 0.45)',
                  },
                }}
              >
                Find Benefits for My Business
              </Button>

              <Button
                variant="outlined"
                size="large"
                startIcon={<SearchIcon sx={{ color: '#0F2E59' }} />}
                onClick={() => navigate('/dashboard')}
                sx={{
                  borderColor: '#CBD5E1',
                  color: '#0F2E59',
                  bgcolor: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '1.02rem',
                  px: 3.5,
                  py: 1.6,
                  borderRadius: '10px',
                  textTransform: 'none',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                  '&:hover': { bgcolor: '#F8FAFC', borderColor: '#0F2E59' },
                }}
              >
                Search schemes, benefits or programs...
              </Button>
            </Stack>

            {/* Trust Underline */}
            <Typography
              variant="caption"
              sx={{
                color: '#64748B',
                fontWeight: 600,
                fontSize: '0.85rem',
                letterSpacing: '0.01em',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 1,
                flexWrap: 'wrap',
              }}
            >
              <span>Verified from official government sources</span>
              <span>•</span>
              <span>Eligibility explained</span>
              <span>•</span>
              <span>Source-backed results</span>
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* ─── SECTION 2: QUICK ACTIONS (4 CARDS) ─── */}
      <Box sx={{ py: 6, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Grid container spacing={2.5}>
            {[
              {
                icon: <SearchIcon sx={{ fontSize: 32, color: '#0F2E59' }} />,
                title: 'Find Schemes',
                desc: 'Filter 11 official schemes across credit, subsidies, technology, clusters and exports.',
                action: () => navigate('/dashboard'),
              },
              {
                icon: <FactCheckOutlinedIcon sx={{ fontSize: 32, color: '#059669' }} />,
                title: 'Check Eligibility',
                desc: 'AI scores your enterprise profile against Gazette rules and identifies match percentages.',
                action: () => {
                  const el = document.getElementById('business-profiler')
                  if (el) el.scrollIntoView({ behavior: 'smooth' })
                },
              },
              {
                icon: <DescriptionOutlinedIcon sx={{ fontSize: 32, color: '#2563EB' }} />,
                title: 'Check Documents',
                desc: 'Inspect mandatory document checklists and statutory attachments before applying.',
                action: () => navigate('/dashboard?mode=documents'),
              },
              {
                icon: <TrackChangesOutlinedIcon sx={{ fontSize: 32, color: '#7C3AED' }} />,
                title: 'Track Applications',
                desc: 'Monitor application milestones, bank sanctions, and PFMS margin money disbursements.',
                action: () => navigate('/dashboard?mode=tracking'),
              },
            ].map((card, i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Paper
                  onClick={card.action}
                  elevation={0}
                  sx={{
                    p: 3,
                    height: '100%',
                    bgcolor: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 6px rgba(15, 23, 42, 0.04)',
                    '&:hover': {
                      borderColor: '#0F2E59',
                      transform: 'translateY(-3px)',
                      boxShadow: '0 8px 20px rgba(15, 23, 42, 0.08)',
                    },
                  }}
                >
                  <Box sx={{ mb: 1.5 }}>{card.icon}</Box>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '1.05rem', mb: 0.8 }}>
                    {card.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', fontSize: '0.86rem', lineHeight: 1.5 }}>
                    {card.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 3: TELL US ABOUT YOUR BUSINESS (ONBOARDING FUNNEL) ─── */}
      <Box id="business-profiler" sx={{ py: 8, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="lg">
          <Paper
            elevation={0}
            sx={{
              p: { xs: 3, md: 5 },
              bgcolor: '#F8FAFC',
              border: '2px solid #E2E8F0',
              borderRadius: '16px',
            }}
          >
            <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1 }}>
              <AutoAwesomeIcon sx={{ color: '#E65100', fontSize: 24 }} />
              <Typography variant="h4" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.5rem', md: '1.9rem' } }}>
                Tell Us About Your Business
              </Typography>
            </Stack>
            <Typography variant="body1" sx={{ color: '#64748B', mb: 4, fontSize: '0.98rem' }}>
              Find benefits you may qualify for. Our AI reasoning engine builds your verified profile and compares it against official scheme guidelines.
            </Typography>

            <form onSubmit={handleProfileSubmit}>
              <Grid container spacing={2.5}>
                {/* 1. Industry */}
                <Grid item xs={12} sm={6} md={2.4}>
                  <Typography variant="caption" sx={{ fontWeight: 700, color: '#1E293B', mb: 0.8, display: 'block' }}>
                    Industry Sector
                  </Typography>
                  <TextField
                    select
                    fullWidth
                    size="small"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    sx={{ bgcolor: '#FFFFFF', borderRadius: '8px' }}
                  >
                    <MenuItem value="manufacturing">Manufacturing</MenuItem>
                    <MenuItem value="textiles">Textiles & Apparel</MenuItem>
                    <MenuItem value="food">Agro & Food Processing</MenuItem>
                    <MenuItem value="chemicals">Chemicals & Allied</MenuItem>
                    <MenuItem value="services">Services & IT Solutions</MenuItem>
                    <MenuItem value="coir">Coir & Natural Fibres</MenuItem>
                  </TextField>
                </Grid>

                {/* 2. State */}
                <Grid item xs={12} sm={6} md={2.4}>
                  <Typography variant="caption" sx={{ fontWeight: 700, color: '#1E293B', mb: 0.8, display: 'block' }}>
                    Operational State
                  </Typography>
                  <TextField
                    select
                    fullWidth
                    size="small"
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    sx={{ bgcolor: '#FFFFFF', borderRadius: '8px' }}
                  >
                    <MenuItem value="Gujarat">Gujarat (SER / GIDC)</MenuItem>
                    <MenuItem value="Maharashtra">Maharashtra</MenuItem>
                    <MenuItem value="Tamil Nadu">Tamil Nadu</MenuItem>
                    <MenuItem value="Karnataka">Karnataka</MenuItem>
                    <MenuItem value="Uttar Pradesh">Uttar Pradesh</MenuItem>
                    <MenuItem value="All India">All-India / Central</MenuItem>
                  </TextField>
                </Grid>

                {/* 3. Enterprise Size */}
                <Grid item xs={12} sm={6} md={2.4}>
                  <Typography variant="caption" sx={{ fontWeight: 700, color: '#1E293B', mb: 0.8, display: 'block' }}>
                    Enterprise Size
                  </Typography>
                  <TextField
                    select
                    fullWidth
                    size="small"
                    value={enterpriseSize}
                    onChange={(e) => setEnterpriseSize(e.target.value)}
                    sx={{ bgcolor: '#FFFFFF', borderRadius: '8px' }}
                  >
                    <MenuItem value="micro">Micro (&le; ₹5 Cr Turn.)</MenuItem>
                    <MenuItem value="small">Small (&le; ₹50 Cr Turn.)</MenuItem>
                    <MenuItem value="medium">Medium (&le; ₹250 Cr)</MenuItem>
                  </TextField>
                </Grid>

                {/* 4. Business Age */}
                <Grid item xs={12} sm={6} md={2.4}>
                  <Typography variant="caption" sx={{ fontWeight: 700, color: '#1E293B', mb: 0.8, display: 'block' }}>
                    Business Age
                  </Typography>
                  <TextField
                    select
                    fullWidth
                    size="small"
                    value={businessAge}
                    onChange={(e) => setBusinessAge(e.target.value)}
                    sx={{ bgcolor: '#FFFFFF', borderRadius: '8px' }}
                  >
                    <MenuItem value="0">New / Startup (&lt;1 Yr)</MenuItem>
                    <MenuItem value="1">1 to 2 Years</MenuItem>
                    <MenuItem value="3">3 Years (Eligible)</MenuItem>
                    <MenuItem value="5">5+ Years</MenuItem>
                  </TextField>
                </Grid>

                {/* 5. Submit Button */}
                <Grid item xs={12} md={2.4} sx={{ display: 'flex', alignItems: 'flex-end' }}>
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    endIcon={<ArrowForwardIcon />}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      fontWeight: 800,
                      py: 1.15,
                      borderRadius: '8px',
                      textTransform: 'none',
                      fontSize: '0.92rem',
                      boxShadow: '0 4px 12px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    Find My Benefits
                  </Button>
                </Grid>
              </Grid>
            </form>
          </Paper>
        </Container>
      </Box>

      {/* ─── SECTION 4: RECOMMENDED BENEFITS (LIVE MATCH CARDS WITH REASONING) ─── */}
      <Box id="recommended-benefits" sx={{ py: 9, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', md: 'center' }} sx={{ mb: 4 }}>
            <Box>
              <Chip label="AI Recommendation Engine" size="small" sx={{ bgcolor: '#FEF3C7', color: '#B45309', fontWeight: 800, mb: 1 }} />
              <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.8rem', md: '2.3rem' } }}>
                Recommended for Your Business
              </Typography>
              <Typography variant="body1" sx={{ color: '#64748B', mt: 0.5 }}>
                Based on your business profile ({enterpriseSize.toUpperCase()} Enterprise in {state}, {industry.toUpperCase()})
              </Typography>
            </Box>
            <Button
              variant="outlined"
              onClick={() => navigate('/dashboard')}
              endIcon={<ArrowForwardIcon />}
              sx={{ mt: { xs: 2, md: 0 }, color: '#0F2E59', borderColor: '#CBD5E1', fontWeight: 700, textTransform: 'none' }}
            >
              View All 11 Verified Matches
            </Button>
          </Stack>

          <Grid container spacing={3}>
            {[
              {
                code: 'PMEGP_MSME_SCHEME',
                name: "Prime Minister's Employment Generation Programme (PMEGP)",
                match: 92,
                benefit: '₹50.00 Lakh Margin Subsidy',
                reasons: [
                  '✓ Registered Micro/Small manufacturing unit',
                  '✓ Location eligible for 25%-35% margin money subsidy',
                  '✓ Up to ₹1 Cr ceiling for 2nd upgrading expansion loan',
                  '⚠ Project report & bank appraisal document required',
                ],
                source: 'Ministry of MSME / KVIC Guidelines',
                color: '#D97706',
              },
              {
                code: 'CGTMSE_EPM_EXPORT_2026',
                name: 'Special Credit Guarantee – Export Credit (EPM - Niryat Protsahan)',
                match: 88,
                benefit: '₹10.00 Crore Collateral-Free Credit',
                reasons: [
                  '✓ Zero collateral required for pre-shipment & post-shipment',
                  '✓ 85% credit guarantee backing (75% CGTMSE + 10% DGFT)',
                  '✓ Reduced annual guarantee fee (AGF) capped at 1.50%',
                  '⚠ IEC code registration required for export credit claim',
                ],
                source: 'CGTMSE Circular No. 257 & DGFT',
                color: '#059669',
              },
              {
                code: 'GUJ_SER_TEXTILE_2025',
                name: 'Assistance for Developing SER Textile and MSME Park (Gujarat)',
                match: 85,
                benefit: '₹1.00 Crore 100% Capital Grant',
                reasons: [
                  '✓ Gujarat operational location qualifies for SER park assistance',
                  '✓ 100% financial assistance for common testing laboratories',
                  '✓ Zero Liquid Discharge (ZLD) effluent recycling support',
                  '⚠ GIDC or private developer partnership verification',
                ],
                source: 'Industries and Mines Department, Govt of Gujarat',
                color: '#2563EB',
              },
              {
                code: 'PMS_MARKETING_SUPPORT',
                name: 'Procurement and Marketing Support (PMS) Scheme',
                match: 81,
                benefit: '100% Stall Subsidy + Barcode Grant',
                reasons: [
                  '✓ 100% space rent reimbursement up to ₹1.50 Lakh for exhibitions',
                  '✓ One-time ₹50,000 reimbursement for GS1 Barcode registration',
                  '✓ E-commerce packaging and digital catalogue support',
                  '⚠ Udyam registration active verification needed',
                ],
                source: 'Office of DC-MSME, Ministry of MSME',
                color: '#CA8A04',
              },
            ].map((scheme, i) => (
              <Grid item xs={12} md={6} key={i}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    bgcolor: '#FFFFFF',
                    border: '1.5px solid #E2E8F0',
                    borderRadius: '14px',
                    p: 1,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: '#0F2E59',
                      boxShadow: '0 8px 24px rgba(15, 23, 42, 0.08)',
                      transform: 'translateY(-3px)',
                    },
                  }}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
                      <Chip
                        label={`${scheme.match}% MATCH`}
                        size="small"
                        sx={{
                          bgcolor: scheme.match > 85 ? '#ECFDF5' : '#EFF6FF',
                          color: scheme.match > 85 ? '#065F46' : '#1D4ED8',
                          fontWeight: 900,
                          fontSize: '0.78rem',
                          border: '1px solid',
                          borderColor: scheme.match > 85 ? '#A7F3D0' : '#BFDBFE',
                        }}
                      />
                      <Typography variant="caption" sx={{ color: '#64748B', fontWeight: 600 }}>
                        {scheme.source}
                      </Typography>
                    </Stack>

                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '1.08rem', lineHeight: 1.35, mb: 1 }}>
                      {scheme.name}
                    </Typography>

                    <Paper sx={{ p: 1.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', mb: 2 }}>
                      <Typography variant="caption" sx={{ color: '#64748B', fontWeight: 600, display: 'block' }}>
                        Maximum Government Financial Assistance
                      </Typography>
                      <Typography variant="subtitle1" sx={{ fontWeight: 900, color: scheme.color }}>
                        {scheme.benefit}
                      </Typography>
                    </Paper>

                    <Typography variant="caption" sx={{ fontWeight: 800, color: '#334155', display: 'block', mb: 1 }}>
                      Why Am I Eligible? (AI Rules Reasoning)
                    </Typography>

                    <Stack spacing={0.6}>
                      {scheme.reasons.map((r, idx) => (
                        <Typography
                          key={idx}
                          variant="caption"
                          sx={{
                            color: r.startsWith('✓') ? '#059669' : '#D97706',
                            fontWeight: 600,
                            lineHeight: 1.4,
                            display: 'block',
                          }}
                        >
                          {r}
                        </Typography>
                      ))}
                    </Stack>
                  </CardContent>

                  <Box sx={{ p: 2, pt: 0 }}>
                    <Stack direction="row" spacing={1.5}>
                      <Button
                        fullWidth
                        variant="contained"
                        onClick={() => navigate(`/scheme/${scheme.code}`)}
                        sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 700, textTransform: 'none', borderRadius: '6px' }}
                      >
                        Check Eligibility & Apply
                      </Button>
                      <Button
                        variant="outlined"
                        onClick={() => navigate(`/scheme/${scheme.code}`)}
                        sx={{ borderColor: '#CBD5E1', color: '#0F2E59', fontWeight: 700, textTransform: 'none', borderRadius: '6px' }}
                      >
                        Details
                      </Button>
                    </Stack>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 5: EXPLORE BY BUSINESS NEED (8 TASK-ORIENTED TILES) ─── */}
      <Box sx={{ py: 9, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 6 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.8rem', md: '2.3rem' }, mb: 1 }}>
              What Does Your Business Need?
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748B' }}>
              Select your priority requirement to filter schemes and subsidies tailored to that operational outcome.
            </Typography>
          </Box>

          <Grid container spacing={2.5}>
            {[
              { title: 'Finance & Credit', desc: 'Collateral-free credit & invoice discounting', icon: <MonetizationOnOutlinedIcon sx={{ fontSize: 32, color: '#059669' }} />, cat: 'credit_guarantee' },
              { title: 'Technology Upgrade', desc: 'Zero defect quality & machinery modernisation', icon: <BuildCircleOutlinedIcon sx={{ fontSize: 32, color: '#2563EB' }} />, cat: 'quality_certification' },
              { title: 'Export Support', desc: 'Global trade fairs, airfare & collateral cover', icon: <FlightTakeoffOutlinedIcon sx={{ fontSize: 32, color: '#EA580C' }} />, cat: 'export_support' },
              { title: 'Marketing', desc: 'Exhibition stalls, barcoding & GeM procurement', icon: <StorefrontOutlinedIcon sx={{ fontSize: 32, color: '#CA8A04' }} />, cat: 'market_development' },
              { title: 'Skill Development', desc: 'Entrepreneurship training & workforce skills', icon: <SchoolOutlinedIcon sx={{ fontSize: 32, color: '#7C3AED' }} />, cat: 'skill_development' },
              { title: 'Start a Business', desc: 'Margin money capital subsidy up to ₹50 Lakh', icon: <RocketLaunchOutlinedIcon sx={{ fontSize: 32, color: '#DB2777' }} />, cat: 'capital_subsidy' },
              { title: 'Innovation', desc: 'Patents, design facilities & testing laboratories', icon: <LightbulbOutlinedIcon sx={{ fontSize: 32, color: '#0891B2' }} />, cat: 'quality_certification' },
              { title: 'Infrastructure', desc: 'Industrial park grants & common facility centres', icon: <ApartmentOutlinedIcon sx={{ fontSize: 32, color: '#4F46E5' }} />, cat: 'infrastructure' },
            ].map((need, i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Paper
                  onClick={() => navigate(`/dashboard?category=${need.cat}`)}
                  elevation={0}
                  sx={{
                    p: 2.5,
                    height: '100%',
                    bgcolor: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: '#0F2E59',
                      transform: 'translateY(-3px)',
                      boxShadow: '0 8px 20px rgba(15, 23, 42, 0.08)',
                    },
                  }}
                >
                  <Box sx={{ mb: 1.5 }}>{need.icon}</Box>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '1rem', mb: 0.5 }}>
                    {need.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', fontSize: '0.84rem', lineHeight: 1.4 }}>
                    {need.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 6: HOW IT WORKS (5 STEPS) ─── */}
      <Box sx={{ py: 9, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 6 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.8rem', md: '2.3rem' }, mb: 1 }}>
              How UdyamNiti Works
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748B' }}>
              From profile creation to bank disbursement in five seamless steps.
            </Typography>
          </Box>

          <Grid container spacing={2}>
            {[
              { num: '01', title: 'Tell us about your business', desc: 'Enter sector, state, size, turnover and export status.' },
              { num: '02', title: 'AI discovers relevant benefits', desc: 'Cross-checks with Central and State scheme databases.' },
              { num: '03', title: 'Eligibility checked against rules', desc: 'Automated verification against official Gazette provisions.' },
              { num: '04', title: 'See missing documents & gaps', desc: 'Clear alerts on required certificates and bank paperwork.' },
              { num: '05', title: 'Prepare and track application', desc: 'Guided assistance to submit and track government sanctions.' },
            ].map((step, i) => (
              <Grid item xs={12} sm={6} md={2.4} key={i}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2.5,
                    height: '100%',
                    bgcolor: '#F8FAFC',
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                    position: 'relative',
                  }}
                >
                  <Typography variant="h3" sx={{ fontWeight: 900, color: '#CBD5E1', fontSize: '2rem', mb: 1 }}>
                    {step.num}
                  </Typography>
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '0.96rem', mb: 0.8 }}>
                    {step.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', fontSize: '0.84rem', lineHeight: 1.5 }}>
                    {step.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 7: AI ASSISTANT ("ASK MSME AI") ─── */}
      <Box sx={{ py: 9, bgcolor: '#0F2E59', color: '#FFFFFF', borderBottom: '1px solid #1E3A8A' }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Chip
              icon={<AutoAwesomeIcon sx={{ fontSize: '15px !important', color: '#FEF08A !important' }} />}
              label="Powered by Agentic RAG & Official Gazette Corpus"
              sx={{ bgcolor: 'rgba(255, 255, 255, 0.15)', color: '#FFFFFF', fontWeight: 700, mb: 1.5 }}
            />
            <Typography variant="h3" sx={{ fontWeight: 800, fontSize: { xs: '1.9rem', md: '2.4rem' }, mb: 1 }}>
              Ask MSME AI Assistant
            </Typography>
            <Typography variant="body1" sx={{ color: '#CBD5E1' }}>
              Instant answers grounded in official Ministry and State Government scheme guidelines.
            </Typography>
          </Box>

          <Paper
            elevation={0}
            sx={{
              p: 1.5,
              bgcolor: '#FFFFFF',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.25)',
              mb: 3,
            }}
          >
            <TextField
              fullWidth
              variant="standard"
              placeholder="What subsidies are available for a textile manufacturing company in Gujarat?"
              value={aiQuestion}
              onChange={(e) => setAiQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleAskAI()
              }}
              InputProps={{
                disableUnderline: true,
                sx: { px: 2, fontSize: '0.98rem', color: '#0F2E59', fontWeight: 500 },
              }}
            />
            <Button
              variant="contained"
              onClick={() => handleAskAI()}
              sx={{
                bgcolor: '#E65100',
                color: '#FFFFFF',
                fontWeight: 800,
                px: 3,
                py: 1.2,
                borderRadius: '8px',
                textTransform: 'none',
                whiteSpace: 'nowrap',
                '&:hover': { bgcolor: '#C2410C' },
              }}
            >
              Ask →
            </Button>
          </Paper>

          {/* Sample Prompts */}
          <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap" sx={{ gap: 1 }}>
            {[
              '“Am I eligible for PMEGP?”',
              '“What documents do I need for CGTMSE?”',
              '“Find export schemes for me”',
              '“Explain Gujarat SER Textile Park grant”',
              '“How does TReDS invoice discounting work?”',
            ].map((q, i) => (
              <Chip
                key={i}
                label={q}
                clickable
                onClick={() => handleAskAI(q.replace(/[“”]/g, ''))}
                sx={{
                  bgcolor: 'rgba(255, 255, 255, 0.12)',
                  color: '#FFFFFF',
                  fontWeight: 600,
                  fontSize: '0.8rem',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.25)' },
                }}
              />
            ))}
          </Stack>
        </Container>
      </Box>

      {/* ─── SECTION 8: GOVERNMENT SOURCES (TRUST & AUTHORITY) ─── */}
      <Box sx={{ py: 6, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Typography
            variant="caption"
            sx={{
              textAlign: 'center',
              display: 'block',
              fontWeight: 800,
              color: '#64748B',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              mb: 3,
            }}
          >
            Information directly verified from trusted government sources
          </Typography>
          <Grid container spacing={2} justifyContent="center">
            {[
              'Ministry of MSME',
              'Udyam Registration',
              'NSIC',
              'KVIC',
              'CGTMSE',
              'Startup India',
              'GeM Portal',
              'Gujarat IMD',
            ].map((source, i) => (
              <Grid item xs={6} sm={4} md={3} lg={1.5} key={i}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 1.5,
                    textAlign: 'center',
                    bgcolor: '#F8FAFC',
                    border: '1px solid #E2E8F0',
                    borderRadius: '8px',
                  }}
                >
                  <AccountBalanceIcon sx={{ color: '#0F2E59', fontSize: 20, mb: 0.5 }} />
                  <Typography variant="caption" sx={{ fontWeight: 800, color: '#1E293B', display: 'block' }}>
                    {source}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 9: LATEST SCHEME UPDATES (PERSONALIZED NOTIFICATIONS) ─── */}
      <Box sx={{ py: 8, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', md: 'center' }} sx={{ mb: 4 }}>
            <Box>
              <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.8rem', md: '2.3rem' } }}>
                Latest Scheme Updates
              </Typography>
              <Typography variant="body1" sx={{ color: '#64748B', mt: 0.5 }}>
                Timely statutory circulars and notifications that may impact your business.
              </Typography>
            </Box>
            <Button
              variant="outlined"
              onClick={() => navigate('/dashboard')}
              sx={{ mt: { xs: 2, md: 0 }, color: '#0F2E59', borderColor: '#CBD5E1', fontWeight: 700, textTransform: 'none' }}
            >
              View All Updates →
            </Button>
          </Stack>

          <Grid container spacing={2.5}>
            {[
              {
                title: 'PMEGP Scheme Guidelines Revised',
                tag: 'Scheme Update',
                time: '2 days ago',
                desc: 'Margin money ceilings enhanced and second loan expansion provisions formally updated.',
              },
              {
                title: 'Export Credit Collateral Support (Circular 257)',
                tag: 'New Application Window',
                time: '5 days ago',
                desc: 'Joint CGTMSE and DGFT 85% credit guarantee framework operationalized for exporters.',
              },
              {
                title: 'Gujarat SER Textile & MSME Park Assistance',
                tag: 'Government Notification',
                time: '8 days ago',
                desc: 'Government Resolution No. IMD/MRT/0597/G opened grants for common testing laboratories.',
              },
              {
                title: 'TReDS Factoring Credit Guarantee (Circular 262)',
                tag: 'Gazette Circular',
                time: '12 days ago',
                desc: 'Sub-24 hour invoice discounting backed by 85% sovereign risk cover on RXIL and M1xchange.',
              },
            ].map((update, i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2.5,
                    height: '100%',
                    bgcolor: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                  }}
                >
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Chip label={update.tag} size="small" sx={{ bgcolor: '#FEF2F2', color: '#991B1B', fontWeight: 700, fontSize: '0.72rem' }} />
                    <Typography variant="caption" sx={{ color: '#94A3B8' }}>{update.time}</Typography>
                  </Stack>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 0.8, fontSize: '0.95rem' }}>
                    {update.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', fontSize: '0.84rem', lineHeight: 1.5 }}>
                    {update.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 10: EXPLORE BY USER TYPE / PERSONAS ─── */}
      <Box sx={{ py: 8, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 4 }}>
            <Typography variant="caption" sx={{ fontWeight: 800, color: '#0F2E59', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              Tailored Assistance
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.8rem', md: '2.3rem' }, mt: 0.5 }}>
              I AM...
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748B', mt: 0.5 }}>
              Select your persona to immediately discover programs specifically intended for you.
            </Typography>
          </Box>

          <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap" sx={{ gap: 1.5 }}>
            {[
              { id: 'startup', label: 'Starting a Business', path: '/dashboard?persona=startup' },
              { id: 'micro', label: 'Micro Enterprise', path: '/dashboard?size=micro' },
              { id: 'small', label: 'Small Enterprise', path: '/dashboard?size=small' },
              { id: 'medium', label: 'Medium Enterprise', path: '/dashboard?size=medium' },
              { id: 'women', label: 'Woman Entrepreneur', path: '/dashboard?persona=women' },
              { id: 'sc_st', label: 'SC/ST Entrepreneur', path: '/dashboard?persona=sc_st' },
              { id: 'exporter', label: 'Exporter', path: '/dashboard?category=export_support' },
              { id: 'artisan', label: 'Artisan / Traditional Business', path: '/dashboard?category=infrastructure' },
            ].map((p) => (
              <Button
                key={p.id}
                variant="outlined"
                onClick={() => navigate(p.path)}
                sx={{
                  bgcolor: '#F8FAFC',
                  borderColor: '#CBD5E1',
                  color: '#1E293B',
                  fontWeight: 700,
                  fontSize: '0.9rem',
                  py: 1.2,
                  px: 2.5,
                  borderRadius: '9999px',
                  textTransform: 'none',
                  '&:hover': { bgcolor: '#0F2E59', color: '#FFFFFF', borderColor: '#0F2E59' },
                }}
              >
                {p.label}
              </Button>
            ))}
          </Stack>
        </Container>
      </Box>

      {/* ─── SECTION 11: VERIFIED IMPACT & SUCCESS NUMBERS ─── */}
      <Box sx={{ py: 8, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="lg">
          <Grid container spacing={3}>
            {[
              { stat: '11', label: 'Verified Official Schemes', desc: 'Directly sourced from uploaded Central & State Gazette PDFs' },
              { stat: '₹10 Cr', label: 'Max Sovereign Guarantee', desc: 'Collateral-free credit backing delivered under CGTMSE EPM' },
              { stat: '35%', label: 'Max Margin Subsidy', desc: 'Direct capital assistance disbursed under PMEGP' },
              { stat: '100%', label: 'Source-Backed Rules', desc: 'Every requirement citations link directly to official guidelines' },
            ].map((s, i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    textAlign: 'center',
                    bgcolor: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                  }}
                >
                  <Typography variant="h3" sx={{ fontWeight: 900, color: '#0F2E59', mb: 0.5 }}>
                    {s.stat}
                  </Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#059669', mb: 0.5 }}>
                    {s.label}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>
                    {s.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 12: FINAL CTA ─── */}
      <Box sx={{ py: 10, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="md">
          <Paper
            elevation={0}
            sx={{
              p: { xs: 4, md: 6 },
              textAlign: 'center',
              bgcolor: '#F8FAFC',
              border: '2px solid #E2E8F0',
              borderRadius: '16px',
            }}
          >
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.8rem', md: '2.3rem' }, mb: 2 }}>
              Don't Miss a Benefit Your Business May Qualify For.
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748B', maxWidth: 560, mx: 'auto', mb: 4 }}>
              Create your business profile and let AI find relevant government support across Central and State portals.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
              <Button
                variant="contained"
                size="large"
                startIcon={<AutoAwesomeIcon sx={{ color: '#FEF08A' }} />}
                onClick={() => navigate('/register')}
                sx={{
                  background: 'linear-gradient(135deg, #E65100 0%, #EA580C 100%)',
                  color: '#FFFFFF',
                  fontWeight: 800,
                  fontSize: '1rem',
                  px: 4,
                  py: 1.4,
                  borderRadius: '8px',
                  textTransform: 'none',
                  '&:hover': { background: 'linear-gradient(135deg, #C2410C 0%, #9A3412 100%)' },
                }}
              >
                Find My Benefits
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/login')}
                sx={{
                  borderColor: '#CBD5E1',
                  color: '#0F2E59',
                  bgcolor: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.98rem',
                  px: 3.5,
                  py: 1.4,
                  borderRadius: '8px',
                  textTransform: 'none',
                  '&:hover': { bgcolor: '#F8FAFC' },
                }}
              >
                Sign In to Existing Account
              </Button>
            </Stack>
          </Paper>
        </Container>
      </Box>

      {/* ─── SECTION 13: COMPREHENSIVE FOOTER WITH STATUTORY DISCLAIMER ─── */}
      <Box
        component="footer"
        sx={{
          bgcolor: '#0F2E59',
          color: '#FFFFFF',
          pt: { xs: 8, md: 10 },
          pb: { xs: 6, md: 8 },
        }}
      >
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Grid container spacing={4} sx={{ mb: 6 }}>
            {/* Col 1: Platform */}
            <Grid item xs={12} md={3}>
              <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
                <Box
                  sx={{
                    width: 38,
                    height: 38,
                    borderRadius: '8px',
                    bgcolor: '#FFFFFF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <PolicyIcon sx={{ color: '#0F2E59', fontSize: 24 }} />
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#FFFFFF' }}>
                  Udyam<Box component="span" sx={{ color: '#FF9933' }}>Niti</Box>
                </Typography>
              </Stack>
              <Typography variant="body2" sx={{ color: '#CBD5E1', lineHeight: 1.7, mb: 3 }}>
                AI-Powered Government Benefits Discovery & Application Assistance Platform for Indian MSMEs.
              </Typography>
              <Typography variant="caption" sx={{ color: '#94A3B8' }}>
                Helpline: <strong>1800 11 7800</strong> • champion-msme@gov.in
              </Typography>
            </Grid>

            {/* Col 2: Schemes */}
            <Grid item xs={6} md={2}>
              <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#FFFFFF', mb: 2 }}>
                SCHEMES
              </Typography>
              <Stack spacing={1}>
                {['All Schemes', 'Credit & Finance', 'Subsidies & Incentives', 'Export Support', 'Technology Upgrade', 'Marketing Support'].map((item, idx) => (
                  <Typography
                    key={idx}
                    variant="body2"
                    sx={{ color: '#94A3B8', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
                    onClick={() => navigate('/dashboard')}
                  >
                    {item}
                  </Typography>
                ))}
              </Stack>
            </Grid>

            {/* Col 3: Resources */}
            <Grid item xs={6} md={2}>
              <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#FFFFFF', mb: 2 }}>
                RESOURCES
              </Typography>
              <Stack spacing={1}>
                {['Acts & Rules', 'Scheme Guidelines', 'Notifications', 'Circulars & Orders', 'Reports', 'FAQs'].map((item, idx) => (
                  <Typography
                    key={idx}
                    variant="body2"
                    sx={{ color: '#94A3B8', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
                    onClick={() => navigate('/dashboard')}
                  >
                    {item}
                  </Typography>
                ))}
              </Stack>
            </Grid>

            {/* Col 4: Government Links */}
            <Grid item xs={6} md={2.5}>
              <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#FFFFFF', mb: 2 }}>
                GOVERNMENT LINKS
              </Typography>
              <Stack spacing={1}>
                {[
                  { name: 'Ministry of MSME', url: 'https://msme.gov.in' },
                  { name: 'Udyam Registration Portal', url: 'https://udyamregistration.gov.in' },
                  { name: 'MSME Champions Portal', url: 'https://champions.gov.in' },
                  { name: 'NSIC Portal', url: 'https://nsic.co.in' },
                  { name: 'KVIC Portal', url: 'https://kvic.gov.in' },
                  { name: 'Gujarat IMD Portal', url: 'https://imd.gujarat.gov.in' },
                ].map((item, idx) => (
                  <Typography
                    key={idx}
                    component="a"
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    variant="body2"
                    sx={{ color: '#94A3B8', textDecoration: 'none', '&:hover': { color: '#FFFFFF' } }}
                  >
                    {item.name} ↗
                  </Typography>
                ))}
              </Stack>
            </Grid>

            {/* Col 5: Legal */}
            <Grid item xs={6} md={2.5}>
              <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#FFFFFF', mb: 2 }}>
                LEGAL & POLICY
              </Typography>
              <Stack spacing={1}>
                {['Privacy Policy', 'Terms of Service', 'Statutory Disclaimer', 'Accessibility Statement', 'Source Attributions'].map((item, idx) => (
                  <Typography
                    key={idx}
                    variant="body2"
                    sx={{ color: '#94A3B8', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
                    onClick={() => navigate('/')}
                  >
                    {item}
                  </Typography>
                ))}
              </Stack>
            </Grid>
          </Grid>

          <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.15)', mb: 3 }} />

          {/* Mandatory Statutory Disclaimer */}
          <Paper
            elevation={0}
            sx={{
              p: 2,
              bgcolor: 'rgba(0, 0, 0, 0.25)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              mb: 3,
            }}
          >
            <Stack direction="row" spacing={1.5} alignItems="flex-start">
              <WarningAmberIcon sx={{ color: '#FBBF24', fontSize: 20, mt: 0.2 }} />
              <Typography variant="caption" sx={{ color: '#CBD5E1', lineHeight: 1.6 }}>
                <strong>Statutory Disclaimer:</strong> This platform provides information and eligibility assistance based on official government sources. Final eligibility, approval and benefits are determined by the respective government authority.
              </Typography>
            </Stack>
          </Paper>

          <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center" spacing={2}>
            <Typography variant="caption" sx={{ color: '#94A3B8' }}>
              © {new Date().getFullYear()} UdyamNiti • Government of India & Gujarat State MSME Scheme Intelligence
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8' }}>
              Standard Compliance with Government of India Web Guidelines (GIGW)
            </Typography>
          </Stack>
        </Container>
      </Box>
    </Box>
  )
}

export default LandingPage
