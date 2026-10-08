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
  TextField,
  InputAdornment,
  Tooltip,
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
import SearchIcon from '@mui/icons-material/Search'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import GroupIcon from '@mui/icons-material/Group'
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter'
import AssessmentIcon from '@mui/icons-material/Assessment'
import ContactPhoneIcon from '@mui/icons-material/ContactPhone'
import ArticleIcon from '@mui/icons-material/Article'
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone'
import SupportAgentIcon from '@mui/icons-material/SupportAgent'
import StarBorderIcon from '@mui/icons-material/StarBorder'
import MonetizationOnOutlinedIcon from '@mui/icons-material/MonetizationOnOutlined'
import BuildCircleOutlinedIcon from '@mui/icons-material/BuildCircleOutlined'
import SchoolOutlinedIcon from '@mui/icons-material/SchoolOutlined'
import StorefrontOutlinedIcon from '@mui/icons-material/StorefrontOutlined'
import FlightTakeoffOutlinedIcon from '@mui/icons-material/FlightTakeoffOutlined'
import ApartmentOutlinedIcon from '@mui/icons-material/ApartmentOutlined'
import FemaleIcon from '@mui/icons-material/Female'
import RocketLaunchOutlinedIcon from '@mui/icons-material/RocketLaunchOutlined'
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined'
import EmailOutlinedIcon from '@mui/icons-material/EmailOutlined'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import { tokens } from '../theme/tokens'
import { toast } from 'sonner'
import { useLanguage, Language, LANGUAGE_LABELS } from '../i18n'
import langIconImg from '../assets/lang_icon.png'

