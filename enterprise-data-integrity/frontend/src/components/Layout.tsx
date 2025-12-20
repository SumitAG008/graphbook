import { ReactNode } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  AppBar,
  Box,
  Toolbar,
  Typography,
  Button,
  Container,
} from '@mui/material'
import {
  Upload as UploadIcon,
  Dashboard as DashboardIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <AssessmentIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Enterprise Data Integrity Control Room
          </Typography>
          <Button
            color="inherit"
            startIcon={<UploadIcon />}
            onClick={() => navigate('/upload')}
            sx={{
              backgroundColor:
                location.pathname === '/upload' ? 'rgba(255,255,255,0.1)' : 'transparent',
            }}
          >
            Upload & Run
          </Button>
          <Button
            color="inherit"
            startIcon={<DashboardIcon />}
            onClick={() => navigate('/dashboard')}
            sx={{
              ml: 2,
              backgroundColor:
                location.pathname === '/dashboard' ? 'rgba(255,255,255,0.1)' : 'transparent',
            }}
          >
            Dashboard
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        {children}
      </Container>
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) => theme.palette.grey[200],
        }}
      >
        <Container maxWidth="xl">
          <Typography variant="body2" color="text.secondary" align="center">
            Enterprise Data Integrity Control Room v1.0.0-mvp
          </Typography>
        </Container>
      </Box>
    </Box>
  )
}
