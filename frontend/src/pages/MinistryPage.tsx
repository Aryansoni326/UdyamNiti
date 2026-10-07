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
  Divider,
  Button,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import GroupIcon from '@mui/icons-material/Group'
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter'
import AssessmentIcon from '@mui/icons-material/Assessment'
import ArticleIcon from '@mui/icons-material/Article'
import ContactPhoneIcon from '@mui/icons-material/ContactPhone'
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import { useLanguage } from '../i18n'

export const MinistryPage: React.FC = () => {
  const navigate = useNavigate()
  const { t } = useLanguage()
  const [searchParams, setSearchParams] = useSearchParams()
  const initialTab = searchParams.get('tab') || 'about'
  const [currentTab, setCurrentTab] = useState<string>(initialTab)

  useEffect(() => {
    const tabParam = searchParams.get('tab')
    if (tabParam) {
      setCurrentTab(tabParam)
    }
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
          borderBottom: '4px solid #E65100',
        }}
      >
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Stack spacing={1.5} sx={{ maxWidth: 900 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={<AccountBalanceIcon sx={{ color: '#FEF08A !important', fontSize: '15px !important' }} />}
                label="Government of India • Ministry of MSME"
                size="small"
                sx={{
                  bgcolor: 'rgba(255, 255, 255, 0.15)',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                }}
              />
              <Chip
                label="Official Institutional Portal"
                size="small"
                sx={{
                  bgcolor: 'rgba(230, 81, 0, 0.25)',
                  color: '#FED7AA',
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
              Ministry of Micro, Small & Medium Enterprises
            </Typography>

            <Typography
              variant="body1"
              sx={{
                color: '#CBD5E1',
                fontSize: { xs: '0.98rem', md: '1.1rem' },
                lineHeight: 1.6,
              }}
            >
              The apex executive body of the Government of India responsible for formulating policies, administering statutory credit & capital schemes, building cluster infrastructure, and accelerating competitiveness across India's 63+ million MSMEs.
            </Typography>
          </Stack>
        </Container>
      </Box>

      {/* Navigation Tabs Bar */}
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
                '&.Mui-selected': { color: '#0F2E59', fontWeight: 800 },
              },
              '& .MuiTabs-indicator': { bgcolor: '#0F2E59', height: 3 },
            }}
          >
            <Tab value="about" label="About Ministry" icon={<AccountBalanceIcon fontSize="small" />} iconPosition="start" />
            <Tab value="vision" label="Vision & Mission" icon={<TrendingUpIcon fontSize="small" />} iconPosition="start" />
            <Tab value="leadership" label="Ministers & Leadership" icon={<GroupIcon fontSize="small" />} iconPosition="start" />
            <Tab value="organisations" label="Attached & Autonomous Bodies" icon={<BusinessCenterIcon fontSize="small" />} iconPosition="start" />
            <Tab value="divisions" label="Departments & Divisions" icon={<AssessmentIcon fontSize="small" />} iconPosition="start" />
            <Tab value="overview" label="National MSME Contribution" icon={<ArticleIcon fontSize="small" />} iconPosition="start" />
            <Tab value="directory" label="Key Contacts & Offices" icon={<ContactPhoneIcon fontSize="small" />} iconPosition="start" />
          </Tabs>
        </Container>
      </Box>

      {/* Main Content Sections */}
      <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 }, mt: 4 }}>
        {/* 1. ABOUT MINISTRY */}
        {currentTab === 'about' && (
          <Grid container spacing={3.5}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0', mb: 3 }}>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
                  Role & Constitutional Mandate
                </Typography>
                <Typography variant="body1" sx={{ color: '#334155', lineHeight: 1.8, mb: 2.5 }}>
                  The Ministry of Micro, Small and Medium Enterprises (M/o MSME) is the nodal ministry for designing, orchestrating, and monitoring statutory policies that foster the sustainable growth of Micro, Small, and Medium Enterprises throughout the country.
                </Typography>
                <Typography variant="body1" sx={{ color: '#334155', lineHeight: 1.8, mb: 3 }}>
                  In accordance with the <strong>Micro, Small and Medium Enterprises Development (MSMED) Act, 2006</strong>, the Ministry facilitates credit flow, technology upgradation, entrepreneurship development, cluster development, market access, and quality certification.
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                        🏛️ National MSME Board
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#64748B', lineHeight: 1.6 }}>
                        Apex consultative forum established under Section 3 of the MSMED Act to review national policies, credit flow, and inter-state coordination.
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#059669', mb: 1 }}>
                        🤝 State Government Partnership
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#64748B', lineHeight: 1.6 }}>
                        Collaborates with State Directorates (such as Gujarat Industries and Mines Dept) to co-finance regional parks, cluster infrastructure, and export corridors.
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Paper>

              <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
                  Statutory Composite Criteria (Notification S.O. 2119(E))
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead sx={{ bgcolor: '#F1F5F9' }}>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 800, color: '#0F2E59' }}>Enterprise Classification</TableCell>
                        <TableCell sx={{ fontWeight: 800, color: '#0F2E59' }}>Investment in Plant & Machinery</TableCell>
                        <TableCell sx={{ fontWeight: 800, color: '#0F2E59' }}>Annual Turnover</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 700, color: '#059669' }}>Micro Enterprise</TableCell>
                        <TableCell>Not exceeding ₹1.00 Crore</TableCell>
                        <TableCell>Not exceeding ₹5.00 Crore</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 700, color: '#2563EB' }}>Small Enterprise</TableCell>
                        <TableCell>Not exceeding ₹10.00 Crore</TableCell>
                        <TableCell>Not exceeding ₹50.00 Crore</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell sx={{ fontWeight: 700, color: '#7C3AED' }}>Medium Enterprise</TableCell>
                        <TableCell>Not exceeding ₹50.00 Crore</TableCell>
                        <TableCell>Not exceeding ₹250.00 Crore</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
                <Typography variant="caption" sx={{ color: '#64748B', mt: 1.5, display: 'block' }}>
                  *Export turnover is exempted from calculation of turnover limits for all categories as per Gazette notification dated 26th June 2020.
                </Typography>
              </Paper>
            </Grid>

            {/* Right Quick Links */}
            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: '16px', border: '1px solid #E2E8F0', mb: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
                    Official Portals & Networks
                  </Typography>
                  <Stack spacing={1.5}>
                    {[
                      { name: 'Udyam Registration Portal', url: 'https://udyamregistration.gov.in', tag: 'Zero Fee • Official' },
                      { name: 'MSME SAMADHAAN (Delayed Payment)', url: 'https://samadhaan.msme.gov.in', tag: 'Statutory Redressal' },
                      { name: 'MSME SAMBANDH (Procurement)', url: 'https://sambandh.msme.gov.in', tag: '25% Mandatory CPSE' },
                      { name: 'MSME CHAMPIONS Control Room', url: 'https://champions.gov.in', tag: 'Multi-lingual Help' },
                      { name: 'CGTMSE Trust Portal', url: 'https://www.cgtmse.in', tag: '₹10 Cr Guarantee' },
                    ].map((link, idx) => (
                      <Paper
                        key={idx}
                        sx={{
                          p: 1.8,
                          bgcolor: '#F8FAFC',
                          border: '1px solid #E2E8F0',
                          borderRadius: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          cursor: 'pointer',
                          '&:hover': { borderColor: '#0F2E59', bgcolor: '#FFFFFF' },
                        }}
                        onClick={() => window.open(link.url, '_blank')}
                      >
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 700, color: '#0F2E59' }}>
                            {link.name}
                          </Typography>
                          <Typography variant="caption" sx={{ color: '#059669', fontWeight: 600 }}>
                            {link.tag}
                          </Typography>
                        </Box>
                        <OpenInNewIcon sx={{ fontSize: 16, color: '#64748B' }} />
                      </Paper>
                    ))}
                  </Stack>
                </CardContent>
              </Card>

              <Card sx={{ borderRadius: '16px', border: '1px solid #E2E8F0', bgcolor: '#FFF7ED' }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#9A3412', mb: 1 }}>
                    Official Schemes Corpus
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#7C2D12', lineHeight: 1.6, mb: 2.5 }}>
                    11 Verified Central & Gujarat State operational guidelines archived with deterministic eligibility reasoning.
                  </Typography>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={() => navigate('/resources')}
                    sx={{ bgcolor: '#EA580C', color: '#FFFFFF', fontWeight: 700, textTransform: 'none', borderRadius: '8px' }}
                  >
                    View Official Guidelines & PDFs →
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* 2. VISION & MISSION */}
        {currentTab === 'vision' && (
          <Grid container spacing={3.5}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#ECFDF5', border: '1.5px solid #A7F3D0', height: '100%' }}>
                <Chip label="OUR VISION" sx={{ bgcolor: '#065F46', color: '#FFFFFF', fontWeight: 800, mb: 2 }} />
                <Typography variant="h4" sx={{ fontWeight: 800, color: '#065F46', mb: 2 }}>
                  Empowered, Globally Competitive & Sustainable Indian MSMEs
                </Typography>
                <Typography variant="body1" sx={{ color: '#047857', lineHeight: 1.8, fontSize: '1.05rem' }}>
                  To establish vibrant, innovative, and resilient Micro, Small, and Medium Enterprises that anchor India's self-reliance (Atmanirbhar Bharat), power inclusive employment, and integrate seamlessly into global supply chains.
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#EFF6FF', border: '1.5px solid #BFDBFE', height: '100%' }}>
                <Chip label="OUR MISSION" sx={{ bgcolor: '#1D4ED8', color: '#FFFFFF', fontWeight: 800, mb: 2 }} />
                <Typography variant="h4" sx={{ fontWeight: 800, color: '#1D4ED8', mb: 2 }}>
                  Catalyzing Credit, Technology & Industrial Infrastructure
                </Typography>
                <Typography variant="body1" sx={{ color: '#1E40AF', lineHeight: 1.8, fontSize: '1.05rem' }}>
                  To promote MSME competitiveness by facilitating seamless access to collateral-free institutional credit, zero-defect quality standards, shared manufacturing infrastructure, entrepreneurship incubation, and export enablement.
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={12}>
              <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0', mt: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 3 }}>
                  7 Strategic National Pillars
                </Typography>
                <Grid container spacing={2.5}>
                  {[
                    { title: '1. Credit Assurance & Liquidity', desc: 'CGTMSE guarantee pool expanded to ₹10 Crore; invoice discounting under TReDS.', icon: '💰' },
                    { title: '2. Technology Modernization', desc: 'MSME Sustainable (ZED) certification up to 80% subsidy and 18 Tool Rooms nationwide.', icon: '⚙️' },
                    { title: '3. Cluster Infrastructure', desc: 'MSE-CDP and SFURTI grant assistance up to ₹30 Crore for Common Facility Centres.', icon: '🏭' },
                    { title: '4. Entrepreneurship & Employment', desc: 'PMEGP margin money subsidies up to ₹50 Lakh for new manufacturing units.', icon: '🚀' },
                    { title: '5. Public Procurement Shield', desc: '25% mandatory purchase from MSEs by all Central Ministries & CPSEs via SAMBANDH.', icon: '🛡️' },
                    { title: '6. Timely Payments Enforcement', desc: 'Section 16-18 compound interest at 3x RBI bank rate for delays past 45 days.', icon: '⚖️' },
                    { title: '7. Export Market Promotion', desc: 'International Cooperation (IC) airfare subsidy & DGFT export credit risk coverage.', icon: '🌐' },
                  ].map((pillar, idx) => (
                    <Grid item xs={12} sm={6} md={3.4} key={idx}>
                      <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', height: '100%' }}>
                        <Typography variant="h4" sx={{ mb: 1 }}>{pillar.icon}</Typography>
                        <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 0.8 }}>
                          {pillar.title}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#64748B', lineHeight: 1.5 }}>
                          {pillar.desc}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        )}

        {/* 3. LEADERSHIP */}
        {currentTab === 'leadership' && (
          <Grid container spacing={3.5}>
            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: '16px', border: '1.5px solid #0F2E59', height: '100%', bgcolor: '#FFFFFF' }}>
                <CardContent sx={{ p: 3.5, textAlign: 'center' }}>
                  <Avatar sx={{ width: 90, height: 90, bgcolor: '#0F2E59', mx: 'auto', mb: 2, fontSize: '2rem', fontWeight: 800 }}>
                    JM
                  </Avatar>
                  <Typography variant="caption" sx={{ fontWeight: 800, color: '#E65100', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                    Cabinet Minister
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 900, color: '#0F2E59', mt: 0.5, mb: 1 }}>
                    Shri Jitan Ram Manjhi
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', fontWeight: 600, mb: 2 }}>
                    Union Minister for Micro, Small and Medium Enterprises
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="body2" sx={{ color: '#334155', textAlign: 'left', lineHeight: 1.6 }}>
                    Directs national policy formulation, statutory approvals, and overall Cabinet stewardship of MSME growth agendas, credit guarantees, and rural industrialization.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: '16px', border: '1.5px solid #E2E8F0', height: '100%', bgcolor: '#FFFFFF' }}>
                <CardContent sx={{ p: 3.5, textAlign: 'center' }}>
                  <Avatar sx={{ width: 90, height: 90, bgcolor: '#059669', mx: 'auto', mb: 2, fontSize: '2rem', fontWeight: 800 }}>
                    SS
                  </Avatar>
                  <Typography variant="caption" sx={{ fontWeight: 800, color: '#059669', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                    Minister of State
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 900, color: '#0F2E59', mt: 0.5, mb: 1 }}>
                    Sushri Shobha Karandlaje
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', fontWeight: 600, mb: 2 }}>
                    Minister of State for Micro, Small and Medium Enterprises
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="body2" sx={{ color: '#334155', textAlign: 'left', lineHeight: 1.6 }}>
                    Oversees implementation of women entrepreneurship initiatives, cluster development, technology upgradation schemes, and inter-state industry liaison.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: '16px', border: '1.5px solid #E2E8F0', height: '100%', bgcolor: '#FFFFFF' }}>
                <CardContent sx={{ p: 3.5, textAlign: 'center' }}>
                  <Avatar sx={{ width: 90, height: 90, bgcolor: '#2563EB', mx: 'auto', mb: 2, fontSize: '2rem', fontWeight: 800 }}>
                    SC
                  </Avatar>
                  <Typography variant="caption" sx={{ fontWeight: 800, color: '#2563EB', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
                    Executive Administrative Head
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 900, color: '#0F2E59', mt: 0.5, mb: 1 }}>
                    Shri Subhash Chandra Lal Das
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', fontWeight: 600, mb: 2 }}>
                    Secretary, Ministry of MSME (IAS)
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="body2" sx={{ color: '#334155', textAlign: 'left', lineHeight: 1.6 }}>
                    Leads administrative apparatus, fiscal disbursements, inter-ministerial taskforces, and operational supervision of attached autonomous organizations.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* 4. ATTACHED & AUTONOMOUS ORGANISATIONS */}
        {currentTab === 'organisations' && (
          <Grid container spacing={3}>
            {[
              {
                acronym: 'KVIC',
                title: 'Khadi & Village Industries Commission',
                hq: 'Mumbai',
                desc: 'Statutory body established under KVIC Act 1956. Apex executing agency for PMEGP margin money subsidies, rural employment generation, and traditional khadi artisans.',
                highlight: 'Nodal Agency for PMEGP (₹50 Lakh Subsidy)',
                color: '#D97706',
              },
              {
                acronym: 'Coir Board',
                title: 'Coir Board of India',
                hq: 'Kochi, Kerala',
                desc: 'Statutory body for promoting coir industry development, coir export incentives, Mahila Coir Yojana training stipends, and natural fiber product modernization.',
                highlight: 'CVY Capital Grant up to ₹25 Lakh',
                color: '#16A34A',
              },
              {
                acronym: 'NSIC',
                title: 'National Small Industries Corporation',
                hq: 'New Delhi',
                desc: 'Mini-Ratna CPSE facilitating raw material assistance, single point registration for government tenders, consortia marketing, and National SC-ST Hub (NSSH).',
                highlight: 'Raw Material Finance & GeM Facilitation',
                color: '#2563EB',
              },
              {
                acronym: 'ni-msme',
                title: 'National Institute for MSME',
                hq: 'Hyderabad',
                desc: 'Pioneering apex institution for entrepreneurship policy research, capacity building, cluster development consultancy, and enterprise incubation.',
                highlight: 'Enterprise Incubation & Training Center',
                color: '#7C3AED',
              },
              {
                acronym: 'MGIRI',
                title: 'Mahatma Gandhi Institute for Rural Industrialization',
                hq: 'Wardha, Maharashtra',
                desc: 'Dedicated R&D institution accelerating technical research, bio-processing, solar appliances, and khadi innovation for rural micro-enterprises.',
                highlight: 'Rural Engineering & Eco-Technology R&D',
                color: '#0891B2',
              },
              {
                acronym: 'TCs / Tool Rooms',
                title: '18 MSME Technology Centres',
                hq: 'Pan-India (Ahmedabad, Indo-German, etc.)',
                desc: 'Precision tooling, CAD/CAM prototyping, testing calibration, and certified skill training in manufacturing, robotics, dies & moulds.',
                highlight: 'Advanced Tooling, Prototyping & CAD/CAM',
                color: '#DC2626',
              },
            ].map((org, i) => (
              <Grid item xs={12} sm={6} md={4} key={i}>
                <Paper
                  sx={{
                    p: 3,
                    borderRadius: '14px',
                    bgcolor: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    '&:hover': { borderColor: org.color, boxShadow: '0 6px 18px rgba(0,0,0,0.06)' },
                  }}
                >
                  <Box>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
                      <Chip label={org.acronym} sx={{ bgcolor: org.color, color: '#FFFFFF', fontWeight: 800 }} />
                      <Typography variant="caption" sx={{ color: '#64748B', fontWeight: 600 }}>
                        HQ: {org.hq}
                      </Typography>
                    </Stack>
                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                      {org.title}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#64748B', lineHeight: 1.6, mb: 2 }}>
                      {org.desc}
                    </Typography>
                  </Box>
                  <Paper sx={{ p: 1.2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
                    <Typography variant="caption" sx={{ fontWeight: 800, color: org.color }}>
                      ★ {org.highlight}
                    </Typography>
                  </Paper>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}

        {/* 5. DEPARTMENTS & DIVISIONS */}
        {currentTab === 'divisions' && (
          <Grid container spacing={3}>
            {[
              {
                title: 'Office of the Development Commissioner (DC-MSME)',
                desc: 'The principal field organization providing extension services, operating MSME Development Facilitation Offices (MSME-DFO) in all States and Union Territories.',
                tasks: ['MSE-CDP Cluster execution', 'ZED scheme administration', 'Procurement & Marketing Support (PMS)', 'RAMP programme coordination'],
              },
              {
                title: 'SME Division (Small & Medium Enterprise)',
                desc: 'Formulates statutory policy frameworks, composite criteria definitions, credit policies with RBI/DFS, and administers CGTMSE trust guidelines.',
                tasks: ['Credit guarantee expansion', 'TReDS framework integration', 'Emergency credit line monitoring', 'Bank branch MSME performance reviews'],
              },
              {
                title: 'ARI Division (Agro & Rural Industry)',
                desc: 'Supervises Khadi and Village Industries, honey mission, coir cultivation, and traditional cluster regeneration across rural belts.',
                tasks: ['PMEGP policy amendments', 'SFURTI cluster sanctions', 'Mahila Coir Yojana', 'Honey & Village Industry programmes'],
              },
              {
                title: 'Data & Statistics / Policy Monitoring Division',
                desc: 'Manages the national Udyam Registration database, releases quarterly economic reports, and oversees MSME SAMADHAAN & SAMBANDH monitoring portals.',
                tasks: ['Udyam API verification', 'Delayed payment tribunal monitoring', 'Public procurement compliance', 'Economic survey inputs'],
              },
            ].map((div, i) => (
              <Grid item xs={12} md={6} key={i}>
                <Paper sx={{ p: 3.5, borderRadius: '14px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0', height: '100%' }}>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                    {div.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', lineHeight: 1.6, mb: 2.5 }}>
                    {div.desc}
                  </Typography>
                  <Typography variant="caption" sx={{ fontWeight: 800, color: '#0F2E59', display: 'block', mb: 1 }}>
                    Key Operational Responsibilities:
                  </Typography>
                  <Stack spacing={0.8}>
                    {div.tasks.map((task, idx) => (
                      <Typography key={idx} variant="caption" sx={{ color: '#334155', display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CheckCircleIcon sx={{ fontSize: 14, color: '#059669' }} />
                        {task}
                      </Typography>
                    ))}
                  </Stack>
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}

        {/* 6. NATIONAL OVERVIEW */}
        {currentTab === 'overview' && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0', mb: 3 }}>
                <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
                  MSME Contribution to India's Economic Engine
                </Typography>
                <Typography variant="body1" sx={{ color: '#334155', lineHeight: 1.8, mb: 3 }}>
                  Recognized globally as the powerhouse of the Indian economy, the Micro, Small and Medium Enterprises sector contributes substantially to industrial output, export earnings, and massive employment generation across tier-2, tier-3, and rural clusters.
                </Typography>

                <Grid container spacing={2.5}>
                  {[
                    { stat: '6.3+ Crore', label: 'Registered Enterprises', desc: 'Across manufacturing and services sectors' },
                    { stat: '~30%', label: 'Contribution to Indian GDP', desc: 'Anchor of domestic economic value add' },
                    { stat: '45%+', label: 'Total Manufacturing Output', desc: 'Critical supply chain supplier base' },
                    { stat: '40%+', label: 'Total Indian Exports', desc: 'Engineering, textiles, chemicals, handicrafts' },
                    { stat: '11+ Crore', label: 'Employment Generated', desc: 'Second largest employer after agriculture' },
                    { stat: '₹5+ Lakh Cr', label: 'Guaranteed Credit Cumulative', desc: 'Under CGTMSE & sovereign trust funds' },
                  ].map((item, idx) => (
                    <Grid item xs={12} sm={6} md={4} key={idx}>
                      <Paper sx={{ p: 2.5, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                        <Typography variant="h4" sx={{ fontWeight: 900, color: '#0F2E59', mb: 0.5 }}>
                          {item.stat}
                        </Typography>
                        <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#E65100', mb: 0.5 }}>
                          {item.label}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#64748B' }}>
                          {item.desc}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Paper>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: '16px', border: '1px solid #E2E8F0', bgcolor: '#FFFFFF' }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
                    Flagship Central & State Schemes
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', lineHeight: 1.6, mb: 2 }}>
                    Browse our structured directory of verified guidelines archived in this gateway:
                  </Typography>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={() => navigate('/schemes')}
                    endIcon={<ArrowForwardIcon />}
                    sx={{ bgcolor: '#0F2E59', color: '#FFFFFF', fontWeight: 700, textTransform: 'none', py: 1.2, borderRadius: '8px' }}
                  >
                    Explore Schemes Directory
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* 7. DIRECTORY & KEY CONTACTS */}
        {currentTab === 'directory' && (
          <Paper sx={{ p: 4, borderRadius: '16px', bgcolor: '#FFFFFF', border: '1px solid #E2E8F0' }}>
            <Typography variant="h5" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2 }}>
              Ministry Headquarters & Contact Directory
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1 }}>
                    📍 Ministry Headquarters
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#334155', lineHeight: 1.7 }}>
                    Udyog Bhawan, Rafi Marg,<br />
                    New Delhi - 110011, India<br />
                    Toll-Free Udyam Helpline: <strong>1800-180-6763</strong><br />
                    Official Email: <strong>sec-msme@nic.in</strong>
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px' }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 800, color: '#059669', mb: 1 }}>
                    🏢 Gujarat State Liaison (MSME-DFO Ahmedabad)
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#334155', lineHeight: 1.7 }}>
                    MSME-Development & Facilitation Office,<br />
                    Harsiddh Chambers, 4th Floor, Ashram Road,<br />
                    Ahmedabad - 380014, Gujarat<br />
                    Phone: <strong>079-27540619 / 27544248</strong>
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

export default MinistryPage
