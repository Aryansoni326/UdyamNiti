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
} from '@mui/material'
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive'
import CampaignIcon from '@mui/icons-material/Campaign'
import EventIcon from '@mui/icons-material/Event'
import DescriptionIcon from '@mui/icons-material/Description'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'

export const UpdatesPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const initialTab = searchParams.get('tab') || 'circulars'
  const [currentTab, setCurrentTab] = useState<string>(initialTab)

  useEffect(() => {
    const tabParam = searchParams.get('tab')
    if (tabParam) setCurrentTab(tabParam)
  }, [searchParams])

  const handleTabChange = (_: React.SyntheticEvent, newValue: string) => {
    setCurrentTab(newValue)
    setSearchParams({ tab: newValue })
  }

  const NOTIFICATIONS = [
    {
      id: 'circ-257',
      title: 'CGTMSE Circular No. 257: Credit Guarantee Scheme for Export Credit (EPM - Niryat Protsahan)',
      date: 'Fiscal Year 2025-26',
      authority: 'Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE) & DGFT',
      pdf: 'Circular 257 - CGS for Export credit merged.pdf',
      tag: 'Export Finance',
      highlight: 'Enhanced guarantee cover of 85% for Micro & Small Enterprises with sovereign DGFT risk participation. Zero third-party collateral.',
      link: '/scheme/CGTMSE_EPM_EXPORT_2026',
    },
    {
      id: 'circ-262',
      title: 'CGTMSE Circular No. 262: Operationalization of Secondary Market Factoring Support under TReDS',
      date: 'Fiscal Year 2025-26',
      authority: 'Ministry of MSME / CGTMSE & Reserve Bank of India',
      pdf: 'TReDS Cicular 262.pdf',
      tag: 'TReDS Bill Discounting',
      highlight: 'Guaranteed liquidity coverage up to ₹1.00 Crore for non-recourse factoring on RBI licensed TReDS platforms (RXIL, M1xchange, Invoicemart).',
      link: '/scheme/TREDS_INVOICE_CGTMSE',
    },
    {
      id: 'guj-gr-0597',
      title: 'Government of Gujarat GR No. IMD/MRT/0597/G: Financial Assistance for Developing SER Textile & MSME Parks',
      date: 'Operational Period 2025-2030',
      authority: 'Industries and Mines Department, Government of Gujarat, Gandhinagar',
      pdf: '1.msme.pdf',
      tag: 'Gujarat Industrial Policy',
      highlight: '100% financial assistance up to ₹1.00 Crore for establishing Common Testing Laboratories and R&D Design Centers in Gujarat textile belts.',
      link: '/scheme/GUJ_SER_TEXTILE_2025',
    },
    {
      id: 'zed-phase2',
      title: 'MSME Sustainable (ZED) Certification Guidance Document for Manufacturing Clusters (NIC Divisions 24 & 27)',
      date: 'Active Guidelines 2022-26',
      authority: 'National Productivity Council & Quality Council of India (QCI) / M/o MSME',
      pdf: 'ZED_Guidance_Document_NIC_Division_24 & 27.pdf',
      tag: 'Quality & Zero Defect',
      highlight: 'Up to 80% subsidy for Micro and 60% for Small units achieving Bronze, Silver or Gold certification. Includes ₹5 Lakh handholding per enterprise.',
      link: '/scheme/MSME_ZED_CERTIFICATION',
    },
    {
      id: 'pmegp-comp',
      title: 'PMEGP Comprehensive National Guidelines: Expanded Project Ceilings and 2nd Loan Facility',
      date: 'Cabinet Approved 2022-26',
      authority: 'Khadi and Village Industries Commission (KVIC) & Ministry of MSME',
      pdf: 'pmegp scheme.pdf',
      tag: 'Capital Subsidy',
      highlight: 'Ceiling raised to ₹50 Lakh for manufacturing and ₹20 Lakh for services. Introduction of 2nd financial assistance loan up to ₹1.00 Crore with 15% subsidy.',
      link: '/scheme/PMEGP_MSME_SCHEME',
    },
    {
      id: 'mse-cdp-rev',
      title: 'MSE Cluster Development Programme (MSE-CDP) Revised Operational Guidelines',
      date: 'Active Guidelines',
      authority: 'Office of Development Commissioner (MSME), New Delhi',
      pdf: '1.MSE-CDP guidelines.pdf',
      tag: 'Cluster Grants',
      highlight: 'Up to ₹30.00 Crore grant assistance for Common Facility Centres (CFC) and ₹15.00 Crore for Infrastructure Development (ID) in industrial estates.',
      link: '/scheme/MSE_CDP_CLUSTER',
    },
  ]

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F8FAFC', pb: 10 }}>
      {/* Header Banner */}
      <Box
        sx={{
          bgcolor: '#0F2E59',
          color: '#FFFFFF',
          pt: { xs: 5, md: 7 },
          pb: { xs: 6, md: 8 },
          borderBottom: '4px solid #7C3AED',
        }}
      >
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Stack spacing={1.5} sx={{ maxWidth: 900 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={<NotificationsActiveIcon sx={{ color: '#E9D5FF !important', fontSize: '15px !important' }} />}
                label="Official Circulars & Policy Dispatch"
                size="small"
                sx={{
                  bgcolor: 'rgba(255, 255, 255, 0.15)',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                }}
              />
              <Chip
                label="Real-time Gazette Tracking"
                size="small"
                sx={{
                  bgcolor: 'rgba(124, 58, 237, 0.25)',
                  color: '#E9D5FF',
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
              Policy Updates, Circulars & Tenders
            </Typography>

            <Typography
              variant="body1"
              sx={{
                color: '#CBD5E1',
                fontSize: { xs: '0.98rem', md: '1.1rem' },
                lineHeight: 1.6,
              }}
            >
              Real-time dissemination of executive circulars, CGTMSE credit notifications, Gujarat Industrial Policy amendments, public tenders, and national MSME conclaves.
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
                '&.Mui-selected': { color: '#7C3AED', fontWeight: 800 },
              },
              '& .MuiTabs-indicator': { bgcolor: '#7C3AED', height: 3 },
            }}
          >
            <Tab value="circulars" label="Policy Notifications & Circulars" icon={<DescriptionIcon fontSize="small" />} iconPosition="start" />
            <Tab value="press" label="Press Releases & Announcements" icon={<CampaignIcon fontSize="small" />} iconPosition="start" />
            <Tab value="events" label="Events, Conclaves & Tenders" icon={<EventIcon fontSize="small" />} iconPosition="start" />
          </Tabs>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 }, mt: 4 }}>
        {/* TAB 1: CIRCULARS */}
        {currentTab === 'circulars' && (
          <Grid container spacing={3}>
            {NOTIFICATIONS.map((notif) => (
              <Grid item xs={12} md={6} key={notif.id}>
                <Paper
                  sx={{
                    p: 3.5,
                    borderRadius: '16px',
                    bgcolor: '#FFFFFF',
                    border: '1.5px solid #E2E8F0',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    transition: 'all 0.2s ease',
                    '&:hover': { borderColor: '#7C3AED', boxShadow: '0 8px 24px rgba(124, 58, 237, 0.08)' },
                  }}
                >
                  <Box>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
                      <Chip label={notif.tag} size="small" sx={{ bgcolor: '#F3E8FF', color: '#6B21A8', fontWeight: 800, fontSize: '0.72rem' }} />
                      <Typography variant="caption" sx={{ color: '#64748B', fontWeight: 600 }}>
                        {notif.date}
                      </Typography>
                    </Stack>

                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '1.08rem', lineHeight: 1.4, mb: 1 }}>
                      {notif.title}
                    </Typography>

                    <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mb: 2, fontWeight: 600 }}>
                      Issuing Authority: {notif.authority}
                    </Typography>

                    <Paper sx={{ p: 1.8, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '10px', mb: 2.5 }}>
                      <Typography variant="caption" sx={{ color: '#0F2E59', fontWeight: 800, display: 'block', mb: 0.5 }}>
                        Gazette Provisions & Highlights:
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#334155', lineHeight: 1.6 }}>
                        {notif.highlight}
                      </Typography>
                    </Paper>

                    <Paper sx={{ p: 1, bgcolor: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <PictureAsPdfIcon sx={{ fontSize: 16, color: '#DC2626' }} />
                      <Typography variant="caption" sx={{ color: '#991B1B', fontWeight: 700, fontFamily: 'monospace' }}>
                        Source File: {notif.pdf}
                      </Typography>
                    </Paper>
                  </Box>

                  <Button
                    variant="contained"
                    fullWidth
                    onClick={() => navigate(notif.link)}
                    endIcon={<ArrowForwardIcon sx={{ fontSize: '15px !important' }} />}
                    sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 700, textTransform: 'none', borderRadius: '8px', py: 1 }}
                  >
                    View Operational Guidelines & Impact
                  </Button>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}

        {/* TAB 2: PRESS RELEASES */}
        {currentTab === 'press' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 3 }}>
              Official Press Information Bureau (PIB) MSME Releases
            </Typography>
            <Stack spacing={3}>
              {[
                { title: 'Union Cabinet Approves ₹10 Crore Credit Guarantee Ceiling for Export Oriented MSMEs', date: 'New Delhi • PIB MSME', summary: 'Under the revamped Credit Guarantee Scheme for Export Credit, eligible export enterprises will receive 85% risk protection through CGTMSE and DGFT partnership.' },
                { title: 'Gujarat State Industries Department Notifies SER MSME Park Common Facility Grants', date: 'Gandhinagar • Industries & Mines', summary: 'Financial assistance of up to ₹1.00 Crore cleared for dedicated testing laboratories, quality check centres, and effluent treatment infrastructure.' },
                { title: 'Over 6.3 Crore Enterprises Registered on Udyam Portal with Complete Digital Verification', date: 'New Delhi • O/o DC-MSME', summary: 'Paperless integration with CBDT and GSTN ensures automatic validation of enterprise composite turnover and investment thresholds.' },
              ].map((item, idx) => (
                <Paper key={idx} sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59' }}>
                      {item.title}
                    </Typography>
                    <Chip label={item.date} size="small" sx={{ bgcolor: '#E2E8F0', fontWeight: 600, fontSize: '0.72rem' }} />
                  </Stack>
                  <Typography variant="body2" sx={{ color: '#475569', lineHeight: 1.6 }}>
                    {item.summary}
                  </Typography>
                </Paper>
              ))}
            </Stack>
          </Paper>
        )}

        {/* TAB 3: EVENTS & TENDERS */}
        {currentTab === 'events' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 3 }}>
              Upcoming National Conclaves, Vendor Development Meets & Tenders
            </Typography>
            <Grid container spacing={3}>
              {[
                { title: 'National Vendor Development Programme (NVDP)', loc: 'Surat International Exhibition Centre, Gujarat', date: 'Nov 14-16, 2026', desc: 'Direct B2B procurement match-making between CPSEs, defense buyers, and registered Micro & Small Enterprises.' },
                { title: 'ZED Certification Intensive Handholding Camp', loc: 'Ahmedabad Management Association (AMA)', date: 'Nov 22, 2026', desc: 'Free on-site assessment for zero-defect compliance with 80% subsidy assistance for Micro units.' },
                { title: 'MSE-CDP Common Facility Centre (CFC) Expression of Interest', loc: 'Gandhinagar GIDC Estates', date: 'Tender Closing: Dec 05, 2026', desc: 'Inviting Special Purpose Vehicles (SPV) of textile and engineering units for ₹30 Cr grant co-financing.' },
              ].map((ev, i) => (
                <Grid item xs={12} md={4} key={i}>
                  <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', height: '100%' }}>
                    <Chip label={ev.date} size="small" sx={{ bgcolor: '#EFF6FF', color: '#1D4ED8', fontWeight: 800, mb: 1.5 }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                      {ev.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#059669', fontWeight: 700, display: 'block', mb: 1 }}>
                      📍 {ev.loc}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#64748B', lineHeight: 1.5 }}>
                      {ev.desc}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}
      </Container>
    </Box>
  )
}

export default UpdatesPage
