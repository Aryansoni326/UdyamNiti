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

  // Interactive Content Modals
  const [modalOpen, setModalOpen] = useState<string | null>(null)

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

  const openModal = (id: string) => {
    closeAllMenus()
    setModalOpen(id)
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
                  width: 42,
                  height: 42,
                  borderRadius: '10px',
                  bgcolor: '#0F2E59',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 12px rgba(15, 46, 89, 0.25)',
                }}
              >
                <PolicyIcon sx={{ color: '#FFFFFF', fontSize: 26 }} />
              </Box>
              <Box>
                <Typography
                  variant="h6"
                  sx={{
                    fontFamily: tokens.font.heading,
                    fontWeight: 800,
                    color: '#0F2E59',
                    fontSize: { xs: '1.25rem', sm: '1.4rem' },
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

            {/* Top Right: Language Selector & Auth Buttons */}
            <Stack direction="row" spacing={1.5} alignItems="center">
              {/* Language Selector (EN / HI / GU) with Official GoI Bilingual Icon */}
              <Button
                id="language-selector-button"
                onClick={(e) => setLangMenuAnchor(e.currentTarget)}
                variant="outlined"
                size="small"
                startIcon={
                  <Box
                    component="img"
                    src={langIconImg}
                    alt="Language Preference"
                    sx={{
                      height: 22,
                      width: 'auto',
                      display: 'inline-block',
                      objectFit: 'contain',
                      mr: 0.3,
                    }}
                  />
                }
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
                ) : (
                  <Button
                    variant="contained"
                    onClick={() => navigate('/register')}
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
                    <Avatar sx={{ width: 32, height: 32, bgcolor: '#0F2E59', fontSize: '0.8rem', fontWeight: 700 }}>
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
                {[
                  { id: 'ministry_about', label: t('aboutMinistry'), icon: <InfoOutlinedIcon fontSize="small" sx={{ color: '#0F2E59' }} /> },
                  { id: 'ministry_vision', label: t('visionMission'), icon: <TrendingUpIcon fontSize="small" sx={{ color: '#059669' }} /> },
                  { id: 'ministry_leadership', label: t('leadership'), icon: <GroupIcon fontSize="small" sx={{ color: '#2563EB' }} /> },
                  { id: 'ministry_divisions', label: t('divisions'), icon: <BusinessCenterIcon fontSize="small" sx={{ color: '#7C3AED' }} /> },
                  { id: 'ministry_organisations', label: t('organisations'), icon: <AccountBalanceIcon fontSize="small" sx={{ color: '#D97706' }} /> },
                  { id: 'ministry_roles', label: t('rolesAndResponsibilities'), icon: <AssessmentIcon fontSize="small" sx={{ color: '#0891B2' }} /> },
                  { id: 'ministry_overview', label: t('msmeOverview'), icon: <ArticleIcon fontSize="small" sx={{ color: '#DC2626' }} /> },
                  { id: 'ministry_directory', label: t('ministryDirectory'), icon: <ContactPhoneIcon fontSize="small" sx={{ color: '#4B5563' }} /> },
                ].map((item, idx) => (
                  <MenuItem key={item.id} onClick={() => openModal(item.id)} sx={{ py: 1.1, px: 2 }}>
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
                    minWidth: 280,
                    borderRadius: '10px',
                    boxShadow: '0 10px 30px rgba(15, 23, 42, 0.14)',
                    border: '1px solid #E2E8F0',
                    py: 1,
                  },
                }}
              >
                <MenuItem onClick={() => openModal('resources_guidelines')} sx={{ py: 1.2, px: 2, bgcolor: '#FEF2F2' }}>
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
                  { id: 'resources_acts', label: t('actsAndRules') },
                  { id: 'resources_policies', label: t('policies') },
                  { id: 'resources_notifications', label: t('notifications') },
                  { id: 'resources_circulars', label: t('circularsAndOrders') },
                  { id: 'resources_reports', label: t('reports') },
                  { id: 'resources_publications', label: t('publications') },
                  { id: 'resources_forms', label: t('formsAndTemplates') },
                  { id: 'resources_faqs', label: t('faqs') },
                ].map((item) => (
                  <MenuItem key={item.id} onClick={() => openModal(item.id)} sx={{ py: 0.9, px: 2 }}>
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
                {[
                  { id: 'updates_whats_new', label: t('whatsNew') },
                  { id: 'updates_announcements', label: t('announcements') },
                  { id: 'updates_scheme_updates', label: t('schemeUpdates') },
                  { id: 'updates_events', label: t('events') },
                  { id: 'updates_press', label: t('pressReleases') },
                  { id: 'updates_success', label: t('successStories') },
                  { id: 'updates_photos', label: t('photoGallery') },
                  { id: 'updates_videos', label: t('videoGallery') },
                ].map((item) => (
                  <MenuItem key={item.id} onClick={() => openModal(item.id)} sx={{ py: 0.9, px: 2 }}>
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
                    minWidth: 260,
                    borderRadius: '10px',
                    boxShadow: '0 10px 30px rgba(15, 23, 42, 0.14)',
                    border: '1px solid #E2E8F0',
                    py: 1,
                  },
                }}
              >
                {[
                  { id: 'support_help_centre', label: t('helpCentre'), icon: <HelpOutlineIcon fontSize="small" sx={{ color: '#0284C7' }} /> },
                  { id: 'support_contact', label: t('contactMinistry'), icon: <PhoneInTalkOutlinedIcon fontSize="small" sx={{ color: '#059669' }} /> },
                  { id: 'ministry_directory', label: t('ministryDirectory'), icon: <ContactPhoneIcon fontSize="small" sx={{ color: '#4B5563' }} /> },
                  { id: 'support_grievance', label: t('grievanceSupport'), icon: <GavelOutlinedIcon fontSize="small" sx={{ color: '#7C3AED' }} /> },
                  { id: 'resources_faqs', label: t('frequentlyAskedQuestions'), icon: <ArticleIcon fontSize="small" sx={{ color: '#D97706' }} /> },
                  { id: 'support_application_help', label: t('applicationHelp'), icon: <SupportAgentIcon fontSize="small" sx={{ color: '#2563EB' }} /> },
                  { id: 'support_feedback', label: t('feedback'), icon: <InfoOutlinedIcon fontSize="small" sx={{ color: '#64748B' }} /> },
                ].map((item) => (
                  <MenuItem key={item.id} onClick={() => openModal(item.id)} sx={{ py: 0.9, px: 2 }}>
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
            <ListItemButton onClick={() => openModal('ministry_about')}>
              <ListItemText primary={t('ministry')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => { navigate('/dashboard'); closeAllMenus(); }}>
              <ListItemText primary={t('schemesAndBenefits')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('resources_guidelines')}>
              <ListItemText primary={t('resources')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('updates_whats_new')}>
              <ListItemText primary={t('updates')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton onClick={() => openModal('support_contact')}>
              <ListItemText primary={t('support')} primaryTypographyProps={{ fontWeight: 700, color: '#1E293B' }} />
            </ListItemButton>
          </ListItem>
        </List>
      </Drawer>

      {/* ─── 5. RICH INTERACTIVE MODALS FOR GOVERNMENT INFORMATION ARCHITECTURE ─── */}

      {/* MODAL: About Ministry */}
      <Dialog open={modalOpen === 'ministry_about'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          About the Ministry of Micro, Small & Medium Enterprises (M/o MSME)
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body1" sx={{ color: '#1E293B', mb: 2, lineHeight: 1.7, fontWeight: 500 }}>
            The Ministry of Micro, Small and Medium Enterprises develops policies, programmes and support systems that help Indian MSMEs start, grow, access finance, adopt technology, develop skills and reach markets.
          </Typography>
          <Paper sx={{ p: 2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', mb: 2 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 0.5 }}>
              Institutional Evolution & History
            </Typography>
            <Typography variant="body2" sx={{ color: '#475569', lineHeight: 1.6 }}>
              The Ministry was established in 2007 through the historic merger of the erstwhile Ministry of Small Scale Industries and the Ministry of Agro and Rural Industries. Under the MSMED Act, 2006, it functions as the apex central body coordinating with State Governments, financial institutions, and autonomous statutory boards.
            </Typography>
          </Paper>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Paper sx={{ p: 2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#059669', mb: 0.5 }}>
                  Role & Core Functions
                </Typography>
                <Typography variant="body2" sx={{ color: '#475569' }}>
                  • Facilitating institutional credit & collateral guarantees<br />
                  • Fostering technology upgrades & zero-defect manufacturing (ZED)<br />
                  • Developing industrial infrastructure & common facility centers<br />
                  • Skill training and entrepreneurship incubation
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Paper sx={{ p: 2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#2563EB', mb: 0.5 }}>
                  State Government Co-operation
                </Typography>
                <Typography variant="body2" sx={{ color: '#475569' }}>
                  The Ministry actively partners with State Directorates of Industries (such as Gujarat Industries and Mines Dept) to co-fund state industrial parks, cluster infrastructure, and export facilitation corridors.
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

      {/* MODAL: Vision, Mission & Objectives */}
      <Dialog open={modalOpen === 'ministry_vision'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#059669', color: '#FFFFFF', fontWeight: 800 }}>
          Vision, Mission & National Objectives
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Grid container spacing={2.5}>
            <Grid item xs={12}>
              <Paper sx={{ p: 2.5, bgcolor: '#ECFDF5', border: '1px solid #A7F3D0' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#065F46', mb: 0.5 }}>
                  VISION
                </Typography>
                <Typography variant="body1" sx={{ color: '#047857', fontWeight: 600 }}>
                  Empowered, globally competitive, resilient, and sustainable Micro, Small and Medium Enterprises across India.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2.5, bgcolor: '#EFF6FF', border: '1px solid #BFDBFE' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#1D4ED8', mb: 0.5 }}>
                  MISSION
                </Typography>
                <Typography variant="body1" sx={{ color: '#1E40AF' }}>
                  Help MSMEs seamlessly access real-time information, statutory schemes, collateral-free credit, modern infrastructure, and government support systems.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                  CORE STRATEGIC OBJECTIVES
                </Typography>
                <Grid container spacing={1.5}>
                  {[
                    'Credit access & collateral guarantees (CGTMSE)',
                    'Technology adoption & modernization (ZED / CITUS)',
                    'Skill development & entrepreneurship (ESDP)',
                    'Domestic & international market access (PMS / IC)',
                    'Cluster infrastructure & common facility centres (CDP / SFURTI)',
                    'Quality improvement, testing & green manufacturing',
                    'Employment generation through margin money (PMEGP)',
                  ].map((obj, i) => (
                    <Grid item xs={12} sm={6} key={i}>
                      <Typography variant="body2" sx={{ color: '#334155', display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CheckCircleIcon sx={{ color: '#059669', fontSize: 16 }} />
                        {obj}
                      </Typography>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC' }}>
          <Button onClick={() => setModalOpen(null)} variant="contained" sx={{ bgcolor: '#059669' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* MODAL: Leadership */}
      <Dialog open={modalOpen === 'ministry_leadership'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Ministry Leadership • Political & Administrative
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mb: 2 }}>
            Information maintained dynamically from official Government of India records:
          </Typography>
          <Grid container spacing={2.5}>
            <Grid item xs={12} sm={6}>
              <Card sx={{ border: '1px solid #E2E8F0', height: '100%' }}>
                <Box sx={{ p: 2.5, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
                  <Chip label="Union Cabinet Minister" size="small" sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 700, mb: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                    Shri Jitan Ram Manjhi
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#64748B', fontWeight: 600 }}>
                    Hon'ble Minister of Micro, Small and Medium Enterprises
                  </Typography>
                </Box>
                <CardContent sx={{ p: 2 }}>
                  <Typography variant="body2" sx={{ color: '#475569' }}>
                    Oversees national MSME policy directives, budget appropriations, and high-level inter-ministerial harmonization.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Card sx={{ border: '1px solid #E2E8F0', height: '100%' }}>
                <Box sx={{ p: 2.5, bgcolor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
                  <Chip label="Minister of State" size="small" sx={{ bgcolor: '#059669', color: '#FFFFFF', fontWeight: 700, mb: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                    Sushri Shobha Karandlaje
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#64748B', fontWeight: 600 }}>
                    Hon'ble Minister of State for MSME
                  </Typography>
                </Box>
                <CardContent sx={{ p: 2 }}>
                  <Typography variant="body2" sx={{ color: '#475569' }}>
                    Assists in operational program delivery, cluster outreach, women & SC/ST entrepreneur initiatives.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                  ADMINISTRATIVE LEADERSHIP
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: '#1E293B' }}>Secretary (MSME)</Typography>
                    <Typography variant="caption" sx={{ color: '#64748B' }}>Administrative Head of the Ministry</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: '#1E293B' }}>Development Commissioner</Typography>
                    <Typography variant="caption" sx={{ color: '#64748B' }}>Head of Office of DC-MSME</Typography>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: '#1E293B' }}>Joint Secretaries & Directors</Typography>
                    <Typography variant="caption" sx={{ color: '#64748B' }}>Heading Scheme & Policy Desks</Typography>
                  </Grid>
                </Grid>
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

      {/* MODAL: Organisations */}
      <Dialog open={modalOpen === 'ministry_organisations'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Organisations in the Ministry Ecosystem
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body2" sx={{ color: '#475569', mb: 2.5 }}>
            The Ministry functions through a coordinated network of specialized statutory boards, public sector undertakings, and autonomous training institutes:
          </Typography>
          <Grid container spacing={2}>
            {[
              { name: 'Office of Development Commissioner (DC-MSME)', role: 'Apex field organisation implementing CDP, ESDP, and technology center networks across states.', website: 'dcmsme.gov.in' },
              { name: 'National Small Industries Corporation (NSIC)', role: 'Facilitates raw material distribution, credit facilitation, and marketing support under NSSH.', website: 'nsic.co.in' },
              { name: 'Khadi & Village Industries Commission (KVIC)', role: 'National implementing agency for PMEGP margin money subsidy, rural employment & khadi development.', website: 'kvic.gov.in' },
              { name: 'Coir Board', role: 'Statutory body administering Coir Vikas Yojana (CVY), export trade fairs, and modernized coir fiber spinning.', website: 'coirboard.gov.in' },
              { name: 'National Institute for MSME (ni-msme)', role: 'Premier training institute delivering capacity building, research, and cluster mentoring for enterprises.', website: 'nimsme.org' },
              { name: 'Mahatma Gandhi Institute for Rural Industrialization (MGIRI)', role: 'R&D organization accelerating rural technology, solar pottery, and bio-processing equipment.', website: 'mgiri.org' },
            ].map((org, i) => (
              <Grid item xs={12} sm={6} key={i}>
                <Paper sx={{ p: 2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', height: '100%' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 0.5 }}>
                    {org.name}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#475569', fontSize: '0.84rem', mb: 1 }}>
                    {org.role}
                  </Typography>
                  <Chip label={org.website} size="small" variant="outlined" sx={{ fontSize: '0.72rem', color: '#2563EB', borderColor: '#BFDBFE' }} />
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

      {/* MODAL: MSME Overview */}
      <Dialog open={modalOpen === 'ministry_overview'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          MSME Classification Criteria & Statutory Overview
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body1" sx={{ color: '#1E293B', mb: 2, lineHeight: 1.6 }}>
            Under the revised composite criteria effective from 1st July 2020, enterprises are classified based on both Investment in Plant & Machinery AND Annual Turnover:
          </Typography>
          <Grid container spacing={2}>
            {[
              { type: 'Micro Enterprise', inv: 'Investment &le; ₹1 Crore', turn: 'Turnover &le; ₹5 Crore', color: '#059669', badge: 'Tier 1' },
              { type: 'Small Enterprise', inv: 'Investment &le; ₹10 Crore', turn: 'Turnover &le; ₹50 Crore', color: '#2563EB', badge: 'Tier 2' },
              { type: 'Medium Enterprise', inv: 'Investment &le; ₹50 Crore', turn: 'Turnover &le; ₹250 Crore', color: '#7C3AED', badge: 'Tier 3' },
            ].map((cls, i) => (
              <Grid item xs={12} md={4} key={i}>
                <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', textAlign: 'center' }}>
                  <Chip label={cls.badge} size="small" sx={{ bgcolor: cls.color, color: '#FFFFFF', fontWeight: 700, mb: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                    {cls.type}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#1E293B', fontWeight: 600 }}>
                    {cls.inv}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', mt: 0.5 }}>
                    {cls.turn}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
          <Paper sx={{ p: 2, bgcolor: '#FEF3C7', border: '1px solid #FDE68A', mt: 2.5 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#92400E', mb: 0.5 }}>
              Udyam Registration Note
            </Typography>
            <Typography variant="body2" sx={{ color: '#78350F' }}>
              Udyam Registration is a completely paperless, free online registration process based on self-declaration linked with Aadhaar, PAN, and GSTIN.
            </Typography>
          </Paper>
        </DialogContent>
        <DialogActions sx={{ p: 2, bgcolor: '#F8FAFC' }}>
          <Button onClick={() => setModalOpen(null)} variant="contained" sx={{ bgcolor: '#0F2E59' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* MODAL: Scheme Guidelines (Official Uploaded PDFs) with "Ask AI About This Document" */}
      <Dialog open={modalOpen === 'resources_guidelines'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Official Scheme Guidelines & Verified PDF Documents
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Typography variant="body2" sx={{ color: '#475569', mb: 2 }}>
            These 11 statutory guideline documents form the authoritative foundation of UdyamNiti's reasoning engine. You can view each PDF or use the AI Assistant to interpret rules.
          </Typography>
          <Grid container spacing={1.5}>
            {[
              { name: 'Prime Minister Employment Generation Programme (PMEGP)', file: 'pmegp scheme.pdf', ministry: 'M/o MSME / KVIC' },
              { name: 'Special Credit Guarantee Scheme – Export Credit (EPM)', file: 'Circular 257 - CGS for Export credit merged.pdf', ministry: 'CGTMSE & DGFT' },
              { name: 'Assistance for Developing SER Textile and MSME Park 2025-26', file: '1.msme.pdf', ministry: 'Govt of Gujarat (IMD)' },
              { name: 'Scheme of Fund for Regeneration of Traditional Industries (SFURTI)', file: 'SFURTI_NEW_GUIDELINES.pdf', ministry: 'M/o MSME' },
              { name: 'MSME Sustainable (ZED) Certification Scheme (Phase-II)', file: 'ZED_Guidance_Document_NIC_Division_24 & 27.pdf', ministry: 'QCI / MSME' },
              { name: 'Credit Guarantee Scheme for Factoring on TReDS (Circular 262)', file: 'TReDS Cicular 262.pdf', ministry: 'RBI / CGTMSE' },
              { name: 'International Cooperation (IC) Scheme Guidelines (MDA & CBFTE)', file: 'Final and approved IC Scheme Guidelines-2021.pdf', ministry: 'M/o MSME' },
              { name: 'Micro and Small Enterprises Cluster Development (MSE-CDP)', file: 'msme-cdp.pdf', ministry: 'O/o DC MSME' },
              { name: 'Coir Vikas Yojana (CVY) Assistance Guidelines', file: 'cvy.schemes.pdf', ministry: 'Coir Board' },
              { name: 'National SC-ST Hub (NSSH) Special Capital Subsidy (SCLCSS)', file: 'NSSH_Guidelines_Sub_scheme_0 & 1.pdf', ministry: 'NSIC / MSME' },
              { name: 'Procurement and Marketing Support (PMS) Scheme', file: 'OM & PMS Scheme Guidelines.pdf', ministry: 'O/o DC MSME' },
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
                        Source: {b.file} • Authority: {b.ministry}
                      </Typography>
                    </Box>
                  </Stack>
                  <Stack direction="row" spacing={1}>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<AutoAwesomeIcon sx={{ fontSize: 14, color: '#D97706' }} />}
                      onClick={() => {
                        setModalOpen(null)
                        navigate(`/dashboard?mode=ai&doc=${encodeURIComponent(b.file)}`)
                      }}
                      sx={{ textTransform: 'none', borderColor: '#CBD5E1', color: '#0F2E59', fontWeight: 700 }}
                    >
                      Ask AI
                    </Button>
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<DownloadIcon sx={{ fontSize: 14 }} />}
                      onClick={() => {
                        toast.success(`Accessing official copy: ${b.file}`)
                      }}
                      sx={{ textTransform: 'none', bgcolor: '#0F2E59', fontWeight: 700 }}
                    >
                      PDF
                    </Button>
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

      {/* MODAL: Contact Ministry / Directory */}
      <Dialog open={modalOpen === 'support_contact' || modalOpen === 'ministry_directory'} onClose={() => setModalOpen(null)} maxWidth="md" fullWidth>
        <DialogTitle sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 800 }}>
          Ministry Contacts & Support Directory
        </DialogTitle>
        <DialogContent sx={{ p: 3, mt: 1 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PhoneInTalkOutlinedIcon sx={{ color: '#059669' }} /> Central MSME Helpdesk
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
                  onClick={() => openModal('ministry_about')}
                  sx={{ color: '#475569', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#0F2E59' } }}
                >
                  {t('aboutMinistry')}
                </Typography>
                <Typography
                  component="a"
                  onClick={() => openModal('support_contact')}
                  sx={{ color: '#475569', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#0F2E59' } }}
                >
                  {t('contactMinistry')}
                </Typography>
                <Typography
                  component="a"
                  onClick={() => openModal('resources_guidelines')}
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
