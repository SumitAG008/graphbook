import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Layout from './components/Layout'
import UploadScreen from './pages/UploadScreen'
import RunScreen from './pages/RunScreen'
import DashboardScreen from './pages/DashboardScreen'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/upload" element={<UploadScreen />} />
            <Route path="/run/:runId" element={<RunScreen />} />
            <Route path="/dashboard" element={<DashboardScreen />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  )
}

export default App
