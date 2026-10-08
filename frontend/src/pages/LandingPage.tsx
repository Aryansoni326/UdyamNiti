import React, { useState, useEffect, useMemo } from 'react'
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
  IconButton,
} from '@mui/material'
import PolicyIcon from '@mui/icons-material/Policy'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import SearchIcon from '@mui/icons-material/Search'
import FactCheckOutlinedIcon from '@mui/icons-material/FactCheckOutlined'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import MonetizationOnOutlinedIcon from '@mui/icons-material/MonetizationOnOutlined'
import BuildCircleOutlinedIcon from '@mui/icons-material/BuildCircleOutlined'
import FlightTakeoffOutlinedIcon from '@mui/icons-material/FlightTakeoffOutlined'
import StorefrontOutlinedIcon from '@mui/icons-material/StorefrontOutlined'
import SchoolOutlinedIcon from '@mui/icons-material/SchoolOutlined'
import RocketLaunchOutlinedIcon from '@mui/icons-material/RocketLaunchOutlined'
import LightbulbOutlinedIcon from '@mui/icons-material/LightbulbOutlined'
import ApartmentOutlinedIcon from '@mui/icons-material/ApartmentOutlined'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore'
import NavigateNextIcon from '@mui/icons-material/NavigateNext'
import PauseIcon from '@mui/icons-material/Pause'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import RestartAltIcon from '@mui/icons-material/RestartAlt'
import { tokens } from '../theme/tokens'
import { useLanguage } from '../i18n'
import { toast } from 'sonner'
import pmegpBanner from '../assets/pmegp_banner.jpg'
import exportCreditBanner from '../assets/export_credit_banner.jpg'
import gujaratTextileBanner from '../assets/gujarat_textile_banner.jpg'
import zedBanner from '../assets/zed_banner.jpg'