export const AppShell: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null)

  // Language state & translation hook
  const { lang, setLang, t } = useLanguage()
  const [langMenuAnchor, setLangMenuAnchor] = useState<null | HTMLElement>(null)

  // 5 Main Navigation Dropdown Anchors
  const [ministryAnchor, setMinistryAnchor] = useState<null | HTMLElement>(null)
  const [schemesAnchor, setSchemesAnchor] = useState<null | HTMLElement>(null)
  const [resourcesAnchor, setResourcesAnchor] = useState<null | HTMLElement>(null)
  const [updatesAnchor, setUpdatesAnchor] = useState<null | HTMLElement>(null)
  const [supportAnchor, setSupportAnchor] = useState<null | HTMLElement>(null)

  // Search Modal
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

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
  const isAuthPage = location.pathname === '/register' || location.pathname === '/login'

  const closeAllMenus = () => {
    setMinistryAnchor(null)
    setSchemesAnchor(null)
    setResourcesAnchor(null)
    setUpdatesAnchor(null)
    setSupportAnchor(null)
    setMobileOpen(false)
  }

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return
    setSearchOpen(false)
    navigate(`/dashboard?search=${encodeURIComponent(searchQuery.trim())}`)
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#F8FAFC' }}>
      {/* ─── 1. TOP HEADER BAR: UDYAMNITI LOGO (LEFT) & LANGUAGE + SIGNIN / REGISTER (RIGHT) ─── */}
      <Box
        sx={{
          bgcolor: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          py: { xs: 2, md: 2.6 },
          px: { xs: 2, md: 4 },
          minHeight: { xs: 72, md: 84 },
          display: 'flex',
          alignItems: 'center',
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
              spacing={1.8}
              sx={{ cursor: 'pointer', userSelect: 'none' }}
              onClick={() => navigate('/')}
            >
              <Box
                sx={{
                  width: { xs: 46, md: 52 },
                  height: { xs: 46, md: 52 },
                  borderRadius: '12px',
                  bgcolor: '#0F2E59',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 14px rgba(15, 46, 89, 0.25)',
                  flexShrink: 0,
                }}
              >
                <PolicyIcon sx={{ color: '#FFFFFF', fontSize: { xs: 28, md: 32 } }} />
              </Box>
              <Box>
                <Typography
                  variant="h6"
                  sx={{
                    fontFamily: tokens.font.heading,
                    fontWeight: 800,
                    color: '#0F2E59',
                    fontSize: { xs: '1.35rem', sm: '1.55rem', md: '1.7rem' },
                    lineHeight: 1.15,
                    letterSpacing: '-0.02em',
                  }}
                >
                  Udyam<Box component="span" sx={{ color: '#E65100' }}>Niti</Box>
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    color: '#64748B',
                    fontSize: { xs: '0.74rem', sm: '0.82rem' },
                    fontWeight: 600,
                    letterSpacing: '0.02em',
                    display: 'block',
                    mt: 0.2,
                  }}
                >
                  {t('tagline')}
                </Typography>
              </Box>
            </Stack>

            {/* Top Right: Language Selector & Auth Buttons */}
            <Stack direction="row" spacing={1.8} alignItems="center">
              {/* Language Selector (EN / HI / GU) with Big, Prominent Bilingual Mark (अ / A) */}
              <Tooltip title="Language Preference / भाषा का चयन / ભાષા પસંદ કરો">
                <Button
                  id="language-selector-button"
                  onClick={(e) => setLangMenuAnchor(e.currentTarget)}
                  variant="outlined"
                  size="medium"
                  aria-label="Change Language Preference"
                  sx={{
                    minWidth: 'auto',
                    px: { xs: 1.8, md: 2.2 },
                    height: { xs: 42, md: 48 },
                    borderColor: '#CBD5E1',
                    bgcolor: '#FFFFFF',
                    borderRadius: '10px',
                    boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                    transition: 'all 0.15s ease',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    '&:hover': {
                      borderColor: '#8B0000',
                      bgcolor: '#FEF2F2',
                    },
                  }}
                >
                  <Box
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'baseline',
                      lineHeight: 1,
                      userSelect: 'none',
                    }}
                  >
                    <Typography
                      component="span"
                      sx={{
                        fontSize: { xs: '1.5rem', md: '1.75rem' },
                        fontWeight: 900,
                        color: '#8B0000',
                        fontFamily: "'Noto Sans Devanagari', 'Mukta', 'Segoe UI', sans-serif",
                        lineHeight: 1,
                        letterSpacing: '-0.02em',
                      }}
                    >
                      अ
                    </Typography>
                    <Typography
                      component="span"
                      sx={{
                        fontSize: { xs: '1.1rem', md: '1.25rem' },
                        fontWeight: 900,
                        color: '#8B0000',
                        lineHeight: 1,
                        ml: 0.3,
                        transform: 'translateY(1px)',
                      }}
                    >
                      A
                    </Typography>
                  </Box>
                  <KeyboardArrowDownIcon sx={{ fontSize: 20, color: '#64748B' }} />
                </Button>
              </Tooltip>
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
                      '&:hover': { bgcolor: '#F8FAFC' },
                    }}
                  >
                    <span>{LANGUAGE_LABELS[l]}</span>
                    {lang === l && <CheckCircleIcon sx={{ fontSize: 16, color: '#0F2E59', ml: 1.5 }} />}
                  </MenuItem>
                ))}
              </Menu>

              {isAuthPage ? (
                location.pathname === '/register' ? (
                  <Button
                    onClick={() => navigate('/login')}
                    sx={{
                      color: '#0F2E59',
                      fontSize: { xs: '0.88rem', md: '0.94rem' },
                      fontWeight: 700,
                      textTransform: 'none',
                      px: { xs: 2.2, md: 2.8 },
                      height: { xs: 42, md: 48 },
                      borderRadius: '10px',
                      border: '1.5px solid #CBD5E1',
                      bgcolor: '#FFFFFF',
                      '&:hover': { bgcolor: '#F8FAFC', borderColor: '#0F2E59' },
                    }}
                  >
                    {t('signIn')}
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    onClick={() => navigate('/register')}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      fontSize: { xs: '0.88rem', md: '0.94rem' },
                      fontWeight: 700,
                      textTransform: 'none',
                      px: { xs: 2.4, md: 3 },
                      height: { xs: 42, md: 48 },
                      borderRadius: '10px',
                      boxShadow: '0 4px 12px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {t('register')}
                  </Button>
                )
              ) : currentUser ? (
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <Button
                    onClick={() => navigate('/dashboard')}
                    variant="contained"
                    size="small"
                    startIcon={<GridViewIcon sx={{ fontSize: 16 }} />}
                    sx={{
                      bgcolor: '#0F2E59',
                      fontSize: { xs: '0.84rem', md: '0.9rem' },
                      fontWeight: 700,
                      borderRadius: '10px',
                      textTransform: 'none',
                      px: { xs: 2, md: 2.5 },
                      height: { xs: 42, md: 48 },
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
                      gap: 1.2,
                      cursor: 'pointer',
                      height: { xs: 42, md: 48 },
                      px: { xs: 1.2, md: 1.8 },
                      borderRadius: '9999px',
                      border: '1.5px solid #CBD5E1',
                      bgcolor: '#F8FAFC',
                      '&:hover': { bgcolor: '#F1F5F9', borderColor: '#0F2E59' },
                    }}
                  >
                    <Avatar sx={{ width: 34, height: 34, bgcolor: '#0F2E59', fontSize: '0.85rem', fontWeight: 700 }}>
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
                      fontSize: { xs: '0.88rem', md: '0.94rem' },
                      fontWeight: 700,
                      textTransform: 'none',
                      px: { xs: 2.2, md: 2.8 },
                      height: { xs: 42, md: 48 },
                      borderRadius: '10px',
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
                    endIcon={<ArrowForwardIcon sx={{ fontSize: '16px !important' }} />}
                    sx={{
                      bgcolor: '#0F2E59',
                      color: '#FFFFFF',
                      fontSize: { xs: '0.88rem', md: '0.94rem' },
                      fontWeight: 700,
                      textTransform: 'none',
                      px: { xs: 2.4, md: 3 },
                      height: { xs: 42, md: 48 },
                      borderRadius: '10px',
                      boxShadow: '0 4px 14px rgba(15, 46, 89, 0.25)',
                      '&:hover': { bgcolor: '#0A1E3A' },
                    }}
                  >
                    {t('register')}
                  </Button>
                </Stack>
              )}

              {/* Mobile Menu Hamburger */}
              {!isAuthPage && (
                <IconButton
                  onClick={() => setMobileOpen(!mobileOpen)}
                  sx={{ display: { md: 'none' }, color: '#0F2E59' }}
                >
                  {mobileOpen ? <CloseIcon /> : <MenuIcon />}
                </IconButton>
              )}
            </Stack>
          </Stack>
        </Container>
      </Box>

      {/* ─── 2. RECOMMENDED NAVBAR: HOME | MINISTRY | SCHEMES & BENEFITS | RESOURCES | UPDATES | SUPPORT | 🔍 SEARCH | ✨ FIND BENEFITS ─── */}
      {!isAuthPage && (
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
            {/* Desktop Navigation Left / Center */}
            <Stack
              direction="row"
              alignItems="center"
              sx={{
                display: { xs: 'none', md: 'flex' },
                height: '100%',
              }}
            >
              {/* 1. Home */}
              <Box
                onClick={() => navigate('/')}
                sx={{
                  px: 2.2,
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  cursor: 'pointer',
                  position: 'relative',
                  fontWeight: 800,
                  fontSize: '0.94rem',
                  color: isLandingPage ? '#8B0000' : '#1E293B',
                  transition: 'all 0.15s ease',
                  borderRight: '1px solid #F1F5F9',
                  '&:after': isLandingPage
                    ? {
                        content: '""',
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        right: 0,
                        height: '4px',
                        bgcolor: '#8B0000',
                      }
                    : {},
                  '&:hover': { color: '#8B0000', bgcolor: '#F8FAFC' },
                }}
              >
                {t('home')}
              </Box>

              {/* 2. Ministry ▾ */}
              <Button
                onClick={(e) => setMinistryAnchor(e.currentTarget)}
                endIcon={<KeyboardArrowDownIcon sx={{ fontSize: 17 }} />}
                sx={{
                  height: '100%',
                  px: 2,
                  color: '#1E293B',
                  fontWeight: 700,
                  fontSize: '0.92rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  borderRight: '1px solid #F1F5F9',
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
                    minWidth: 280,
                    borderRadius: '10px',
                    boxShadow: '0 10px 30px rgba(15, 23, 42, 0.14)',
                    border: '1px solid #E2E8F0',
                    py: 1,
                  },
                }}
              >
                <MenuItem
                  onClick={() => { closeAllMenus(); navigate('/ministry'); }}
                  sx={{ py: 1.2, px: 2, bgcolor: '#F8FAFC' }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: '#0F2E59' }}>
                    <AccountBalanceIcon fontSize="small" />
                  </ListItemIcon>
                  <Typography variant="body2" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                    {t('ministry')} Overview & Portal
                  </Typography>
                </MenuItem>
                <Divider sx={{ my: 0.5 }} />
                {[
                  { tab: 'about', label: t('aboutMinistry'), icon: <InfoOutlinedIcon fontSize="small" sx={{ color: '#0F2E59' }} /> },
                  { tab: 'vision', label: t('visionMission'), icon: <TrendingUpIcon fontSize="small" sx={{ color: '#059669' }} /> },
                  { tab: 'leadership', label: t('leadership'), icon: <GroupIcon fontSize="small" sx={{ color: '#2563EB' }} /> },
                  { tab: 'divisions', label: t('divisions'), icon: <BusinessCenterIcon fontSize="small" sx={{ color: '#7C3AED' }} /> },
                  { tab: 'bodies', label: t('organisations'), icon: <AccountBalanceIcon fontSize="small" sx={{ color: '#D97706' }} /> },
                  { tab: 'about', label: t('rolesAndResponsibilities'), icon: <AssessmentIcon fontSize="small" sx={{ color: '#0891B2' }} /> },
                  { tab: 'directory', label: t('ministryDirectory'), icon: <ContactPhoneIcon fontSize="small" sx={{ color: '#4B5563' }} /> },
                ].map((item, idx) => (
                  <MenuItem
                    key={idx}
                    onClick={() => { closeAllMenus(); navigate(`/ministry?tab=${item.tab}`); }}
                    sx={{ py: 1.1, px: 2 }}
                  >
                    <ListItemIcon sx={{ minWidth: 32 }}>{item.icon}</ListItemIcon>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#1E293B' }}>
                      {item.label}
                    </Typography>
                  </MenuItem>
                ))}
              </Menu>

              {/* 3. Schemes & Benefits ▾ */}
              <Button
                onClick={(e) => setSchemesAnchor(e.currentTarget)}
                endIcon={<KeyboardArrowDownIcon sx={{ fontSize: 17 }} />}
                sx={{
                  height: '100%',
                  px: 2,
                  color: '#1E293B',
                  fontWeight: 700,
                  fontSize: '0.92rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  borderRight: '1px solid #F1F5F9',
                  '&:hover': { bgcolor: '#F8FAFC', color: '#0F2E59' },
                }}
              >
                {t('schemesAndBenefits')}
              </Button>
              <Menu
                anchorEl={schemesAnchor}
                open={Boolean(schemesAnchor)}
                onClose={() => setSchemesAnchor(null)}
                PaperProps={{
                  sx: {
                    mt: 1,
                    minWidth: 320,
                    borderRadius: '10px',
                    boxShadow: '0 10px 30px rgba(15, 23, 42, 0.14)',
                    border: '1px solid #E2E8F0',
                    py: 1,
                  },
                }}
              >
                <MenuItem
                  onClick={() => { closeAllMenus(); navigate('/dashboard'); }}
                  sx={{ py: 1.2, px: 2, bgcolor: '#F8FAFC' }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: '#0F2E59' }}>
                    <GridViewIcon fontSize="small" />
                  </ListItemIcon>
                  <Typography variant="body2" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                    {t('exploreAllSchemes')}
                  </Typography>
                </MenuItem>
                <MenuItem
                  onClick={() => { closeAllMenus(); navigate('/dashboard?mode=finder'); }}
                  sx={{ py: 1.2, px: 2, bgcolor: '#FEF3C7' }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: '#B45309' }}>
                    <StarBorderIcon fontSize="small" />
                  </ListItemIcon>
                  <Typography variant="body2" sx={{ fontWeight: 800, color: '#B45309' }}>
                    {t('findSchemesForMyBusiness')}
                  </Typography>
                </MenuItem>
                <Divider sx={{ my: 0.5 }} />
                {[
                  { label: t('creditAndFinance'), category: 'credit_guarantee', icon: <MonetizationOnOutlinedIcon fontSize="small" sx={{ color: '#059669' }} /> },
                  { label: t('subsidiesAndIncentives'), category: 'capital_subsidy', icon: <AssessmentIcon fontSize="small" sx={{ color: '#D97706' }} /> },
                  { label: t('technologyAndInnovation'), category: 'quality_certification', icon: <BuildCircleOutlinedIcon fontSize="small" sx={{ color: '#2563EB' }} /> },
                  { label: t('skillDevelopment'), category: 'skill_development', icon: <SchoolOutlinedIcon fontSize="small" sx={{ color: '#7C3AED' }} /> },
                  { label: t('marketingSupport'), category: 'market_development', icon: <StorefrontOutlinedIcon fontSize="small" sx={{ color: '#CA8A04' }} /> },
                  { label: t('exportSupport'), category: 'export_support', icon: <FlightTakeoffOutlinedIcon fontSize="small" sx={{ color: '#EA580C' }} /> },
                  { label: t('infrastructureAndClusters'), category: 'infrastructure', icon: <ApartmentOutlinedIcon fontSize="small" sx={{ color: '#0891B2' }} /> },
                  { label: t('womenEntrepreneurs'), persona: 'women', icon: <FemaleIcon fontSize="small" sx={{ color: '#DB2777' }} /> },
                  { label: t('scstEntrepreneurs'), persona: 'sc_st', icon: <GroupIcon fontSize="small" sx={{ color: '#9333EA' }} /> },
                  { label: t('startupAndEntrepreneurship'), persona: 'startup', icon: <RocketLaunchOutlinedIcon fontSize="small" sx={{ color: '#4F46E5' }} /> },
                ].map((item, idx) => (
                  <MenuItem
                    key={idx}
                    onClick={() => {
                      closeAllMenus()
                      if (item.category) navigate(`/dashboard?category=${item.category}`)
                      else if (item.persona) navigate(`/dashboard?persona=${item.persona}`)
                    }}
                    sx={{ py: 0.9, px: 2 }}
                  >
                    <ListItemIcon sx={{ minWidth: 32 }}>{item.icon}</ListItemIcon>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#334155' }}>
                      {item.label}
                    </Typography>
                  </MenuItem>
                ))}
              </Menu>

              {/* 4. Resources ▾ */}
              <Button
                onClick={(e) => setResourcesAnchor(e.currentTarget)}
                endIcon={<KeyboardArrowDownIcon sx={{ fontSize: 17 }} />}
                sx={{
                  height: '100%',
                  px: 2,
                  color: '#1E293B',
                  fontWeight: 700,
                  fontSize: '0.92rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  borderRight: '1px solid #F1F5F9',
                  '&:hover': { bgcolor: '#F8FAFC', color: '#0F2E59' },
                }}
              >
                {t('resources')}
              </Button>
              <Menu
                anchorEl={resourcesAnchor}
                open={Boolean(resourcesAnchor)}
                onClose={() => setResourcesAnchor(null)}
                PaperProps={{
                  sx: {
                    mt: 1,
                    minWidth: 290,
                    borderRadius: '10px',
                    boxShadow: '0 10px 30px rgba(15, 23, 42, 0.14)',
                    border: '1px solid #E2E8F0',
                    py: 1,
                  },
                }}
              >
                <MenuItem
                  onClick={() => { closeAllMenus(); navigate('/resources'); }}
                  sx={{ py: 1.2, px: 2, bgcolor: '#F8FAFC' }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: '#0F2E59' }}>
                    <ArticleIcon fontSize="small" />
                  </ListItemIcon>
                  <Typography variant="body2" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                    {t('resources')} Portal
                  </Typography>
                </MenuItem>
                <Divider sx={{ my: 0.5 }} />
                <MenuItem
                  onClick={() => { closeAllMenus(); navigate('/resources?tab=guidelines'); }}
                  sx={{ py: 1.2, px: 2, bgcolor: '#FEF2F2' }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: '#DC2626' }}>
                    <PictureAsPdfOutlinedIcon fontSize="small" />
                  </ListItemIcon>
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 800, color: '#991B1B' }}>
                      {t('schemeGuidelines')}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#DC2626', fontSize: '0.72rem' }}>
                      11 Verified Official Guidelines
                    </Typography>
                  </Box>
                </MenuItem>
                <Divider sx={{ my: 0.5 }} />
                {[
                  { tab: 'acts', label: t('actsAndRules') },
                  { route: '/updates?tab=circulars', label: t('notifications') },
                  { route: '/updates?tab=circulars', label: t('circularsAndOrders') },
                  { route: '/ministry?tab=overview', label: t('reports') },
                  { tab: 'dpr', label: t('formsAndTemplates') },
                  { route: '/support?tab=faqs', label: t('faqs') },
                ].map((item, idx) => (
                  <MenuItem
                    key={idx}
                    onClick={() => {
                      closeAllMenus()
                      if (item.route) navigate(item.route)
                      else navigate(`/resources?tab=${item.tab}`)
                    }}
                    sx={{ py: 0.9, px: 2 }}
                  >
                    <ListItemIcon sx={{ minWidth: 32, color: '#64748B' }}>
                      <ArticleIcon fontSize="small" />
                    </ListItemIcon>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#334155' }}>
                      {item.label}
                    </Typography>
                  </MenuItem>
                ))}
              </Menu>

              {/* 5. Updates ▾ */}
              <Button
                onClick={(e) => setUpdatesAnchor(e.currentTarget)}
                endIcon={<KeyboardArrowDownIcon sx={{ fontSize: 17 }} />}
                sx={{
                  height: '100%',
                  px: 2,
                  color: '#1E293B',
                  fontWeight: 700,
                  fontSize: '0.92rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  borderRight: '1px solid #F1F5F9',
                  '&:hover': { bgcolor: '#F8FAFC', color: '#0F2E59' },
                }}
              >
                {t('updates')}
              </Button>
              <Menu
                anchorEl={updatesAnchor}
                open={Boolean(updatesAnchor)}
                onClose={() => setUpdatesAnchor(null)}
                PaperProps={{
                  sx: {
                    mt: 1,
                    minWidth: 260,
                    borderRadius: '10px',
                    boxShadow: '0 10px 30px rgba(15, 23, 42, 0.14)',
                    border: '1px solid #E2E8F0',
                    py: 1,
                  },
                }}
              >
                <MenuItem
                  onClick={() => { closeAllMenus(); navigate('/updates'); }}
                  sx={{ py: 1.2, px: 2, bgcolor: '#F8FAFC' }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: '#0F2E59' }}>
                    <NotificationsNoneIcon fontSize="small" />
                  </ListItemIcon>
                  <Typography variant="body2" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                    {t('updates')} Portal
                  </Typography>
                </MenuItem>
                <Divider sx={{ my: 0.5 }} />
                {[
                  { tab: 'circulars', label: t('whatsNew') },
                  { tab: 'press', label: t('announcements') },
                  { tab: 'circulars', label: t('schemeUpdates') },
                  { tab: 'events', label: t('events') },
                  { tab: 'press', label: t('pressReleases') },
                  { tab: 'press', label: t('successStories') },
                  { tab: 'events', label: t('photoGallery') },
                  { tab: 'events', label: t('videoGallery') },
                ].map((item, idx) => (
                  <MenuItem
                    key={idx}
                    onClick={() => { closeAllMenus(); navigate(`/updates?tab=${item.tab}`); }}
                    sx={{ py: 0.9, px: 2 }}
                  >
                    <ListItemIcon sx={{ minWidth: 32, color: '#0F2E59' }}>
                      <NotificationsNoneIcon fontSize="small" />
                    </ListItemIcon>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#334155' }}>
                      {item.label}
                    </Typography>
                  </MenuItem>
                ))}
              </Menu>

              {/* 6. Support ▾ */}
              <Button
                onClick={(e) => setSupportAnchor(e.currentTarget)}
                endIcon={<KeyboardArrowDownIcon sx={{ fontSize: 17 }} />}
                sx={{
                  height: '100%',
                  px: 2,
                  color: '#1E293B',
                  fontWeight: 700,
                  fontSize: '0.92rem',
                  textTransform: 'none',
                  borderRadius: 0,
                  borderRight: '1px solid #F1F5F9',
                  '&:hover': { bgcolor: '#F8FAFC', color: '#0F2E59' },
                }}
              >
                {t('support')}
              </Button>
              <Menu
                anchorEl={supportAnchor}
                open={Boolean(supportAnchor)}
                onClose={() => setSupportAnchor(null)}
                PaperProps={{
                  sx: {
                    mt: 1,
                    minWidth: 280,
                    borderRadius: '10px',
                    boxShadow: '0 10px 30px rgba(15, 23, 42, 0.14)',
                    border: '1px solid #E2E8F0',
                    py: 1,
                  },
                }}
              >
                <MenuItem
                  onClick={() => { closeAllMenus(); navigate('/support'); }}
                  sx={{ py: 1.2, px: 2, bgcolor: '#F8FAFC' }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: '#0F2E59' }}>
                    <SupportAgentIcon fontSize="small" />
                  </ListItemIcon>
                  <Typography variant="body2" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                    {t('support')} & Grievance Portal
                  </Typography>
                </MenuItem>
                <Divider sx={{ my: 0.5 }} />
                {[
                  { route: '/support?tab=helpdesk', label: t('helpCentre'), icon: <HelpOutlineIcon fontSize="small" sx={{ color: '#0284C7' }} /> },
                  { route: '/support?tab=helpdesk', label: t('contactMinistry'), icon: <PhoneInTalkOutlinedIcon fontSize="small" sx={{ color: '#059669' }} /> },
                  { route: '/ministry?tab=directory', label: t('ministryDirectory'), icon: <ContactPhoneIcon fontSize="small" sx={{ color: '#4B5563' }} /> },
                  { route: '/support?tab=samadhaan', label: t('grievanceSupport'), icon: <GavelOutlinedIcon fontSize="small" sx={{ color: '#7C3AED' }} /> },
                  { route: '/resources?tab=udyam', label: t('frequentlyAskedQuestions'), icon: <ArticleIcon fontSize="small" sx={{ color: '#D97706' }} /> },
                  { route: '/support?tab=champions', label: t('applicationHelp'), icon: <SupportAgentIcon fontSize="small" sx={{ color: '#2563EB' }} /> },
                  { route: '/support?tab=helpdesk', label: t('feedback'), icon: <InfoOutlinedIcon fontSize="small" sx={{ color: '#64748B' }} /> },
                ].map((item, idx) => (
                  <MenuItem
                    key={idx}
                    onClick={() => { closeAllMenus(); navigate(item.route); }}
                    sx={{ py: 0.9, px: 2 }}
                  >
                    <ListItemIcon sx={{ minWidth: 32 }}>{item.icon}</ListItemIcon>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: '#334155' }}>
                      {item.label}
                    </Typography>
                  </MenuItem>
                ))}
                <Divider sx={{ my: 0.5 }} />
                <MenuItem
                  onClick={() => { closeAllMenus(); navigate('/dashboard?mode=ai'); }}
                  sx={{ py: 1.1, px: 2, bgcolor: '#F0FDF4' }}
                >
                  <ListItemIcon sx={{ minWidth: 32, color: '#16A34A' }}>
                    <AutoAwesomeIcon fontSize="small" />
                  </ListItemIcon>
                  <Typography variant="body2" sx={{ fontWeight: 800, color: '#15803D' }}>
                    {t('askAiAssistant')}
                  </Typography>
                </MenuItem>
              </Menu>
            </Stack>

            {/* Desktop Navigation Right: 🔍 Search & ✨ Find Benefits for My Business */}
            <Stack direction="row" spacing={1.5} alignItems="center">
              {/* 🔍 Search Button */}
              <Button
                variant="outlined"
                size="small"
                startIcon={<SearchIcon sx={{ fontSize: 18, color: '#64748B' }} />}
                onClick={() => setSearchOpen(true)}
                sx={{
                  color: '#475569',
                  borderColor: '#CBD5E1',
                  bgcolor: '#F8FAFC',
                  fontWeight: 600,
                  fontSize: '0.84rem',
                  textTransform: 'none',
                  px: 1.8,
                  py: 0.6,
                  borderRadius: '8px',
                  display: { xs: 'none', sm: 'inline-flex' },
                  '&:hover': { bgcolor: '#F1F5F9', borderColor: '#94A3B8' },
                }}
              >
                {t('search')}
              </Button>

              {/* ✨ Prominent "Find Benefits for My Business" Button */}
              <Button
                variant="contained"
                size="small"
                startIcon={<AutoAwesomeIcon sx={{ fontSize: 17, color: '#FEF08A' }} />}
                onClick={() => navigate('/dashboard?mode=finder')}
                sx={{
                  background: 'linear-gradient(135deg, #E65100 0%, #EA580C 100%)',
                  color: '#FFFFFF',
                  fontWeight: 800,
                  fontSize: '0.88rem',
                  textTransform: 'none',
                  px: 2.2,
                  py: 0.8,
                  borderRadius: '8px',
                  boxShadow: '0 4px 14px rgba(230, 81, 0, 0.35)',
                  whiteSpace: 'nowrap',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #C2410C 0%, #9A3412 100%)',
                    boxShadow: '0 6px 18px rgba(230, 81, 0, 0.45)',
                  },
                }}
              >
                {t('findBenefitsForMyBusiness')}
              </Button>
            </Stack>

            {/* Mobile Title */}
            <Typography variant="subtitle2" sx={{ display: { xs: 'block', md: 'none' }, fontWeight: 800, color: '#0F2E59' }}>
              Udyam<Box component="span" sx={{ color: '#E65100' }}>Niti</Box>
            </Typography>
          </Toolbar>
        </Container>
      </Box>
      )}

      {/* ─── 3. SEARCH MODAL ─── */}
      <Dialog open={searchOpen} onClose={() => setSearchOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Search MSME Schemes & Benefits
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <form onSubmit={handleSearchSubmit}>
            <TextField
              fullWidth
              autoFocus
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t('searchPlaceholder')}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: '#0F2E59' }} />
                  </InputAdornment>
                ),
              }}
              sx={{ my: 1 }}
            />
            <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mt: 1 }}>
              Search across 11 official guidelines: PMEGP, CGTMSE, Gujarat SER, ZED, TReDS, SFURTI, and more.
            </Typography>
          </form>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC' }}>
          <Button onClick={() => setSearchOpen(false)} sx={{ color: '#64748B' }}>
            Cancel
          </Button>
          <Button onClick={handleSearchSubmit} variant="contained" sx={{ bgcolor: '#0F2E59' }}>
            Search Schemes →
          </Button>
        </DialogActions>
      </Dialog>

      {/* ─── 4. MOBILE DRAWER MENU ─── */}
      <Drawer
        anchor="right"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        PaperProps={{
          sx: {
            width: 300,
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

        <Button
          fullWidth
          variant="contained"
          startIcon={<AutoAwesomeIcon sx={{ color: '#FEF08A' }} />}
          onClick={() => { closeAllMenus(); navigate('/dashboard?mode=finder'); }}
          sx={{
            mb: 2,
            background: 'linear-gradient(135deg, #E65100 0%, #EA580C 100%)',
            color: '#FFFFFF',
            fontWeight: 800,
            fontSize: '0.84rem',
            textTransform: 'none',
          }}
        >
          {t('findBenefitsForMyBusiness')}
        </Button>

        <List disablePadding>
          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/'); closeAllMenus(); }}>
              <ListItemText primary={t('home')} primaryTypographyProps={{ fontWeight: 700, color: '#8B0000' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/ministry'); closeAllMenus(); }}>
              <ListItemText primary={t('ministry')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/dashboard'); closeAllMenus(); }}>
              <ListItemText primary={t('schemesAndBenefits')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/resources'); closeAllMenus(); }}>
              <ListItemText primary={t('resources')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/updates'); closeAllMenus(); }}>
              <ListItemText primary={t('updates')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/support'); closeAllMenus(); }}>
              <ListItemText primary={t('support')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
        </List>
      </Drawer>


      {/* ─── MAIN CONTENT ─── */}
      <Box component="main" sx={{ flex: 1 }}>
        <Outlet />
      </Box>

      {/* ─── MINIMAL CLEAN FOOTER (For dashboard routes only) ─── */}
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
                  onClick={() => navigate('/ministry')}
                  sx={{ color: '#475569', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#0F2E59' } }}
                >
                  {t('aboutMinistry')}
                </Typography>
                <Typography
                  component="a"
                  onClick={() => navigate('/support?tab=helpdesk')}
                  sx={{ color: '#475569', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#0F2E59' } }}
                >
                  {t('contactMinistry')}
                </Typography>
                <Typography
                  component="a"
                  onClick={() => navigate('/resources?tab=guidelines')}
                  sx={{ color: '#475569', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#0F2E59' } }}
                >
                  {t('schemeGuidelines')}
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
