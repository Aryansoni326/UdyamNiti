import React, { useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Divider,
  alpha,
} from '@mui/material'
import PolicyIcon from '@mui/icons-material/Policy'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import StarIcon from '@mui/icons-material/Star'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import CalendarTodayOutlinedIcon from '@mui/icons-material/CalendarTodayOutlined'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import SpeedIcon from '@mui/icons-material/Speed'
import GavelOutlinedIcon from '@mui/icons-material/GavelOutlined'
import FactCheckOutlinedIcon from '@mui/icons-material/FactCheckOutlined'
import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined'
import NotificationsActiveOutlinedIcon from '@mui/icons-material/NotificationsActiveOutlined'
import LoginIcon from '@mui/icons-material/Login'
import PersonAddAltIcon from '@mui/icons-material/PersonAddAlt'
import { tokens } from '../theme/tokens'

const KEY_SCHEMES = [
  {
    code: 'CGTMSE_EPM_EXPORT_2026',
    title: 'Special Credit Guarantee Scheme for Export Credit',
    ministry: 'DGFT & Ministry of Commerce / CGTMSE',
    benefit: 'Up to ₹10 Crore (85% Guarantee Cover)',
    highlight: 'Zero hard collateral or third-party guarantee required. Pre & post-shipment export credit for manufacturing MSMEs.',
    deadline: 'Valid till 31 March 2027',
    tag: 'CREDIT GUARANTEE',
    level: 'Central Government',
    docs: '6 Mandatory Documents',
  },
  {
    code: 'COIR_VIKAS_YOJANA_CVY',
    title: 'Coir Vikas Yojana – CITUS Technology Upgradation',
    ministry: 'Ministry of MSME / Coir Board Kochi',
    benefit: '25% Capital Subsidy up to ₹2.50 Cr',
    highlight: 'Direct Benefit Transfer (DBT) via PFMS for modern BIS-compliant plant & machinery modernization.',
    deadline: 'Rolling Annual Window',
    tag: 'CAPITAL SUBSIDY',
    level: 'Central Government',
    docs: '8 Mandatory Documents',
  },
  {
    code: 'GUJ_SER_TEXTILE_2025',
    title: 'Surat Economic Region (SER) Textile & MSME Park Assistance',
    ministry: 'Industries and Mines Department, Govt of Gujarat',
    benefit: '₹1.00 Crore Infrastructure Grant',
    highlight: 'Dedicated textile testing labs, R&D design facilities, warehousing, and solar power linkages in Gujarat.',
    deadline: 'Two-Year Window (May 2027)',
    tag: 'GUJARAT STATE',
    level: 'Gujarat State',
    docs: '6 Mandatory Documents',
  },
  {
    code: 'MSME_IC_SCHEME_2021',
    title: 'International Cooperation (IC) Scheme – MDA & Capacity Building',
    ministry: 'Ministry of Micro, Small & Medium Enterprises',
    benefit: '100% Space Rent (₹3L) & Airfare (₹1.5L)',
    highlight: 'Subsidies for international trade exhibitions, CBFTE export testing, and RCMC fee reimbursements.',
    deadline: 'Apply 60 days before event',
    tag: 'GLOBAL EXPORTS',
    level: 'Central Government',
    docs: '7 Mandatory Documents',
  },
]

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  // Handle smooth scroll when navigating to anchors
  useEffect(() => {
    if (location.hash) {
      const targetId = location.hash.replace('#', '')
      const el = document.getElementById(targetId)
      if (el) {
        setTimeout(() => el.scrollIntoView({ behavior: 'smooth' }), 100)
      }
    }
  }, [location.hash])

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#0A0F1E', color: '#F1F5F9' }}>
      {/* ─── HERO SECTION ─── */}
      <Box
        sx={{
          pt: { xs: 8, md: 12 },
          pb: { xs: 8, md: 12 },
          background: 'radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.22) 0%, rgba(10, 15, 30, 0) 70%)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: 880, mx: 'auto' }}>
            {/* Top pill badge */}
            <Chip
              icon={<VerifiedUserIcon sx={{ fontSize: '15px !important', color: '#34D399 !important' }} />}
              label="Official Central & Gujarat State Government MSME Intelligence"
              sx={{
                mb: 3,
                bgcolor: 'rgba(16, 185, 129, 0.12)',
                color: '#34D399',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                fontWeight: 600,
                fontSize: '0.82rem',
                py: 2,
                px: 1,
              }}
            />

            {/* Main Headline */}
            <Typography
              variant="h2"
              component="h1"
              sx={{
                fontWeight: 800,
                fontSize: { xs: '2.2rem', sm: '3rem', md: '3.6rem' },
                lineHeight: { xs: 1.2, md: 1.15 },
                letterSpacing: '-0.03em',
                color: '#FFFFFF',
                mb: 2.5,
              }}
            >
              The Government Schemes & Subsidies Platform for{' '}
              <Box
                component="span"
                sx={{
                  background: 'linear-gradient(135deg, #818CF8 0%, #38BDF8 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Indian MSMEs
              </Box>
            </Typography>

            {/* Sub-headline */}
            <Typography
              variant="body1"
              sx={{
                color: '#94A3B8',
                fontSize: { xs: '1rem', md: '1.2rem' },
                lineHeight: 1.6,
                maxWidth: 760,
                mx: 'auto',
                mb: 4.5,
              }}
            >
              Discover 30+ Central and Gujarat Government schemes, unlock up to ₹10 Crore in collateral-free credit,
              and calculate eligible capital subsidies with 100% legal certainty.
            </Typography>

            {/* Main Call to Action Buttons */}
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
              alignItems="center"
              sx={{ mb: 6 }}
            >
              <Button
                variant="contained"
                size="large"
                startIcon={<PersonAddAltIcon />}
                endIcon={<ArrowForwardIcon />}
                onClick={() => navigate('/register')}
                sx={{
                  background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '1rem',
                  px: 4,
                  py: 1.5,
                  borderRadius: '10px',
                  textTransform: 'none',
                  boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)',
                  },
                }}
              >
                Register Enterprise
              </Button>

              <Button
                variant="outlined"
                size="large"
                startIcon={<LoginIcon />}
                onClick={() => navigate('/login')}
                sx={{
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  color: '#FFFFFF',
                  fontWeight: 600,
                  fontSize: '1rem',
                  px: 3.5,
                  py: 1.5,
                  borderRadius: '10px',
                  textTransform: 'none',
                  bgcolor: 'rgba(255, 255, 255, 0.04)',
                  '&:hover': {
                    borderColor: '#818CF8',
                    bgcolor: 'rgba(255, 255, 255, 0.08)',
                  },
                }}
              >
                Sign In to Account
              </Button>
            </Stack>

            {/* Quick 4-column metric highlights */}
            <Grid container spacing={2}>
              {[
                { value: '₹10 Crore', label: 'Max Collateral-Free Credit' },
                { value: '15% – 25%', label: 'Capital & Machinery Subsidies' },
                { value: '30+ Schemes', label: 'Central & Gujarat Mapped' },
                { value: '100% Verified', label: 'Official Gazette Citations' },
              ].map((m, i) => (
                <Grid item xs={6} sm={3} key={i}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      bgcolor: 'rgba(26, 34, 53, 0.6)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                      borderRadius: '10px',
                    }}
                  >
                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#FFFFFF', fontSize: '1.25rem' }}>
                      {m.value}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.78rem' }}>
                      {m.label}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
        </Container>
      </Box>

      {/* ─── SECTION 1: SERVICES WE PROVIDE ─── */}
      <Box id="services" sx={{ py: { xs: 8, md: 12 }, bgcolor: 'rgba(10, 15, 30, 0.5)' }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 6 }}>
            <Chip
              label="OUR SERVICES"
              size="small"
              sx={{
                mb: 1.5,
                bgcolor: 'rgba(99, 102, 241, 0.15)',
                color: '#818CF8',
                fontWeight: 700,
                fontSize: '0.75rem',
                letterSpacing: '0.05em',
              }}
            />
            <Typography
              variant="h3"
              component="h2"
              sx={{ fontWeight: 800, fontSize: { xs: '1.8rem', md: '2.4rem' }, mb: 1.5, color: '#FFFFFF' }}
            >
              Services We Provide to Users
            </Typography>
            <Typography variant="body1" sx={{ color: '#94A3B8', fontSize: '1.05rem' }}>
              Everything your enterprise needs to identify, verify, and secure government financial assistance.
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {[
              {
                icon: <AutoAwesomeIcon sx={{ fontSize: 30, color: '#818CF8' }} />,
                title: '1. AI Scheme Discovery & Matching',
                desc: 'Instantly matches your enterprise Udyam details, plant & machinery investment, turnover, and sector against all active Central and Gujarat State schemes.',
              },
              {
                icon: <AccountTreeOutlinedIcon sx={{ fontSize: 30, color: '#34D399' }} />,
                title: '2. Multi-Scheme Stacking Optimization',
                desc: 'Combines credit guarantees with state capital subsidies safely and legally without triggering mutual exclusion disqualifications.',
              },
              {
                icon: <FactCheckOutlinedIcon sx={{ fontSize: 30, color: '#38BDF8' }} />,
                title: '3. Statutory Document Audit Checklist',
                desc: 'Generates an itemized checklist of mandatory documents (DPR, CE Valuation, Bank Sanction) extracted verbatim from government gazette releases.',
              },
              {
                icon: <NotificationsActiveOutlinedIcon sx={{ fontSize: 30, color: '#FBBF24' }} />,
                title: '4. Live Policy & Gazette Radar',
                desc: 'Monitors ongoing gazette notifications and circulars, notifying your business when deadlines extend or budget limits expand.',
              },
              {
                icon: <GavelOutlinedIcon sx={{ fontSize: 30, color: '#C084FC' }} />,
                title: '5. Clause-Level Legal Citations',
                desc: 'Provides exact operational guideline paragraph and circular citations for every scheme so banks and DIC officers approve without delays.',
              },
              {
                icon: <SpeedIcon sx={{ fontSize: 30, color: '#F472B6' }} />,
                title: '6. End-to-End Application Guidance',
                desc: 'A structured roadmap guiding your team from pre-qualification to portal submission and DBT subsidy disbursement.',
              },
            ].map((service, i) => (
              <Grid item xs={12} md={4} key={i}>
                <Card
                  sx={{
                    height: '100%',
                    bgcolor: '#1A2235',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '12px',
                    p: 1.5,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: '#6366F1',
                      transform: 'translateY(-3px)',
                    },
                  }}
                >
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ mb: 2 }}>{service.icon}</Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#FFFFFF', fontSize: '1.1rem', mb: 1 }}>
                      {service.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.88rem', lineHeight: 1.6 }}>
                      {service.desc}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 2: BENEFITS WE PROVIDE ─── */}
      <Box
        id="benefits"
        sx={{
          py: { xs: 8, md: 12 },
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 6 }}>
            <Chip
              label="BENEFITS"
              size="small"
              sx={{
                mb: 1.5,
                bgcolor: 'rgba(16, 185, 129, 0.15)',
                color: '#34D399',
                fontWeight: 700,
                fontSize: '0.75rem',
                letterSpacing: '0.05em',
              }}
            />
            <Typography
              variant="h3"
              component="h2"
              sx={{ fontWeight: 800, fontSize: { xs: '1.8rem', md: '2.4rem' }, mb: 1.5, color: '#FFFFFF' }}
            >
              Benefits Provided to MSME Users
            </Typography>
            <Typography variant="body1" sx={{ color: '#94A3B8', fontSize: '1.05rem' }}>
              Why MSME founders, CFOs, and business owners choose UdyamNiti over manual research.
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {[
              {
                stat: '₹15L – ₹10Cr',
                title: 'Non-Dilutive Capital Access',
                desc: 'Claim capital subsidies, interest subvention, and collateral guarantees without losing company equity or pledging personal family property.',
                color: '#34D399',
              },
              {
                stat: '90% Time Saved',
                title: 'Minutes, Not Weeks',
                desc: 'Replace weeks of reading complex 80-page government PDF guidelines with an automated 2-minute scheme eligibility scan.',
                color: '#38BDF8',
              },
              {
                stat: 'Zero Rejections',
                title: 'First-Time Application Approval',
                desc: 'Pre-validated document checklists prevent missing paperwork mistakes that cause 68% of MSME government claims to stall.',
                color: '#818CF8',
              },
              {
                stat: '35%+ Combined Yield',
                title: 'Multi-Scheme Advantage',
                desc: 'Learn how to legally combine Gujarat State assistance with Central schemes to maximize total capital recovery for your factory.',
                color: '#FBBF24',
              },
              {
                stat: '100% Legal Proof',
                title: 'Zero AI Hallucinations',
                desc: 'Every single subsidy number, percentage, and condition is mathematically verified against the official gazette notifications.',
                color: '#F472B6',
              },
              {
                stat: 'Year-Round Alerts',
                title: 'Never Miss a Deadline',
                desc: 'Automated monitoring keeps your business notified of annual fiscal year cutoffs and special cluster incentive windows.',
                color: '#C084FC',
              },
            ].map((benefit, i) => (
              <Grid item xs={12} sm={6} md={4} key={i}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    height: '100%',
                    bgcolor: '#1A2235',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '12px',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: benefit.color,
                      transform: 'translateY(-3px)',
                    },
                  }}
                >
                  <Typography variant="h4" sx={{ fontWeight: 900, color: benefit.color, fontSize: '1.6rem', mb: 1 }}>
                    {benefit.stat}
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#FFFFFF', fontSize: '1.05rem', mb: 1 }}>
                    {benefit.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.86rem', lineHeight: 1.6 }}>
                    {benefit.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 3: HOW IT WORKS ─── */}
      <Box id="how-it-works" sx={{ py: { xs: 8, md: 12 }, bgcolor: 'rgba(10, 15, 30, 0.4)' }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 6 }}>
            <Chip
              label="THE WORKFLOW"
              size="small"
              sx={{
                mb: 1.5,
                bgcolor: 'rgba(99, 102, 241, 0.15)',
                color: '#818CF8',
                fontWeight: 700,
                fontSize: '0.75rem',
              }}
            />
            <Typography
              variant="h3"
              component="h2"
              sx={{ fontWeight: 800, fontSize: { xs: '1.8rem', md: '2.4rem' }, mb: 1.5, color: '#FFFFFF' }}
            >
              How It Works
            </Typography>
            <Typography variant="body1" sx={{ color: '#94A3B8', fontSize: '1.05rem' }}>
              From registration on this landing page straight to your active scheme intelligence dashboard.
            </Typography>
          </Box>

          <Grid container spacing={3.5}>
            {[
              {
                step: '01',
                title: 'Register or Sign In',
                desc: 'Click Register or Sign In on the top right. Enter your enterprise profile (or demo credentials) in under 30 seconds.',
              },
              {
                step: '02',
                title: 'Instant Redirect to Dashboard',
                desc: 'Once authenticated, you are instantly redirected to your enterprise Schemes Dashboard where all 30+ schemes are ready for you.',
              },
              {
                step: '03',
                title: 'Claim & File Subsidies',
                desc: 'View your pre-calculated eligibility, download document checklists, and generate verified reports for your bank and DIC officer.',
              },
            ].map((st, i) => (
              <Grid item xs={12} md={4} key={i}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3.5,
                    height: '100%',
                    bgcolor: '#1A2235',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '12px',
                  }}
                >
                  <Typography
                    variant="h3"
                    sx={{ fontWeight: 900, color: 'rgba(99, 102, 241, 0.3)', fontFamily: tokens.font.mono, mb: 1 }}
                  >
                    {st.step}
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: '#FFFFFF', fontSize: '1.15rem', mb: 1.5 }}>
                    {st.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.88rem', lineHeight: 1.6 }}>
                    {st.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 4: KEY SCHEMES ─── */}
      <Box id="schemes" sx={{ py: { xs: 8, md: 12 }, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
        <Container maxWidth="lg">
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            justifyContent="space-between"
            alignItems={{ xs: 'flex-start', sm: 'flex-end' }}
            sx={{ mb: 4 }}
          >
            <Box>
              <Chip
                label="CATALOG PREVIEW"
                size="small"
                sx={{
                  mb: 1.5,
                  bgcolor: 'rgba(99, 102, 241, 0.15)',
                  color: '#818CF8',
                  fontWeight: 700,
                  fontSize: '0.75rem',
                }}
              />
              <Typography
                variant="h3"
                component="h2"
                sx={{ fontWeight: 800, fontSize: { xs: '1.8rem', md: '2.2rem' }, color: '#FFFFFF' }}
              >
                Key Supported Schemes
              </Typography>
            </Box>

            <Button
              onClick={() => navigate('/register')}
              endIcon={<ArrowForwardIcon sx={{ fontSize: 16 }} />}
              sx={{
                color: '#818CF8',
                fontWeight: 600,
                fontSize: '0.9rem',
                textTransform: 'none',
                p: 0,
                '&:hover': { color: '#FFFFFF' },
              }}
            >
              Register to View All Schemes →
            </Button>
          </Stack>

          <Grid container spacing={3}>
            {KEY_SCHEMES.map((scheme) => (
              <Grid item xs={12} sm={6} key={scheme.code}>
                <Card
                  sx={{
                    height: '100%',
                    bgcolor: '#1A2235',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '12px',
                    p: 2.5,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                  }}
                >
                  <Box>
                    <Stack direction="row" spacing={1} sx={{ mb: 1.5 }}>
                      <Chip
                        label={scheme.tag}
                        size="small"
                        sx={{ bgcolor: '#F59E0B', color: '#0F172A', fontWeight: 800, fontSize: '0.65rem', height: 20 }}
                      />
                      <Chip
                        label={scheme.level}
                        size="small"
                        sx={{ bgcolor: 'rgba(255, 255, 255, 0.08)', color: '#CBD5E1', fontSize: '0.68rem', height: 20 }}
                      />
                    </Stack>

                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#FFFFFF', fontSize: '1.05rem', mb: 0.5 }}>
                      {scheme.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#94A3B8', display: 'block', mb: 1.5 }}>
                      {scheme.ministry}
                    </Typography>

                    <Box sx={{ p: 1.5, borderRadius: '8px', bgcolor: 'rgba(10, 15, 30, 0.6)', mb: 2 }}>
                      <Typography variant="caption" sx={{ color: '#94A3B8', display: 'block', fontSize: '0.72rem' }}>
                        Maximum Benefit:
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#34D399', fontWeight: 800, fontSize: '0.92rem' }}>
                        {scheme.benefit}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#E2E8F0', display: 'block', mt: 0.5, fontSize: '0.76rem' }}>
                        {scheme.highlight}
                      </Typography>
                    </Box>
                  </Box>

                  <Button
                    size="small"
                    onClick={() => navigate('/register')}
                    endIcon={<ArrowForwardIcon sx={{ fontSize: 14 }} />}
                    sx={{
                      color: '#818CF8',
                      fontSize: '0.82rem',
                      fontWeight: 700,
                      textTransform: 'none',
                      justifyContent: 'flex-start',
                      p: 0,
                      '&:hover': { color: '#FFFFFF' },
                    }}
                  >
                    Register to Unlock Scheme Details →
                  </Button>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── SECTION 5: FAQ ─── */}
      <Box id="faq" sx={{ py: { xs: 8, md: 12 }, bgcolor: 'rgba(10, 15, 30, 0.6)', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center', mb: 5 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, fontSize: '2rem', mb: 1.5, color: '#FFFFFF' }}>
              Frequently Asked Questions
            </Typography>
            <Typography variant="body2" sx={{ color: '#94A3B8' }}>
              Answers to questions about accessing the platform and scheme qualification.
            </Typography>
          </Box>

          <Stack spacing={2}>
            {[
              {
                q: 'How do I access the Dashboard?',
                a: 'Click "Register" or "Sign In" at the top of this landing page. After filling in your enterprise details and clicking submit, you are instantly redirected to the Home / Dashboard.',
              },
              {
                q: 'Can my business combine Gujarat State schemes with Central Government schemes?',
                a: 'Yes! Our multi-scheme stacking engine analyzes whether pairing Central schemes (such as CGTMSE credit guarantee) with Gujarat state subsidies is legally permissible without mutual exclusion penalties.',
              },
              {
                q: 'Do I need an active Udyam registration to get started?',
                a: 'No. You can register using your approximate plant & machinery investment, turnover, and sector. Our system will evaluate what you qualify for and guide you on obtaining your official certificate.',
              },
            ].map((faq, i) => (
              <Accordion
                key={i}
                elevation={0}
                sx={{
                  bgcolor: '#1A2235',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '10px !important',
                  '&:before': { display: 'none' },
                }}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#94A3B8' }} />}>
                  <Typography sx={{ fontWeight: 700, color: '#FFFFFF', fontSize: '0.96rem' }}>
                    {faq.q}
                  </Typography>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0, pb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.88rem', lineHeight: 1.6 }}>
                    {faq.a}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        </Container>
      </Box>

      {/* ─── FINAL CTA SECTION ─── */}
      <Box sx={{ py: 10, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
        <Container maxWidth="md">
          <Paper
            elevation={0}
            sx={{
              p: { xs: 4, md: 6 },
              textAlign: 'center',
              borderRadius: '16px',
              bgcolor: '#1A2235',
              border: '1px solid rgba(99, 102, 241, 0.3)',
            }}
          >
            <Typography variant="h3" sx={{ fontWeight: 800, fontSize: { xs: '1.8rem', md: '2.2rem' }, mb: 2, color: '#FFFFFF' }}>
              Ready to Claim Your Eligible Subsidies?
            </Typography>
            <Typography variant="body1" sx={{ color: '#94A3B8', mb: 4, maxWidth: 560, mx: 'auto' }}>
              Register your enterprise in 30 seconds and enter the Schemes Dashboard directly.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
              <Button
                variant="contained"
                size="large"
                startIcon={<PersonAddAltIcon />}
                onClick={() => navigate('/register')}
                sx={{
                  bgcolor: '#4F46E5',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.98rem',
                  px: 3.5,
                  py: 1.4,
                  borderRadius: '8px',
                  textTransform: 'none',
                  '&:hover': { bgcolor: '#4338CA' },
                }}
              >
                Register & Go to Dashboard
              </Button>
              <Button
                variant="outlined"
                size="large"
                startIcon={<LoginIcon />}
                onClick={() => navigate('/login')}
                sx={{
                  borderColor: 'rgba(255, 255, 255, 0.25)',
                  color: '#FFFFFF',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  px: 3,
                  py: 1.4,
                  borderRadius: '8px',
                  textTransform: 'none',
                  '&:hover': { borderColor: '#818CF8' },
                }}
              >
                Sign In to Account
              </Button>
            </Stack>
          </Paper>
        </Container>
      </Box>
    </Box>
  )
}

export default LandingPage
