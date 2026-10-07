import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Box, AppBar, Toolbar, Typography, Button, Chip, IconButton, Tooltip } from '@mui/material'
import PolicyIcon from '@mui/icons-material/Policy'
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone'
import HomeIcon from '@mui/icons-material/Home'

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          bgcolor: 'rgba(10, 15, 30, 0.85)',
          backdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        <Toolbar sx={{ px: { xs: 2, md: 4 } }}>
          <Box
            sx={{ display: 'flex', alignItems: 'center', gap: 1.5, cursor: 'pointer', flex: 1 }}
            onClick={() => navigate('/')}
          >
            <PolicyIcon sx={{ color: 'primary.main', fontSize: 28 }} />
            <Typography
              variant="h6"
              sx={{
                fontFamily: 'Outfit, sans-serif',
                fontWeight: 800,
                background: 'linear-gradient(135deg, #6C63FF 0%, #10B981 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              UdyamNiti
            </Typography>
            <Chip
              label="Beta"
              size="small"
              sx={{
                bgcolor: 'rgba(108, 99, 255, 0.15)',
                color: 'primary.light',
                fontSize: '0.65rem',
                height: 18,
                fontWeight: 600,
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Tooltip title="Home">
              <IconButton
                size="small"
                onClick={() => navigate('/')}
                sx={{
                  color: location.pathname === '/' ? 'primary.main' : 'text.secondary',
                  '&:hover': { color: 'primary.light' },
                }}
                id="nav-home"
              >
                <HomeIcon />
              </IconButton>
            </Tooltip>
            <Button
              variant="text"
              size="small"
              startIcon={<NotificationsNoneIcon />}
              onClick={() => navigate('/monitor')}
              sx={{
                color: location.pathname === '/monitor' ? 'primary.light' : 'text.secondary',
                fontSize: '0.8rem',
                '&:hover': { color: 'text.primary' },
              }}
              id="nav-monitor"
            >
              Policy Updates
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Outlet />
    </Box>
  )
}
