import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Chip,
  Card,
  CardContent,
  Grid,
  Stack,
  Stepper,
  Step,
  StepLabel,
  InputAdornment,
  IconButton,
  Tooltip,
  Alert,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  alpha,
  Divider,
} from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing'
import DomainAddIcon from '@mui/icons-material/DomainAdd'
import PublicIcon from '@mui/icons-material/Public'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'
import SolarPowerIcon from '@mui/icons-material/SolarPower'
import WorkspacePremiumIcon from '@mui/icons-material/WorkspacePremium'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import EditOutlinedIcon from '@mui/icons-material/EditOutlined'
import CheckCircleOutlinedIcon from '@mui/icons-material/CheckCircleOutlined'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import TranslateIcon from '@mui/icons-material/Translate'
import BoltIcon from '@mui/icons-material/Bolt'
import ClearIcon from '@mui/icons-material/Clear'
import { tokens } from '../theme/tokens'
import { apiClient } from '../api/client'
import { StatusChip } from '../components/StatusChip'
import { EvidenceBadge } from '../components/EvidenceBadge'
import { toast } from 'sonner'

// ─── Preset Goals & Translations ──────────────────────────────────────────────

interface GoalPreset {
  label: string
  labelGu: string
  fullGoal: string
  fullGoalGu: string
  projectType: string
  investmentLakhs: number
  supportCategories: string[]
  icon: React.ReactElement
}

const GOAL_PRESETS: GoalPreset[] = [
  {
    label: 'Buy new machinery',
    labelGu: 'નવી મશીનરી ખરીદો',
    fullGoal: 'I want to purchase a ₹50 lakh CNC machine to expand production capacity for precision engineering components.',
    fullGoalGu: 'હું પ્રિસિઝન એન્જિનિયરિંગ પાર્ટ્સના ઉત્પાદન માટે ₹50 લાખનું CNC મશીન ખરીદવા માંગુ છું.',
    projectType: 'machinery_purchase',
    investmentLakhs: 50,
    supportCategories: ['capital_subsidy', 'credit_guarantee', 'technology_adoption'],
    icon: <PrecisionManufacturingIcon sx={{ fontSize: 18 }} />,
  },
  {
    label: 'Expand factory floor',
    labelGu: 'ફેક્ટરી વિસ્તરણ',
    fullGoal: 'We plan to construct an additional manufacturing bay and invest ₹1.5 crore in modern automated plant equipment.',
    fullGoalGu: 'અમે ફેક્ટરીનું વિસ્તરણ કરવા અને આધુનિક ઓટોમેટેડ પ્લાન્ટમાં ₹1.5 કરોડનું રોકાણ કરવા માંગીએ છીએ.',
    projectType: 'expansion_new_unit',
    investmentLakhs: 150,
    supportCategories: ['capital_subsidy', 'interest_subvention', 'infrastructure_grant'],
    icon: <DomainAddIcon sx={{ fontSize: 18 }} />,
  },
  {
    label: 'Start exporting',
    labelGu: 'નિકાસ શરૂ કરો',
    fullGoal: 'We want to expand into international markets and need working capital of ₹40 lakh plus export freight incentives.',
    fullGoalGu: 'અમે આંતરરાષ્ટ્રીય બજારોમાં પ્રવેશવા માંગીએ છીએ અને ₹40 લાખ વર્કિંગ કેપિટલ તેમજ એક્સપોર્ટ ઇન્સેન્ટિવ્સની જરૂર છે.',
    projectType: 'export_expansion',
    investmentLakhs: 40,
    supportCategories: ['export_incentive', 'market_development', 'collateral_free_credit'],
    icon: <PublicIcon sx={{ fontSize: 18 }} />,
  },
  {
    label: 'Get collateral-free loan',
    labelGu: 'કોલેટરલ-મુક્ત લોન',
    fullGoal: 'Need ₹30 lakh collateral-free bank credit for working capital and raw material procurement for sudden orders.',
    fullGoalGu: 'ઓર્ડર પૂરા કરવા માટે કાચા માલ અને વર્કિંગ કેપિટલ માટે ₹30 લાખની કોલેટરલ-મુક્ત બેંક ક્રેડિટ જોઈએ છે.',
    projectType: 'working_capital',
    investmentLakhs: 30,
    supportCategories: ['collateral_free_credit', 'interest_subvention'],
    icon: <AccountBalanceIcon sx={{ fontSize: 18 }} />,
  },
  {
    label: 'Reduce energy cost',
    labelGu: 'ઊર્જા ખર્ચ ઘટાડો',
    fullGoal: 'Install a 100 kW rooftop solar PV installation to lower high monthly manufacturing electricity bills.',
    fullGoalGu: 'માસિક વીજળી બિલ ઘટાડવા માટે અમારી ફેક્ટરીની છત પર 100 kW સોલાર પાવર પ્લાન્ટ સ્થાપિત કરવો છે.',
    projectType: 'green_energy',
    investmentLakhs: 35,
    supportCategories: ['capital_subsidy', 'technology_adoption'],
    icon: <SolarPowerIcon sx={{ fontSize: 18 }} />,
  },
  {
    label: 'Obtain certifications',
    labelGu: 'સર્ટિફિકેશન મેળવો',
    fullGoal: 'Implement ZED Gold certification and ISO 9001:2015 quality standards for government procurement eligibility.',
    fullGoalGu: 'સરકારી ટેન્ડરોમાં ભાગ લેવા માટે ZED ગોલ્ડ અને ISO 9001 ક્વોલિટી સર્ટિફિકેશન મેળવવું છે.',
    projectType: 'quality_certification',
    investmentLakhs: 8,
    supportCategories: ['quality_certification', 'market_development'],
    icon: <WorkspacePremiumIcon sx={{ fontSize: 18 }} />,
  },
]