interface SchemeSlide {
  id: number
  tag: string
  title: string
  highlightText: string
  subtitle: string
  maxBenefit: string
  officialGazette: string
  schemeCode: string
  ctaText: string
  imageUrl: string
  gradientBg: string
}

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()
  const { t } = useLanguage()

  // ─── 1. AUTOMATIC ROTATING SLIDESHOW BANNER (DATA FROM OFFICIAL SCHEME PDFS) ───
  const SCHEME_SLIDES: SchemeSlide[] = [
    {
      id: 1,
      tag: 'Central Ministry • KVIC Guidelines',
      title: "Prime Minister's Employment Generation Programme (PMEGP)",
      highlightText: 'Up to ₹50 Lakh Project • 35% Margin Money Subsidy',
      subtitle:
        'Direct DBT capital subsidy for Micro Enterprises in manufacturing and services. 2nd financial assistance loan up to ₹1.00 Crore for upgrading technology and capacity.',
      maxBenefit: '₹50.00 Lakh Subsidy',
      officialGazette: 'Source: pmegp scheme.pdf (Ministry of MSME / KVIC)',
      schemeCode: 'PMEGP_MSME_SCHEME',
      ctaText: 'Check PMEGP Eligibility',
      imageUrl: pmegpBanner,
      gradientBg: 'linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 45%, #FEF3C7 100%)',
    },
    {
      id: 2,
      tag: 'CGTMSE Circular 257 & DGFT',
      title: 'Special Credit Guarantee Scheme – Export Credit (EPM - Niryat Protsahan)',
      highlightText: '₹10.00 Crore Collateral-Free Credit • 85% Guarantee',
      subtitle:
        'Sovereign risk coverage for pre-shipment & post-shipment export finance. Zero third-party collateral required. Annual Guarantee Fee (AGF) reduced and capped at 1.50%.',
      maxBenefit: '₹10.00 Crore Guarantee',
      officialGazette: 'Source: Circular 257 - CGS for Export credit merged.pdf',
      schemeCode: 'CGTMSE_EPM_EXPORT_2026',
      ctaText: 'View Export Credit Cover',
      imageUrl: exportCreditBanner,
      gradientBg: 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 45%, #E0E7FF 100%)',
    },
    {
      id: 3,
      tag: 'Government of Gujarat • Industries and Mines Department',
      title: 'Assistance for Developing SER Textile and MSME Park 2025-26',
      highlightText: '100% Capital Grant for Testing Labs & Common Facilities',
      subtitle:
        'Financial assistance up to ₹1.00 Crore for developing common testing laboratories, R&D design studios, and Zero Liquid Discharge (ZLD) effluent facilities in Gujarat textile clusters.',
      maxBenefit: '₹1.00 Crore Grant',
      officialGazette: 'Source: 1.msme.pdf (GR No. IMD/MRT/0597/G, Gandhinagar)',
      schemeCode: 'GUJ_SER_TEXTILE_2025',
      ctaText: 'Explore Gujarat SER Assistance',
      imageUrl: gujaratTextileBanner,
      gradientBg: 'linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 45%, #CCFBF1 100%)',
    },
    {
      id: 4,
      tag: 'Quality Council of India (QCI) & M/o MSME',
      title: 'MSME Sustainable (ZED) Certification Scheme (Phase-II)',
      highlightText: 'Up to 80% Certification Subsidy + ₹5 Lakh Handholding',
      subtitle:
        'Bronze, Silver & Gold zero-defect certification with 80% subsidy for Micro, 60% for Small. Includes bank interest concessions and international quality compliance support.',
      maxBenefit: 'Up to 80% Subsidy',
      officialGazette: 'Source: ZED_Guidance_Document_NIC_Division_24 & 27.pdf',
      schemeCode: 'MSME_ZED_CERTIFICATION',
      ctaText: 'Get ZED Certification Assistance',
      imageUrl: zedBanner,
      gradientBg: 'linear-gradient(135deg, #FAF5FF 0%, #F3E8FF 45%, #EDE9FE 100%)',
    },
  ]

  // Slideshow State (3-second continuous automatic rotation)
  const [currentSlide, setCurrentSlide] = useState<number>(0)

  // User Authentication State
  const [currentUser, setCurrentUser] = useState<any>(null)

  useEffect(() => {
    try {
      const stored = localStorage.getItem('udyamniti_user')
      if (stored) {
        const parsed = JSON.parse(stored)
        if (parsed && (parsed.isLoggedIn || parsed.email || parsed.directorName)) {
          setCurrentUser(parsed)
        }
      }
    } catch {
      setCurrentUser(null)
    }
  }, [])

  const isLoggedIn = Boolean(currentUser)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % SCHEME_SLIDES.length)
    }, 3000)
    return () => clearInterval(timer)
  }, [SCHEME_SLIDES.length])

  const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % SCHEME_SLIDES.length)
  const prevSlide = () => setCurrentSlide((prev) => (prev - 1 + SCHEME_SLIDES.length) % SCHEME_SLIDES.length)

  // ─── 2. ALL 11 VERIFIED SCHEMES DERIVED FROM UPLOADED PDFS (REUSABLE DATA) ───
  const ALL_OFFICIAL_SCHEMES = [
    {
      code: 'CGTMSE_EPM_EXPORT_2026',
      name: 'Special Credit Guarantee Scheme – Export Credit (EPM - Niryat Protsahan)',
      shortName: 'Export Credit Collateral Support (EPM)',
      ministry: 'Dept of Commerce / CGTMSE & DGFT',
      gazette: 'CGTMSE Circular No. 257 / 2025-26',
      pdfFile: 'Circular 257 - CGS for Export credit merged.pdf',
      level: 'central',
      category: 'credit_guarantee',
      maxBenefit: '₹10.00 Crore',
      highlight: '85% Guarantee for Micro & Small (75% CGTMSE + 10% DGFT), 65% for Medium. Zero collateral required.',
      categoryColor: '#059669',
      targetSectors: ['manufacturing', 'textiles', 'chemicals', 'food', 'services'],
      targetStates: ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Uttar Pradesh', 'All India'],
      targetSizes: ['micro', 'small', 'medium'],
      baseMatch: 88,
    },
    {
      code: 'PMEGP_MSME_SCHEME',
      name: "Prime Minister's Employment Generation Programme (PMEGP)",
      shortName: 'PMEGP Margin Money Subsidy',
      ministry: 'Ministry of MSME / KVIC',
      gazette: 'PMEGP Comprehensive Guidelines 2022-26',
      pdfFile: 'pmegp scheme.pdf',
      level: 'central',
      category: 'capital_subsidy',
      maxBenefit: '₹50.00 Lakh',
      highlight: '15% to 35% margin money capital subsidy. Up to ₹17.5L in rural areas; 2nd loan up to ₹1 Cr.',
      categoryColor: '#D97706',
      targetSectors: ['manufacturing', 'services', 'food', 'textiles', 'coir'],
      targetStates: ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Uttar Pradesh', 'All India'],
      targetSizes: ['micro', 'small'],
      baseMatch: 92,
    },
    {
      code: 'GUJ_SER_TEXTILE_2025',
      name: 'Assistance for Developing SER Textile and MSME Park 2025-26',
      shortName: 'SER Textile & MSME Park Assistance (Gujarat)',
      ministry: 'Industries and Mines Department, Government of Gujarat',
      gazette: 'GR No. IMD/MRT/e-file/9/2025/0597/G, Gandhinagar',
      pdfFile: '1.msme.pdf',
      level: 'state_gujarat',
      category: 'infrastructure',
      maxBenefit: '₹1.00 Crore',
      highlight: '100% grant for common testing labs, R&D design facilities, zero-liquid effluent recycling in Surat hub.',
      categoryColor: '#2563EB',
      targetSectors: ['textiles', 'manufacturing'],
      targetStates: ['Gujarat'],
      targetSizes: ['micro', 'small', 'medium'],
      baseMatch: 95,
    },
    {
      code: 'MSME_ZED_CERTIFICATION',
      name: 'MSME Sustainable (ZED) Certification Scheme (Phase-II)',
      shortName: 'ZED Sustainable Certification',
      ministry: 'Ministry of MSME / QCI',
      gazette: 'MSME Sustainable (ZED) Guidelines 2022',
      pdfFile: 'ZED_Guidance_Document_NIC_Division_24 & 27.pdf',
      level: 'central',
      category: 'quality_certification',
      maxBenefit: 'Up to 80% Subsidy',
      highlight: '₹5L consulting + ₹3L tech support + 80% certification reimbursement + bank interest concessions.',
      categoryColor: '#16A34A',
      targetSectors: ['manufacturing', 'textiles', 'chemicals', 'food'],
      targetStates: ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Uttar Pradesh', 'All India'],
      targetSizes: ['micro', 'small', 'medium'],
      baseMatch: 87,
    },
    {
      code: 'TREDS_CGTMSE_CIRCULAR_262',
      name: 'Credit Guarantee Scheme for Factoring on TReDS (Circular 262)',
      shortName: 'TReDS Invoice Discounting Guarantee',
      ministry: 'Ministry of MSME & RBI / CGTMSE',
      gazette: 'CGTMSE Circular No. 262 / 2025-26',
      pdfFile: 'TReDS Cicular 262.pdf',
      level: 'central',
      category: 'credit_guarantee',
      maxBenefit: '₹5.00 Crore',
      highlight: '85% credit cover on factored receivables. Sub-24 hour liquidity on RXIL/M1xchange without collateral.',
      categoryColor: '#059669',
      targetSectors: ['manufacturing', 'services', 'textiles', 'chemicals'],
      targetStates: ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Uttar Pradesh', 'All India'],
      targetSizes: ['micro', 'small', 'medium'],
      baseMatch: 84,
    },
    {
      code: 'PMS_MARKETING_SUPPORT',
      name: 'Procurement and Marketing Support (PMS) Scheme',
      shortName: 'Procurement & Marketing Support (PMS)',
      ministry: 'Office of DC-MSME, Ministry of MSME',
      gazette: 'OM F.No. 21(1)/2018-MA, PMS Guidelines',
      pdfFile: 'OM & PMS Scheme Guidelines.pdf',
      level: 'central',
      category: 'market_development',
      maxBenefit: '₹1.50 Lakh Stall + Barcode',
      highlight: '100% stall rent reimbursement, ₹50,000 barcode support, and e-commerce packaging grants.',
      categoryColor: '#CA8A04',
      targetSectors: ['manufacturing', 'textiles', 'food', 'services', 'coir'],
      targetStates: ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Uttar Pradesh', 'All India'],
      targetSizes: ['micro', 'small'],
      baseMatch: 81,
    },
    {
      code: 'MSME_IC_SCHEME_2021',
      name: 'International Cooperation (IC) Scheme (MDA & CBFTE)',
      shortName: 'International Cooperation Scheme',
      ministry: 'Ministry of MSME, Government of India',
      gazette: 'F.No.4/8/2021-IC, Ministry of MSME',
      pdfFile: 'Final and approved IC Scheme Guidelines-2021.pdf',
      level: 'central',
      category: 'export_support',
      maxBenefit: '100% Stall + Airfare',
      highlight: '₹3.00L stall rent + ₹1.50L airfare + 75% testing & RCMC fee reimbursement under CBFTE.',
      categoryColor: '#EA580C',
      targetSectors: ['manufacturing', 'textiles', 'chemicals', 'food'],
      targetStates: ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Uttar Pradesh', 'All India'],
      targetSizes: ['micro', 'small', 'medium'],
      baseMatch: 83,
    },
    {
      code: 'MSE_CDP_CLUSTER_DEV',
      name: 'Micro and Small Enterprises Cluster Development Programme (MSE-CDP)',
      shortName: 'MSE Cluster Development (MSE-CDP)',
      ministry: 'Office of Development Commissioner (MSME)',
      gazette: 'MSE-CDP Revised Scheme Guidelines 2022',
      pdfFile: 'msme-cdp.pdf',
      level: 'central',
      category: 'infrastructure',
      maxBenefit: '₹21.00 Crore Grant',
      highlight: '70% GoI grant for Common Facility Centres (CFCs on projects up to ₹30 Cr) and new industrial estates.',
      categoryColor: '#0891B2',
      targetSectors: ['manufacturing', 'textiles', 'chemicals', 'food'],
      targetStates: ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Uttar Pradesh', 'All India'],
      targetSizes: ['micro', 'small'],
      baseMatch: 80,
    },
    {
      code: 'COIR_VIKAS_YOJANA_CVY',
      name: 'Coir Vikas Yojana (CVY) – CITUS, MCY, EMP, DMP',
      shortName: 'Coir Vikas Yojana (CVY)',
      ministry: 'Ministry of MSME / Coir Board',
      gazette: 'Order No. 5(9)/2017-Coir/77, CVY Guidelines',
      pdfFile: 'cvy.schemes.pdf',
      level: 'central',
      category: 'capital_subsidy',
      maxBenefit: '₹2.50 Crore',
      highlight: '25% capital subsidy on BIS modern machinery (CITUS) via DBT/PFMS + overseas fair stall grants.',
      categoryColor: '#7C3AED',
      targetSectors: ['coir', 'manufacturing'],
      targetStates: ['Gujarat', 'Tamil Nadu', 'Karnataka', 'All India'],
      targetSizes: ['micro', 'small'],
      baseMatch: 78,
    },
    {
      code: 'SFURTI_CLUSTER_SCHEME',
      name: 'Scheme of Fund for Regeneration of Traditional Industries (SFURTI)',
      shortName: 'SFURTI Traditional Clusters',
      ministry: 'Ministry of MSME / KVIC / Coir Board',
      gazette: 'SFURTI Comprehensive Scheme Guidelines 2021-26',
      pdfFile: 'SFURTI_NEW_GUIDELINES.pdf',
      level: 'central',
      category: 'infrastructure',
      maxBenefit: '₹5.00 Crore',
      highlight: '90-95% GoI grant for CFCs, modern machinery, and artisan raw material banks.',
      categoryColor: '#4F46E5',
      targetSectors: ['manufacturing', 'textiles', 'coir', 'food'],
      targetStates: ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Uttar Pradesh', 'All India'],
      targetSizes: ['micro', 'small'],
      baseMatch: 79,
    },
    {
      code: 'NSSH_SPECIAL_CLCSS',
      name: 'National SC-ST Hub (NSSH) – Special Capital Subsidy (SCLCSS)',
      shortName: 'NSSH Special Capital Subsidy',
      ministry: 'Ministry of MSME / NSIC',
      gazette: 'National SC-ST Hub Guidelines 2021-26',
      pdfFile: 'NSSH_Guidelines_Sub_scheme_0 & 1.pdf',
      level: 'central',
      category: 'capital_subsidy',
      maxBenefit: '₹25.00 Lakh',
      highlight: '25% upfront subsidy on term loans up to ₹1 Cr for SC/ST-owned enterprises + 100% tender fee waivers.',
      categoryColor: '#BE185D',
      targetSectors: ['manufacturing', 'textiles', 'services', 'food'],
      targetStates: ['Gujarat', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Uttar Pradesh', 'All India'],
      targetSizes: ['micro', 'small'],
      baseMatch: 82,
    },
  ]

  // AI Assistant Query State
  const [aiQuestion, setAiQuestion] = useState('')

  const handleAskAI = (sampleQuery?: string) => {
    const q = sampleQuery || aiQuestion
    if (!q.trim()) {
      toast.info('Please enter a question for MSME AI.')
      return
    }
    navigate(`/dashboard?mode=ai&q=${encodeURIComponent(q.trim())}`)
  }

  const activeSlide = SCHEME_SLIDES[currentSlide]

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F8FAFC', color: '#0F172A' }}>
      {/* ─── 1. HERO SLIDESHOW: ANIMATED & AUTOMATIC MOVING SCHEMES BANNER ─── */}
      <Box
        sx={{
          width: '100%',
          bgcolor: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          position: 'relative',
          overflow: 'hidden',
          userSelect: 'none',
        }}
        onMouseEnter={() => setIsSlidePaused(true)}
        onMouseLeave={() => setIsSlidePaused(false)}
      >
        <Container maxWidth="xl" disableGutters sx={{ px: { xs: 2, md: 3 }, py: { xs: 2, md: 2.5 } }}>
          <Box
            sx={{
              position: 'relative',
              borderRadius: { xs: '12px', md: '16px' },
              overflow: 'hidden',
              minHeight: { xs: 360, sm: 400, md: 450 },
              background: activeSlide.gradientBg,
              border: '1px solid #E2E8F0',
              boxShadow: '0 4px 20px rgba(15, 23, 42, 0.06)',
              display: 'flex',
              alignItems: 'center',
              transition: 'background 0.5s ease',
            }}
          >
            <Grid container alignItems="center" sx={{ height: '100%' }}>
              {/* Left Column: Scheme Title, Highlights & Action */}
              <Grid item xs={12} md={7} sx={{ p: { xs: 3, sm: 4, md: 5.5 } }}>
                <Chip
                  label={activeSlide.tag}
                  size="small"
                  sx={{
                    bgcolor: '#0F2E59',
                    color: '#FFFFFF',
                    fontWeight: 800,
                    fontSize: '0.74rem',
                    mb: 1.5,
                    letterSpacing: '0.03em',
                    textTransform: 'uppercase',
                  }}
                />

                <Typography
                  variant="h3"
                  sx={{
                    fontFamily: tokens.font.heading,
                    fontWeight: 800,
                    fontSize: { xs: '1.5rem', sm: '1.95rem', md: '2.35rem' },
                    lineHeight: 1.2,
                    color: '#0F2E59',
                    mb: 1.5,
                  }}
                >
                  {activeSlide.title}
                </Typography>

                {/* Highlighted Benefit Pill */}
                <Box
                  sx={{
                    display: 'inline-block',
                    bgcolor: '#8B0000',
                    color: '#FFFFFF',
                    px: 1.8,
                    py: 0.7,
                    borderRadius: '6px',
                    fontWeight: 800,
                    fontSize: { xs: '0.92rem', md: '1.05rem' },
                    mb: 1.8,
                    boxShadow: '0 2px 8px rgba(139, 0, 0, 0.25)',
                  }}
                >
                  {activeSlide.highlightText}
                </Box>

                <Typography
                  variant="body1"
                  sx={{
                    color: '#334155',
                    fontSize: { xs: '0.9rem', md: '0.98rem' },
                    lineHeight: 1.6,
                    maxWidth: 620,
                    mb: 2.5,
                    fontWeight: 500,
                  }}
                >
                  {activeSlide.subtitle}
                </Typography>

                <Typography
                  variant="caption"
                  sx={{ color: '#64748B', fontWeight: 600, display: 'block', mb: 3 }}
                >
                  <PictureAsPdfIcon sx={{ fontSize: 14, color: '#DC2626', verticalAlign: 'middle', mr: 0.5 }} />
                  {activeSlide.officialGazette}
                </Typography>

                <Stack direction="row" spacing={2} alignItems="center">
                  <Button
                    variant="contained"
                    size="large"
                    endIcon={<ArrowForwardIcon />}
                    onClick={() => navigate(`/scheme/${activeSlide.schemeCode}`)}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      fontWeight: 800,
                      fontSize: '0.95rem',
                      px: 3,
                      py: 1.2,
                      borderRadius: '8px',
                      textTransform: 'none',
                      boxShadow: '0 4px 14px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {activeSlide.ctaText}
                  </Button>

                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<AutoAwesomeIcon sx={{ color: '#E65100' }} />}
                    onClick={() => {
                      const el = document.getElementById('business-profiler')
                      if (el) el.scrollIntoView({ behavior: 'smooth' })
                    }}
                    sx={{
                      borderColor: '#0F2E59',
                      color: '#0F2E59',
                      fontWeight: 700,
                      fontSize: '0.95rem',
                      px: 2.5,
                      py: 1.2,
                      borderRadius: '8px',
                      textTransform: 'none',
                      bgcolor: 'rgba(255, 255, 255, 0.7)',
                      '&:hover': { bgcolor: '#FFFFFF' },
                    }}
                  >
                    Find Schemes for My Business
                  </Button>
                </Stack>
              </Grid>

              {/* Right Column: High-Res Visual Representative Image */}
              <Grid
                item
                xs={12}
                md={5}
                sx={{
                  display: { xs: 'none', md: 'flex' },
                  justifyContent: 'center',
                  alignItems: 'center',
                  p: 4,
                  height: '100%',
                }}
              >
                <Box
                  sx={{
                    width: '100%',
                    maxWidth: 420,
                    height: 330,
                    borderRadius: '16px',
                    overflow: 'hidden',
                    boxShadow: '0 12px 30px rgba(15, 23, 42, 0.15)',
                    border: '4px solid #FFFFFF',
                    position: 'relative',
                  }}
                >
                  <Box
                    component="img"
                    src={activeSlide.imageUrl}
                    alt={activeSlide.title}
                    onError={(e) => {
                      const target = e.currentTarget as HTMLImageElement
                      target.src = pmegpBanner
                    }}
                    sx={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      display: 'block',
                      transition: 'transform 0.4s ease',
                      '&:hover': { transform: 'scale(1.03)' },
                    }}
                  />
                  <Box
                    sx={{
                      position: 'absolute',
                      bottom: 0,
                      left: 0,
                      right: 0,
                      bgcolor: 'rgba(15, 46, 89, 0.88)',
                      backdropFilter: 'blur(4px)',
                      color: '#FFFFFF',
                      p: 1.2,
                      textAlign: 'center',
                    }}
                  >
                    <Typography variant="caption" sx={{ fontWeight: 700, letterSpacing: '0.02em', display: 'block' }}>
                      Official Operational Scheme • UdyamNiti Verified Corpus
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>

            {/* Left & Right Slideshow Arrows */}
            <IconButton
              onClick={prevSlide}
              aria-label="Previous Slide"
              sx={{
                position: 'absolute',
                left: { xs: 8, md: 16 },
                top: '50%',
                transform: 'translateY(-50%)',
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                color: '#0F2E59',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                '&:hover': { bgcolor: '#FFFFFF', transform: 'translateY(-50%) scale(1.08)' },
              }}
            >
              <NavigateBeforeIcon sx={{ fontSize: 28 }} />
            </IconButton>

            <IconButton
              onClick={nextSlide}
              aria-label="Next Slide"
              sx={{
                position: 'absolute',
                right: { xs: 8, md: 16 },
                top: '50%',
                transform: 'translateY(-50%)',
                bgcolor: 'rgba(255, 255, 255, 0.9)',
                color: '#0F2E59',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                '&:hover': { bgcolor: '#FFFFFF', transform: 'translateY(-50%) scale(1.08)' },
              }}
            >
              <NavigateNextIcon sx={{ fontSize: 28 }} />
            </IconButton>

          </Box>
        </Container>
      </Box>

      {/* ─── 2. QUICK ACTIONS (3 CARDS) ─── */}
      <Box sx={{ py: 5, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Grid container spacing={2.5}>
            {[
              {
                icon: <SearchIcon sx={{ fontSize: 30, color: '#0F2E59' }} />,
                title: 'Find Schemes',
                desc: 'Explore 52+ official schemes across credit, subsidies, technology, clusters & export promotion.',
                action: () => navigate('/login'),
              },
              {
                icon: <FactCheckOutlinedIcon sx={{ fontSize: 30, color: '#059669' }} />,
                title: 'Check Eligibility',
                desc: 'Sign in to assess your business profile against official Gazette provisions with verified percentages.',
                action: () => navigate('/login'),
              },
              {
                icon: <DescriptionOutlinedIcon sx={{ fontSize: 30, color: '#2563EB' }} />,
                title: 'Check Documents',
                desc: 'Review required certificates, project reports, and statutory checklists before filing.',
                action: () => navigate('/resources'),
              },
            ].map((card, i) => (
              <Grid item xs={12} sm={6} md={4} key={i}>
                <Paper
                  onClick={card.action}
                  elevation={0}
                  sx={{
                    p: 2.5,
                    height: '100%',
                    bgcolor: '#F8FAFC',
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: '#0F2E59',
                      transform: 'translateY(-3px)',
                      boxShadow: '0 6px 18px rgba(15, 23, 42, 0.08)',
                    },
                  }}
                >
                  <Box sx={{ mb: 1.2 }}>{card.icon}</Box>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '1rem', mb: 0.5 }}>
                    {card.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', fontSize: '0.84rem', lineHeight: 1.5 }}>
                    {card.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
      {/* ─── 3. ENTERPRISE GATEWAY PORTAL ACCESS (LOGIN REQUIRED TO SEARCH & SCORE SCHEMES) ─── */}
      <Box sx={{ py: 7, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="lg">
          <Paper
            elevation={0}
            sx={{
              p: { xs: 3.5, md: 5 },
              bgcolor: '#FFFFFF',
              border: '2px solid #E2E8F0',
              borderRadius: '20px',
              boxShadow: '0 8px 30px rgba(15, 23, 42, 0.06)',
              background: 'linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)',
              textAlign: 'center',
            }}
          >
            <Chip
              icon={<VerifiedUserIcon sx={{ fontSize: '15px !important', color: '#0F2E59 !important' }} />}
              label="Secured Enterprise Gateway • Official MSME Corpus"
              sx={{ bgcolor: '#EFF6FF', color: '#0F2E59', fontWeight: 800, mb: 2, border: '1px solid #BFDBFE' }}
            />
            <Typography variant="h3" sx={{ fontWeight: 900, color: '#0F2E59', fontSize: { xs: '1.65rem', md: '2.3rem' }, mb: 1.5 }}>
              Personalized Scheme Discovery & Application Tracking
            </Typography>
            <Typography variant="body1" sx={{ color: '#475569', maxWidth: 780, mx: 'auto', mb: 4, fontSize: { xs: '0.94rem', md: '1.05rem' }, lineHeight: 1.6 }}>
              To ensure 100% statutory precision and safeguard enterprise data, customized scheme discovery, verified eligibility percentage scoring, and detailed scheme searches are enabled within your authenticated enterprise workspace.
            </Typography>

            <Grid container spacing={3} sx={{ mb: 4, textAlign: 'left', maxWidth: 900, mx: 'auto' }}>
              <Grid item xs={12} sm={4}>
                <Paper sx={{ p: 2.5, bgcolor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px', height: '100%' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 0.5 }}>
                    🎯 Accurate Percentage Scoring
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#64748B', display: 'block', lineHeight: 1.5 }}>
                    Evaluates turnover, investment, caste/gender category, and state location against official Gazette rules.
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Paper sx={{ p: 2.5, bgcolor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px', height: '100%' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#059669', mb: 0.5 }}>
                    🔍 Targeted Scheme Search
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#64748B', display: 'block', lineHeight: 1.5 }}>
                    Filter across 52+ official Central & Gujarat schemes from 33+ Gazette guidelines by credit guarantees, capital subsidies, and quality.
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Paper sx={{ p: 2.5, bgcolor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px', height: '100%' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#E65100', mb: 0.5 }}>
                    📋 Pre-Application Checklists
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#64748B', display: 'block', lineHeight: 1.5 }}>
                    Download bank-ready DPR formats, verify statutory certificates, and track DBT margin money status.
                  </Typography>
                </Paper>
              </Grid>
            </Grid>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center" alignItems="center">
              {isLoggedIn ? (
                <Button
                  variant="contained"
                  size="large"
                  onClick={() => navigate('/dashboard')}
                  endIcon={<ArrowForwardIcon />}
                  sx={{
                    bgcolor: '#0F2E59',
                    color: '#FFFFFF',
                    fontWeight: 800,
                    fontSize: '0.96rem',
                    px: 4,
                    py: 1.3,
                    borderRadius: '10px',
                    boxShadow: '0 6px 20px rgba(15, 46, 89, 0.25)',
                    textTransform: 'none',
                    '&:hover': { bgcolor: '#0A1E3A' },
                  }}
                >
                  Go to Schemes Dashboard
                </Button>
              ) : (
                <>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => navigate('/login')}
                    endIcon={<ArrowForwardIcon />}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      fontWeight: 800,
                      fontSize: '0.96rem',
                      px: 4,
                      py: 1.3,
                      borderRadius: '10px',
                      boxShadow: '0 6px 20px rgba(15, 46, 89, 0.25)',
                      textTransform: 'none',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    Sign In to Search & View Schemes
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={() => navigate('/register')}
                    sx={{
                      borderColor: '#CBD5E1',
                      color: '#0F2E59',
                      fontWeight: 700,
                      fontSize: '0.96rem',
                      px: 3.5,
                      py: 1.3,
                      borderRadius: '10px',
                      bgcolor: '#FFFFFF',
                      textTransform: 'none',
                      '&:hover': { bgcolor: '#F8FAFC', borderColor: '#0F2E59' },
                    }}
                  >
                    Register Enterprise Account
                  </Button>
                </>
              )}
            </Stack>
          </Paper>
        </Container>
      </Box>
      {/* ─── 5. EXPLORE BY BUSINESS NEED (8 TASK TILES) ─── */}
      <Box sx={{ py: 8, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 5 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.75rem', md: '2.2rem' }, mb: 1 }}>
              What Does Your Business Need?
            </Typography>
            <Typography variant="body1" sx={{ color: '#64748B' }}>
              Select your priority requirement to filter schemes and subsidies tailored to that operational outcome.
            </Typography>
          </Box>

          <Grid container spacing={2.5}>
            {[
              { id: 'finance_credit', title: 'Finance & Credit', desc: 'Collateral-free credit & invoice discounting', icon: <MonetizationOnOutlinedIcon sx={{ fontSize: 30, color: '#059669' }} /> },
              { id: 'tech_upgrade', title: 'Technology Upgrade', desc: 'Zero defect quality & machinery modernisation', icon: <BuildCircleOutlinedIcon sx={{ fontSize: 30, color: '#2563EB' }} /> },
              { id: 'export_support', title: 'Export Support', desc: 'Global trade fairs, airfare & collateral cover', icon: <FlightTakeoffOutlinedIcon sx={{ fontSize: 30, color: '#EA580C' }} /> },
              { id: 'marketing', title: 'Marketing', desc: 'Exhibition stalls, barcoding & GeM procurement', icon: <StorefrontOutlinedIcon sx={{ fontSize: 30, color: '#CA8A04' }} /> },
              { id: 'skill_development', title: 'Skill Development', desc: 'Entrepreneurship training & workforce skills', icon: <SchoolOutlinedIcon sx={{ fontSize: 30, color: '#7C3AED' }} /> },
              { id: 'start_business', title: 'Start a Business', desc: 'Margin money capital subsidy up to ₹50 Lakh', icon: <RocketLaunchOutlinedIcon sx={{ fontSize: 30, color: '#DB2777' }} /> },
              { id: 'innovation', title: 'Innovation', desc: 'Patents, design facilities & testing laboratories', icon: <LightbulbOutlinedIcon sx={{ fontSize: 30, color: '#0891B2' }} /> },
              { id: 'infrastructure', title: 'Infrastructure', desc: 'Industrial park grants & common facility centres', icon: <ApartmentOutlinedIcon sx={{ fontSize: 30, color: '#4F46E5' }} /> },
            ].map((need, i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Paper
                  onClick={() => navigate(`/dashboard?need=${need.id}`)}
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
                  <Box sx={{ mb: 1.2 }}>{need.icon}</Box>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '0.98rem', mb: 0.5 }}>
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

      {/* ─── 6. HOW IT WORKS (5 STEPS) ─── */}
      <Box sx={{ py: 8, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 5 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.75rem', md: '2.2rem' }, mb: 1 }}>
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

      {/* ─── 7. AI ASSISTANT ("ASK MSME AI") - CRISP HIGH-CONTRAST TEXT ─── */}
      <Box sx={{ py: 9, bgcolor: '#0F2E59', color: '#FFFFFF', borderBottom: '1px solid #1E3A8A' }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Chip
              icon={<AutoAwesomeIcon sx={{ fontSize: '15px !important', color: '#FEF08A !important' }} />}
              label="Powered by Agentic RAG & Official Gazette Corpus"
              sx={{ bgcolor: 'rgba(255, 255, 255, 0.15)', color: '#FFFFFF', fontWeight: 700, mb: 1.5 }}
            />
            {/* Fixed Screenshot 2: Explicit high-contrast white text */}
            <Typography
              variant="h3"
              sx={{
                fontWeight: 800,
                fontSize: { xs: '1.9rem', md: '2.4rem' },
                mb: 1,
                color: '#FFFFFF !important',
              }}
            >
              Ask MSME AI Assistant
            </Typography>
            <Typography variant="body1" sx={{ color: '#E2E8F0 !important' }}>
              Instant answers grounded in official Ministry and State Government scheme guidelines.
            </Typography>
          </Box>

          <Paper
            elevation={0}
            sx={{
              p: 1.2,
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

      {/* ─── 8. GOVERNMENT SOURCES (TRUST & AUTHORITY) ─── */}
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

      {/* ─── 9. LATEST SCHEME UPDATES (TIMELY NOTIFICATIONS) ─── */}
      <Box sx={{ py: 7, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', md: 'center' }} sx={{ mb: 3.5 }}>
            <Box>
              <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.75rem', md: '2.2rem' } }}>
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

      {/* ─── 10. EXPLORE BY USER TYPE / PERSONAS ─── */}
      <Box sx={{ py: 7, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 4 }}>
            <Typography variant="caption" sx={{ fontWeight: 800, color: '#0F2E59', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              Tailored Assistance
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.75rem', md: '2.2rem' }, mt: 0.5 }}>
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

      {/* ─── 11. VERIFIED IMPACT & SUCCESS NUMBERS ─── */}
      <Box sx={{ py: 7, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="lg">
          <Grid container spacing={3}>
            {[
              { stat: '52+', label: 'Verified Official Schemes', desc: 'Directly sourced from 33+ uploaded Central & State Gazette PDFs' },
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

      {/* ─── 12. FINAL CTA ─── */}
      <Box sx={{ py: 9, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
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
            <Typography variant="h3" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: { xs: '1.75rem', md: '2.2rem' }, mb: 2 }}>
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
                onClick={() => navigate(isLoggedIn ? '/dashboard' : '/register')}
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
                {isLoggedIn ? 'Go to Enterprise Dashboard' : 'Find My Benefits'}
              </Button>
              {!isLoggedIn && (
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
              )}
            </Stack>
          </Paper>
        </Container>
      </Box>

      {/* ─── 13. COMPREHENSIVE FOOTER & REFINED STATUTORY DISCLAIMER (SCREENSHOT 3 FIX) ─── */}
      <Box
        component="footer"
        sx={{
          bgcolor: '#0F2E59',
          color: '#FFFFFF',
          pt: { xs: 8, md: 9 },
          pb: { xs: 6, md: 7 },
        }}
      >
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Grid container spacing={4} sx={{ mb: 6 }}>
            {/* Col 1: Platform */}
            <Grid item xs={12} md={3.5}>
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
            <Grid item xs={6} md={2.5}>
              <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#FFFFFF', mb: 2 }}>
                SCHEMES
              </Typography>
              <Stack spacing={1}>
                {[
                  { name: 'All Schemes', path: '/dashboard' },
                  { name: 'Credit & Finance', path: '/dashboard?search=credit' },
                  { name: 'Subsidies & Incentives', path: '/dashboard?search=subsidy' },
                  { name: 'Export Support', path: '/dashboard?search=export' },
                  { name: 'Technology Upgrade', path: '/dashboard?search=technology' },
                  { name: 'Marketing Support', path: '/dashboard?search=marketing' },
                ].map((item, idx) => (
                  <Typography
                    key={idx}
                    variant="body2"
                    sx={{ color: '#94A3B8', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
                    onClick={() => navigate(item.path)}
                  >
                    {item.name}
                  </Typography>
                ))}
              </Stack>
            </Grid>

            {/* Col 3: Resources */}
            <Grid item xs={6} md={2.5}>
              <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#FFFFFF', mb: 2 }}>
                RESOURCES
              </Typography>
              <Stack spacing={1}>
                {[
                  { name: 'Acts & Rules', path: '/resources?tab=acts' },
                  { name: 'Scheme Guidelines', path: '/resources?tab=guidelines' },
                  { name: 'Notifications', path: '/updates?tab=circulars' },
                  { name: 'Circulars & Orders', path: '/updates?tab=circulars' },
                  { name: 'Reports', path: '/resources?tab=dpr' },
                  { name: 'FAQs', path: '/support?tab=faqs' },
                ].map((item, idx) => (
                  <Typography
                    key={idx}
                    variant="body2"
                    sx={{ color: '#94A3B8', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
                    onClick={() => navigate(item.path)}
                  >
                    {item.name}
                  </Typography>
                ))}
              </Stack>
            </Grid>

            {/* Col 4: Government Links */}
            <Grid item xs={12} md={3.5}>
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
          </Grid>

          <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.15)', mb: 3 }} />

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
