import React, { Component, ErrorInfo, ReactNode } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { theme } from './theme'
import { queryClient } from './api/queryClient'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import SchemesDashboard from './pages/SchemesDashboard'
import SchemeDetailPage from './pages/SchemeDetailPage'
import GoalOnboarding from './pages/GoalOnboarding'
import ProfileSetup from './pages/ProfileSetup'
import GoalEntry from './pages/GoalEntry'
import StrategyDashboard from './pages/StrategyDashboard'
import PolicyMonitor from './pages/PolicyMonitor'
import ApplicationWorkspace from './pages/ApplicationWorkspace'
import PrototypeEvaluationDashboard from './pages/PrototypeEvaluationDashboard'
import MinistryPage from './pages/MinistryPage'
import ResourcesPage from './pages/ResourcesPage'
import UpdatesPage from './pages/UpdatesPage'
import SupportPage from './pages/SupportPage'
import AppShell from './components/AppShell'
import { LanguageProvider } from './i18n'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public state: ErrorBoundaryState = {
    hasError: false,
    error: null,
  }

  public static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', fontFamily: 'Inter, sans-serif', maxWidth: '680px', margin: '60px auto', background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0,0,0,0.06)' }}>
          <h2 style={{ color: '#991B1B', margin: '0 0 12px 0' }}>Application Display Notice</h2>
          <p style={{ color: '#374151', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '20px' }}>
            {this.state.error?.message || 'An unexpected rendering error occurred.'}
          </p>
          <button
            onClick={() => { window.location.href = '/' }}
            style={{ padding: '10px 22px', background: '#0F2E59', color: '#FFFFFF', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 700, fontSize: '0.9rem' }}
          >
            Reload Home Page
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

function App() {
  return (
    <ErrorBoundary>
      <LanguageProvider>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <Toaster
              position="top-right"
              theme="light"
              richColors
              toastOptions={{
                style: {
                  background: '#FFFFFF',
                  border: '1px solid #E2E8F0',
                  color: '#0F172A',
                  fontFamily: 'Inter, sans-serif',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(15, 23, 42, 0.08)',
                },
              }}
            />
            <BrowserRouter>
              <Routes>
                <Route element={<AppShell />}>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/ministry" element={<MinistryPage />} />
                  <Route path="/resources" element={<ResourcesPage />} />
                  <Route path="/updates" element={<UpdatesPage />} />
                  <Route path="/support" element={<SupportPage />} />
                  <Route path="/dashboard" element={<SchemesDashboard />} />
                  <Route path="/schemes" element={<SchemesDashboard />} />
                  <Route path="/scheme/:id" element={<SchemeDetailPage />} />
                  <Route path="/schemes/:id" element={<SchemeDetailPage />} />
                  <Route path="/onboard" element={<GoalOnboarding />} />
                  <Route path="/goal" element={<GoalOnboarding />} />
                  <Route path="/goal/:profileId" element={<GoalEntry />} />
                  <Route path="/profile/manual" element={<ProfileSetup />} />
                  <Route path="/strategy/:strategyId" element={<StrategyDashboard />} />
                  <Route path="/workspace/:profileId/:schemeId" element={<ApplicationWorkspace />} />
                  <Route path="/monitor" element={<PolicyMonitor />} />
                  <Route path="/evaluation" element={<PrototypeEvaluationDashboard />} />
                  <Route path="/metrics" element={<PrototypeEvaluationDashboard />} />
                </Route>
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </BrowserRouter>
          </ThemeProvider>
        </QueryClientProvider>
      </LanguageProvider>
    </ErrorBoundary>
  )
}

export default App
