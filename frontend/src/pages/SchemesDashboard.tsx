import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Box,
  Typography,
  TextField,
  Button,
  Stack,
  Card,
  CardContent,
  Chip,
  Grid,
  InputAdornment,
  MenuItem,
  CircularProgress,
  Divider,
  Paper,
  alpha,
  Tooltip,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import FilterListIcon from '@mui/icons-material/FilterList'
import CalendarTodayOutlinedIcon from '@mui/icons-material/CalendarTodayOutlined'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import StarIcon from '@mui/icons-material/Star'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import BusinessIcon from '@mui/icons-material/Business'
import ClearIcon from '@mui/icons-material/Clear'
import { tokens } from '../theme/tokens'
import { apiClient } from '../api/client'
import type { SchemeResult } from '../types'
import { toast } from 'sonner'

export const SchemesDashboard: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const initialQuery = searchParams.get('q') || searchParams.get('search') || ''

  const [searchQuery, setSearchQuery] = useState(initialQuery)
  const [activeSearch, setActiveSearch] = useState(initialQuery)
  const [levelFilter, setLevelFilter] = useState('all')
  const [supportFilter, setSupportFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')
  
  const [schemes, setSchemes] = useState<SchemeResult[]>([])
  const [loading, setLoading] = useState(true)
  const [ragLoading, setRagLoading] = useState(false)
  const [ragBestDeal, setRagBestDeal] = useState<any>(null)
  
  // Current user info from localStorage
  const user = JSON.parse(localStorage.getItem('udyamniti_user') || '{"name":"ABC Engineering Ltd.","category":"Small Enterprise","udyam":"UDYAM-GJ-01-0023456"}')

  // Load schemes from backend API
  const fetchSchemes = async (query = activeSearch) => {
    setLoading(true)
    try {
      const res = await apiClient.getSchemes({
        search: query || undefined,
        level: levelFilter !== 'all' ? levelFilter : undefined,
        support_type: supportFilter !== 'all' ? supportFilter : undefined,
        category: categoryFilter !== 'all' ? categoryFilter : undefined,
      })
      setSchemes(res.data.results || [])
    } catch (err) {
      console.error('Failed to load schemes:', err)
      toast.error('Could not connect to schemes database.')
    } finally {
      setLoading(false)
    }
  }

  // Trigger RAG recommendation
  const runRagRecommendation = async (query: string) => {
    if (!query) {
      setRagBestDeal(null)
      return
    }
    setRagLoading(true)
    try {
      const res = await apiClient.ragRecommend({
        query,
        sector: 'all',
        msme_type: 'small',
      })
      if (res.data && res.data.top_deal) {
        setRagBestDeal(res.data.top_deal)
      }
    } catch (err) {
      console.error('RAG recommendation error:', err)
    } finally {
      setRagLoading(false)
    }
  }

  useEffect(() => {
    fetchSchemes(activeSearch)
    if (activeSearch) {
      runRagRecommendation(activeSearch)
    }
  }, [activeSearch, levelFilter, supportFilter, categoryFilter])

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setActiveSearch(searchQuery)
    setSearchParams(searchQuery ? { search: searchQuery } : {})
    runRagRecommendation(searchQuery)
  }

  const handleQuickChipClick = (term: string) => {
    setSearchQuery(term)
    setActiveSearch(term)
    setSearchParams({ search: term })
    runRagRecommendation(term)
  }

  const handleClearSearch = () => {
    setSearchQuery('')
    setActiveSearch('')
    setSearchParams({})
    setRagBestDeal(null)
  }

  // Top highlight deal (either from RAG or the first priority best deal)
  const featuredDeal = ragBestDeal || schemes.find((s) => s.is_best_deal) || schemes[0]

  return (
    <Box sx={{ maxWidth: 1240, mx: 'auto', px: { xs: 2, sm: 3, md: 4 }, py: 3.5 }}>
      {/* Top Enterprise Context Ribbon */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          mb: 3.5,
          borderRadius: '12px',
          bgcolor: tokens.color.surface.elevated,
          border: `1px solid ${tokens.color.border.subtle}`,
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 2,
        }}
      >
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <Box
            sx={{
              width: 38,
              height: 38,
              borderRadius: '8px',
              bgcolor: alpha(tokens.color.violet[500], 0.15),
              color: tokens.color.violet[400],
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <BusinessIcon fontSize="small" />
          </Box>
          <Box>
            <Stack direction="row" alignItems="center" spacing={1}>
              <Typography variant="body2" sx={{ fontWeight: 700, color: tokens.color.slate[100] }}>
                {user.name}
              </Typography>
              <Chip
                label={user.category || 'Small Enterprise'}
                size="small"
                sx={{
                  bgcolor: alpha(tokens.color.violet[500], 0.12),
                  color: tokens.color.violet[300],
                  fontSize: '0.7rem',
                  height: 20,
                  fontWeight: 600,
                }}
              />
            </Stack>
            <Typography variant="caption" sx={{ color: tokens.color.slate[400] }}>
              Active Udyam: {user.udyam} • Central & Gujarat State Database Synced
            </Typography>
          </Box>
        </Stack>

        <Stack direction="row" spacing={1.5} alignItems="center">
          <Tooltip title="Government circulars and Gazette resolutions extracted with deterministic verification rules">
            <Chip
              icon={<VerifiedUserIcon sx={{ fontSize: '14px !important', color: `${tokens.color.emerald[400]} !important` }} />}
              label="Official PDF Database Active"
              size="small"
              sx={{
                bgcolor: alpha(tokens.color.emerald[500], 0.1),
                color: tokens.color.emerald[300],
                border: `1px solid ${alpha(tokens.color.emerald[500], 0.25)}`,
                fontWeight: 600,
                fontSize: '0.72rem',
              }}
            />
          </Tooltip>
        </Stack>
      </Paper>

      {/* Hero Section & RAG Search */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h5"
          component="h1"
          sx={{
            fontWeight: 800,
            letterSpacing: '-0.02em',
            color: tokens.color.slate[50],
            fontSize: { xs: '1.4rem', md: '1.75rem' },
          }}
        >
          Schemes & Policy Intelligence Dashboard
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: tokens.color.slate[400],
            mt: 0.5,
            fontSize: '0.9rem',
            maxWidth: 800,
          }}
        >
          Find government subsidies, collateral-free credit guarantees, and park infrastructure assistance extracted from official policy circulars.
        </Typography>

        {/* Search Bar Form */}
        <Paper
          component="form"
          onSubmit={handleSearchSubmit}
          elevation={0}
          sx={{
            p: '4px 6px',
            mt: 2.5,
            display: 'flex',
            alignItems: 'center',
            bgcolor: tokens.color.surface.card,
            border: `1px solid ${tokens.color.border.subtle}`,
            borderRadius: '10px',
            boxShadow: '0 4px 18px rgba(0, 0, 0, 0.25)',
            '&:focus-within': {
              borderColor: tokens.color.violet[500],
              boxShadow: `0 0 0 2px ${alpha(tokens.color.violet[500], 0.25)}`,
            },
          }}
        >
          <InputAdornment position="start" sx={{ pl: 1.5, mr: 1 }}>
            <SearchIcon sx={{ color: tokens.color.slate[400], fontSize: 22 }} />
          </InputAdornment>
          <TextField
            fullWidth
            variant="standard"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Type your requirement (e.g., 'export credit collateral support', 'textile park surat', 'coir machinery 25%', 'international fair stall')..."
            InputProps={{
              disableUnderline: true,
              sx: {
                color: tokens.color.slate[100],
                fontSize: '0.92rem',
                py: 0.75,
              },
            }}
          />
          {searchQuery && (
            <Button
              size="small"
              onClick={handleClearSearch}
              sx={{ minWidth: 32, p: 0.5, color: tokens.color.slate[400], mr: 1 }}
            >
              <ClearIcon fontSize="small" />
            </Button>
          )}
          <Button
            type="submit"
            variant="contained"
            disabled={loading || ragLoading}
            startIcon={ragLoading ? <CircularProgress size={16} color="inherit" /> : <AutoAwesomeIcon sx={{ fontSize: 18 }} />}
            sx={{
              bgcolor: tokens.color.violet[500],
              color: '#FFFFFF',
              fontWeight: 700,
              fontSize: '0.82rem',
              borderRadius: '8px',
              px: 2.5,
              py: 1,
              textTransform: 'none',
              whiteSpace: 'nowrap',
              '&:hover': { bgcolor: tokens.color.violet[600] },
            }}
          >
            {ragLoading ? 'Searching...' : 'Find Schemes'}
          </Button>
        </Paper>

        {/* Quick Suggestion Chips */}
        <Stack direction="row" spacing={1} sx={{ mt: 1.75, flexWrap: 'wrap', gap: 1 }}>
          <Typography variant="caption" sx={{ color: tokens.color.slate[400], alignSelf: 'center', mr: 0.5, fontSize: '0.78rem' }}>
            Quick searches:
          </Typography>
          {[
            { label: 'Export Credit Guarantee (₹10 Cr)', q: 'export credit collateral support' },
            { label: 'Surat SER Textile Park (₹1 Cr)', q: 'textile park surat' },
            { label: 'Coir Machinery Subsidy (25%)', q: 'coir industry machinery' },
            { label: 'International Fairs & Airfare', q: 'international exhibition airfare' },
          ].map((chip) => (
            <Chip
              key={chip.label}
              label={chip.label}
              size="small"
              onClick={() => handleQuickChipClick(chip.q)}
              clickable
              sx={{
                bgcolor: activeSearch === chip.q ? alpha(tokens.color.violet[500], 0.25) : alpha(tokens.color.surface.elevated, 0.8),
                color: activeSearch === chip.q ? tokens.color.violet[300] : tokens.color.slate[300],
                border: `1px solid ${activeSearch === chip.q ? tokens.color.violet[500] : tokens.color.border.subtle}`,
                fontSize: '0.75rem',
                height: 26,
                fontWeight: 500,
                '&:hover': { bgcolor: alpha(tokens.color.violet[500], 0.15) },
              }}
            />
          ))}
        </Stack>
      </Box>

      {/* RAG "BEST DEAL" SPOTLIGHT BANNER */}
      {featuredDeal && (
        <Card
          sx={{
            mb: 4,
            borderRadius: '14px',
            bgcolor: tokens.color.surface.card,
            border: `1px solid ${alpha(tokens.color.amber[500], 0.45)}`,
            boxShadow: `0 8px 28px ${alpha(tokens.color.amber[500], 0.12)}`,
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 3,
              background: 'linear-gradient(90deg, #F59E0B 0%, #6366F1 50%, #10B981 100%)',
            }}
          />
          <CardContent sx={{ p: { xs: 2.5, md: 3.5 } }}>
            <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={2.5}>
              <Box sx={{ flex: 1 }}>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.2 }}>
                  <Chip
                    icon={<StarIcon sx={{ fontSize: '15px !important', color: '#0F172A !important' }} />}
                    label="RECOMMENDED BEST DEAL"
                    size="small"
                    sx={{
                      bgcolor: tokens.color.amber[400],
                      color: '#0F172A',
                      fontWeight: 800,
                      fontSize: '0.72rem',
                      letterSpacing: '0.04em',
                      height: 24,
                    }}
                  />
                  {ragBestDeal && (
                    <Chip
                      label={`${ragBestDeal.match_score || 98}% RAG Match`}
                      size="small"
                      sx={{
                        bgcolor: alpha(tokens.color.emerald[500], 0.15),
                        color: tokens.color.emerald[300],
                        fontWeight: 700,
                        fontSize: '0.72rem',
                        height: 24,
                      }}
                    />
                  )}
                  <Chip
                    label={featuredDeal.level === 'state_gujarat' ? 'Gujarat State' : 'Central Government'}
                    size="small"
                    sx={{
                      bgcolor: alpha(tokens.color.slate[700], 0.5),
                      color: tokens.color.slate[300],
                      fontSize: '0.72rem',
                      height: 24,
                    }}
                  />
                </Stack>

                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 800,
                    color: tokens.color.slate[50],
                    fontSize: { xs: '1.15rem', md: '1.3rem' },
                    lineHeight: 1.3,
                  }}
                >
                  {featuredDeal.name}
                </Typography>

                <Typography
                  variant="body2"
                  sx={{
                    color: tokens.color.slate[300],
                    mt: 1,
                    fontSize: '0.86rem',
                    lineHeight: 1.5,
                  }}
                >
                  {featuredDeal.best_deal_highlight || featuredDeal.benefit_description}
                </Typography>

                {/* Deal Key Metrics Row */}
                <Grid container spacing={2} sx={{ mt: 1.5 }}>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block' }}>
                      Financial Scale
                    </Typography>
                    <Typography variant="subtitle2" sx={{ fontWeight: 800, color: tokens.color.emerald[400], fontSize: '0.95rem' }}>
                      {featuredDeal.max_benefit_lakhs
                        ? `Up to ₹${featuredDeal.max_benefit_lakhs >= 100 ? `${(featuredDeal.max_benefit_lakhs / 100).toFixed(1)} Cr` : `${featuredDeal.max_benefit_lakhs} Lakhs`}`
                        : '100% Grant'}
                    </Typography>
                  </Grid>

                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block' }}>
                      Assistance Ratio
                    </Typography>
                    <Typography variant="subtitle2" sx={{ fontWeight: 800, color: tokens.color.violet[300], fontSize: '0.95rem' }}>
                      {featuredDeal.benefit_percentage ? `${featuredDeal.benefit_percentage}% Cover` : 'Full Subsidy'}
                    </Typography>
                  </Grid>

                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block' }}>
                      Application Deadline
                    </Typography>
                    <Stack direction="row" spacing={0.5} alignItems="center">
                      <CalendarTodayOutlinedIcon sx={{ fontSize: 13, color: tokens.color.amber[400] }} />
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, color: tokens.color.amber[300], fontSize: '0.85rem' }}>
                        {featuredDeal.deadline || 'March 31, 2027'}
                      </Typography>
                    </Stack>
                  </Grid>

                  <Grid item xs={6} sm={3}>
                    <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block' }}>
                      Required Documents
                    </Typography>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: tokens.color.slate[200], fontSize: '0.85rem' }}>
                      {featuredDeal.document_count || 6} Verified Items
                    </Typography>
                  </Grid>
                </Grid>
              </Box>

              {/* Action Column */}
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: { xs: 'stretch', md: 'flex-end' },
                  minWidth: { md: 240 },
                  pt: { xs: 1, md: 0 },
                }}
              >
                <Button
                  variant="contained"
                  onClick={() => navigate(`/scheme/${featuredDeal.id || featuredDeal.scheme_code}`)}
                  endIcon={<ArrowForwardIcon />}
                  sx={{
                    bgcolor: tokens.color.violet[500],
                    color: '#FFFFFF',
                    fontWeight: 700,
                    fontSize: '0.875rem',
                    py: 1.1,
                    px: 3,
                    borderRadius: '8px',
                    textTransform: 'none',
                    boxShadow: '0 4px 16px rgba(99, 102, 241, 0.35)',
                    '&:hover': { bgcolor: tokens.color.violet[600] },
                  }}
                >
                  View Scheme & Documents
                </Button>
                {featuredDeal.official_portal_url && (
                  <Button
                    size="small"
                    component="a"
                    href={featuredDeal.official_portal_url}
                    target="_blank"
                    rel="noreferrer"
                    endIcon={<OpenInNewIcon sx={{ fontSize: 14 }} />}
                    sx={{
                      color: tokens.color.slate[400],
                      fontSize: '0.75rem',
                      mt: 1,
                      textTransform: 'none',
                      '&:hover': { color: tokens.color.slate[200] },
                    }}
                  >
                    Official Government Portal
                  </Button>
                )}
              </Box>
            </Stack>
          </CardContent>
        </Card>
      )}

      {/* Filter Bar & Controls */}
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        justifyContent="space-between"
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        spacing={2}
        sx={{ mb: 3 }}
      >
        <Stack direction="row" spacing={1} alignItems="center">
          <FilterListIcon sx={{ color: tokens.color.slate[400], fontSize: 20 }} />
          <Typography variant="body2" sx={{ fontWeight: 700, color: tokens.color.slate[300], fontSize: '0.88rem' }}>
            Filter Catalog ({schemes.length} Schemes)
          </Typography>
        </Stack>

        <Stack direction="row" spacing={1.5} flexWrap="wrap" gap={1}>
          {/* Level Filter */}
          <TextField
            select
            size="small"
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
            sx={{ minWidth: 150 }}
            InputProps={{
              sx: {
                bgcolor: tokens.color.surface.elevated,
                borderRadius: '8px',
                fontSize: '0.82rem',
                color: tokens.color.slate[200],
              },
            }}
          >
            <MenuItem value="all">All Jurisdictions</MenuItem>
            <MenuItem value="central">Central Government</MenuItem>
            <MenuItem value="state_gujarat">Gujarat State</MenuItem>
          </TextField>

          {/* Support Type Filter */}
          <TextField
            select
            size="small"
            value={supportFilter}
            onChange={(e) => setSupportFilter(e.target.value)}
            sx={{ minWidth: 160 }}
            InputProps={{
              sx: {
                bgcolor: tokens.color.surface.elevated,
                borderRadius: '8px',
                fontSize: '0.82rem',
                color: tokens.color.slate[200],
              },
            }}
          >
            <MenuItem value="all">All Benefit Types</MenuItem>
            <MenuItem value="credit_guarantee">Credit Guarantee</MenuItem>
            <MenuItem value="capital_subsidy">Capital Subsidy</MenuItem>
            <MenuItem value="technology_grant">Technology Grant</MenuItem>
            <MenuItem value="infrastructure">Infrastructure Support</MenuItem>
            <MenuItem value="market_development">Market Development</MenuItem>
          </TextField>

          {/* MSME Category Filter */}
          <TextField
            select
            size="small"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            sx={{ minWidth: 130 }}
            InputProps={{
              sx: {
                bgcolor: tokens.color.surface.elevated,
                borderRadius: '8px',
                fontSize: '0.82rem',
                color: tokens.color.slate[200],
              },
            }}
          >
            <MenuItem value="all">All Sizes</MenuItem>
            <MenuItem value="micro">Micro</MenuItem>
            <MenuItem value="small">Small</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
          </TextField>
        </Stack>
      </Stack>

      {/* Schemes Grid */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress size={36} sx={{ color: tokens.color.violet[500] }} />
        </Box>
      ) : schemes.length === 0 ? (
        <Card sx={{ bgcolor: tokens.color.surface.card, p: 4, textAlign: 'center', borderRadius: '12px' }}>
          <Typography variant="body1" sx={{ color: tokens.color.slate[300], fontWeight: 600 }}>
            No schemes matched your filters or search query.
          </Typography>
          <Typography variant="body2" sx={{ color: tokens.color.slate[400], mt: 1 }}>
            Try resetting filters or searching with terms like "export", "textile", "subsidy", or "machinery".
          </Typography>
          <Button
            variant="outlined"
            onClick={handleClearSearch}
            sx={{ mt: 2, textTransform: 'none', color: tokens.color.violet[400], borderColor: tokens.color.violet[500] }}
          >
            Reset Search
          </Button>
        </Card>
      ) : (
        <Grid container spacing={2.5}>
          {schemes.map((scheme) => {
            const isDeal = scheme.is_best_deal
            const docCount = scheme.document_count || (scheme.required_documents ? scheme.required_documents.length : 4)
            return (
              <Grid item xs={12} md={6} key={scheme.id || scheme.scheme_code}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    bgcolor: tokens.color.surface.card,
                    border: `1px solid ${isDeal ? alpha(tokens.color.amber[500], 0.35) : tokens.color.border.subtle}`,
                    borderRadius: '12px',
                    transition: 'all 0.2s ease',
                    boxShadow: isDeal ? '0 4px 20px rgba(245, 158, 11, 0.08)' : 'none',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      borderColor: isDeal ? tokens.color.amber[400] : tokens.color.violet[500],
                      boxShadow: '0 8px 24px rgba(0, 0, 0, 0.28)',
                    },
                  }}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    {/* Header Badges */}
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
                      <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                        {isDeal && (
                          <Chip
                            icon={<StarIcon sx={{ fontSize: '13px !important', color: '#0F172A !important' }} />}
                            label="BEST DEAL"
                            size="small"
                            sx={{
                              bgcolor: tokens.color.amber[400],
                              color: '#0F172A',
                              fontWeight: 800,
                              fontSize: '0.68rem',
                              height: 22,
                            }}
                          />
                        )}
                        <Chip
                          label={scheme.scheme_code}
                          size="small"
                          sx={{
                            bgcolor: alpha(tokens.color.slate[700], 0.4),
                            color: tokens.color.slate[300],
                            fontSize: '0.68rem',
                            height: 22,
                            fontWeight: 600,
                          }}
                        />
                        <Chip
                          label={scheme.level === 'state_gujarat' ? 'Gujarat State' : 'Central'}
                          size="small"
                          sx={{
                            bgcolor: scheme.level === 'state_gujarat' ? alpha(tokens.color.emerald[500], 0.12) : alpha(tokens.color.blue[500], 0.12),
                            color: scheme.level === 'state_gujarat' ? tokens.color.emerald[300] : tokens.color.blue[300],
                            fontSize: '0.68rem',
                            height: 22,
                            fontWeight: 600,
                          }}
                        />
                      </Stack>

                      {/* Deadline Tag */}
                      <Stack direction="row" spacing={0.5} alignItems="center">
                        <CalendarTodayOutlinedIcon sx={{ fontSize: 13, color: tokens.color.slate[400] }} />
                        <Typography variant="caption" sx={{ color: tokens.color.slate[300], fontSize: '0.72rem', fontWeight: 600 }}>
                          {scheme.deadline ? scheme.deadline.replace(' (Annual Rolling)', '').replace(' (2-Year Utilization Cap)', '') : 'March 2027'}
                        </Typography>
                      </Stack>
                    </Stack>

                    {/* Scheme Name */}
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 700,
                        color: tokens.color.slate[100],
                        fontSize: '1.02rem',
                        lineHeight: 1.35,
                        mb: 0.75,
                        cursor: 'pointer',
                        '&:hover': { color: tokens.color.violet[300] },
                      }}
                      onClick={() => navigate(`/scheme/${scheme.id || scheme.scheme_code}`)}
                    >
                      {scheme.name}
                    </Typography>

                    {/* Ministry / Department */}
                    <Typography
                      variant="caption"
                      sx={{
                        color: tokens.color.slate[400],
                        display: 'block',
                        fontSize: '0.76rem',
                        mb: 1.5,
                        lineHeight: 1.3,
                      }}
                    >
                      {scheme.ministry}
                    </Typography>

                    {/* Benefit Snippet */}
                    <Box
                      sx={{
                        p: 1.25,
                        borderRadius: '8px',
                        bgcolor: alpha(tokens.color.surface.elevated, 0.7),
                        border: `1px solid ${tokens.color.border.subtle}`,
                        mb: 2,
                      }}
                    >
                      <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', fontSize: '0.7rem' }}>
                        Key Benefit / Assistance Scale:
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#047857', fontWeight: 800, fontSize: '0.88rem' }}>
                        {scheme.max_benefit_lakhs
                          ? `Up to ₹${scheme.max_benefit_lakhs >= 100 ? `${(scheme.max_benefit_lakhs / 100).toFixed(1)} Cr` : `${scheme.max_benefit_lakhs} Lakhs`}`
                          : '100% Grant Funding'}
                        {scheme.benefit_percentage ? ` (${scheme.benefit_percentage}% cover)` : ''}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          color: tokens.color.slate[300],
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                          fontSize: '0.75rem',
                          mt: 0.5,
                        }}
                      >
                        {scheme.benefit_description}
                      </Typography>
                    </Box>

                    {/* Bottom Metadata & Required Documents Pill */}
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
                      <Stack direction="row" spacing={0.75} alignItems="center">
                        <DescriptionOutlinedIcon sx={{ fontSize: 15, color: tokens.color.slate[400] }} />
                        <Typography variant="caption" sx={{ color: tokens.color.slate[300], fontSize: '0.75rem', fontWeight: 600 }}>
                          {docCount} Required Documents
                        </Typography>
                      </Stack>

                      {scheme.target_msme_categories && scheme.target_msme_categories.length > 0 && (
                        <Typography variant="caption" sx={{ color: tokens.color.slate[400], fontSize: '0.72rem' }}>
                          Target: {scheme.target_msme_categories.map((c) => c.toUpperCase()).join(', ')}
                        </Typography>
                      )}
                    </Stack>
                  </CardContent>

                  {/* Card Actions Footer */}
                  <Box
                    sx={{
                      px: 2.5,
                      py: 1.5,
                      borderTop: `1px solid ${tokens.color.border.subtle}`,
                      bgcolor: alpha(tokens.color.surface.elevated, 0.4),
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <Button
                      size="small"
                      onClick={() => navigate(`/scheme/${scheme.id || scheme.scheme_code}`)}
                      endIcon={<ArrowForwardIcon sx={{ fontSize: 14 }} />}
                      sx={{
                        color: '#0F2E59',
                        fontSize: '0.84rem',
                        fontWeight: 700,
                        textTransform: 'none',
                        p: 0,
                        '&:hover': { color: '#1E40AF', bgcolor: 'transparent' },
                      }}
                    >
                      View Details & Checklist
                    </Button>

                    {scheme.official_portal_url && (
                      <Tooltip title="Open official government portal" arrow>
                        <Button
                          size="small"
                          component="a"
                          href={scheme.official_portal_url}
                          target="_blank"
                          rel="noreferrer"
                          sx={{
                            color: tokens.color.slate[400],
                            fontSize: '0.72rem',
                            textTransform: 'none',
                            p: 0,
                            minWidth: 0,
                            '&:hover': { color: tokens.color.slate[200] },
                          }}
                        >
                          <OpenInNewIcon sx={{ fontSize: 15 }} />
                        </Button>
                      </Tooltip>
                    )}
                  </Box>
                </Card>
              </Grid>
            )
          })}
        </Grid>
      )}
    </Box>
  )
}

export default SchemesDashboard
