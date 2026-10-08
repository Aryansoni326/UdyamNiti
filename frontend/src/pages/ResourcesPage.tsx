import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Stack,
  Paper,
  Tabs,
  Tab,
  Button,
  Divider,
  TextField,
  InputAdornment,
} from '@mui/material'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import SearchIcon from '@mui/icons-material/Search'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import GavelIcon from '@mui/icons-material/Gavel'
import DescriptionIcon from '@mui/icons-material/Description'
import FileDownloadIcon from '@mui/icons-material/FileDownload'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import { ALL_OFFICIAL_SCHEMES } from '../data/officialSchemes'

export const ResourcesPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const initialTab = searchParams.get('tab') || 'guidelines'
  const [currentTab, setCurrentTab] = useState<string>(initialTab)
  const [pdfSearch, setPdfSearch] = useState<string>('')
  const [selectedDivision, setSelectedDivision] = useState<string>('all')
  const [selectedState, setSelectedState] = useState<string>('all')

  useEffect(() => {
    const tabParam = searchParams.get('tab')
    if (tabParam) setCurrentTab(tabParam)
  }, [searchParams])

  const handleTabChange = (_: React.SyntheticEvent, newValue: string) => {
    setCurrentTab(newValue)
    setSearchParams({ tab: newValue })
  }

  const filteredPdfs = ALL_OFFICIAL_SCHEMES.filter((s) => {
    const query = pdfSearch.toLowerCase()
    const matchesSearch =
      !pdfSearch ||
      s.name.toLowerCase().includes(query) ||
      s.pdfFile.toLowerCase().includes(query) ||
      s.ministry.toLowerCase().includes(query) ||
      s.division.toLowerCase().includes(query) ||
      s.targetStates.some((st) => st.toLowerCase().includes(query))

    const matchesDivision =
      selectedDivision === 'all' || s.division.toLowerCase().includes(selectedDivision.toLowerCase())

    const matchesState =
      selectedState === 'all' ||
      (selectedState === 'Gujarat' && (s.level === 'state_gujarat' || s.targetStates.includes('Gujarat') || s.targetStates.includes('All India'))) ||
      s.targetStates.includes(selectedState) ||
      s.targetStates.includes('All India')

    return matchesSearch && matchesDivision && matchesState
  })

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F8FAFC', pb: 10 }}>
      {/* Header Banner */}
      <Box
        sx={{
          bgcolor: '#0F2E59',
          color: '#FFFFFF',
          pt: { xs: 5, md: 7 },
          pb: { xs: 6, md: 8 },
          borderBottom: '4px solid #059669',
        }}
      >
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Stack spacing={1.5} sx={{ maxWidth: 900 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                icon={<MenuBookIcon sx={{ color: '#A7F3D0 !important', fontSize: '15px !important' }} />}
                label="Official Document Repository"
                size="small"
                sx={{
                  bgcolor: 'rgba(255, 255, 255, 0.15)',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                }}
              />
              <Chip
                label={`${ALL_OFFICIAL_SCHEMES.length} Verified Gazette Guidelines`}
                size="small"
                sx={{
                  bgcolor: 'rgba(5, 150, 105, 0.25)',
                  color: '#A7F3D0',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                }}
              />
              <Chip
                label="5 Departmental Divisions"
                size="small"
                sx={{
                  bgcolor: 'rgba(59, 130, 246, 0.25)',
                  color: '#93C5FD',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                }}
              />
            </Box>

            <Typography
              variant="h2"
              sx={{
                fontWeight: 900,
                fontSize: { xs: '2rem', md: '2.8rem' },
                lineHeight: 1.2,
                color: '#FFFFFF',
              }}
            >
              Statutory Resources & Scheme Guidelines
            </Typography>

            <Typography
              variant="body1"
              sx={{
                color: '#CBD5E1',
                fontSize: { xs: '0.98rem', md: '1.1rem' },
                lineHeight: 1.6,
              }}
            >
              Access the complete digital library of Gazette notifications, operational scheme PDFs, statutory Acts, DPR project templates, and Udyam registration manuals archived in the UdyamNiti corpus.
            </Typography>
          </Stack>
        </Container>
      </Box>

      {/* Tabs */}
      <Box sx={{ bgcolor: '#FFFFFF', borderBottom: '1px solid #E2E8F0', position: 'sticky', top: 58, zIndex: 100 }}>
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                fontWeight: 700,
                fontSize: '0.9rem',
                textTransform: 'none',
                minHeight: 52,
                color: '#64748B',
                '&.Mui-selected': { color: '#059669', fontWeight: 800 },
              },
              '& .MuiTabs-indicator': { bgcolor: '#059669', height: 3 },
            }}
          >
            <Tab value="guidelines" label="Scheme Guidelines & Official PDFs" icon={<PictureAsPdfIcon fontSize="small" />} iconPosition="start" />
            <Tab value="acts" label="Statutory Acts & Rules" icon={<GavelIcon fontSize="small" />} iconPosition="start" />
            <Tab value="dpr" label="DPR Templates & Formats" icon={<DescriptionIcon fontSize="small" />} iconPosition="start" />
            <Tab value="udyam" label="Udyam Registration Guide" icon={<VerifiedUserIcon fontSize="small" />} iconPosition="start" />
          </Tabs>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 }, mt: 4 }}>
        {/* TAB 1: GUIDELINES & PDFS */}
        {currentTab === 'guidelines' && (
          <Box>
            <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', md: 'center' }} sx={{ mb: 2.5, gap: 2 }}>
              <Box>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                  Archived Operational Scheme Guidelines ({filteredPdfs.length} of {ALL_OFFICIAL_SCHEMES.length})
                </Typography>
                <Typography variant="body2" sx={{ color: '#64748B' }}>
                  Official scheme gazettes and policy documents extracted from Central Ministries and State Departments.
                </Typography>
              </Box>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems="center" sx={{ width: { xs: '100%', md: 'auto' } }}>
                <TextField
                  select
                  size="small"
                  value={selectedState}
                  onChange={(e) => setSelectedState(e.target.value)}
                  sx={{ width: { xs: '100%', sm: 160 }, bgcolor: '#FFFFFF', borderRadius: '8px' }}
                >
                  <MenuItem value="all">All States & UTs</MenuItem>
                  <MenuItem value="Gujarat">Gujarat</MenuItem>
                  <MenuItem value="All India">All India</MenuItem>
                  <MenuItem value="Assam">Assam</MenuItem>
                  <MenuItem value="Maharashtra">Maharashtra</MenuItem>
                  <MenuItem value="Tamil Nadu">Tamil Nadu</MenuItem>
                  <MenuItem value="Karnataka">Karnataka</MenuItem>
                </TextField>

                <TextField
                  size="small"
                  placeholder="Search PDF, Scheme, Ministry..."
                  value={pdfSearch}
                  onChange={(e) => setPdfSearch(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon sx={{ color: '#64748B' }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ width: { xs: '100%', sm: 260 }, bgcolor: '#FFFFFF', borderRadius: '8px' }}
                />
              </Stack>
            </Stack>

            {/* Division Filter Pills */}
            <Stack direction="row" spacing={1} sx={{ mb: 3, flexWrap: 'wrap', gap: 1 }}>
              {[
                { id: 'all', label: 'All Divisions' },
                { id: 'MSME & Enterprise Development', label: 'MSME & Enterprise' },
                { id: 'Gujarat State & Infrastructure', label: 'Gujarat State' },
                { id: 'Social Welfare & Inclusive Development', label: 'Social Welfare & Inclusion' },
                { id: 'Agriculture, Food & Fisheries', label: 'Agriculture & Food' },
                { id: 'Education, Youth, Defence & Science', label: 'Education & Science' },
              ].map((div) => (
                <Chip
                  key={div.id}
                  label={div.label}
                  onClick={() => setSelectedDivision(div.id)}
                  clickable
                  size="small"
                  sx={{
                    bgcolor: selectedDivision === div.id ? '#0F2E59' : '#FFFFFF',
                    color: selectedDivision === div.id ? '#FFFFFF' : '#475569',
                    border: '1px solid #CBD5E1',
                    fontWeight: 700,
                    fontSize: '0.78rem',
                    py: 1.8,
                    '&:hover': { bgcolor: selectedDivision === div.id ? '#0F2E59' : '#F1F5F9' },
                  }}
                />
              ))}
            </Stack>

            <Grid container spacing={3}>
              {filteredPdfs.map((scheme) => (
                <Grid item xs={12} md={6} lg={4} key={scheme.code}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      borderRadius: '14px',
                      border: '1.5px solid #E2E8F0',
                      bgcolor: '#FFFFFF',
                      p: 1,
                      transition: 'all 0.2s ease',
                      '&:hover': { borderColor: '#059669', transform: 'translateY(-3px)', boxShadow: '0 8px 24px rgba(0,0,0,0.06)' },
                    }}
                  >
                    <CardContent sx={{ p: 2.5 }}>
                      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5, flexWrap: 'wrap', gap: 0.5 }}>
                        <Stack direction="row" spacing={0.5} alignItems="center">
                          <Chip
                            icon={<PictureAsPdfIcon sx={{ fontSize: '14px !important', color: '#DC2626 !important' }} />}
                            label={scheme.level === 'state_gujarat' ? 'Gujarat State' : scheme.level === 'state' ? 'State Scheme' : 'Central'}
                            size="small"
                            sx={{
                              bgcolor: scheme.level === 'state_gujarat' ? '#EFF6FF' : '#FEF2F2',
                              color: scheme.level === 'state_gujarat' ? '#1D4ED8' : '#991B1B',
                              fontWeight: 800,
                              fontSize: '0.7rem',
                            }}
                          />
                          <Chip
                            label={scheme.division}
                            size="small"
                            sx={{
                              bgcolor: '#F1F5F9',
                              color: '#334155',
                              fontWeight: 700,
                              fontSize: '0.68rem',
                            }}
                          />
                        </Stack>
                        <Typography variant="caption" sx={{ fontWeight: 800, color: scheme.categoryColor }}>
                          {scheme.maxBenefit}
                        </Typography>
                      </Stack>

                      <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '1.05rem', lineHeight: 1.35, mb: 1 }}>
                        {scheme.name}
                      </Typography>

                      <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mb: 1.5, fontWeight: 600 }}>
                        {scheme.ministry}
                      </Typography>

                      <Paper sx={{ p: 1.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', mb: 2 }}>
                        <Typography variant="caption" sx={{ color: '#059669', fontWeight: 700, display: 'block', mb: 0.5 }}>
                          Gazette / Circular Reference:
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#334155', fontWeight: 600, display: 'block' }}>
                          {scheme.gazette}
                        </Typography>
                      </Paper>

                      <Paper sx={{ p: 1.2, bgcolor: '#F1F5F9', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: 1 }}>
                        <PictureAsPdfIcon sx={{ fontSize: 16, color: '#DC2626' }} />
                        <Typography variant="caption" sx={{ color: '#475569', fontWeight: 700, fontFamily: 'monospace' }} noWrap>
                          {scheme.pdfFile}
                        </Typography>
                      </Paper>
                    </CardContent>

                    <Box sx={{ p: 2, pt: 0 }}>
                      <Button
                        fullWidth
                        variant="contained"
                        onClick={() => navigate(`/scheme/${scheme.code}`)}
                        endIcon={<ArrowForwardIcon sx={{ fontSize: '15px !important' }} />}
                        sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 700, textTransform: 'none', borderRadius: '8px', py: 0.9 }}
                      >
                        Read Guidelines & Criteria
                      </Button>
                    </Box>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* TAB 2: ACTS & RULES */}
        {currentTab === 'acts' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
              Statutory Legislation & Regulatory Framework
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1.5px solid #E2E8F0', borderRadius: '12px' }}>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                    Micro, Small and Medium Enterprises Development (MSMED) Act, 2006
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#475569', lineHeight: 1.7, mb: 2 }}>
                    The foundational Parliamentary Act governing enterprise definitions, Delayed Payments Tribunals (MSEFC), procurement preferences, and National MSME Board powers.
                  </Typography>
                  <Stack spacing={1}>
                    <Typography variant="caption" sx={{ color: '#0F2E59', fontWeight: 700 }}>
                      • Section 15-24: Delayed Payments Penal Compound Interest (3x RBI Bank Rate)
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#0F2E59', fontWeight: 700 }}>
                      • Section 11: Public Procurement Preference Mandate
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#0F2E59', fontWeight: 700 }}>
                      • Section 7: Statutory Classification Power & Composite Criteria
                    </Typography>
                  </Stack>
                  <Button
                    variant="outlined"
                    size="small"
                    fullWidth
                    onClick={() => window.open('https://msme.gov.in/acts-rules-notifications', '_blank')}
                    sx={{ mt: 2.5, borderColor: '#0F2E59', color: '#0F2E59', fontWeight: 700, textTransform: 'none' }}
                  >
                    Open Official Act (MSME Portal) ↗
                  </Button>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1.5px solid #E2E8F0', borderRadius: '12px' }}>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                    Gazette Notification S.O. 2119(E) (June 26, 2020)
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#475569', lineHeight: 1.7, mb: 2 }}>
                    Historic statutory resolution merging manufacturing & services criteria into a unified composite turnover and investment threshold with complete exemption for export earnings.
                  </Typography>
                  <Stack spacing={1}>
                    <Typography variant="caption" sx={{ color: '#059669', fontWeight: 700 }}>
                      ✓ Micro: Investment &le; ₹1 Cr &amp; Turnover &le; ₹5 Cr
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#2563EB', fontWeight: 700 }}>
                      ✓ Small: Investment &le; ₹10 Cr &amp; Turnover &le; ₹50 Cr
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#7C3AED', fontWeight: 700 }}>
                      ✓ Medium: Investment &le; ₹50 Cr &amp; Turnover &le; ₹250 Cr
                    </Typography>
                  </Stack>
                  <Button
                    variant="outlined"
                    size="small"
                    fullWidth
                    onClick={() => window.open('https://msme.gov.in/gazette-notifications', '_blank')}
                    sx={{ mt: 2.5, borderColor: '#059669', color: '#059669', fontWeight: 700, textTransform: 'none' }}
                  >
                    Open Official Gazette Notice (e-Gazette) ↗
                  </Button>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* TAB 3: DPR TEMPLATES */}
        {currentTab === 'dpr' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
              Bank-Ready Detailed Project Report (DPR) Formats
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748B', mb: 3 }}>
              Standardized project report templates recognized by public sector banks, KVIC, and CGTMSE member lending institutions:
            </Typography>
            <Grid container spacing={3}>
              {[
                { title: 'PMEGP Manufacturing DPR Template', target: 'Manufacturing units seeking up to ₹50 Lakh project loans with 35% subsidy', fields: 'Machinery quotes, raw material cycle, civil works, DSCR cashflow statement' },
                { title: 'PMEGP Service Sector DPR Template', target: 'Service enterprises seeking up to ₹20 Lakh project assistance', fields: 'Office equipment, IT hardware, working capital, monthly revenue projections' },
                { title: 'Cluster Common Facility Centre (CFC) DPR', target: 'MSE-CDP consortia seeking grants up to ₹30.00 Crore', fields: 'SPV structure, member user commitments, environmental impact, fee model' },
                { title: 'Gujarat SER Park DPR Guidelines', target: 'Special Economic Region textile & MSME park developers', fields: 'Zero liquid discharge infrastructure, common testing labs, land lease' },
              ].map((dpr, idx) => (
                <Grid item xs={12} sm={6} key={idx}>
                  <Paper sx={{ p: 3, border: '1px solid #E2E8F0', bgcolor: '#F8FAFC', borderRadius: '12px' }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                      {dpr.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#64748B', mb: 1.5 }}>
                      {dpr.target}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#059669', fontWeight: 700, display: 'block' }}>
                      Key Sections: {dpr.fields}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}

        {/* TAB 4: UDYAM GUIDE */}
        {currentTab === 'udyam' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
              Official Udyam Registration & Verification Process
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={7}>
                <Typography variant="body1" sx={{ color: '#334155', lineHeight: 1.8, mb: 2 }}>
                  Udyam Registration is the only official government identity proof for an enterprise in India. Registration is 100% free, paperless, and digital.
                </Typography>
                <Stack spacing={1.5}>
                  {[
                    'Aadhaar Number of the proprietor / managing partner / authorized director is mandatory.',
                    'PAN & GSTIN are automatically linked with income tax and GST databases for composite calculations.',
                    'Zero documentation upload needed — data is pulled via API from Income Tax & GSTN servers.',
                    'Generates a permanent 19-digit Udyam Registration Number (URN) with dynamic QR code.',
                  ].map((step, i) => (
                    <Typography key={i} variant="body2" sx={{ color: '#334155', display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CheckCircleIcon sx={{ fontSize: 16, color: '#059669' }} />
                      {step}
                    </Typography>
                  ))}
                </Stack>
              </Grid>
              <Grid item xs={12} md={5}>
                <Paper sx={{ p: 3, bgcolor: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: '12px' }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#065F46', mb: 1 }}>
                    Official Registration Portal
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#047857', mb: 2 }}>
                    Never pay fees on unauthorized portals. The official Government of India portal charges zero fee.
                  </Typography>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={() => window.open('https://udyamregistration.gov.in', '_blank')}
                    sx={{ bgcolor: '#059669', color: '#FFFFFF', fontWeight: 700, textTransform: 'none' }}
                  >
                    Open Udyam Registration Portal →
                  </Button>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        )}
      </Container>
    </Box>
  )
}

export default ResourcesPage
