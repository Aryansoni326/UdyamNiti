import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  TextField,
  Button,
  Stack,
  Chip,
  Card,
  CardContent,
  Grid,
  IconButton,
  CircularProgress,
  Paper,
  Divider,
  Tooltip,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CloseIcon from '@mui/icons-material/Close'
import SearchIcon from '@mui/icons-material/Search'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import WarningAmberIcon from '@mui/icons-material/WarningAmber'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import PsychologyIcon from '@mui/icons-material/Psychology'
import LightbulbOutlinedIcon from '@mui/icons-material/LightbulbOutlined'
import TaskAltIcon from '@mui/icons-material/TaskAlt'
import { matchSchemesWithGemini, type GeminiMatchResponse, type GeminiMatchResultItem } from '../utils/geminiSchemeMatcher'
import { toast } from 'sonner'

interface FindBenefitsAiModalProps {
  open: boolean
  onClose: () => void
  onPreviewPdf?: (pdfFilename: string, schemeName: string) => void
}

const QUICK_PROMPT_SUGGESTIONS = [
  { label: '⚙️ Collateral-free loan for machinery', prompt: 'I run a manufacturing unit and need a collateral-free loan to buy CNC and automated machinery.' },
  { label: '☀️ Solar rooftop subsidy for factory', prompt: 'I run a small textile mill in Surat and need a loan for solar panels without collateral.' },
  { label: '🚢 Export credit support', prompt: 'I want to export handicraft and engineering goods and need export credit guarantee without bank mortgage.' },
  { label: '👩‍💼 Women entrepreneur capital subsidy', prompt: 'I am a woman entrepreneur starting a micro enterprise and need margin money capital subsidy.' },
  { label: '🛡️ ZED quality certification grant', prompt: 'We manufacture precision components and want to get ZED certification and testing lab grants.' },
  { label: '🌾 Food processing business grant', prompt: 'I want to set up a micro food processing and packaging unit and need central scheme subsidies.' },
]

