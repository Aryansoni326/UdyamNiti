import React, { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Stack,
  Container,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  ListItemIcon,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Card,
  CardContent,
  Paper,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import CloseIcon from '@mui/icons-material/Close'
import PolicyIcon from '@mui/icons-material/Policy'
import LogoutIcon from '@mui/icons-material/Logout'
import GridViewIcon from '@mui/icons-material/GridView'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown'
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import PhotoCameraOutlinedIcon from '@mui/icons-material/PhotoCameraOutlined'
import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined'
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined'
import PhoneInTalkOutlinedIcon from '@mui/icons-material/PhoneInTalkOutlined'
import GavelOutlinedIcon from '@mui/icons-material/GavelOutlined'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import DownloadIcon from '@mui/icons-material/Download'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import LanguageIcon from '@mui/icons-material/Language'
import PhoneOutlinedIcon from '@mui/icons-material/PhoneOutlined'
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined'
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined'
import { tokens } from '../theme/tokens'
import { toast } from 'sonner'
import { useLanguage, Language, LANGUAGE_LABELS } from '../i18n'

export const AppShell: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null)

  // Language state & translation hook
  const { lang, setLang, t } = useLanguage()
  const [langMenuAnchor, setLangMenuAnchor] = useState<null | HTMLElement>(null)

  // Dropdown Menu Anchors
  const [ministryAnchor, setMinistryAnchor] = useState<null | HTMLElement>(null)
  const [mediaAnchor, setMediaAnchor] = useState<null | HTMLElement>(null)
  const [connectAnchor, setConnectAnchor] = useState<null | HTMLElement>(null)

  // Interactive Content Modals
  const [modalOpen, setModalOpen] = useState<string | null>(null)

  // Accessibility Font Zoom simulation
  const [fontSizeMultiplier, setFontSizeMultiplier] = useState<number>(1)

  useEffect(() => {
    const stored = localStorage.getItem('udyamniti_user')
    if (stored) {
      try {
        setCurrentUser(JSON.parse(stored))
      } catch {
        setCurrentUser(null)
      }
    } else {
      setCurrentUser(null)
    }
  }, [location.pathname])

  const handleLogout = () => {
    localStorage.removeItem('udyamniti_user')
    setCurrentUser(null)
    setUserMenuAnchor(null)
    toast.info('Signed out successfully.')
    navigate('/')
  }

  const isLandingPage = location.pathname === '/'
  const isDashboard = location.pathname.startsWith('/dashboard') || location.pathname.startsWith('/schemes')
  const isMonitor = location.pathname.startsWith('/monitor')

  const openModal = (id: string) => {
    setMinistryAnchor(null)
    setMediaAnchor(null)
    setConnectAnchor(null)
    setMobileOpen(false)
    setModalOpen(id)
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#F8FAFC' }}>
      {/* ─── 1. TOP HEADER BAR: UDYAMNITI LOGO (LEFT) & REGISTER / SIGN IN (RIGHT) ─── */}
      <Box
        sx={{
          bgcolor: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          py: 1.5,
          px: { xs: 2, md: 4 },
          zIndex: 1300,
        }}
      >
        <Container maxWidth="xl" disableGutters>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            {/* Top Left: UdyamNiti Logo */}
            <Stack
              direction="row"
              alignItems="center"
              spacing={1.5}
              sx={{ cursor: 'pointer', userSelect: 'none' }}
              onClick={() => navigate('/')}
            >
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: '10px',
                  bgcolor: '#0F2E59',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 12px rgba(15, 46, 89, 0.25)',
                }}
              >
                <PolicyIcon sx={{ color: '#FFFFFF', fontSize: 24 }} />
              </Box>
              <Box>
                <Typography
                  variant="h6"
                  sx={{
                    fontFamily: tokens.font.heading,
                    fontWeight: 800,
                    color: '#0F2E59',
                    fontSize: { xs: '1.2rem', sm: '1.35rem' },
                    lineHeight: 1.1,
                    letterSpacing: '-0.02em',
                  }}
                >
                  Udyam<Box component="span" sx={{ color: '#E65100' }}>Niti</Box>
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    color: '#64748B',
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    letterSpacing: '0.02em',
                    display: 'block',
                  }}
                >
                  {t('tagline')}
                </Typography>
              </Box>
            </Stack>

            {/* Top Right: Language Option Beside Register & Sign In Buttons */}
            <Stack direction="row" spacing={1.5} alignItems="center">
              {/* ─── LANGUAGE SELECTOR BUTTON (English / Hindi / Gujarati) ─── */}
              <Button
                id="language-selector-button"
                onClick={(e) => setLangMenuAnchor(e.currentTarget)}
                variant="outlined"
                size="small"
                startIcon={<LanguageIcon sx={{ fontSize: 18, color: '#0F2E59' }} />}
                endIcon={<KeyboardArrowDownIcon sx={{ fontSize: 16, color: '#64748B' }} />}
                sx={{
                  color: '#0F2E59',
                  borderColor: '#CBD5E1',
                  bgcolor: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.84rem',
                  textTransform: 'none',
                  px: 1.5,
                  py: 0.6,
                  borderRadius: '8px',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                  transition: 'all 0.15s ease',
                  '&:hover': {
                    borderColor: '#0F2E59',
                    bgcolor: '#F8FAFC',
                  },
                }}
              >
                {LANGUAGE_LABELS[lang]}
              </Button>
              <Menu
                id="language-menu"
                anchorEl={langMenuAnchor}
                open={Boolean(langMenuAnchor)}
                onClose={() => setLangMenuAnchor(null)}
                PaperProps={{
                  sx: {
                    mt: 1,
                    minWidth: 160,
                    borderRadius: '8px',
                    border: '1px solid #E2E8F0',
                    boxShadow: '0 6px 20px rgba(15, 23, 42, 0.12)',
                    p: 0.5,
                  },
                }}
              >
                {(['en', 'hi', 'gu'] as Language[]).map((l) => (
                  <MenuItem
                    key={l}
                    selected={lang === l}
                    onClick={() => {
                      setLang(l)
                      setLangMenuAnchor(null)
                    }}
                    sx={{
                      py: 1,
                      px: 2,
                      borderRadius: '6px',
                      fontWeight: lang === l ? 700 : 500,
                      color: lang === l ? '#0F2E59' : '#334155',
                      bgcolor: lang === l ? '#F1F5F9' : 'transparent',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      '&:hover': {
                        bgcolor: '#F8FAFC',
                      },
                    }}
                  >
                    <span>{LANGUAGE_LABELS[l]}</span>
                    {lang === l && <CheckCircleIcon sx={{ fontSize: 16, color: '#0F2E59', ml: 1.5 }} />}
                  </MenuItem>
                ))}
              </Menu>

              {currentUser ? (
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <Button
                    onClick={() => navigate('/dashboard')}
                    variant="contained"
                    size="small"
                    startIcon={<GridViewIcon sx={{ fontSize: 16 }} />}
                    sx={{
                      bgcolor: '#0F2E59',
                      fontSize: '0.84rem',
                      fontWeight: 700,
                      borderRadius: '8px',
                      textTransform: 'none',
                      px: 2,
                      py: 0.8,
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {t('dashboard')}
                  </Button>
                  <Box
                    onClick={(e) => setUserMenuAnchor(e.currentTarget)}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      cursor: 'pointer',
                      p: '3px 10px 3px 4px',
                      borderRadius: '9999px',
                      border: '1px solid #CBD5E1',
                      bgcolor: '#F8FAFC',
                    }}
                  >
                    <Avatar sx={{ width: 30, height: 30, bgcolor: '#0F2E59', fontSize: '0.75rem', fontWeight: 700 }}>
                      {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
                    </Avatar>
                    <Typography variant="body2" sx={{ color: '#0F172A', fontWeight: 700, maxWidth: 120 }} noWrap>
                      {currentUser.name || 'Enterprise'}
                    </Typography>
                  </Box>
                  <Menu
                    anchorEl={userMenuAnchor}
                    open={Boolean(userMenuAnchor)}
                    onClose={() => setUserMenuAnchor(null)}
                    PaperProps={{ sx: { mt: 1, minWidth: 200, borderRadius: '8px', border: '1px solid #E2E8F0' } }}
                  >
                    <Box sx={{ px: 2, py: 1 }}>
                      <Typography variant="caption" sx={{ color: '#64748B', display: 'block', fontSize: '0.72rem' }}>
                        {t('loggedInAs')}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#0F2E59', fontWeight: 700 }} noWrap>
                        {currentUser.email || 'director@msme.in'}
                      </Typography>
                    </Box>
                    <Divider />
                    <MenuItem onClick={() => { navigate('/dashboard'); setUserMenuAnchor(null); }}>
                      <ListItemIcon sx={{ minWidth: 28, color: '#0F2E59' }}>
                        <GridViewIcon fontSize="small" />
                      </ListItemIcon>
                      {t('schemesDashboard')}
                    </MenuItem>
                    <MenuItem onClick={handleLogout} sx={{ color: '#DC2626' }}>
                      <ListItemIcon sx={{ minWidth: 28, color: '#DC2626' }}>
                        <LogoutIcon fontSize="small" />
                      </ListItemIcon>
                      {t('signOut')}
                    </MenuItem>
                  </Menu>
                </Stack>
              ) : (
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <Button
                    onClick={() => navigate('/login')}
                    sx={{
                      color: '#0F2E59',
                      fontSize: '0.88rem',
                      fontWeight: 700,
                      textTransform: 'none',
                      px: 2.2,
                      py: 0.7,
                      borderRadius: '8px',
                      border: '1.5px solid #CBD5E1',
                      bgcolor: '#FFFFFF',
                      '&:hover': { bgcolor: '#F8FAFC', borderColor: '#0F2E59' },
                    }}
                  >
                    {t('signIn')}
                  </Button>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/register')}
                    endIcon={<ArrowForwardIcon sx={{ fontSize: '15px !important' }} />}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      fontSize: '0.88rem',
                      fontWeight: 700,
                      textTransform: 'none',
                      px: 2.4,
                      py: 0.7,
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {t('register')}
                  </Button>
                </Stack>
              )}

              {/* Mobile Menu Hamburger */}
              <IconButton
                onClick={() => setMobileOpen(!mobileOpen)}
                sx={{ display: { md: 'none' }, color: '#0F2E59' }}
              >
                {mobileOpen ? <CloseIcon /> : <MenuIcon />}
              </IconButton>
            </Stack>
          </Stack>
        </Container>
      </Box>

      {/* ─── 3. BIG MAIN NAVBAR (AS IN MSME.GOV.IN) ─── */}
      <Box
        component="nav"
        sx={{
          bgcolor: '#FFFFFF',
          borderBottom: '2px solid #E2E8F0',
          boxShadow: '0 4px 14px rgba(15, 23, 42, 0.05)',
          position: 'sticky',
          top: 0,
          zIndex: 1200,
        }}
      >
        <Container maxWidth="xl" disableGutters sx={{ px: { xs: 2, md: 3 } }}>
          <Toolbar
            disableGutters
            sx={{
              minHeight: { xs: '54px !important', md: '58px !important' },
              height: { xs: 54, md: 58 },
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            {/* Desktop Navigation Items */}
            <Stack
              direction="row"
              spacing={0.5}
              alignItems="center"
              sx={{ display: { xs: 'none', md: 'flex' }, height: '100%' }}
            >
              {/* 1. Home - Active Indicator in Maroon/Red */}
              <Box
                onClick={() => navigate('/')}
                sx={{
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  px: 2.2,
                  cursor: 'pointer',
                  position: 'relative',
                  fontWeight: 800,
                  fontSize: '0.96rem',
                  color: isLandingPage ? '#8B0000' : '#1E293B',
                  letterSpacing: '0.01em',
                  transition: 'all 0.15s ease',
                  '&:after': isLandingPage
                    ? {
                        content: '""',
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        bgcolor: '#8B0000',
                        borderTopLeftRadius: '3px',
                        borderTopRightRadius: '3px',
                      }
                    : {},
                  '&:hover': {
                    color: '#8B0000',
                    bgcolor: '#F8FAFC',
                  },
                }}
              >
                {t('home')}
              </Box>

              {/* 2. Ministry ▾ (About us, Our Performance) */}
              <Button
                onClick={(e) => setMinistryAnchor(e.currentTarget)}
                endIcon={<KeyboardArrowDownIcon sx={{ fontSize: 18 }} />}
                sx={{
                  height: '100%',
                  px: 2,
                  color: '#1E293B',
                  fontWeight: 700,
                  fontSize: '0.94rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  '&:hover': { bgcolor: '#F8FAFC', color: '#0F2E59' },
                }}
              >
                {t('ministry')}
              </Button>
              <Menu
                anchorEl={ministryAnchor}
                open={Boolean(ministryAnchor)}
                onClose={() => setMinistryAnchor(null)}
                PaperProps={{
                  sx: {
                    mt: 1,
                    minWidth: 240,
                    borderRadius: '8px',
                    boxShadow: '0 8px 24px rgba(15, 23, 42, 0.12)',
                    border: '1px solid #E2E8F0',
                  },
                }}
              >
                <MenuItem onClick={() => openModal('about_us')} sx={{ py: 1.2 }}>
                  <ListItemIcon sx={{ minWidth: 32, color: '#0F2E59' }}>
                    <InfoOutlinedIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={t('aboutUs')}
                    secondary={t('aboutUsDesc')}
                    primaryTypographyProps={{ fontWeight: 700, fontSize: '0.9rem', color: '#0F2E59' }}
                    secondaryTypographyProps={{ fontSize: '0.74rem' }}
                  />
                </MenuItem>
                <Divider sx={{ my: 0.5 }} />
                <MenuItem onClick={() => openModal('performance')} sx={{ py: 1.2 }}>
                  <ListItemIcon sx={{ minWidth: 32, color: '#059669' }}>
                    <TrendingUpIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={t('ourPerformance')}
                    secondary={t('ourPerformanceDesc')}
                    primaryTypographyProps={{ fontWeight: 700, fontSize: '0.9rem', color: '#0F2E59' }}
                    secondaryTypographyProps={{ fontSize: '0.74rem' }}
                  />
                </MenuItem>
              </Menu>

              {/* 3. Media ▾ (Photos, Videos, Brochures) */}
              <Button
                onClick={(e) => setMediaAnchor(e.currentTarget)}
                endIcon={<KeyboardArrowDownIcon sx={{ fontSize: 18 }} />}
                sx={{
                  height: '100%',
                  px: 2,
                  color: '#1E293B',
                  fontWeight: 700,
                  fontSize: '0.94rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  '&:hover': { bgcolor: '#F8FAFC', color: '#0F2E59' },
                }}
              >
                {t('media')}
              </Button>
              <Menu
                anchorEl={mediaAnchor}
                open={Boolean(mediaAnchor)}
                onClose={() => setMediaAnchor(null)}
                PaperProps={{
                  sx: {
                    mt: 1,
                    minWidth: 260,
                    borderRadius: '8px',
                    boxShadow: '0 8px 24px rgba(15, 23, 42, 0.12)',
                    border: '1px solid #E2E8F0',
                  },
                }}
              >
                <MenuItem onClick={() => openModal('photos')} sx={{ py: 1.2 }}>
                  <ListItemIcon sx={{ minWidth: 32, color: '#0284C7' }}>
                    <PhotoCameraOutlinedIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={t('photos')}
                    secondary={t('photosDesc')}
                    primaryTypographyProps={{ fontWeight: 700, fontSize: '0.9rem', color: '#0F2E59' }}
                    secondaryTypographyProps={{ fontSize: '0.74rem' }}
                  />
                </MenuItem>
                <MenuItem onClick={() => openModal('videos')} sx={{ py: 1.2 }}>
                  <ListItemIcon sx={{ minWidth: 32, color: '#DC2626' }}>
                    <VideocamOutlinedIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={t('videos')}
                    secondary={t('videosDesc')}
                    primaryTypographyProps={{ fontWeight: 700, fontSize: '0.9rem', color: '#0F2E59' }}
                    secondaryTypographyProps={{ fontSize: '0.74rem' }}
                  />
                </MenuItem>
                <Divider sx={{ my: 0.5 }} />
                <MenuItem onClick={() => openModal('brochures')} sx={{ py: 1.2 }}>
                  <ListItemIcon sx={{ minWidth: 32, color: '#D97706' }}>
                    <PictureAsPdfOutlinedIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={t('brochures')}
                    secondary={t('brochuresDesc')}
                    primaryTypographyProps={{ fontWeight: 700, fontSize: '0.9rem', color: '#0F2E59' }}
                    secondaryTypographyProps={{ fontSize: '0.74rem' }}
                  />
                </MenuItem>
              </Menu>

              {/* 4. Connect ▾ (Contact us, RTI) */}
              <Button
                onClick={(e) => setConnectAnchor(e.currentTarget)}
                endIcon={<KeyboardArrowDownIcon sx={{ fontSize: 18 }} />}
                sx={{
                  height: '100%',
                  px: 2,
                  color: '#1E293B',
                  fontWeight: 700,
                  fontSize: '0.94rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  '&:hover': { bgcolor: '#F8FAFC', color: '#0F2E59' },
                }}
              >
                {t('connect')}
              </Button>
              <Menu
                anchorEl={connectAnchor}
                open={Boolean(connectAnchor)}
                onClose={() => setConnectAnchor(null)}
                PaperProps={{
                  sx: {
                    mt: 1,
                    minWidth: 260,
                    borderRadius: '8px',
                    boxShadow: '0 8px 24px rgba(15, 23, 42, 0.12)',
                    border: '1px solid #E2E8F0',
                  },
                }}
              >
                <MenuItem onClick={() => openModal('contact_us')} sx={{ py: 1.2 }}>
                  <ListItemIcon sx={{ minWidth: 32, color: '#10B981' }}>
                    <PhoneInTalkOutlinedIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={t('contactUs')}
                    secondary={t('contactUsDesc')}
                    primaryTypographyProps={{ fontWeight: 700, fontSize: '0.9rem', color: '#0F2E59' }}
                    secondaryTypographyProps={{ fontSize: '0.74rem' }}
                  />
                </MenuItem>
                <Divider sx={{ my: 0.5 }} />
                <MenuItem onClick={() => openModal('rti')} sx={{ py: 1.2 }}>
                  <ListItemIcon sx={{ minWidth: 32, color: '#7C3AED' }}>
                    <GavelOutlinedIcon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={t('rti')}
                    secondary={t('rtiDesc')}
                    primaryTypographyProps={{ fontWeight: 700, fontSize: '0.9rem', color: '#0F2E59' }}
                    secondaryTypographyProps={{ fontSize: '0.74rem' }}
                  />
                </MenuItem>
              </Menu>

              {/* 5. Schemes Dashboard Link */}
              <Button
                onClick={() => navigate('/dashboard')}
                sx={{
                  height: '100%',
                  px: 2,
                  color: isDashboard ? '#0F2E59' : '#1E293B',
                  fontWeight: isDashboard ? 800 : 700,
                  fontSize: '0.94rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  position: 'relative',
                  '&:after': isDashboard
                    ? {
                        content: '""',
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        bgcolor: '#0F2E59',
                      }
                    : {},
                  '&:hover': { bgcolor: '#F8FAFC', color: '#0F2E59' },
                }}
              >
                {t('schemesDashboard')}
              </Button>

              {/* 6. Gazette Radar Link */}
              <Button
                onClick={() => navigate('/monitor')}
                sx={{
                  height: '100%',
                  px: 2,
                  color: isMonitor ? '#0F2E59' : '#1E293B',
                  fontWeight: isMonitor ? 800 : 700,
                  fontSize: '0.94rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  position: 'relative',
                  '&:after': isMonitor
                    ? {
                        content: '""',
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        bgcolor: '#0F2E59',
                      }
                    : {},
                  '&:hover': { bgcolor: '#F8FAFC', color: '#0F2E59' },
                }}
              >
                {t('gazetteRadar')}
              </Button>
            </Stack>

            {/* Quick Portal Action on Right of Navbar */}
            <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 1 }}>
              <Chip
                label={t('verifiedSchemesBadge')}
                size="small"
                sx={{
                  bgcolor: '#ECFDF5',
                  color: '#065F46',
                  fontWeight: 700,
                  border: '1px solid #A7F3D0',
                  fontSize: '0.76rem',
                }}
              />
              <Button
                size="small"
                variant="outlined"
                onClick={() => navigate('/dashboard')}
                endIcon={<OpenInNewIcon sx={{ fontSize: '13px !important' }} />}
                sx={{
                  borderColor: '#0F2E59',
                  color: '#0F2E59',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  textTransform: 'none',
                  px: 1.5,
                  py: 0.4,
                  borderRadius: '6px',
                  '&:hover': { bgcolor: '#F1F5F9' },
                }}
              >
                {t('browseCatalog')}
              </Button>
            </Box>

            {/* Mobile Branding Bar */}
            <Typography variant="subtitle2" sx={{ display: { xs: 'block', md: 'none' }, fontWeight: 800, color: '#0F2E59' }}>
              Udyam<Box component="span" sx={{ color: '#E65100' }}>Niti</Box> Navigation
            </Typography>
          </Toolbar>
        </Container>
      </Box>

      {/* ─── 4. MOBILE DRAWER MENU ─── */}
      <Drawer
        anchor="right"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        PaperProps={{
          sx: {
            width: 290,
            bgcolor: '#FFFFFF',
            borderLeft: '1px solid #E2E8F0',
            p: 2,
          },
        }}
      >
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59' }}>
            Udyam<Box component="span" sx={{ color: '#E65100' }}>Niti</Box>
          </Typography>
          <IconButton onClick={() => setMobileOpen(false)} size="small">
            <CloseIcon />
          </IconButton>
        </Stack>
        {/* Mobile Language Selector */}
        <Box sx={{ mb: 2, p: 1.5, bgcolor: '#F8FAFC', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
          <Typography variant="caption" sx={{ color: '#64748B', fontWeight: 800, display: 'block', mb: 1 }}>
            {t('selectLanguage')}
          </Typography>
          <Stack direction="row" spacing={1}>
            {(['en', 'hi', 'gu'] as Language[]).map((l) => (
              <Button
                key={l}
                size="small"
                variant={lang === l ? 'contained' : 'outlined'}
                onClick={() => setLang(l)}
                sx={{
                  flex: 1,
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  py: 0.5,
                  px: 0.5,
                  minWidth: 0,
                  bgcolor: lang === l ? '#0F2E59' : '#FFFFFF',
                  borderColor: lang === l ? '#0F2E59' : '#CBD5E1',
                  color: lang === l ? '#FFFFFF' : '#334155',
                  textTransform: 'none',
                }}
              >
                {LANGUAGE_LABELS[l]}
              </Button>
            ))}
          </Stack>
        </Box>

        <List disablePadding>
          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/'); setMobileOpen(false); }}>
              <ListItemText primary={t('home')} primaryTypographyProps={{ fontWeight: 700, color: '#8B0000' }} />
            </ListItemButton>
          </ListItem>

          <Typography variant="caption" sx={{ px: 2, pt: 1.5, display: 'block', color: '#64748B', fontWeight: 800 }}>
            {t('ministry').toUpperCase()}
          </Typography>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('about_us')}>
              <ListItemText primary={t('aboutUs')} primaryTypographyProps={{ fontSize: '0.9rem', color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('performance')}>
              <ListItemText primary={t('ourPerformance')} primaryTypographyProps={{ fontSize: '0.9rem', color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>

          <Typography variant="caption" sx={{ px: 2, pt: 1.5, display: 'block', color: '#64748B', fontWeight: 800 }}>
            {t('media').toUpperCase()}
          </Typography>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('photos')}>
              <ListItemText primary={t('photos')} primaryTypographyProps={{ fontSize: '0.9rem', color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('videos')}>
              <ListItemText primary={t('videos')} primaryTypographyProps={{ fontSize: '0.9rem', color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('brochures')}>
              <ListItemText primary={t('brochures')} primaryTypographyProps={{ fontSize: '0.9rem', color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>

          <Typography variant="caption" sx={{ px: 2, pt: 1.5, display: 'block', color: '#64748B', fontWeight: 800 }}>
            {t('connect').toUpperCase()}
          </Typography>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('contact_us')}>
              <ListItemText primary={t('contactUs')} primaryTypographyProps={{ fontSize: '0.9rem', color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('rti')}>
              <ListItemText primary={t('rti')} primaryTypographyProps={{ fontSize: '0.9rem', color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>

          <Divider sx={{ my: 1.5 }} />

          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/dashboard'); setMobileOpen(false); }}>
              <ListItemText primary={t('schemesDashboard')} primaryTypographyProps={{ fontWeight: 700, color: '#0F2E59' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/monitor'); setMobileOpen(false); }}>
              <ListItemText primary={t('gazetteRadar')} primaryTypographyProps={{ fontWeight: 700, color: '#0F2E59' }} />
            </ListItemButton>
          </ListItem>
        </List>
      </Drawer>

      {/* ─── 5. INTERACTIVE CONTENT MODALS FOR DROPDOWN ITEMS ─── */}

      {/* MODAL 1: About Us */}
      <Dialog open={modalOpen === 'about_us'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          About Ministry of Micro, Small & Medium Enterprises
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body1" sx={{ color: '#1E293B', mb: 2, lineHeight: 1.7 }}>
            The Ministry of Micro, Small and Medium Enterprises (M/o MSME) envisions a vibrant MSME sector by promoting growth and development of the MSME Sector, including Khadi, Village and Coir Industries, in cooperation with concerned Ministries/Departments, State Governments and other Stakeholders.
          </Typography>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <Paper sx={{ p: 2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                  Our Mission
                </Typography>
                <Typography variant="body2" sx={{ color: '#475569' }}>
                  Promote growth and development of technically sound, competitive and sustainable micro, small and medium enterprises across manufacturing and services.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Paper sx={{ p: 2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                  Key Divisions & Organizations
                </Typography>
                <Typography variant="body2" sx={{ color: '#475569' }}>
                  • Development Commissioner (MSME)<br />
                  • Khadi and Village Industries Commission (KVIC)<br />
                  • Coir Board & National Small Industries Corp (NSIC)<br />
                  • National Institute for MSME (ni-msme)
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC', borderTop: '1px solid #E2E8F0' }}>
          <Button onClick={() => setModalOpen(null)} variant="contained" sx={{ bgcolor: '#0F2E59' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* MODAL 2: Our Performance */}
      <Dialog open={modalOpen === 'performance'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#059669', color: '#FFFFFF', fontWeight: 800 }}>
          Our Performance & National MSME Milestones
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body1" sx={{ color: '#1E293B', mb: 3 }}>
            Verified impact indicators reflecting national economic contribution of Indian Micro, Small and Medium Enterprises:
          </Typography>
          <Grid container spacing={2}>
            {[
              { stat: '6.3+ Crore', label: 'Registered Enterprises', desc: 'Active Udyam Verified MSME units nationwide' },
              { stat: '₹5.2 Lakh Cr', label: 'Credit Guaranteed', desc: 'Collateral-free credit backing delivered under CGTMSE' },
              { stat: '₹12,400 Cr', label: 'Margin Money Subsidy', desc: 'Direct financial assistance disbursed through PMEGP' },
              { stat: '500+ Clusters', label: 'SFURTI & CDP Clusters', desc: 'Traditional artisanal and manufacturing common facilities' },
            ].map((card, i) => (
              <Grid item xs={12} sm={6} key={i}>
                <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', textAlign: 'center' }}>
                  <Typography variant="h4" sx={{ fontWeight: 900, color: '#0F2E59', mb: 0.5 }}>
                    {card.stat}
                  </Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#059669', mb: 0.5 }}>
                    {card.label}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>
                    {card.desc}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC', borderTop: '1px solid #E2E8F0' }}>
          <Button onClick={() => setModalOpen(null)} variant="contained" sx={{ bgcolor: '#059669' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* MODAL 3: Photos */}
      <Dialog open={modalOpen === 'photos'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Media Gallery • Photos
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body2" sx={{ color: '#475569', mb: 2 }}>
            High-resolution visual highlights from National MSME Summits, Award Ceremonies, and Cluster Exhibitions:
          </Typography>
          <Grid container spacing={2}>
            {[
              {
                title: 'National MSME Awards Ceremony',
                desc: 'Honoring top performing Micro & Small entrepreneurs in manufacturing excellence.',
                tag: 'National Awards',
              },
              {
                title: 'SFURTI Cluster Exhibition & Khadi Pavilions',
                desc: 'Showcasing rural artisans, coir products, and traditional textile technologies.',
                tag: 'Cluster Expo',
              },
              {
                title: 'ZED Certification Industry Conclave',
                desc: 'Recognizing zero-defect and green-rated manufacturing facilities across India.',
                tag: 'Quality Conclave',
              },
              {
                title: 'International MSME Trade Delegation',
                desc: 'Facilitating global market access for Indian exporters under the IC Scheme.',
                tag: 'Global Access',
              },
            ].map((p, i) => (
              <Grid item xs={12} sm={6} key={i}>
                <Card sx={{ border: '1px solid #E2E8F0' }}>
                  <Box
                    sx={{
                      height: 140,
                      bgcolor: '#E2E8F0',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: `linear-gradient(135deg, ${i % 2 === 0 ? '#0F2E59' : '#059669'} 0%, #1E3A8A 100%)`,
                      color: '#FFFFFF',
                    }}
                  >
                    <Stack alignItems="center" spacing={1}>
                      <PhotoCameraOutlinedIcon sx={{ fontSize: 36 }} />
                      <Chip label={p.tag} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: '#FFFFFF', fontWeight: 700 }} />
                    </Stack>
                  </Box>
                  <CardContent sx={{ p: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 0.5 }}>
                      {p.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#64748B' }}>
                      {p.desc}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC' }}>
          <Button onClick={() => setModalOpen(null)} variant="contained" sx={{ bgcolor: '#0F2E59' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* MODAL 4: Videos */}
      <Dialog open={modalOpen === 'videos'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Media Gallery • Videos
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body2" sx={{ color: '#475569', mb: 2 }}>
            Official video tutorials, policy announcements, and documentary features on Indian MSME transformation:
          </Typography>
          <Grid container spacing={2}>
            {[
              { title: 'Prime Minister Address at Udyami Bharat', duration: '18 mins', topic: 'Credit & Export Vision' },
              { title: 'How to Obtain ZED Bronze & Gold Subsidy', duration: '12 mins', topic: 'Technical Guide' },
              { title: 'Step-by-Step PMEGP Margin Money Loan Process', duration: '15 mins', topic: 'Financial Literacy' },
              { title: 'TReDS: Resolving Delayed Payments in 48 Hours', duration: '8 mins', topic: 'Invoice Discounting' },
            ].map((v, i) => (
              <Grid item xs={12} sm={6} key={i}>
                <Paper sx={{ p: 2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <Box sx={{ width: 44, height: 44, borderRadius: '8px', bgcolor: '#FEF2F2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <VideocamOutlinedIcon sx={{ color: '#DC2626' }} />
                    </Box>
                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                        {v.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748B' }}>
                        {v.topic} • {v.duration}
                      </Typography>
                    </Box>
                  </Stack>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC' }}>
          <Button onClick={() => setModalOpen(null)} variant="contained" sx={{ bgcolor: '#0F2E59' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* MODAL 5: Brochures & Guidelines (Featuring user's uploaded PDFs) */}
      <Dialog open={modalOpen === 'brochures'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Official Policy Guidelines & Scheme Brochures
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body2" sx={{ color: '#475569', mb: 2 }}>
            Official Gazette publications and operational scheme guideline PDFs archived in your product's scheme repository:
          </Typography>
          <Grid container spacing={1.5}>
            {[
              { name: 'Prime Minister Employment Generation Programme (PMEGP)', file: 'pmegp scheme.pdf', ministry: 'M/o MSME' },
              { name: 'Scheme of Fund for Regeneration of Traditional Industries (SFURTI)', file: 'SFURTI_NEW_GUIDELINES.pdf', ministry: 'M/o MSME' },
              { name: 'Zero Defect Zero Effect (ZED) Certification Guidance', file: 'ZED_Guidance_Document_NIC_Division_24.pdf', ministry: 'QCI / MSME' },
              { name: 'Trade Receivables Discounting System (TReDS) Circular 262', file: 'TReDS Cicular 262.pdf', ministry: 'RBI / MSME' },
              { name: 'International Cooperation (IC) Scheme Guidelines', file: 'Final and approved IC Scheme Guidelines-2021.pdf', ministry: 'M/o MSME' },
              { name: 'Micro & Small Enterprises Cluster Development (MSME-CDP)', file: 'msme-cdp.pdf', ministry: 'O/o DC MSME' },
              { name: 'Coir Vikas Yojana (CVY) Assistance Framework', file: 'cvy.schemes.pdf', ministry: 'Coir Board' },
              { name: 'Credit Guarantee Scheme (CGS) for Export Credit', file: 'Circular 257 - CGS for Export credit merged.pdf', ministry: 'CGTMSE' },
            ].map((b, i) => (
              <Grid item xs={12} key={i}>
                <Paper sx={{ p: 1.8, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <PictureAsPdfOutlinedIcon sx={{ color: '#DC2626', fontSize: 24 }} />
                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '0.88rem' }}>
                        {b.name}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#64748B' }}>
                        File: {b.file} • Authority: {b.ministry}
                      </Typography>
                    </Box>
                  </Stack>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<DownloadIcon sx={{ fontSize: 15 }} />}
                    onClick={() => {
                      toast.success(`Opening ${b.file} from backend/data/scheme_pdfs/`)
                    }}
                    sx={{ textTransform: 'none', borderColor: '#CBD5E1', color: '#0F2E59', fontWeight: 700 }}
                  >
                    View PDF
                  </Button>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC' }}>
          <Button onClick={() => setModalOpen(null)} variant="contained" sx={{ bgcolor: '#0F2E59' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* MODAL 6: Contact Us */}
      <Dialog open={modalOpen === 'contact_us'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Contact Directory & MSME Facilitation Centers
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PhoneInTalkOutlinedIcon sx={{ color: '#059669' }} /> Central Helpdesk
                </Typography>
                <Typography variant="body2" sx={{ color: '#1E293B', mb: 1 }}>
                  <strong>Toll-Free Helpline:</strong> 1800 11 7800 (9:00 AM - 6:00 PM)
                </Typography>
                <Typography variant="body2" sx={{ color: '#1E293B', mb: 1 }}>
                  <strong>Alternative Line:</strong> 1800 180 6763
                </Typography>
                <Typography variant="body2" sx={{ color: '#1E293B' }}>
                  <strong>Email:</strong> champion-msme@gov.in / support@udyamniti.gov.in
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocationOnOutlinedIcon sx={{ color: '#DC2626' }} /> Head Office
                </Typography>
                <Typography variant="body2" sx={{ color: '#475569', lineHeight: 1.6 }}>
                  Ministry of Micro, Small and Medium Enterprises<br />
                  Udyog Bhawan, Rafi Marg, New Delhi - 110011<br />
                  Government of India
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC' }}>
          <Button onClick={() => setModalOpen(null)} variant="contained" sx={{ bgcolor: '#0F2E59' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* MODAL 7: RTI */}
      <Dialog open={modalOpen === 'rti'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Right to Information (RTI) Act, 2005
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body1" sx={{ color: '#1E293B', mb: 2, lineHeight: 1.7 }}>
            In accordance with the Right to Information Act, 2005, the Ministry of MSME maintains proactive public disclosures under Section 4(1)(b) to ensure statutory transparency, administrative accountability, and citizen empowerment.
          </Typography>
          <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', mb: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
              Filing an Online RTI Application
            </Typography>
            <Typography variant="body2" sx={{ color: '#475569', mb: 1.5 }}>
              Indian citizens may submit online RTI requests and first appeals regarding Central MSME policies, budget allocations, and subsidy sanctions directly through the official National RTI Portal:
            </Typography>
            <Button
              variant="outlined"
              size="small"
              href="https://rtionline.gov.in"
              target="_blank"
              endIcon={<OpenInNewIcon sx={{ fontSize: 14 }} />}
              sx={{ textTransform: 'none', borderColor: '#0F2E59', color: '#0F2E59', fontWeight: 700 }}
            >
              Visit rtionline.gov.in
            </Button>
          </Paper>
          <Typography variant="caption" sx={{ color: '#64748B' }}>
            Appellate Authority: Joint Secretary, Ministry of MSME, Udyog Bhawan, New Delhi.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC' }}>
          <Button onClick={() => setModalOpen(null)} variant="contained" sx={{ bgcolor: '#0F2E59' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* ─── MAIN CONTENT ─── */}
      <Box component="main" sx={{ flex: 1 }}>
        <Outlet />
      </Box>

      {/* ─── MINIMAL CLEAN FOOTER (For internal dashboard routes) ─── */}
      {!isLandingPage && (
        <Box
          component="footer"
          sx={{
            py: 3,
            borderTop: '1px solid #E2E8F0',
            bgcolor: '#FFFFFF',
          }}
        >
          <Container maxWidth="xl" disableGutters sx={{ px: 3 }}>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              justifyContent="space-between"
              alignItems="center"
              spacing={2}
            >
              <Typography variant="body2" sx={{ color: '#64748B', fontSize: '0.85rem' }}>
                © {new Date().getFullYear()} UdyamNiti • Government of India & Gujarat State MSME Scheme Intelligence
              </Typography>
              <Stack direction="row" spacing={3}>
                <Typography
                  component="a"
                  onClick={() => openModal('about_us')}
                  sx={{ color: '#475569', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#0F2E59' } }}
                >
                  {t('aboutUs')}
                </Typography>
                <Typography
                  component="a"
                  onClick={() => openModal('contact_us')}
                  sx={{ color: '#475569', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#0F2E59' } }}
                >
                  {t('contactUs')}
                </Typography>
                <Typography
                  component="a"
                  onClick={() => openModal('rti')}
                  sx={{ color: '#475569', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#0F2E59' } }}
                >
                  {t('rti')}
                </Typography>
              </Stack>
            </Stack>
          </Container>
        </Box>
      )}
    </Box>
  )
}

export default AppShell
