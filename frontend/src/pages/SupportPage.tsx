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
import SupportAgentIcon from '@mui/icons-material/SupportAgent'
import GavelIcon from '@mui/icons-material/Gavel'
import StorefrontIcon from '@mui/icons-material/Storefront'
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'
import LocationCityIcon from '@mui/icons-material/LocationCity'
import PhoneInTalkIcon from '@mui/icons-material/PhoneInTalk'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'

export const SupportPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const initialTab = searchParams.get('tab') || 'samadhaan'
  const [currentTab, setCurrentTab] = useState<string>(initialTab)

  useEffect(() => {
    const tabParam = searchParams.get('tab')
    if (tabParam) setCurrentTab(tabParam)
  }, [searchParams])

  const handleTabChange = (_: React.SyntheticEvent, newValue: string) => {
    setCurrentTab(newValue)
    setSearchParams({ tab: newValue })
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#F8FAFC', pb: 10 }}>
      {/* Header Banner */}
      <Box
        sx={{
          bgcolor: '#0F2E59',
          color: '#FFFFFF',
          pt: { xs: 5, md: 7 },
          pb: { xs: 6, md: 8 },
          borderBottom: '4px solid #DC2626',
        }}
      >
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Stack spacing={1.5} sx={{ maxWidth: 900 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={<SupportAgentIcon sx={{ color: '#FECACA !important', fontSize: '15px !important' }} />}
                label="Enterprise Grievance & Statutory Redressal"
                size="small"
                sx={{
                  bgcolor: 'rgba(255, 255, 255, 0.15)',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                }}
              />
              <Chip
                label="SAMADHAAN • SAMBANDH • CHAMPIONS"
                size="small"
                sx={{
                  bgcolor: 'rgba(220, 38, 38, 0.25)',
                  color: '#FECACA',
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
              Enterprise Support & Grievance Redressal
            </Typography>

            <Typography
              variant="body1"
              sx={{
                color: '#CBD5E1',
                fontSize: { xs: '0.98rem', md: '1.1rem' },
                lineHeight: 1.6,
              }}
            >
              Statutory mechanisms designed to protect MSME liquidity, enforce mandatory public procurement quotas, resolve delayed corporate payments, and connect directly with District Industries Centres (DICs).
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
                '&.Mui-selected': { color: '#DC2626', fontWeight: 800 },
              },
              '& .MuiTabs-indicator': { bgcolor: '#DC2626', height: 3 },
            }}
          >
            <Tab value="samadhaan" label="MSME SAMADHAAN (Delayed Payments)" icon={<GavelIcon fontSize="small" />} iconPosition="start" />
            <Tab value="sambandh" label="MSME SAMBANDH (Procurement Monitor)" icon={<StorefrontIcon fontSize="small" />} iconPosition="start" />
            <Tab value="champions" label="CHAMPIONS Portal" icon={<EmojiEventsIcon fontSize="small" />} iconPosition="start" />
            <Tab value="dic" label="Gujarat DIC Network" icon={<LocationCityIcon fontSize="small" />} iconPosition="start" />
            <Tab value="helpdesk" label="National Helpdesk & Contacts" icon={<PhoneInTalkIcon fontSize="small" />} iconPosition="start" />
          </Tabs>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 }, mt: 4 }}>
        {/* TAB 1: SAMADHAAN */}
        {currentTab === 'samadhaan' && (
          <Grid container spacing={3.5}>
            <Grid item xs={12} md={7}>
              <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0', height: '100%' }}>
                <Chip label="Section 18 MSMED Act 2006" sx={{ bgcolor: '#FEF2F2', color: '#991B1B', fontWeight: 800, mb: 2 }} />
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
                  Delayed Payments Monitoring System (MSME SAMADHAAN)
                </Typography>
                <Typography variant="body1" sx={{ color: '#334155', lineHeight: 1.8, mb: 2.5 }}>
                  Under the statutory provisions of Sections 15–24 of the MSMED Act 2006, any buyer who fails to make payment to a Micro or Small enterprise within 45 days is legally liable to pay compound interest with monthly rests at <strong>three times the Bank Rate notified by the Reserve Bank of India</strong>.
                </Typography>

                <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                  Tribunal Procedure Before MSEFC (Facilitation Council):
                </Typography>
                <Stack spacing={1.2} sx={{ mb: 3 }}>
                  {[
                    'Step 1: Enterprise files delayed payment application online with Udyam number & tax invoices.',
                    'Step 2: Automated legal notice dispatched to the buyer (corporate, CPSE, or government entity).',
                    'Step 3: State Micro and Small Enterprises Facilitation Council (MSEFC) initiates conciliation.',
                    'Step 4: If conciliation fails, MSEFC acts as statutory arbitral tribunal with enforceable court decrees.',
                  ].map((s, i) => (
                    <Typography key={i} variant="body2" sx={{ color: '#334155', display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CheckCircleIcon sx={{ fontSize: 16, color: '#059669' }} />
                      {s}
                    </Typography>
                  ))}
                </Stack>

                <Button
                  variant="contained"
                  onClick={() => window.open('https://samadhaan.msme.gov.in', '_blank')}
                  endIcon={<OpenInNewIcon />}
                  sx={{ bgcolor: '#DC2626', color: '#FFFFFF', fontWeight: 700, textTransform: 'none', px: 3, py: 1.1, borderRadius: '8px' }}
                >
                  File Delayed Payment Case on Official SAMADHAAN Portal
                </Button>
              </Paper>
            </Grid>

            <Grid item xs={12} md={5}>
              <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FEF2F2', border: '1.5px solid #FECACA', height: '100%' }}>
                <Typography variant="h6" sx={{ fontWeight: 800, color: '#991B1B', mb: 1.5 }}>
                  Legal Rights Every MSME Should Know:
                </Typography>
                <Typography variant="body2" sx={{ color: '#7F1D1D', lineHeight: 1.7, mb: 2 }}>
                  • Buyer cannot withhold payment exceeding 45 days even if contract terms state longer periods.<br />
                  • If the buyer appeals an MSEFC order in High Court, they must pre-deposit <strong>75% of the awarded amount</strong>.<br />
                  • Section 43B(h) of the Income Tax Act disallows buyer expense deductions unless payments to MSEs are cleared within 45 days.
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        )}

        {/* TAB 2: SAMBANDH */}
        {currentTab === 'sambandh' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
              Public Procurement Policy Monitoring Portal (MSME SAMBANDH)
            </Typography>
            <Typography variant="body1" sx={{ color: '#334155', lineHeight: 1.8, mb: 3 }}>
              Monitors the mandatory 25% annual procurement by all Central Ministries, Departments, and Central Public Sector Enterprises (CPSEs) from Micro and Small Enterprises under the Public Procurement Policy Order 2012.
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                  <Typography variant="h3" sx={{ fontWeight: 900, color: '#0F2E59', mb: 0.5 }}>25%</Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>Overall Mandatory Procurement</Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>By every CPSE and Central Government Ministry annually.</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                  <Typography variant="h3" sx={{ fontWeight: 900, color: '#059669', mb: 0.5 }}>4%</Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#059669', mb: 1 }}>Reserved for SC/ST MSEs</Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>Monitored through the National SC-ST Hub (NSSH).</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                  <Typography variant="h3" sx={{ fontWeight: 900, color: '#7C3AED', mb: 0.5 }}>3%</Typography>
                  <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#7C3AED', mb: 1 }}>Reserved for Women MSEs</Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>Dedicated quotas for women owned and operated units.</Typography>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* TAB 3: CHAMPIONS */}
        {currentTab === 'champions' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
              MSME CHAMPIONS Unified Single-Window Control Room
            </Typography>
            <Typography variant="body1" sx={{ color: '#334155', lineHeight: 1.8, mb: 3 }}>
              <strong>C</strong>reation and <strong>H</strong>armonious <strong>A</strong>pplication of <strong>M</strong>odern <strong>P</strong>rocesses for <strong>I</strong>ncreasing the <strong>O</strong>utput and <strong>N</strong>ational <strong>S</strong>trength — a Hub & Spoke system linking the central MSME Ministry control room with 68 field stations across India.
            </Typography>
            <Grid container spacing={3}>
              {[
                { title: 'Grievance Resolution', desc: 'Resolves finance, regulatory, licensing, raw material, and labor issues within 7 business days.' },
                { title: 'Handholding New Units', desc: 'Direct guidance on DPR preparation, bank branch coordination, and PMEGP subsidy tracking.' },
                { title: 'National Hub-and-Spoke', desc: 'Connected directly with MSME-DFO Ahmedabad and DICs in all 33 Gujarat districts.' },
              ].map((c, i) => (
                <Grid item xs={12} md={4} key={i}>
                  <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', height: '100%' }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                      {c.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#64748B' }}>
                      {c.desc}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}

        {/* TAB 4: GUJARAT DIC NETWORK */}
        {currentTab === 'dic' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
              Gujarat District Industries Centres (DIC) Contact Network
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748B', mb: 3 }}>
              DICs are the primary district-level offices of the Gujarat Industries and Mines Department executing State MSME policies, SER grants, and PMEGP approvals:
            </Typography>
            <Grid container spacing={2.5}>
              {[
                { dist: 'Ahmedabad DIC', address: 'Bahumali Bhavan, Block A, 1st Floor, Near RTO, Ahmedabad - 380027', contact: '079-27552520 • dic-ahd@gujarat.gov.in' },
                { dist: 'Surat DIC', address: 'Nanpura Bahumali Bhavan, 4th Floor, Surat - 395001', contact: '0261-2465355 • dic-sur@gujarat.gov.in' },
                { dist: 'Rajkot DIC', address: 'Old Collector Office Compound, Rajkot - 360001', contact: '0281-2224033 • dic-raj@gujarat.gov.in' },
                { dist: 'Vadodara DIC', address: 'Narmada Bhavan, C-Block, 4th Floor, Vadodara - 390001', contact: '0265-2432240 • dic-vad@gujarat.gov.in' },
                { dist: 'Gandhinagar DIC', address: 'MSME Bhawan, Sector 11, Gandhinagar - 382017', contact: '079-23253500 • dic-gnr@gujarat.gov.in' },
                { dist: 'Bharuch DIC', address: 'District Industries Centre, Court Compound, Bharuch - 392001', contact: '02642-261543 • dic-bhr@gujarat.gov.in' },
              ].map((dic, idx) => (
                <Grid item xs={12} sm={6} md={4} key={idx}>
                  <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', height: '100%' }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 0.8 }}>
                      📍 {dic.dist}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#475569', display: 'block', mb: 1, lineHeight: 1.5 }}>
                      {dic.address}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#059669', fontWeight: 700, display: 'block' }}>
                      {dic.contact}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}

        {/* TAB 5: HELPDESK */}
        {currentTab === 'helpdesk' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
              Official National Helpline Numbers & Support Desks
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                    📞 Udyam National Toll-Free Support
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 900, color: '#059669', mb: 1 }}>
                    1800-180-6763
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B' }}>
                    Operational Monday to Friday, 9:30 AM to 6:00 PM IST (Excluding National Holidays).
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                    📧 Official Email Helpdesk
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 900, color: '#2563EB', mb: 1 }}>
                    support-udyamniti@msme.gov.in
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B' }}>
                    Response turnaround time: Within 24-48 business hours with ticket tracking.
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        )}
      </Container>
    </Box>
  )
}

export default SupportPage