export const FindBenefitsAiModal: React.FC<FindBenefitsAiModalProps> = ({ open, onClose, onPreviewPdf }) => {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiResult, setAiResult] = useState<GeminiMatchResponse | null>(null)

  const handleSearchWithGemini = async (searchPrompt?: string) => {
    const textToSearch = (searchPrompt || query).trim()
    if (!textToSearch) {
      toast.error('Please enter what your business requires.')
      return
    }

    setLoading(true)
    try {
      let storedUser = null
      try {
        const raw = localStorage.getItem('udyamniti_user')
        if (raw) storedUser = JSON.parse(raw)
      } catch {}

      const result = await matchSchemesWithGemini(textToSearch, storedUser)
      setAiResult(result)
      toast.success(`Gemini AI matched ${result.matchedSchemes.length} relevant schemes!`)
    } catch (err: any) {
      console.error('Gemini scheme matching error:', err)
      toast.error(err?.message || 'Unable to connect to Gemini AI. Please check your query and try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectQuickPrompt = (promptText: string) => {
    setQuery(promptText)
    handleSearchWithGemini(promptText)
  }

  const handleResetSearch = () => {
    setQuery('')
    setAiResult(null)
  }

  const handleNavigateToDashboard = () => {
    onClose()
    if (aiResult?.matchedSchemes?.length) {
      const topCode = aiResult.matchedSchemes[0].scheme.code
      navigate(`/dashboard?search=${encodeURIComponent(aiResult.matchedSchemes[0].scheme.shortName || topCode)}`)
    } else {
      navigate('/dashboard')
    }
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: '18px',
          boxShadow: '0 24px 80px rgba(15, 23, 42, 0.35)',
          border: '1px solid #E2E8F0',
          overflow: 'hidden',
          maxHeight: '92vh',
          display: 'flex',
          flexDirection: 'column',
        },
      }}
    >
      {/* Modal Header */}
      <DialogTitle
        sx={{
          background: 'linear-gradient(135deg, #0F2E59 0%, #1E3A8A 100%)',
          color: '#FFFFFF',
          py: 2.2,
          px: 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Stack direction="row" spacing={1.5} alignItems="center">
          <Box
            sx={{
              width: 38,
              height: 38,
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #E65100 0%, #EA580C 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 12px rgba(230, 81, 0, 0.4)',
            }}
          >
            <AutoAwesomeIcon sx={{ color: '#FEF08A', fontSize: 22 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 800, fontSize: '1.15rem', color: '#FFFFFF', lineHeight: 1.2 }}>
              Find Benefits for My Business
            </Typography>
            <Typography variant="caption" sx={{ color: '#93C5FD', fontWeight: 600 }}>
              Powered by Google Gemini AI & 52+ Official Gazette Scheme Guidelines
            </Typography>
          </Box>
        </Stack>

        <IconButton onClick={onClose} size="small" sx={{ color: '#94A3B8', '&:hover': { color: '#FFFFFF' } }}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ p: { xs: 2.5, md: 3 }, bgcolor: '#F8FAFC', flex: 1, overflowY: 'auto' }}>
        {/* Natural Language Prompt Input */}
        <Paper
          elevation={0}
          sx={{
            p: 2.5,
            mb: 3,
            bgcolor: '#FFFFFF',
            borderRadius: '14px',
            border: '1.5px solid #CBD5E1',
            boxShadow: '0 4px 20px rgba(15, 23, 42, 0.05)',
          }}
        >
          <Typography variant="subtitle2" sx={{ fontWeight: 800, color: '#0F2E59', mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <PsychologyIcon sx={{ color: '#E65100', fontSize: 20 }} />
            Tell Gemini AI what your business needs:
          </Typography>
          <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mb: 1.5 }}>
            Type anything freely in natural language — machinery purchase, working capital loan, export support, solar panels, quality certification, or women/SC-ST subsidies (English, Hindi, or Gujarati):
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={3}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSearchWithGemini()
              }
            }}
            placeholder="e.g. I run a small textile mill in Surat and need a loan for solar panels without collateral... or I want to buy CNC machines for my workshop with capital subsidy."
            sx={{
              mb: 2,
              '& .MuiOutlinedInput-root': {
                bgcolor: '#F8FAFC',
                borderRadius: '10px',
                fontSize: '0.94rem',
                color: '#0F172A',
                '& fieldset': { borderColor: '#CBD5E1' },
                '&:hover fieldset': { borderColor: '#0F2E59' },
                '&.Mui-focused fieldset': { borderColor: '#E65100', borderWidth: '2px' },
              },
            }}
          />

          {/* Quick Clickable Suggestions */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" sx={{ color: '#475569', fontWeight: 700, display: 'block', mb: 0.8 }}>
              Try these quick business requirement examples:
            </Typography>
            <Stack direction="row" spacing={0.8} sx={{ flexWrap: 'wrap', gap: 0.8 }}>
              {QUICK_PROMPT_SUGGESTIONS.map((item, idx) => (
                <Chip
                  key={idx}
                  label={item.label}
                  onClick={() => handleSelectQuickPrompt(item.prompt)}
                  clickable
                  size="small"
                  sx={{
                    bgcolor: '#EFF6FF',
                    color: '#1E40AF',
                    border: '1px solid #BFDBFE',
                    fontWeight: 700,
                    fontSize: '0.74rem',
                    py: 1.6,
                    '&:hover': { bgcolor: '#DBEAFE', borderColor: '#3B82F6' },
                  }}
                />
              ))}
            </Stack>
          </Box>

          <Stack direction="row" spacing={1.5} justifyContent="flex-end" alignItems="center">
            {aiResult && (
              <Button
                variant="text"
                size="small"
                onClick={handleResetSearch}
                sx={{ color: '#64748B', fontWeight: 600, textTransform: 'none' }}
              >
                Clear Results
              </Button>
            )}
            <Button
              variant="contained"
              disabled={loading || !query.trim()}
              onClick={() => handleSearchWithGemini()}
              startIcon={
                loading ? (
                  <CircularProgress size={16} sx={{ color: '#FFFFFF' }} />
                ) : (
                  <AutoAwesomeIcon sx={{ fontSize: 18, color: '#FEF08A' }} />
                )
              }
              sx={{
                background: 'linear-gradient(135deg, #E65100 0%, #EA580C 100%)',
                color: '#FFFFFF',
                fontWeight: 800,
                fontSize: '0.88rem',
                textTransform: 'none',
                px: 3,
                py: 1,
                borderRadius: '8px',
                boxShadow: '0 4px 14px rgba(230, 81, 0, 0.35)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #C2410C 0%, #9A3412 100%)',
                },
              }}
            >
              {loading ? 'Gemini AI is Matching Schemes...' : '✨ Find Relevant Schemes with Gemini AI'}
            </Button>
          </Stack>
        </Paper>

        {/* Loading Animation State */}
        {loading && (
          <Box sx={{ py: 6, textAlign: 'center' }}>
            <CircularProgress size={46} sx={{ color: '#E65100', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#0F2E59', fontWeight: 800 }}>
              Analyzing requirement with Google Gemini AI...
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748B', mt: 0.5, maxWidth: 500, mx: 'auto' }}>
              Scanning 52+ official schemes, extracting required documents from Gazette PDFs, and identifying matching financial incentives for your business.
            </Typography>
          </Box>
        )}

        {/* AI Results Display */}
        {aiResult && !loading && (
          <Box>
            {/* Executive Synthesis Card */}
            <Paper
              sx={{
                p: 2.5,
                mb: 3,
                borderRadius: '14px',
                bgcolor: '#F0FDF4',
                border: '1.5px solid #86EFAC',
                boxShadow: '0 4px 16px rgba(16, 185, 129, 0.08)',
              }}
            >
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1, flexWrap: 'wrap', gap: 0.5 }}>
                <Chip
                  icon={<TaskAltIcon sx={{ color: '#15803D !important', fontSize: '15px !important' }} />}
                  label={`Gemini AI Analysis: ${aiResult.matchedSchemes.length} Schemes Matched`}
                  size="small"
                  sx={{ bgcolor: '#DCFCE7', color: '#166534', fontWeight: 800, fontSize: '0.74rem' }}
                />
                <Chip
                  label={`Sector: ${aiResult.detectedSector}`}
                  size="small"
                  sx={{ bgcolor: '#FFFFFF', color: '#334155', border: '1px solid #CBD5E1', fontWeight: 700, fontSize: '0.72rem' }}
                />
                <Chip
                  label={`Scale: ${aiResult.detectedScale}`}
                  size="small"
                  sx={{ bgcolor: '#FFFFFF', color: '#334155', border: '1px solid #CBD5E1', fontWeight: 700, fontSize: '0.72rem' }}
                />
                <Chip
                  label={aiResult.modelUsed}
                  size="small"
                  sx={{ bgcolor: '#EFF6FF', color: '#1D4ED8', border: '1px solid #BFDBFE', fontWeight: 700, fontSize: '0.7rem' }}
                />
              </Stack>

              <Typography variant="body1" sx={{ color: '#166534', fontWeight: 700, lineHeight: 1.6, fontSize: '0.96rem' }}>
                {aiResult.executiveSummary}
              </Typography>
            </Paper>

            {/* Matched Relevant Schemes List */}
            <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <span>Relevant Schemes for Your Requirement:</span>
              <Chip label={`${aiResult.matchedSchemes.length} Schemes`} size="small" sx={{ bgcolor: '#E65100', color: '#FFFFFF', fontWeight: 800 }} />
            </Typography>

            <Grid container spacing={2.5}>
              {aiResult.matchedSchemes.map((item, idx) => (
                <Grid item xs={12} key={item.scheme.code || idx}>
                  <Card
                    sx={{
                      borderRadius: '14px',
                      border: item.isFullyDocumentReady ? '2px solid #059669' : '1.5px solid #CBD5E1',
                      bgcolor: '#FFFFFF',
                      p: 2.5,
                      boxShadow: '0 4px 16px rgba(15, 23, 42, 0.05)',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        borderColor: '#0F2E59',
                        boxShadow: '0 8px 24px rgba(15, 23, 42, 0.1)',
                      },
                    }}
                  >
                    <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} sx={{ mb: 1.5, gap: 1 }}>
                      <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                        <Chip
                          label={`${item.matchScore}% Match`}
                          size="small"
                          sx={{
                            bgcolor: item.matchScore >= 90 ? '#ECFDF5' : '#EFF6FF',
                            color: item.matchScore >= 90 ? '#047857' : '#1D4ED8',
                            border: `1px solid ${item.matchScore >= 90 ? '#A7F3D0' : '#BFDBFE'}`,
                            fontWeight: 800,
                            fontSize: '0.74rem',
                          }}
                        />
                        <Chip
                          label={item.scheme.division}
                          size="small"
                          sx={{ bgcolor: '#F1F5F9', color: '#334155', fontWeight: 700, fontSize: '0.7rem' }}
                        />
                        {item.isFullyDocumentReady ? (
                          <Chip
                            icon={<CheckCircleIcon sx={{ fontSize: '14px !important', color: '#059669 !important' }} />}
                            label="100% Document Ready"
                            size="small"
                            sx={{ bgcolor: '#ECFDF5', color: '#047857', fontWeight: 800, fontSize: '0.7rem' }}
                          />
                        ) : (
                          <Chip
                            icon={<WarningAmberIcon sx={{ fontSize: '14px !important', color: '#D97706 !important' }} />}
                            label={`${item.missingDocuments.length} Documents Missing`}
                            size="small"
                            sx={{ bgcolor: '#FEF3C7', color: '#B45309', fontWeight: 800, fontSize: '0.7rem' }}
                          />
                        )}
                      </Stack>

                      <Typography variant="subtitle1" sx={{ fontWeight: 900, color: '#059669' }}>
                        {item.keyBenefit}
                      </Typography>
                    </Stack>

                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#0F2E59', fontSize: '1.1rem', mb: 0.5, lineHeight: 1.3 }}>
                      {item.scheme.name}
                    </Typography>

                    <Typography variant="caption" sx={{ color: '#64748B', display: 'block', mb: 1.5, fontWeight: 600 }}>
                      {item.scheme.ministry} • Gazette: {item.scheme.gazette}
                    </Typography>

                    {/* Why Gemini Matched This */}
                    <Paper sx={{ p: 1.5, mb: 2, bgcolor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
                      <Typography variant="caption" sx={{ color: '#E65100', fontWeight: 800, display: 'block', mb: 0.3 }}>
                        Why Gemini AI recommends this for your business:
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#1E293B', fontWeight: 600, fontSize: '0.84rem' }}>
                        {item.whyMatched}
                      </Typography>
                    </Paper>

                    {/* Document Breakdown */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" sx={{ color: '#475569', fontWeight: 800, display: 'block', mb: 0.8 }}>
                        Required Documents (From Scheme PDF):
                      </Typography>
                      <Stack direction="row" spacing={0.8} sx={{ flexWrap: 'wrap', gap: 0.8 }}>
                        {item.mandatoryDocuments.map((docName, dIdx) => {
                          const isHeld = item.heldDocuments.includes(docName)
                          return (
                            <Chip
                              key={dIdx}
                              icon={isHeld ? <CheckCircleIcon sx={{ fontSize: '13px !important', color: '#059669 !important' }} /> : <WarningAmberIcon sx={{ fontSize: '13px !important', color: '#DC2626 !important' }} />}
                              label={docName}
                              size="small"
                              sx={{
                                bgcolor: isHeld ? '#F0FDF4' : '#FEF2F2',
                                color: isHeld ? '#166534' : '#991B1B',
                                border: `1px solid ${isHeld ? '#BBF7D0' : '#FECDD3'}`,
                                fontWeight: 700,
                                fontSize: '0.72rem',
                              }}
                            />
                          )
                        })}
                      </Stack>
                    </Box>

                    {/* Action Step & Buttons */}
                    <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} sx={{ pt: 1, borderTop: '1px solid #F1F5F9', gap: 1 }}>
                      <Typography variant="caption" sx={{ color: '#047857', fontWeight: 700 }}>
                        Next Action: {item.actionStep}
                      </Typography>

                      <Stack direction="row" spacing={1}>
                        {onPreviewPdf && item.scheme.pdfFile && (
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<PictureAsPdfIcon sx={{ fontSize: 15, color: '#DC2626' }} />}
                            onClick={() => onPreviewPdf(item.scheme.pdfFile, item.scheme.name)}
                            sx={{
                              borderColor: '#CBD5E1',
                              color: '#0F2E59',
                              fontWeight: 700,
                              textTransform: 'none',
                              fontSize: '0.76rem',
                              '&:hover': { bgcolor: '#F1F5F9', borderColor: '#0F2E59' },
                            }}
                          >
                            Preview PDF
                          </Button>
                        )}
                        <Button
                          size="small"
                          variant="contained"
                          endIcon={<ArrowForwardIcon sx={{ fontSize: 15 }} />}
                          onClick={() => {
                            onClose()
                            navigate(`/scheme/${item.scheme.code}`)
                          }}
                          sx={{
                            bgcolor: '#0F2E59',
                            color: '#FFFFFF',
                            fontWeight: 700,
                            textTransform: 'none',
                            fontSize: '0.78rem',
                            '&:hover': { bgcolor: '#0A1E3A' },
                          }}
                        >
                          View Scheme & Apply
                        </Button>
                      </Stack>
                    </Stack>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 2, px: 3, bgcolor: '#FFFFFF', borderTop: '1px solid #E2E8F0', justifyContent: 'space-between' }}>
        <Button onClick={onClose} sx={{ color: '#64748B', fontWeight: 600, textTransform: 'none' }}>
          Close
        </Button>
        <Button
          variant="contained"
          onClick={handleNavigateToDashboard}
          sx={{
            bgcolor: '#0F2E59',
            color: '#FFFFFF',
            fontWeight: 700,
            textTransform: 'none',
            borderRadius: '8px',
            '&:hover': { bgcolor: '#0A1E3A' },
          }}
        >
          Explore All 52+ Schemes in Dashboard →
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default FindBenefitsAiModal
