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
import AppShell from './components/AppShell'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Toaster
          position="top-right"
          theme="dark"
          richColors
          toastOptions={{
            style: {
              background: '#1E293B',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#F8FAFC',
              fontFamily: 'Inter, sans-serif',
              borderRadius: '10px',
            },
          }}
        />
        <BrowserRouter>
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
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
  )
}

export default App