const GUJARAT_DISTRICTS = [
  'Ahmedabad',
  'Rajkot',
  'Surat',
  'Vadodara',
  'Jamnagar',
  'Bhavnagar',
  'Gandhinagar',
  'Anand',
  'Bharuch',
  'Morbi',
  'Kutch',
  'Surendranagar',
  'Other District / State',
]

// ─── Goal Onboarding Component ────────────────────────────────────────────────

export const GoalOnboarding: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const [lang, setLang] = useState<'en' | 'gu'>('en')

  // Step state: 0 = Goal Input & Structured Review, 1 = Targeted Profiling, 2 = Generating Strategy
  const [activeStep, setActiveStep] = useState(0)

  // Goal & Parsing State
  const initialPrefill = (location.state as any)?.prefillGoal || ''
  const [goalText, setGoalText] = useState(initialPrefill)
  const [isEditingStructured, setIsEditingStructured] = useState(false)
  const [parsedObjective, setParsedObjective] = useState(initialPrefill)
  const [parsedProjectType, setParsedProjectType] = useState('machinery_purchase')
  const [parsedInvestmentLakhs, setParsedInvestmentLakhs] = useState<number>(50)
  const [parsedSupportCategories, setParsedSupportCategories] = useState<string[]>([
    'capital_subsidy',
    'credit_guarantee',
    'technology_adoption',
  ])

  // Targeted Follow-up Profiling State
  const [msmeCategory, setMsmeCategory] = useState<'micro' | 'small' | 'medium' | 'unknown'>('small')
  const [stateName, setStateName] = useState('Gujarat')
  const [district, setDistrict] = useState('Ahmedabad')
  const [isManufacturing, setIsManufacturing] = useState(true)
  const [isWomenOwned, setIsWomenOwned] = useState(false)
  const [isScStOwned, setIsScStOwned] = useState(false)
  const [hasNpaHistory, setHasNpaHistory] = useState<'no' | 'yes' | 'unknown'>('no')
  const [businessName, setBusinessName] = useState('ABC Precision Components')

  // Analysis / Loading state
  const [submitting, setSubmitting] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisStepLabel, setAnalysisStepLabel] = useState('Initializing...')

  // Automatically update structured fields when goal changes
  const applyPreset = (preset: GoalPreset) => {
    const text = lang === 'gu' ? preset.fullGoalGu : preset.fullGoal
    setGoalText(text)
    setParsedObjective(text)
    setParsedProjectType(preset.projectType)
    setParsedInvestmentLakhs(preset.investmentLakhs)
    setParsedSupportCategories(preset.supportCategories)
  }

  // Pre-fill default benchmark on load if empty
  useEffect(() => {
    if (!goalText) {
      if (initialPrefill) {
        setGoalText(initialPrefill)
        setParsedObjective(initialPrefill)
      } else {
        applyPreset(GOAL_PRESETS[0])
      }
    }
  }, [lang])

  // Quick 1-Click Demo CNC Benchmark
  const handleLoadDemoBenchmark = () => {
    applyPreset(GOAL_PRESETS[0])
    setMsmeCategory('small')
    setStateName('Gujarat')
    setDistrict('Ahmedabad')
    setIsManufacturing(true)
    setIsWomenOwned(false)
    setIsScStOwned(false)
    setHasNpaHistory('no')
    setBusinessName('ABC Precision Tooling LLP')
    toast.success('Loaded benchmark: ₹50 Lakh CNC Machine (Ahmedabad Small Enterprise)')
  }

  // Execute Pipeline & Strategy Generation
  const handleGenerateStrategy = async () => {
    setSubmitting(true)
    setActiveStep(2)

    const steps = [
      { label: 'Interpreting goal intent & material facts (Goal Agent)...', pct: 20 },
      { label: 'Querying official Central & Gujarat Gazette sources (Hybrid RAG)...', pct: 40 },
      { label: 'Evaluating deterministic boolean rules against enterprise facts (Rule Engine)...', pct: 60 },
      { label: 'Mapping cross-scheme stacking & prerequisite unlocks (Relationship Engine)...', pct: 80 },
      { label: 'Synthesizing evidence-backed strategy and topological action plan...', pct: 95 },
    ]

    for (const s of steps) {
      setAnalysisStepLabel(s.label)
      setAnalysisProgress(s.pct)
      await new Promise((r) => setTimeout(r, 450))
    }

    try {
      // Generate client correlation ID for full request tracing
      const correlationId = 'corr_' + Math.random().toString(36).substring(2, 10)

      // 1. Auto login / get demo context
      const demoRes = await apiClient.demoLogin().catch(() => null)
      const fallbackDemoProfileId = demoRes?.data?.profile_id || ''

      // 2. Fetch or create a profile with the targeted facts
      const profileData = {
        business_name: businessName || 'Enterprise ' + Math.floor(Math.random() * 1000),
        msme_category: msmeCategory === 'unknown' ? 'small' : msmeCategory,
        entity_type: 'proprietorship',
        industry_sector: isManufacturing ? 'Manufacturing / Precision Engineering' : 'Services',
        state: stateName,
        district: district,
        investment_in_plant_machinery_lakhs: parsedInvestmentLakhs,
        annual_turnover_lakhs: parsedInvestmentLakhs * 3,
        is_women_owned: isWomenOwned,
        is_sc_st_owned: isScStOwned,
        is_npa: hasNpaHistory === 'yes',
        has_bank_account: true,
        has_existing_loan: false,
      }

      let profileId = ''
      try {
        const createRes = await apiClient.createProfile(profileData as any)
        profileId = createRes.data?.id || ''
      } catch {
        // Fallback to existing profiles
        try {
          const listRes = await apiClient.getProfiles()
          const profiles = listRes.data?.results || (listRes.data as any)
          profileId = profiles?.[0]?.id || ''
        } catch {}
      }

      if (!profileId) {
        profileId = fallbackDemoProfileId
      }

      // 3. Submit the goal with correlation ID
      const submitRes = await apiClient.submitGoal(profileId, goalText, correlationId)
      let strategyId = submitRes.data?.strategy_id
      const finalCorrelationId = submitRes.data?.correlation_id || correlationId

      if (!strategyId && submitRes.data?.goal?.id) {
        try {
          const stratRes = await apiClient.getStrategyForGoal(submitRes.data.goal.id)
          strategyId = stratRes.data?.id
        } catch {}
      }

      if (strategyId) {
        setAnalysisProgress(100)
        setAnalysisStepLabel('Strategy Ready! Loading decision landscape...')
        await new Promise((r) => setTimeout(r, 300))

        toast.success('Evidence-backed strategy formulated successfully!')
        navigate(`/strategy/${strategyId}`, { state: { correlationId: finalCorrelationId } })
        return
      } else {
        throw new Error('Strategy ID was not returned by the server.')
      }
    } catch (err: any) {
      console.error('Goal submission error:', err)
      // Resilient recovery: try to find any ready goal & strategy
      try {
        const goalsRes = await apiClient.getGoals()
        const goals = goalsRes.data?.results || (goalsRes.data as any)
        const readyGoal = Array.isArray(goals) ? goals.find((g: any) => g.status === 'ready') : null
        if (readyGoal) {
          const stratRes = await apiClient.getStrategyForGoal(readyGoal.id)
          if (stratRes.data?.id) {
            toast.info('Loaded existing strategy roadmap.')
            navigate(`/strategy/${stratRes.data.id}`)
            return
          }
        }
      } catch {}

      const errorMsg =
        err?.response?.data?.error ||
        err?.response?.data?.detail ||
        err?.message ||
        'Unable to synthesize strategy. Please check your inputs and try again.'
      toast.error(errorMsg)
      setActiveStep(1)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Box sx={{ minHeight: '85vh', py: { xs: 3, md: 5 } }}>
      <Container maxWidth="lg">
        {/* Top Control Bar: Language & Benchmark Fast-Track */}
        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 4, flexWrap: 'wrap', gap: 1.5 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip
              icon={<AutoAwesomeIcon sx={{ color: tokens.color.violet[300], fontSize: 16 }} />}
              label="Goal-First MSME Intelligence"
              size="small"
              sx={{
                bgcolor: alpha(tokens.color.violet[500], 0.15),
                color: tokens.color.violet[300],
                border: `1px solid ${alpha(tokens.color.violet[500], 0.3)}`,
                fontWeight: 700,
                fontSize: '0.72rem',
              }}
            />
            <Chip
              label="No lengthy registration required"
              size="small"
              sx={{
                bgcolor: alpha(tokens.color.emerald[500], 0.12),
                color: tokens.color.emerald[300],
                border: `1px solid ${alpha(tokens.color.emerald[500], 0.25)}`,
                fontSize: '0.7rem',
              }}
            />
          </Stack>

          <Stack direction="row" spacing={1.5} alignItems="center">
            <Button
              size="small"
              variant="outlined"
              startIcon={<BoltIcon sx={{ color: tokens.color.amber[400] }} />}
              onClick={handleLoadDemoBenchmark}
              sx={{
                borderColor: alpha(tokens.color.amber[500], 0.4),
                color: tokens.color.amber[300],
                fontSize: '0.75rem',
                fontWeight: 600,
                bgcolor: alpha(tokens.color.amber[500], 0.08),
                '&:hover': {
                  borderColor: tokens.color.amber[400],
                  bgcolor: alpha(tokens.color.amber[500], 0.15),
                },
              }}
            >
              Load Demo Benchmark (₹50L CNC)
            </Button>

            <Button
              size="small"
              variant="text"
              startIcon={<TranslateIcon sx={{ fontSize: 16 }} />}
              onClick={() => setLang(lang === 'en' ? 'gu' : 'en')}
              sx={{
                color: tokens.color.slate[300],
                fontSize: '0.8rem',
                border: `1px solid ${tokens.color.border.subtle}`,
                px: 1.5,
              }}
            >
              {lang === 'en' ? 'ગુજરાતી' : 'English'}
            </Button>
          </Stack>
        </Stack>

        {/* Hero Question */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography
            variant="h3"
            sx={{
              fontFamily: tokens.font.heading,
              fontWeight: 800,
              fontSize: { xs: '1.8rem', sm: '2.4rem', md: '2.8rem' },
              lineHeight: 1.2,
              mb: 1.5,
              background: 'linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {lang === 'en'
              ? 'What are you trying to accomplish for your business?'
              : 'તમારા વ્યવસાય માટે તમે શું સિદ્ધ કરવા માંગો છો?'}
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: tokens.color.slate[400],
              maxWidth: 700,
              mx: 'auto',
              fontSize: { xs: '0.95rem', md: '1.05rem' },
            }}
          >
            {lang === 'en'
              ? 'Express your goal in plain words. We decode official Central and Gujarat policy guidelines, evaluate deterministic eligibility, and structure your maximum government benefits.'
              : 'તમારા ધ્યેયને સરળ શબ્દોમાં જણાવો. અમે કેન્દ્રીય અને ગુજરાતની સત્તાવાર પોલિસી ચકાસીને તમને મહત્તમ સરકારી લાભો મેળવી આપીશું.'}
          </Typography>
        </Box>

        {/* Stepper Header */}
        <Box sx={{ maxWidth: 640, mx: 'auto', mb: 4 }}>
          <Stepper
            activeStep={activeStep}
            sx={{
              '& .MuiStepLabel-label': {
                color: tokens.color.slate[400],
                fontSize: '0.8rem',
                fontWeight: 600,
                '&.Mui-active': { color: tokens.color.violet[300], fontWeight: 700 },
                '&.Mui-completed': { color: tokens.color.emerald[400] },
              },
              '& .MuiStepIcon-root': {
                color: alpha(tokens.color.slate[700], 0.8),
                '&.Mui-active': { color: tokens.color.violet[500] },
                '&.Mui-completed': { color: tokens.color.emerald[500] },
              },
            }}
          >
            <Step>
              <StepLabel>1. Express Business Goal</StepLabel>
            </Step>
            <Step>
              <StepLabel>2. Targeted Eligibility Facts</StepLabel>
            </Step>
            <Step>
              <StepLabel>3. Formulate Strategy</StepLabel>
            </Step>
          </Stepper>
        </Box>

        {/* Step 0: Goal Input & Suggested Chips & Structured Interpretation */}
        {activeStep === 0 && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            {/* Suggested Goal Chips */}
            <Box sx={{ mb: 3 }}>
              <Typography
                variant="overline"
                sx={{ color: tokens.color.slate[400], fontWeight: 700, letterSpacing: '0.08em', display: 'block', mb: 1.5, textAlign: 'center' }}
              >
                Suggested Common Objectives
              </Typography>
              <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', justifyContent: 'center', gap: 1 }}>
                {GOAL_PRESETS.map((preset, idx) => (
                  <Chip
                    key={idx}
                    icon={preset.icon}
                    label={lang === 'gu' ? preset.labelGu : preset.label}
                    onClick={() => applyPreset(preset)}
                    clickable
                    sx={{
                      bgcolor:
                        goalText === (lang === 'gu' ? preset.fullGoalGu : preset.fullGoal)
                          ? alpha(tokens.color.violet[500], 0.25)
                          : alpha(tokens.color.surface.card, 0.9),
                      borderColor:
                        goalText === (lang === 'gu' ? preset.fullGoalGu : preset.fullGoal)
                          ? tokens.color.violet[400]
                          : tokens.color.border.subtle,
                      borderWidth: '1px',
                      borderStyle: 'solid',
                      color: tokens.color.slate[200],
                      py: 2.2,
                      px: 0.8,
                      borderRadius: tokens.radius.full,
                      fontWeight: 600,
                      fontSize: '0.82rem',
                      transition: tokens.transition.fast,
                      '&:hover': {
                        bgcolor: alpha(tokens.color.violet[500], 0.18),
                        borderColor: tokens.color.violet[400],
                        transform: 'translateY(-1px)',
                      },
                    }}
                  />
                ))}
              </Stack>
            </Box>

            {/* Natural Language Goal Input Card */}
            <Card
              sx={{
                maxWidth: 820,
                mx: 'auto',
                bgcolor: tokens.color.surface.card,
                border: `1px solid ${tokens.color.border.subtle}`,
                borderRadius: tokens.radius.xl,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.35)',
                p: { xs: 2.5, sm: 3.5 },
                mb: 4,
              }}
            >
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: tokens.color.slate[200], mb: 1 }}>
                Describe your objective in detail:
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                value={goalText}
                onChange={(e) => {
                  setGoalText(e.target.value)
                  setParsedObjective(e.target.value)
                }}
                placeholder={
                  lang === 'en'
                    ? "e.g., I want to purchase a ₹50 lakh CNC machine to expand our precision machining capacity..."
                    : "દા.ત., હું ઉત્પાદન ક્ષમતા વધારવા માટે ₹50 લાખનું CNC મશીન ખરીદવા માંગુ છું..."
                }
                InputProps={{
                  endAdornment: goalText ? (
                    <InputAdornment position="end">
                      <IconButton
                        size="small"
                        aria-label="Clear entered goal text"
                        onClick={() => setGoalText('')}
                        sx={{ color: tokens.color.slate[500] }}
                      >
                        <ClearIcon fontSize="small" />
                      </IconButton>
                    </InputAdornment>

                  ) : null,
                  sx: {
                    bgcolor: alpha(tokens.color.surface.base, 0.7),
                    borderRadius: tokens.radius.md,
                    fontSize: '0.98rem',
                    color: tokens.color.slate[100],
                  },
                }}
              />

              {/* Structured Interpretation Card */}
              {goalText.trim().length > 10 && (
                <Box
                  sx={{
                    mt: 3,
                    p: 2.5,
                    bgcolor: alpha(tokens.color.violet[500], 0.05),
                    border: `1px solid ${alpha(tokens.color.violet[500], 0.25)}`,
                    borderRadius: tokens.radius.lg,
                  }}
                >
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <AutoAwesomeIcon sx={{ color: tokens.color.violet[400], fontSize: 18 }} />
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, color: tokens.color.violet[300] }}>
                        Structured Policy Interpretation
                      </Typography>
                    </Stack>
                    <Button
                      size="small"
                      startIcon={<EditOutlinedIcon sx={{ fontSize: 14 }} />}
                      onClick={() => setIsEditingStructured(!isEditingStructured)}
                      sx={{ fontSize: '0.72rem', color: tokens.color.slate[400] }}
                    >
                      {isEditingStructured ? 'Done Editing' : 'Fine-Tune Attributes'}
                    </Button>
                  </Stack>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mb: 0.5 }}>
                        Project Type
                      </Typography>
                      {isEditingStructured ? (
                        <Select
                          size="small"
                          fullWidth
                          value={parsedProjectType}
                          onChange={(e) => setParsedProjectType(e.target.value)}
                          sx={{ fontSize: '0.82rem' }}
                        >
                          <MenuItem value="machinery_purchase">Machinery & Plant Purchase</MenuItem>
                          <MenuItem value="expansion_new_unit">Expansion / New Factory Unit</MenuItem>
                          <MenuItem value="working_capital">Working Capital Credit</MenuItem>
                          <MenuItem value="export_expansion">Export & Market Expansion</MenuItem>
                          <MenuItem value="green_energy">Green / Solar Energy</MenuItem>
                          <MenuItem value="quality_certification">ZED / Quality Certification</MenuItem>
                        </Select>
                      ) : (
                        <Box sx={{ fontWeight: 600, color: tokens.color.slate[200], fontSize: '0.88rem' }}>
                          {parsedProjectType.replace(/_/g, ' ').toUpperCase()}
                        </Box>
                      )}
                    </Grid>

                    <Grid item xs={12} sm={4}>
                      <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mb: 0.5 }}>
                        Target Investment
                      </Typography>
                      {isEditingStructured ? (
                        <TextField
                          size="small"
                          fullWidth
                          type="number"
                          value={parsedInvestmentLakhs}
                          onChange={(e) => setParsedInvestmentLakhs(Number(e.target.value))}
                          InputProps={{
                            startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                            endAdornment: <InputAdornment position="end">Lakhs</InputAdornment>,
                          }}
                          sx={{ fontSize: '0.82rem' }}
                        />
                      ) : (
                        <Box sx={{ fontWeight: 700, color: tokens.color.emerald[400], fontSize: '0.92rem' }}>
                          ₹{parsedInvestmentLakhs} Lakhs
                        </Box>
                      )}
                    </Grid>

                    <Grid item xs={12} sm={4}>
                      <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mb: 0.5 }}>
                        Support Categories Detected
                      </Typography>
                      <Stack direction="row" spacing={0.6} sx={{ flexWrap: 'wrap', gap: 0.5 }}>
                        {parsedSupportCategories.map((cat, idx) => (
                          <Chip
                            key={idx}
                            label={cat.replace(/_/g, ' ')}
                            size="small"
                            sx={{
                              fontSize: '0.65rem',
                              height: 20,
                              bgcolor: alpha(tokens.color.sky[500], 0.15),
                              color: tokens.color.sky[300],
                              border: `1px solid ${alpha(tokens.color.sky[500], 0.3)}`,
                            }}
                          />
                        ))}
                      </Stack>
                    </Grid>
                  </Grid>
                </Box>
              )}

              {/* Action Button: Next Step */}
              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  size="large"
                  endIcon={<ArrowForwardIcon />}
                  disabled={goalText.trim().length < 8}
                  onClick={() => setActiveStep(1)}
                  sx={{
                    px: 4,
                    py: 1.2,
                    fontWeight: 700,
                    fontSize: '0.92rem',
                  }}
                >
                  Continue to Targeted Questions
                </Button>
              </Box>
            </Card>
          </motion.div>
        )}

        {/* Step 1: Targeted Follow-up Stepper (Only High-Impact Questions) */}
        {activeStep === 1 && (
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3 }}>
            <Card
              sx={{
                maxWidth: 820,
                mx: 'auto',
                bgcolor: tokens.color.surface.card,
                border: `1px solid ${tokens.color.border.subtle}`,
                borderRadius: tokens.radius.xl,
                p: { xs: 2.5, sm: 4 },
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.35)',
              }}
            >
              <Box sx={{ mb: 3 }}>
                <Typography variant="h5" sx={{ fontWeight: 800, color: tokens.color.slate[100], mb: 0.5 }}>
                  Targeted Policy Eligibility Check
                </Typography>
                <Typography variant="body2" sx={{ color: tokens.color.slate[400] }}>
                  We ask only 3 targeted questions whose answers directly alter subsidy percentages and scheme qualifications.
                </Typography>
              </Box>

              <Stack spacing={3.5}>
                {/* Question 1: Enterprise Classification */}
                <Box
                  sx={{
                    p: 2.5,
                    bgcolor: alpha(tokens.color.surface.elevated, 0.4),
                    borderRadius: tokens.radius.lg,
                    border: `1px solid ${tokens.color.border.subtle}`,
                  }}
                >
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: tokens.color.slate[100], mb: 0.5 }}>
                    1. Enterprise Scale & Investment Limit
                  </Typography>
                  <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mb: 2 }}>
                    <strong>Why this matters:</strong> Determines whether you qualify for MSME Capital Subsidy (up to 25%) under Gujarat MSME Policy 2020 and CLCSS.
                  </Typography>

                  <Grid container spacing={1.5}>
                    {[
                      { val: 'micro', title: 'Micro Enterprise', desc: 'Plant & Machinery ≤ ₹1 Cr | Turnover ≤ ₹5 Cr' },
                      { val: 'small', title: 'Small Enterprise', desc: 'Plant & Machinery ≤ ₹10 Cr | Turnover ≤ ₹50 Cr' },
                      { val: 'medium', title: 'Medium Enterprise', desc: 'Plant & Machinery ≤ ₹50 Cr | Turnover ≤ ₹250 Cr' },
                      { val: 'unknown', title: 'Decide Later (Unknown)', desc: 'Evaluate baseline schemes and refine later' },
                    ].map((item) => (
                      <Grid item xs={12} sm={6} key={item.val}>
                        <Box
                          onClick={() => setMsmeCategory(item.val as any)}
                          sx={{
                            p: 2,
                            borderRadius: tokens.radius.md,
                            cursor: 'pointer',
                            bgcolor:
                              msmeCategory === item.val
                                ? alpha(tokens.color.violet[500], 0.15)
                                : alpha(tokens.color.surface.base, 0.6),
                            border: `1px solid ${
                              msmeCategory === item.val ? tokens.color.violet[400] : tokens.color.border.subtle
                            }`,
                            transition: tokens.transition.fast,
                            '&:hover': { borderColor: tokens.color.violet[400] },
                          }}
                        >
                          <Stack direction="row" justifyContent="space-between" alignItems="center">
                            <Typography variant="subtitle2" sx={{ fontWeight: 700, color: tokens.color.slate[200] }}>
                              {item.title}
                            </Typography>
                            {msmeCategory === item.val && (
                              <CheckCircleOutlinedIcon sx={{ color: tokens.color.emerald[400], fontSize: 18 }} />
                            )}
                          </Stack>
                          <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mt: 0.5 }}>
                            {item.desc}
                          </Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </Box>

                {/* Question 2: Location & Manufacturing Sector */}
                <Box
                  sx={{
                    p: 2.5,
                    bgcolor: alpha(tokens.color.surface.elevated, 0.4),
                    borderRadius: tokens.radius.lg,
                    border: `1px solid ${tokens.color.border.subtle}`,
                  }}
                >
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: tokens.color.slate[100], mb: 0.5 }}>
                    2. Location & Industry Activity
                  </Typography>
                  <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mb: 2 }}>
                    <strong>Why this matters:</strong> Gujarat Industrial Policy classifies talukas into Category 1, 2, and 3. Manufacturing units receive higher capital and interest subvention.
                  </Typography>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth size="small">
                        <InputLabel>State</InputLabel>
                        <Select
                          value={stateName}
                          label="State"
                          onChange={(e) => setStateName(e.target.value)}
                        >
                          <MenuItem value="Gujarat">Gujarat (Special Package Active)</MenuItem>
                          <MenuItem value="Maharashtra">Maharashtra</MenuItem>
                          <MenuItem value="Other">Other State (Central Schemes)</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth size="small">
                        <InputLabel>District</InputLabel>
                        <Select
                          value={district}
                          label="District"
                          onChange={(e) => setDistrict(e.target.value)}
                        >
                          {GUJARAT_DISTRICTS.map((dist) => (
                            <MenuItem key={dist} value={dist}>
                              {dist}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={isManufacturing}
                            onChange={(e) => setIsManufacturing(e.target.checked)}
                            color="primary"
                          />
                        }
                        label={
                          <Typography variant="body2" sx={{ color: tokens.color.slate[200] }}>
                            <strong>Manufacturing Unit</strong> (Required for Capital Subsidy on Plant & Machinery)
                          </Typography>
                        }
                      />
                    </Grid>
                  </Grid>
                </Box>

                {/* Question 3: Ownership Multipliers & Credit Standing */}
                <Box
                  sx={{
                    p: 2.5,
                    bgcolor: alpha(tokens.color.surface.elevated, 0.4),
                    borderRadius: tokens.radius.lg,
                    border: `1px solid ${tokens.color.border.subtle}`,
                  }}
                >
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: tokens.color.slate[100], mb: 0.5 }}>
                    3. Priority Category Unlocks & Credit Health
                  </Typography>
                  <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mb: 2 }}>
                    <strong>Why this matters:</strong> Women and SC/ST ownership adds 5% - 10% extra subsidy and raises CGTMSE guarantee cover to 85%. Non-NPA status is mandatory for bank loans.
                  </Typography>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={isWomenOwned}
                            onChange={(e) => setIsWomenOwned(e.target.checked)}
                            color="secondary"
                          />
                        }
                        label={
                          <Typography variant="body2" sx={{ color: tokens.color.slate[200] }}>
                            Women-Owned Enterprise (≥ 51% stake)
                          </Typography>
                        }
                      />
                    </Grid>

                    <Grid item xs={12} sm={6}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={isScStOwned}
                            onChange={(e) => setIsScStOwned(e.target.checked)}
                            color="secondary"
                          />
                        }
                        label={
                          <Typography variant="body2" sx={{ color: tokens.color.slate[200] }}>
                            SC / ST Owned Enterprise
                          </Typography>
                        }
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Divider sx={{ my: 1, borderColor: tokens.color.border.subtle }} />
                      <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mb: 1 }}>
                        Are there any overdue loan accounts or past NPA declarations?
                      </Typography>
                      <Stack direction="row" spacing={1.5}>
                        {[
                          { val: 'no', label: 'Clean Credit History (No NPA)', color: tokens.color.emerald[400] },
                          { val: 'unknown', label: 'Not Sure / Pending Check', color: tokens.color.amber[400] },
                          { val: 'yes', label: 'Has Past NPA Record', color: tokens.color.red[400] },
                        ].map((opt) => (
                          <Chip
                            key={opt.val}
                            label={opt.label}
                            onClick={() => setHasNpaHistory(opt.val as any)}
                            sx={{
                              bgcolor:
                                hasNpaHistory === opt.val
                                  ? alpha(tokens.color.surface.card, 0.9)
                                  : 'transparent',
                              borderColor: hasNpaHistory === opt.val ? opt.color : tokens.color.border.subtle,
                              borderWidth: '1px',
                              borderStyle: 'solid',
                              color: hasNpaHistory === opt.val ? opt.color : tokens.color.slate[400],
                              fontWeight: 600,
                              fontSize: '0.75rem',
                              cursor: 'pointer',
                            }}
                          />
                        ))}
                      </Stack>
                    </Grid>
                  </Grid>
                </Box>
              </Stack>

              {/* Navigation CTAs */}
              <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Button
                  variant="text"
                  startIcon={<ArrowBackIcon />}
                  onClick={() => setActiveStep(0)}
                  sx={{ color: tokens.color.slate[400] }}
                >
                  Back to Goal
                </Button>

                <Button
                  variant="contained"
                  size="large"
                  endIcon={<AutoAwesomeIcon />}
                  onClick={handleGenerateStrategy}
                  sx={{
                    px: 4,
                    py: 1.2,
                    fontWeight: 700,
                    fontSize: '0.92rem',
                    background: tokens.gradient.hero,
                  }}
                >
                  Formulate Evidence-Backed Strategy
                </Button>
              </Box>
            </Card>
          </motion.div>
        )}

        {/* Step 2: Synthesis & Generation View */}
        {activeStep === 2 && (
          <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}>
            <Card
              sx={{
                maxWidth: 680,
                mx: 'auto',
                bgcolor: tokens.color.surface.card,
                border: `1px solid ${tokens.color.border.subtle}`,
                borderRadius: tokens.radius.xl,
                p: { xs: 4, sm: 6 },
                textAlign: 'center',
                boxShadow: '0 12px 48px rgba(0, 0, 0, 0.5)',
              }}
            >
              <Box sx={{ mb: 3 }}>
                <CircularProgress
                  variant="determinate"
                  value={analysisProgress}
                  size={72}
                  thickness={4}
                  sx={{ color: tokens.color.violet[400] }}
                />
              </Box>

              <Typography variant="h5" sx={{ fontWeight: 800, color: tokens.color.slate[100], mb: 1 }}>
                Building Your Government-Support Strategy
              </Typography>
              <Typography variant="body2" sx={{ color: tokens.color.slate[400], mb: 3 }}>
                {analysisStepLabel}
              </Typography>

              <Box sx={{ p: 2, bgcolor: alpha(tokens.color.surface.base, 0.7), borderRadius: tokens.radius.md, mb: 3 }}>
                <Stack direction="row" spacing={1} justifyContent="center" alignItems="center">
                  <EvidenceBadge sourceType="rule_matched" />
                  <EvidenceBadge sourceType="official_source" />
                  <EvidenceBadge sourceType="ai_explanation" />
                </Stack>
                <Typography variant="caption" sx={{ color: tokens.color.slate[400], display: 'block', mt: 1 }}>
                  Every scheme recommendation is cross-referenced with Gujarat Industrial Policy & Central MSMED guidelines.
                </Typography>
              </Box>

              <Typography variant="caption" sx={{ color: tokens.color.slate[500] }}>
                Please wait while the deterministic rule engine verifies eligibility limits...
              </Typography>
            </Card>
          </motion.div>
        )}
      </Container>
    </Box>
  )
}

export default GoalOnboarding
