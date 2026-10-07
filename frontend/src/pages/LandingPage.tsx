import React, { useState, useEffect, useRef } from 'react'
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
  IconButton,
  Divider,
} from '@mui/material'
import PolicyIcon from '@mui/icons-material/Policy'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
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
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore'
import NavigateNextIcon from '@mui/icons-material/NavigateNext'
import PauseIcon from '@mui/icons-material/Pause'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import CampaignIcon from '@mui/icons-material/Campaign'
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import { tokens } from '../theme/tokens'
import { useLanguage } from '../i18n'

interface BannerSlide {
  id: number
  tag: string
  title: string
  subtitle: string
  highlightText: string
  ctaText: string
  ctaPath: string
  imageUrl: string
  gradientBg: string
}

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { lang, t } = useLanguage()

  // Dynamic localized slides
  const SLIDES: BannerSlide[] = [
    {
      id: 1,
      tag: t('slide1Tag'),
      title: t('slide1Title'),
      highlightText: t('slide1Highlight'),
      subtitle: t('slide1Subtitle'),
      ctaText: t('slide1Cta'),
      ctaPath: '/dashboard',
      imageUrl: 'https://images.unsplash.com/photo-1577962917302-cd874c4e31d2?auto=format&fit=crop&w=1200&q=80',
      gradientBg: 'linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 40%, #FEF3C7 100%)',
    },
    {
      id: 2,
      tag: t('slide2Tag'),
      title: t('slide2Title'),
      highlightText: t('slide2Highlight'),
      subtitle: t('slide2Subtitle'),
      ctaText: t('slide2Cta'),
      ctaPath: '/dashboard',
      imageUrl: 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=1200&q=80',
      gradientBg: 'linear-gradient(135deg, #FAF5FF 0%, #F3E8FF 40%, #EDE9FE 100%)',
    },
  ]

  // Localized announcements ticker notices
  const ANNOUNCEMENTS = [
    t('announcementsNotice1'),
    t('announcementsNotice2'),
    t('announcementsNotice3'),
    t('announcementsNotice4'),
    t('announcementsNotice5'),
    t('announcementsNotice6'),
  ]

  // Slideshow States (3-second auto rotation)
  const [currentSlide, setCurrentSlide] = useState<number>(0)
  const [isSlidePaused, setIsSlidePaused] = useState<boolean>(false)

  // Announcements Marquee States
  const [isTickerPaused, setIsTickerPaused] = useState<boolean>(false)

  // 3 Seconds Automatic Slide Show Timer
  useEffect(() => {
    if (isSlidePaused) return
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % SLIDES.length)
    }, 3000)

    return () => clearInterval(timer)
  }, [isSlidePaused, SLIDES.length])

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % SLIDES.length)
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + SLIDES.length) % SLIDES.length)
  }

  const activeBanner = SLIDES[currentSlide]

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F8FAFC', color: '#0F172A' }}>
      {/* ─── 1. PHOTOS WITH 3 SECONDS AUTOMATIC SLIDE SHOW ─── */}
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
              minHeight: { xs: 340, sm: 380, md: 440 },
              background: activeBanner.gradientBg,
              border: '1px solid #E2E8F0',
              boxShadow: '0 4px 20px rgba(15, 23, 42, 0.06)',
              display: 'flex',
              alignItems: 'center',
              transition: 'background 0.5s ease',
            }}
          >
            <Grid container alignItems="center" sx={{ height: '100%' }}>
              {/* Left Column: Text & Content */}
              <Grid item xs={12} md={7} sx={{ p: { xs: 3, sm: 4, md: 6 } }}>
                <Chip
                  label={activeBanner.tag}
                  size="small"
                  sx={{
                    bgcolor: '#0F2E59',
                    color: '#FFFFFF',
                    fontWeight: 800,
                    fontSize: '0.75rem',
                    mb: 2,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                  }}
                />

                <Typography
                  variant="h3"
                  sx={{
                    fontFamily: tokens.font.heading,
                    fontWeight: 800,
                    fontSize: { xs: '1.6rem', sm: '2.1rem', md: '2.6rem' },
                    lineHeight: 1.15,
                    color: '#0F2E59',
                    mb: 1.5,
                  }}
                >
                  {activeBanner.title}
                </Typography>

                {/* Highlighted Banner Text */}
                <Box
                  sx={{
                    display: 'inline-block',
                    bgcolor: '#8B0000',
                    color: '#FFFFFF',
                    px: 1.8,
                    py: 0.8,
                    borderRadius: '6px',
                    fontWeight: 800,
                    fontSize: { xs: '0.95rem', md: '1.15rem' },
                    mb: 2,
                    boxShadow: '0 2px 8px rgba(139, 0, 0, 0.25)',
                  }}
                >
                  {activeBanner.highlightText}
                </Box>

                <Typography
                  variant="body1"
                  sx={{
                    color: '#334155',
                    fontSize: { xs: '0.9rem', md: '1rem' },
                    lineHeight: 1.6,
                    maxWidth: 620,
                    mb: 3,
                    fontWeight: 500,
                  }}
                >
                  {activeBanner.subtitle}
                </Typography>

                <Stack direction="row" spacing={2} alignItems="center">
                  <Button
                    variant="contained"
                    size="large"
                    endIcon={<ArrowForwardIcon />}
                    onClick={() => navigate(activeBanner.ctaPath)}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      fontWeight: 700,
                      fontSize: '0.95rem',
                      px: 3,
                      py: 1.2,
                      borderRadius: '8px',
                      textTransform: 'none',
                      boxShadow: '0 4px 12px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {activeBanner.ctaText}
                  </Button>

                  <Button
                    variant="outlined"
                    size="large"
                    onClick={() => navigate('/register')}
                    sx={{
                      borderColor: '#0F2E59',
                      color: '#0F2E59',
                      fontWeight: 700,
                      fontSize: '0.95rem',
                      px: 2.5,
                      py: 1.2,
                      borderRadius: '8px',
                      textTransform: 'none',
                      bgcolor: 'rgba(255, 255, 255, 0.6)',
                      '&:hover': { bgcolor: '#FFFFFF' },
                    }}
                  >
                    {t('registerEnterprise')}
                  </Button>
                </Stack>
              </Grid>

              {/* Right Column: Visual Photo Representation */}
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
                    height: 320,
                    borderRadius: '16px',
                    overflow: 'hidden',
                    boxShadow: '0 12px 30px rgba(15, 23, 42, 0.15)',
                    border: '4px solid #FFFFFF',
                    position: 'relative',
                  }}
                >
                  <Box
                    component="img"
                    src={activeBanner.imageUrl}
                    alt={activeBanner.title}
                    sx={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
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
                      bgcolor: 'rgba(15, 46, 89, 0.85)',
                      backdropFilter: 'blur(4px)',
                      color: '#FFFFFF',
                      p: 1.5,
                      textAlign: 'center',
                    }}
                  >
                    <Typography variant="caption" sx={{ fontWeight: 700, letterSpacing: '0.02em', display: 'block' }}>
                      {t('officialInitiative')}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>

            {/* Left & Right Navigation Arrows */}
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

            {/* Bottom Pagination Dots & Pause/Play Control (As in msme.gov.in) */}
            <Box
              sx={{
                position: 'absolute',
                bottom: 14,
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                alignItems: 'center',
                gap: 1.2,
                bgcolor: 'rgba(255, 255, 255, 0.85)',
                backdropFilter: 'blur(6px)',
                px: 2,
                py: 0.6,
                borderRadius: '9999px',
                border: '1px solid #CBD5E1',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
              }}
            >
              {SLIDES.map((slide, idx) => (
                <Box
                  key={slide.id}
                  onClick={() => setCurrentSlide(idx)}
                  sx={{
                    width: currentSlide === idx ? 22 : 9,
                    height: 9,
                    borderRadius: '9999px',
                    bgcolor: currentSlide === idx ? '#8B0000' : '#CBD5E1',
                    cursor: 'pointer',
                    transition: 'all 0.25s ease',
                  }}
                />
              ))}

              <Divider orientation="vertical" flexItem sx={{ mx: 0.5, borderColor: '#CBD5E1', height: 16 }} />

              {/* Pause / Play Toggle Button (⏸ / ▶) */}
              <IconButton
                size="small"
                onClick={() => setIsSlidePaused(!isSlidePaused)}
                aria-label={isSlidePaused ? 'Play slide show' : 'Pause slide show'}
                sx={{ p: 0.2, color: '#0F2E59' }}
              >
                {isSlidePaused ? <PlayArrowIcon sx={{ fontSize: 16 }} /> : <PauseIcon sx={{ fontSize: 16 }} />}
              </IconButton>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* ─── 2. ANNOUNCEMENTS NEWSLINE WITH AUTOMATIC MOVING (TICKER) ─── */}
      <Box
        sx={{
          bgcolor: '#F1F5F9',
          borderBottom: '2px solid #E2E8F0',
          py: 0.8,
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
        }}
        onMouseEnter={() => setIsTickerPaused(true)}
        onMouseLeave={() => setIsTickerPaused(false)}
      >
        <Container maxWidth="xl" disableGutters sx={{ px: { xs: 2, md: 3 } }}>
          <Stack direction="row" alignItems="center" spacing={2}>
            {/* Announcements Badge (Deep Maroon / Crimson) */}
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.8,
                bgcolor: '#8B0000',
                color: '#FFFFFF',
                px: 1.8,
                py: 0.5,
                borderRadius: '4px',
                flexShrink: 0,
                boxShadow: '0 1px 4px rgba(139, 0, 0, 0.2)',
              }}
            >
              <CampaignIcon sx={{ fontSize: 18 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 800, fontSize: '0.84rem', letterSpacing: '0.02em' }}>
                {t('announcements')}
              </Typography>
            </Box>

            {/* Continuous Moving Marquee Animation */}
            <Box
              sx={{
                flex: 1,
                overflow: 'hidden',
                whiteSpace: 'nowrap',
                position: 'relative',
              }}
            >
              <Box
                sx={{
                  display: 'inline-block',
                  whiteSpace: 'nowrap',
                  animation: 'marqueeScroll 40s linear infinite',
                  animationPlayState: isTickerPaused ? 'paused' : 'running',
                  '@keyframes marqueeScroll': {
                    '0%': { transform: 'translateX(0%)' },
                    '100%': { transform: 'translateX(-50%)' },
                  },
                }}
              >
                {/* Duplicate the array twice so the loop is seamless */}
                {[...ANNOUNCEMENTS, ...ANNOUNCEMENTS].map((item, idx) => (
                  <Typography
                    key={idx}
                    component="span"
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      color: '#1E293B',
                      fontSize: '0.88rem',
                      fontWeight: 600,
                      mr: 6,
                      cursor: 'pointer',
                      '&:hover': { color: '#0F2E59', textDecoration: 'underline' },
                    }}
                    onClick={() => navigate('/dashboard')}
                  >
                    {item}
                  </Typography>
                ))}
              </Box>
            </Box>

            {/* Marquee Ticker Pause / Play Controller */}
            <IconButton
              size="small"
              onClick={() => setIsTickerPaused(!isTickerPaused)}
              aria-label={isTickerPaused ? 'Resume ticker' : 'Pause ticker'}
              sx={{
                bgcolor: '#FFFFFF',
                border: '1px solid #CBD5E1',
                p: 0.5,
                flexShrink: 0,
                color: '#0F2E59',
                '&:hover': { bgcolor: '#F8FAFC' },
              }}
            >
              {isTickerPaused ? <PlayArrowIcon sx={{ fontSize: 16 }} /> : <PauseIcon sx={{ fontSize: 16 }} />}
            </IconButton>
          </Stack>
        </Container>
      </Box>

      {/* ─── 3. CORE VALUE PROPOSITION (LIGHT THEME) ─── */}
      <Box sx={{ py: { xs: 6, md: 9 }, bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0' }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: 860, mx: 'auto' }}>
            <Chip
              icon={<VerifiedUserIcon sx={{ fontSize: '15px !important', color: '#059669 !important' }} />}
              label={t('heroBadge')}
              sx={{
                mb: 2.5,
                bgcolor: '#ECFDF5',
                color: '#065F46',
                border: '1px solid #A7F3D0',
                fontWeight: 700,
                fontSize: '0.82rem',
                py: 2,
                px: 1,
              }}
            />

            <Typography
              variant="h2"
              component="h1"
              sx={{
                fontWeight: 800,
                fontSize: { xs: '2.1rem', sm: '2.8rem', md: '3.4rem' },
                lineHeight: 1.15,
                letterSpacing: '-0.025em',
                color: '#0F2E59',
                mb: 2,
              }}
            >
              {t('heroTitlePrefix')}{' '}
              <Box
                component="span"
                sx={{
                  color: '#E65100',
                  borderBottom: '3px solid #E65100',
                }}
              >
                {t('heroTitleHighlight')}
              </Box>
            </Typography>

            <Typography
              variant="body1"
              sx={{
                color: '#475569',
                fontSize: { xs: '1rem', md: '1.18rem' },
                lineHeight: 1.65,
                maxWidth: 740,
                mx: 'auto',
                mb: 4,
              }}
            >
              {t('heroSubtitle')}
            </Typography>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center" alignItems="center">
              <Button
                variant="contained"
                size="large"
                startIcon={<PersonAddAltIcon />}
                endIcon={<ArrowForwardIcon />}
                onClick={() => navigate('/register')}
                sx={{
                  bgcolor: '#0F2E59',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '1rem',
                  px: 4,
                  py: 1.4,
                  borderRadius: '8px',
                  textTransform: 'none',
                  boxShadow: '0 4px 14px rgba(15, 46, 89, 0.25)',
                  '&:hover': { bgcolor: '#0A1E3A' },
                }}
              >
                {t('registerEnterpriseBtn')}
              </Button>

              <Button
                variant="outlined"
                size="large"
                startIcon={<LoginIcon />}
                onClick={() => navigate('/login')}
                sx={{
                  borderColor: '#CBD5E1',
                  color: '#0F2E59',
                  fontWeight: 700,
                  fontSize: '1rem',
                  px: 3.5,
                  py: 1.4,
                  borderRadius: '8px',
                  textTransform: 'none',
                  bgcolor: '#FFFFFF',
                  '&:hover': { bgcolor: '#F8FAFC', borderColor: '#0F2E59' },
                }}
              >
                {t('signInAccountBtn')}
              </Button>
            </Stack>
          </Box>
        </Container>
      </Box>

      {/* ─── 4. SERVICES WE PROVIDE TO USERS (CLEAN LIGHT CARDS) ─── */}
      <Box id="services" sx={{ py: { xs: 8, md: 10 }, bgcolor: '#F8FAFC' }}>
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 6 }}>
            <Chip
              label={t('services')}
              size="small"
              sx={{
                mb: 1.5,
                bgcolor: '#EFF6FF',
                color: '#1D4ED8',
                fontWeight: 700,
                fontSize: '0.75rem',
                border: '1px solid #BFDBFE',
              }}
            />
            <Typography
              variant="h3"
              component="h2"
              sx={{ fontWeight: 800, fontSize: { xs: '1.8rem', md: '2.4rem' }, mb: 1.5, color: '#0F2E59' }}
            >
              {t('servicesTitle')}
            </Typography>
            <Typography variant="body1" sx={{ color: '#475569', fontSize: '1.05rem' }}>
              {t('servicesSubtitle')}
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {[
              {
                icon: <AutoAwesomeIcon sx={{ fontSize: 30, color: '#1E40AF' }} />,
                title: t('service1Title'),
                desc: t('service1Desc'),
              },
              {
                icon: <AccountTreeOutlinedIcon sx={{ fontSize: 30, color: '#059669' }} />,
                title: t('service2Title'),
                desc: t('service2Desc'),
              },
              {
                icon: <FactCheckOutlinedIcon sx={{ fontSize: 30, color: '#0284C7' }} />,
                title: t('service3Title'),
                desc: t('service3Desc'),
              },
              {
                icon: <NotificationsActiveOutlinedIcon sx={{ fontSize: 30, color: '#D97706' }} />,
                title: t('service4Title'),
                desc: t('service4Desc'),
              },
              {
                icon: <GavelOutlinedIcon sx={{ fontSize: 30, color: '#7C3AED' }} />,
                title: t('service5Title'),
                desc: t('service5Desc'),
              },
              {
                icon: <SpeedIcon sx={{ fontSize: 30, color: '#DB2777' }} />,
                title: t('service6Title'),
                desc: t('service6Desc'),
              },
            ].map((service, i) => (
              <Grid item xs={12} md={4} key={i}>
                <Card
                  sx={{
                    height: '100%',
                    bgcolor: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                    p: 1.5,
                    boxShadow: '0 1px 3px rgba(15, 23, 42, 0.05)',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: '#0F2E59',
                      transform: 'translateY(-3px)',
                      boxShadow: '0 6px 18px rgba(15, 23, 42, 0.08)',
                    },
                  }}
                >
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ mb: 2 }}>{service.icon}</Box>
                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '1.1rem', mb: 1 }}>
                      {service.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#475569', fontSize: '0.88rem', lineHeight: 1.6 }}>
                      {service.desc}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── 5. BENEFITS PROVIDED TO MSMES ─── */}
      <Box
        id="benefits"
        sx={{
          py: { xs: 8, md: 10 },
          bgcolor: '#FFFFFF',
          borderTop: '1px solid #E2E8F0',
          borderBottom: '1px solid #E2E8F0',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', maxWidth: 700, mx: 'auto', mb: 6 }}>
            <Chip
              label={t('benefits')}
              size="small"
              sx={{
                mb: 1.5,
                bgcolor: '#ECFDF5',
                color: '#065F46',
                fontWeight: 700,
                fontSize: '0.75rem',
                border: '1px solid #A7F3D0',
              }}
            />
            <Typography
              variant="h3"
              component="h2"
              sx={{ fontWeight: 800, fontSize: { xs: '1.8rem', md: '2.4rem' }, mb: 1.5, color: '#0F2E59' }}
            >
              {t('benefitsTitle')}
            </Typography>
            <Typography variant="body1" sx={{ color: '#475569', fontSize: '1.05rem' }}>
              {t('benefitsSubtitle')}
            </Typography>
          </Box>

          <Grid container spacing={3}>
            {[
              {
                stat: '₹15L - ₹10Cr',
                title: t('benefit1Title'),
                desc: t('benefit1Desc'),
                color: '#059669',
              },
              {
                stat: '90% Time Saved',
                title: t('benefit2Title'),
                desc: t('benefit2Desc'),
                color: '#0284C7',
              },
              {
                stat: 'Zero Rejections',
                title: t('benefit3Title'),
                desc: t('benefit3Desc'),
                color: '#1E40AF',
              },
              {
                stat: '35%+ Combined Yield',
                title: t('benefit4Title'),
                desc: t('benefit4Desc'),
                color: '#D97706',
              },
              {
                stat: '100% Legal Proof',
                title: t('benefit5Title'),
                desc: t('benefit5Desc'),
                color: '#DB2777',
              },
              {
                stat: 'Year-Round Alerts',
                title: t('benefit6Title'),
                desc: t('benefit6Desc'),
                color: '#7C3AED',
              },
            ].map((benefit, i) => (
              <Grid item xs={12} sm={6} md={4} key={i}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    height: '100%',
                    bgcolor: '#F8FAFC',
                    border: '1px solid #E2E8F0',
                    borderRadius: '12px',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: benefit.color,
                      transform: 'translateY(-3px)',
                      boxShadow: '0 6px 18px rgba(15, 23, 42, 0.06)',
                    },
                  }}
                >
                  <Typography variant="h4" sx={{ fontWeight: 900, color: benefit.color, fontSize: '1.6rem', mb: 1 }}>
                    {benefit.stat}
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '1.05rem', mb: 1 }}>
                    {benefit.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#475569', fontSize: '0.86rem', lineHeight: 1.6 }}>
                    {benefit.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* ─── 6. FREQUENTLY ASKED QUESTIONS (FAQ) ─── */}
      <Box id="faq" sx={{ py: { xs: 8, md: 10 }, bgcolor: '#F8FAFC' }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center', mb: 5 }}>
            <Typography variant="h3" sx={{ fontWeight: 800, fontSize: '2rem', mb: 1.5, color: '#0F2E59' }}>
              {t('faq')}
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748B' }}>
              {t('faqSubtitle')}
            </Typography>
          </Box>

          <Stack spacing={2}>
            {[
              {
                q: t('faq1Q'),
                a: t('faq1A'),
              },
              {
                q: t('faq2Q'),
                a: t('faq2A'),
              },
              {
                q: t('faq3Q'),
                a: t('faq3A'),
              },
              {
                q: t('faq4Q'),
                a: t('faq4A'),
              },
            ].map((faq, i) => (
              <Accordion
                key={i}
                elevation={0}
                sx={{
                  bgcolor: '#FFFFFF',
                  border: '1px solid #E2E8F0',
                  borderRadius: '10px !important',
                  '&:before': { display: 'none' },
                }}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon sx={{ color: '#0F2E59' }} />}>
                  <Typography sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '0.96rem' }}>
                    {faq.q}
                  </Typography>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0, pb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#475569', fontSize: '0.88rem', lineHeight: 1.6 }}>
                    {faq.a}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            ))}
          </Stack>
        </Container>
      </Box>

      {/* ─── 7. FINAL ENTERPRISE CTA BANNER ─── */}
      <Box sx={{ py: 9, bgcolor: '#FFFFFF', borderTop: '1px solid #E2E8F0' }}>
        <Container maxWidth="md">
          <Paper
            elevation={0}
            sx={{
              p: { xs: 4, md: 6 },
              textAlign: 'center',
              borderRadius: '16px',
              bgcolor: '#F8FAFC',
              border: '2px solid #E2E8F0',
            }}
          >
            <Typography variant="h3" sx={{ fontWeight: 800, fontSize: { xs: '1.8rem', md: '2.2rem' }, mb: 2, color: '#0F2E59' }}>
              {t('ctaTitle')}
            </Typography>
            <Typography variant="body1" sx={{ color: '#475569', mb: 4, maxWidth: 560, mx: 'auto' }}>
              {t('ctaSubtitle')}
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} justifyContent="center">
              <Button
                variant="contained"
                size="large"
                startIcon={<PersonAddAltIcon />}
                onClick={() => navigate('/register')}
                sx={{
                  bgcolor: '#0F2E59',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.98rem',
                  px: 3.5,
                  py: 1.4,
                  borderRadius: '8px',
                  textTransform: 'none',
                  '&:hover': { bgcolor: '#0A1E3A' },
                }}
              >
                {t('registerAndGo')}
              </Button>
              <Button
                variant="outlined"
                size="large"
                startIcon={<LoginIcon />}
                onClick={() => navigate('/login')}
                sx={{
                  borderColor: '#CBD5E1',
                  color: '#0F2E59',
                  fontWeight: 700,
                  fontSize: '0.95rem',
                  px: 3,
                  py: 1.4,
                  borderRadius: '8px',
                  textTransform: 'none',
                  bgcolor: '#FFFFFF',
                  '&:hover': { bgcolor: '#F8FAFC' },
                }}
              >
                {t('signInAccountBtn')}
              </Button>
            </Stack>
          </Paper>
        </Container>
      </Box>

      {/* ─── 8. OFFICIAL PORTAL FOOTER (LIGHT THEME) ─── */}
      <Box
        component="footer"
        sx={{
          bgcolor: '#0F2E59',
          color: '#FFFFFF',
          pt: { xs: 7, md: 8 },
          pb: { xs: 5, md: 6 },
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} sx={{ mb: 6 }}>
            <Grid item xs={12} md={5}>
              <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: '8px',
                    bgcolor: '#FFFFFF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <PolicyIcon sx={{ color: '#0F2E59', fontSize: 22 }} />
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#FFFFFF' }}>
                  Udyam<Box component="span" sx={{ color: '#FF9933' }}>Niti</Box>
                </Typography>
              </Stack>
              <Typography variant="body2" sx={{ color: '#CBD5E1', lineHeight: 1.7, maxWidth: 420, mb: 3 }}>
                {t('footerDesc')}
              </Typography>
              <Typography variant="caption" sx={{ color: '#94A3B8' }}>
                {t('officialGateway')}
              </Typography>
            </Grid>

            <Grid item xs={6} md={2}>
              <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#FFFFFF', mb: 2 }}>
                {t('footerMinistry')}
              </Typography>
              <Stack spacing={1}>
                {[
                  { key: 'aboutUs', label: t('aboutUs') },
                  { key: 'ourPerformance', label: t('ourPerformance') },
                  { key: 'citizenCharter', label: t('citizenCharter') },
                  { key: 'annualReports', label: t('annualReports') },
                ].map((item) => (
                  <Typography
                    key={item.key}
                    variant="body2"
                    sx={{ color: '#94A3B8', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
                    onClick={() => navigate('/dashboard')}
                  >
                    {item.label}
                  </Typography>
                ))}
              </Stack>
            </Grid>

            <Grid item xs={6} md={2}>
              <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#FFFFFF', mb: 2 }}>
                {t('footerOfferings')}
              </Typography>
              <Stack spacing={1}>
                {[
                  { key: 'creditGuarantees', label: t('creditGuarantees') },
                  { key: 'capitalSubsidies', label: t('capitalSubsidies') },
                  { key: 'clusterDevelopment', label: t('clusterDevelopment') },
                  { key: 'zedCertification', label: t('zedCertification') },
                ].map((item) => (
                  <Typography
                    key={item.key}
                    variant="body2"
                    sx={{ color: '#94A3B8', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
                    onClick={() => navigate('/dashboard')}
                  >
                    {item.label}
                  </Typography>
                ))}
              </Stack>
            </Grid>

            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#FFFFFF', mb: 2 }}>
                {t('footerHelpline')}
              </Typography>
              <Typography variant="body2" sx={{ color: '#CBD5E1', mb: 1 }}>
                Toll-Free: <strong>1800 11 7800</strong>
              </Typography>
              <Typography variant="body2" sx={{ color: '#CBD5E1', mb: 2 }}>
                Email: support@udyamniti.gov.in
              </Typography>
              <Button
                variant="outlined"
                size="small"
                onClick={() => navigate('/dashboard')}
                sx={{
                  borderColor: '#94A3B8',
                  color: '#FFFFFF',
                  textTransform: 'none',
                  fontWeight: 700,
                  '&:hover': { borderColor: '#FFFFFF', bgcolor: 'rgba(255,255,255,0.08)' },
                }}
              >
                {t('accessSchemesPortal')}
              </Button>
            </Grid>
          </Grid>

          <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.15)', mb: 3 }} />

          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            justifyContent="space-between"
            alignItems="center"
            spacing={2}
          >
            <Typography variant="caption" sx={{ color: '#94A3B8' }}>
              © {new Date().getFullYear()} {t('footerCopyright')}
            </Typography>
            <Typography variant="caption" sx={{ color: '#94A3B8' }}>
              {t('footerCompliance')}
            </Typography>
          </Stack>
        </Container>
      </Box>
    </Box>
  )
}

export default LandingPage
