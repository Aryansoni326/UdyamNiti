import React, { useState, useEffect } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  AppBar,
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
  alpha,
  Container,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  ListItemIcon,
  Chip,
} from '@mui/material'
import MenuIcon from '@mui/icons-material/Menu'
import CloseIcon from '@mui/icons-material/Close'
import PolicyIcon from '@mui/icons-material/Policy'
import LogoutIcon from '@mui/icons-material/Logout'
import GridViewIcon from '@mui/icons-material/GridView'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord'
import { tokens } from '../theme/tokens'
import { toast } from 'sonner'

export const AppShell: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(null)
  const [activeNav, setActiveNav] = useState<string>('services')

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

  // Track active section on scroll for landing page
  useEffect(() => {
    if (location.pathname !== '/') return

    const handleScroll = () => {
      const sections = ['services', 'benefits', 'faq']
      const scrollPos = window.scrollY + 200

      for (const sec of sections) {
        const el = document.getElementById(sec)
        if (el) {
          const top = el.offsetTop
          const height = el.offsetHeight
          if (scrollPos >= top && scrollPos < top + height) {
            setActiveNav(sec)
            break
          }
        }
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [location.pathname])

  const handleLogout = () => {
    localStorage.removeItem('udyamniti_user')
    setCurrentUser(null)
    setUserMenuAnchor(null)
    toast.info('Signed out successfully.')
    navigate('/')
  }

  const isLandingPage = location.pathname === '/'

  const scrollToSection = (sectionId: string) => {
    setMobileOpen(false)
    setActiveNav(sectionId)
    if (location.pathname !== '/') {
      navigate(`/#${sectionId}`)
      setTimeout(() => {
        const el = document.getElementById(sectionId)
        if (el) el.scrollIntoView({ behavior: 'smooth' })
      }, 150)
    } else {
      const el = document.getElementById(sectionId)
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#0A0F1E' }}>
      {/* ─── WORLD-CLASS SAAS FLOATING GLASS NAVBAR ─── */}
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          bgcolor: 'rgba(10, 15, 30, 0.78)',
          backdropFilter: 'blur(20px) saturate(180%)',
          WebkitBackdropFilter: 'blur(20px) saturate(180%)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.07)',
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3 } }}>
          <Toolbar
            disableGutters
            sx={{
              height: 64,
              minHeight: '64px !important',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            {/* ─── BRAND LOGO & SAAS BADGE ─── */}
            <Box
              onClick={() => navigate('/')}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                cursor: 'pointer',
                userSelect: 'none',
              }}
            >
              <Box
                sx={{
                  width: 34,
                  height: 34,
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 50%, #3B82F6 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: 'inset 0 1px 1px rgba(255, 255, 255, 0.4), 0 2px 10px rgba(99, 102, 241, 0.35)',
                  transition: 'transform 0.2s',
                  '&:hover': { transform: 'scale(1.04)' },
                }}
              >
                <PolicyIcon sx={{ color: '#FFFFFF', fontSize: 20 }} />
              </Box>

              <Stack direction="row" alignItems="center" spacing={1}>
                <Typography
                  variant="h6"
                  component="span"
                  sx={{
                    fontFamily: tokens.font.heading,
                    fontWeight: 800,
                    fontSize: '1.25rem',
                    letterSpacing: '-0.025em',
                    color: '#FFFFFF',
                    lineHeight: 1,
                  }}
                >
                  Udyam<Box component="span" sx={{ color: '#818CF8' }}>Niti</Box>
                </Typography>

                <Chip
                  label="GovTech AI"
                  size="small"
                  sx={{
                    height: 19,
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    letterSpacing: '0.04em',
                    fontFamily: tokens.font.mono,
                    bgcolor: 'rgba(99, 102, 241, 0.12)',
                    color: '#A5B4FC',
                    border: '1px solid rgba(99, 102, 241, 0.28)',
                    display: { xs: 'none', sm: 'inline-flex' },
                  }}
                />
              </Stack>
            </Box>

            {/* ─── CENTERED SAAS PILL NAVIGATION (SERVICES, BENEFITS, FAQS ONLY) ─── */}
            {isLandingPage ? (
              <Box
                sx={{
                  display: { xs: 'none', md: 'flex' },
                  alignItems: 'center',
                  bgcolor: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '9999px',
                  p: '3px 6px',
                  boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.04)',
                }}
              >
                <Box
                  component="button"
                  onClick={() => scrollToSection('services')}
                  sx={{
                    background: activeNav === 'services' ? 'rgba(99, 102, 241, 0.18)' : 'transparent',
                    border: 'none',
                    borderRadius: '9999px',
                    px: 2,
                    py: 0.7,
                    color: activeNav === 'services' ? '#FFFFFF' : '#94A3B8',
                    fontWeight: activeNav === 'services' ? 600 : 500,
                    fontSize: '0.84rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.6,
                    '&:hover': {
                      color: '#FFFFFF',
                      background: 'rgba(255, 255, 255, 0.08)',
                    },
                  }}
                >
                  Services
                </Box>

                <Box
                  component="button"
                  onClick={() => scrollToSection('benefits')}
                  sx={{
                    background: activeNav === 'benefits' ? 'rgba(99, 102, 241, 0.18)' : 'transparent',
                    border: 'none',
                    borderRadius: '9999px',
                    px: 2,
                    py: 0.7,
                    color: activeNav === 'benefits' ? '#FFFFFF' : '#94A3B8',
                    fontWeight: activeNav === 'benefits' ? 600 : 500,
                    fontSize: '0.84rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.6,
                    '&:hover': {
                      color: '#FFFFFF',
                      background: 'rgba(255, 255, 255, 0.08)',
                    },
                  }}
                >
                  Benefits
                </Box>

                <Box
                  component="button"
                  onClick={() => scrollToSection('faq')}
                  sx={{
                    background: activeNav === 'faq' ? 'rgba(99, 102, 241, 0.18)' : 'transparent',
                    border: 'none',
                    borderRadius: '9999px',
                    px: 2,
                    py: 0.7,
                    color: activeNav === 'faq' ? '#FFFFFF' : '#94A3B8',
                    fontWeight: activeNav === 'faq' ? 600 : 500,
                    fontSize: '0.84rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 0.6,
                    '&:hover': {
                      color: '#FFFFFF',
                      background: 'rgba(255, 255, 255, 0.08)',
                    },
                  }}
                >
                  FAQs
                </Box>
              </Box>
            ) : (
              <Stack
                direction="row"
                spacing={1}
                alignItems="center"
                sx={{
                  display: { xs: 'none', md: 'flex' },
                  bgcolor: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '9999px',
                  p: '3px 6px',
                }}
              >
                <Button
                  size="small"
                  onClick={() => navigate('/')}
                  sx={{
                    color: '#94A3B8',
                    fontSize: '0.82rem',
                    textTransform: 'none',
                    fontWeight: 500,
                    borderRadius: '9999px',
                    px: 1.8,
                    py: 0.5,
                    '&:hover': { color: '#FFFFFF', bgcolor: 'rgba(255, 255, 255, 0.08)' },
                  }}
                >
                  Landing
                </Button>
                <Button
                  size="small"
                  onClick={() => navigate('/dashboard')}
                  sx={{
                    color: location.pathname === '/dashboard' ? '#FFFFFF' : '#94A3B8',
                    bgcolor: location.pathname === '/dashboard' ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                    fontSize: '0.82rem',
                    textTransform: 'none',
                    fontWeight: 600,
                    borderRadius: '9999px',
                    px: 1.8,
                    py: 0.5,
                    '&:hover': { color: '#FFFFFF', bgcolor: 'rgba(255, 255, 255, 0.08)' },
                  }}
                >
                  Schemes Dashboard
                </Button>
                <Button
                  size="small"
                  onClick={() => navigate('/monitor')}
                  sx={{
                    color: location.pathname === '/monitor' ? '#FFFFFF' : '#94A3B8',
                    bgcolor: location.pathname === '/monitor' ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                    fontSize: '0.82rem',
                    textTransform: 'none',
                    fontWeight: 500,
                    borderRadius: '9999px',
                    px: 1.8,
                    py: 0.5,
                    '&:hover': { color: '#FFFFFF', bgcolor: 'rgba(255, 255, 255, 0.08)' },
                  }}
                >
                  Gazette Radar
                </Button>
              </Stack>
            )}

            {/* ─── RIGHT SECTION: STATUS PILL + AUTH BUTTONS ─── */}
            <Stack direction="row" spacing={1.8} alignItems="center">
              {/* SaaS Live Trust Indicator */}
              <Box
                sx={{
                  display: { xs: 'none', lg: 'flex' },
                  alignItems: 'center',
                  gap: 0.9,
                  px: 1.4,
                  py: 0.5,
                  borderRadius: '9999px',
                  bgcolor: 'rgba(16, 185, 129, 0.08)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                }}
              >
                <FiberManualRecordIcon
                  sx={{
                    color: '#10B981',
                    fontSize: 10,
                    filter: 'drop-shadow(0 0 5px #10B981)',
                  }}
                />
                <Typography
                  variant="caption"
                  sx={{
                    color: '#6EE7B7',
                    fontWeight: 600,
                    fontSize: '0.72rem',
                    letterSpacing: '0.02em',
                  }}
                >
                  Gazette Live
                </Typography>
              </Box>

              {/* Hairline vertical divider */}
              <Box
                sx={{
                  display: { xs: 'none', lg: 'block' },
                  width: '1px',
                  height: 18,
                  bgcolor: 'rgba(255, 255, 255, 0.12)',
                }}
              />

              {currentUser ? (
                /* Authenticated State */
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <Button
                    onClick={() => navigate('/dashboard')}
                    variant="contained"
                    size="small"
                    startIcon={<GridViewIcon sx={{ fontSize: 16 }} />}
                    sx={{
                      background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                      color: '#FFFFFF',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      borderRadius: '8px',
                      textTransform: 'none',
                      px: 2,
                      py: 0.65,
                      boxShadow: '0 2px 10px rgba(99, 102, 241, 0.3)',
                      '&:hover': { background: 'linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)' },
                    }}
                  >
                    Dashboard
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
                      bgcolor: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.2s',
                      '&:hover': {
                        borderColor: 'rgba(255, 255, 255, 0.25)',
                        bgcolor: 'rgba(255, 255, 255, 0.08)',
                      },
                    }}
                  >
                    <Avatar
                      sx={{
                        width: 28,
                        height: 28,
                        bgcolor: '#6366F1',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                      }}
                    >
                      {currentUser.name ? currentUser.name.charAt(0).toUpperCase() : 'U'}
                    </Avatar>
                    <Typography
                      variant="caption"
                      sx={{
                        color: '#F1F5F9',
                        fontWeight: 600,
                        fontSize: '0.8rem',
                        display: { xs: 'none', sm: 'block' },
                        maxWidth: 130,
                      }}
                      noWrap
                    >
                      {currentUser.name || 'Enterprise'}
                    </Typography>
                  </Box>

                  <Menu
                    anchorEl={userMenuAnchor}
                    open={Boolean(userMenuAnchor)}
                    onClose={() => setUserMenuAnchor(null)}
                    PaperProps={{
                      sx: {
                        mt: 1.2,
                        bgcolor: '#1A2235',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: '12px',
                        minWidth: 200,
                        boxShadow: '0 12px 32px rgba(0,0,0,0.5)',
                      },
                    }}
                  >
                    <Box sx={{ px: 2, py: 1.2 }}>
                      <Typography variant="caption" sx={{ color: '#94A3B8', display: 'block', fontSize: '0.72rem' }}>
                        Signed in as
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#FFFFFF', fontWeight: 700, fontSize: '0.85rem' }} noWrap>
                        {currentUser.email || 'director@msme.in'}
                      </Typography>
                    </Box>
                    <Divider sx={{ my: 0.5, borderColor: 'rgba(255, 255, 255, 0.08)' }} />
                    <MenuItem
                      onClick={() => {
                        navigate('/dashboard')
                        setUserMenuAnchor(null)
                      }}
                      sx={{ color: '#F1F5F9', fontSize: '0.85rem', py: 1 }}
                    >
                      <ListItemIcon sx={{ color: '#818CF8', minWidth: 28 }}>
                        <GridViewIcon fontSize="small" />
                      </ListItemIcon>
                      Schemes Dashboard
                    </MenuItem>
                    <Divider sx={{ my: 0.5, borderColor: 'rgba(255, 255, 255, 0.08)' }} />
                    <MenuItem
                      onClick={handleLogout}
                      sx={{ color: '#F87171', fontSize: '0.85rem', py: 1 }}
                    >
                      <ListItemIcon sx={{ color: '#F87171', minWidth: 28 }}>
                        <LogoutIcon fontSize="small" />
                      </ListItemIcon>
                      Sign Out
                    </MenuItem>
                  </Menu>
                </Stack>
              ) : (
                /* Unauthenticated State: Sign In & Register */
                <Stack direction="row" spacing={1.2} alignItems="center">
                  <Button
                    onClick={() => navigate('/login')}
                    sx={{
                      color: '#CBD5E1',
                      fontSize: '0.86rem',
                      fontWeight: 600,
                      textTransform: 'none',
                      px: 1.8,
                      py: 0.7,
                      borderRadius: '8px',
                      transition: 'all 0.15s ease',
                      '&:hover': {
                        color: '#FFFFFF',
                        bgcolor: 'rgba(255, 255, 255, 0.06)',
                      },
                    }}
                  >
                    Sign In
                  </Button>

                  <Button
                    variant="contained"
                    onClick={() => navigate('/register')}
                    endIcon={<ArrowForwardIcon sx={{ fontSize: '13px !important' }} />}
                    sx={{
                      background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                      color: '#FFFFFF',
                      fontSize: '0.86rem',
                      fontWeight: 600,
                      textTransform: 'none',
                      px: 2.2,
                      py: 0.75,
                      borderRadius: '8px',
                      boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.25), 0 4px 14px rgba(99, 102, 241, 0.35)',
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)',
                        boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.35), 0 6px 20px rgba(99, 102, 241, 0.5)',
                        transform: 'translateY(-1px)',
                      },
                    }}
                  >
                    Register
                  </Button>
                </Stack>
              )}

              {/* Mobile Menu Icon */}
              <IconButton
                onClick={() => setMobileOpen(!mobileOpen)}
                sx={{
                  display: { md: 'none' },
                  color: '#CBD5E1',
                  p: 0.8,
                  borderRadius: '8px',
                  bgcolor: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.1)' },
                }}
              >
                {mobileOpen ? <CloseIcon fontSize="small" /> : <MenuIcon fontSize="small" />}
              </IconButton>
            </Stack>
          </Toolbar>
        </Container>
      </AppBar>

      {/* ─── ULTRA-CLEAN MOBILE DRAWER ─── */}
      <Drawer
        anchor="right"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        PaperProps={{
          sx: {
            width: 280,
            bgcolor: '#0E1626',
            backgroundImage: 'radial-gradient(ellipse at 80% 0%, rgba(99, 102, 241, 0.18) 0%, transparent 70%)',
            borderLeft: '1px solid rgba(255, 255, 255, 0.1)',
            p: 2.5,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          },
        }}
      >
        <Box>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
            <Stack direction="row" alignItems="center" spacing={1.2}>
              <Box
                sx={{
                  width: 30,
                  height: 30,
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <PolicyIcon sx={{ color: '#FFFFFF', fontSize: 18 }} />
              </Box>
              <Typography variant="h6" sx={{ color: '#FFFFFF', fontWeight: 800, fontSize: '1.15rem' }}>
                Udyam<Box component="span" sx={{ color: '#818CF8' }}>Niti</Box>
              </Typography>
            </Stack>
            <IconButton size="small" onClick={() => setMobileOpen(false)} sx={{ color: '#94A3B8' }}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Stack>

          {/* Live Status inside mobile drawer */}
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 0.8,
              px: 1.2,
              py: 0.4,
              borderRadius: '9999px',
              bgcolor: 'rgba(16, 185, 129, 0.08)',
              border: '1px solid rgba(16, 185, 129, 0.2)',
              mb: 3,
            }}
          >
            <FiberManualRecordIcon sx={{ color: '#10B981', fontSize: 8 }} />
            <Typography variant="caption" sx={{ color: '#6EE7B7', fontWeight: 600, fontSize: '0.7rem' }}>
              Gazette Intelligence Active
            </Typography>
          </Box>

          <Typography variant="caption" sx={{ color: '#64748B', fontWeight: 700, letterSpacing: '0.05em', px: 1, mb: 1, display: 'block' }}>
            NAVIGATION
          </Typography>

          <List sx={{ p: 0 }}>
            {isLandingPage ? (
              <>
                <ListItem disablePadding sx={{ mb: 1 }}>
                  <ListItemButton
                    onClick={() => scrollToSection('services')}
                    sx={{
                      borderRadius: '8px',
                      color: activeNav === 'services' ? '#FFFFFF' : '#CBD5E1',
                      bgcolor: activeNav === 'services' ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 32, color: '#818CF8' }}>
                      <AutoAwesomeIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Services" primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: 600 }} />
                  </ListItemButton>
                </ListItem>

                <ListItem disablePadding sx={{ mb: 1 }}>
                  <ListItemButton
                    onClick={() => scrollToSection('benefits')}
                    sx={{
                      borderRadius: '8px',
                      color: activeNav === 'benefits' ? '#FFFFFF' : '#CBD5E1',
                      bgcolor: activeNav === 'benefits' ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 32, color: '#34D399' }}>
                      <VerifiedUserIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="Benefits" primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: 600 }} />
                  </ListItemButton>
                </ListItem>

                <ListItem disablePadding sx={{ mb: 1 }}>
                  <ListItemButton
                    onClick={() => scrollToSection('faq')}
                    sx={{
                      borderRadius: '8px',
                      color: activeNav === 'faq' ? '#FFFFFF' : '#CBD5E1',
                      bgcolor: activeNav === 'faq' ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 32, color: '#FBBF24' }}>
                      <HelpOutlineIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary="FAQs" primaryTypographyProps={{ fontSize: '0.9rem', fontWeight: 600 }} />
                  </ListItemButton>
                </ListItem>
              </>
            ) : (
              <>
                <ListItem disablePadding sx={{ mb: 1 }}>
                  <ListItemButton onClick={() => { navigate('/'); setMobileOpen(false) }} sx={{ borderRadius: '8px', color: '#E2E8F0' }}>
                    <ListItemText primary="Landing Page" />
                  </ListItemButton>
                </ListItem>
                <ListItem disablePadding sx={{ mb: 1 }}>
                  <ListItemButton onClick={() => { navigate('/dashboard'); setMobileOpen(false) }} sx={{ borderRadius: '8px', color: '#E2E8F0' }}>
                    <ListItemText primary="Schemes Dashboard" />
                  </ListItemButton>
                </ListItem>
              </>
            )}
          </List>
        </Box>

        {/* Bottom Drawer CTAs */}
        <Box sx={{ pt: 2, borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
          {currentUser ? (
            <Button
              fullWidth
              variant="outlined"
              onClick={handleLogout}
              sx={{ borderColor: '#EF4444', color: '#EF4444', textTransform: 'none', borderRadius: '8px' }}
            >
              Sign Out
            </Button>
          ) : (
            <Stack spacing={1.5}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => { navigate('/login'); setMobileOpen(false) }}
                sx={{
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  color: '#FFFFFF',
                  textTransform: 'none',
                  borderRadius: '8px',
                  fontWeight: 600,
                  py: 1,
                }}
              >
                Sign In
              </Button>
              <Button
                fullWidth
                variant="contained"
                onClick={() => { navigate('/register'); setMobileOpen(false) }}
                endIcon={<ArrowForwardIcon sx={{ fontSize: 14 }} />}
                sx={{
                  background: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)',
                  color: '#FFFFFF',
                  textTransform: 'none',
                  borderRadius: '8px',
                  fontWeight: 600,
                  py: 1,
                  boxShadow: '0 4px 14px rgba(99, 102, 241, 0.4)',
                }}
              >
                Register Enterprise
              </Button>
            </Stack>
          )}
        </Box>
      </Drawer>

      {/* ─── MAIN CONTENT ─── */}
      <Box component="main" sx={{ flex: 1 }}>
        <Outlet />
      </Box>

      {/* ─── MINIMAL CLEAN FOOTER ─── */}
      <Box
        component="footer"
        sx={{
          py: 4,
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          bgcolor: 'rgba(10, 15, 30, 0.95)',
        }}
      >
        <Container maxWidth="lg">
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            justifyContent="space-between"
            alignItems="center"
            spacing={2}
          >
            <Typography variant="body2" sx={{ color: '#94A3B8', fontSize: '0.85rem' }}>
              © {new Date().getFullYear()} UdyamNiti • Central & Gujarat Government MSME Scheme Intelligence
            </Typography>

            <Stack direction="row" spacing={3}>
              <Typography
                component="a"
                href="#services"
                onClick={(e) => { e.preventDefault(); scrollToSection('services') }}
                sx={{ color: '#94A3B8', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
              >
                Services
              </Typography>
              <Typography
                component="a"
                href="#benefits"
                onClick={(e) => { e.preventDefault(); scrollToSection('benefits') }}
                sx={{ color: '#94A3B8', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
              >
                Benefits
              </Typography>
              <Typography
                component="a"
                href="#faq"
                onClick={(e) => { e.preventDefault(); scrollToSection('faq') }}
                sx={{ color: '#94A3B8', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
              >
                FAQs
              </Typography>
              <Typography
                component="a"
                href="/login"
                onClick={(e) => { e.preventDefault(); navigate('/login') }}
                sx={{ color: '#94A3B8', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
              >
                Sign In
              </Typography>
              <Typography
                component="a"
                href="/register"
                onClick={(e) => { e.preventDefault(); navigate('/register') }}
                sx={{ color: '#94A3B8', fontSize: '0.82rem', textDecoration: 'none', cursor: 'pointer', '&:hover': { color: '#FFFFFF' } }}
              >
                Register
              </Typography>
            </Stack>
          </Stack>
        </Container>
      </Box>
    </Box>
  )
}

export default AppShell
