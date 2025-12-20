import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Alert,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
} from '@mui/material'
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { getHealthDashboard, getRecentRuns } from '../services/api'

export default function DashboardScreen() {
  const navigate = useNavigate()
  const [health, setHealth] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      const [healthData, runsData] = await Promise.all([
        getHealthDashboard(),
        getRecentRuns(),
      ])
      setHealth(healthData)
      setRuns(runsData)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon color="success" fontSize="large" />
      case 'warning':
        return <WarningIcon color="warning" fontSize="large" />
      case 'critical':
        return <ErrorIcon color="error" fontSize="large" />
      default:
        return <CheckCircleIcon color="disabled" fontSize="large" />
    }
  }

  const getHealthColor = (status: string): any => {
    switch (status) {
      case 'healthy':
        return 'success'
      case 'warning':
        return 'warning'
      case 'critical':
        return 'error'
      default:
        return 'default'
    }
  }

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading dashboard...</Typography>
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Integration Health Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Monitor data quality and integration health across your systems
      </Typography>

      {/* Overall Health Status */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          {getHealthIcon(health?.overall_status)}
          <Box>
            <Typography variant="h5">
              Overall Status:{' '}
              <Chip
                label={health?.overall_status?.toUpperCase()}
                color={getHealthColor(health?.overall_status)}
              />
            </Typography>
          </Box>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Healthy Connectors
                </Typography>
                <Typography variant="h3" color="success.main">
                  {health?.healthy_connectors || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Warning Connectors
                </Typography>
                <Typography variant="h3" color="warning.main">
                  {health?.warning_connectors || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Critical Connectors
                </Typography>
                <Typography variant="h3" color="error.main">
                  {health?.critical_connectors || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Recent Runs */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Data Quality Runs
        </Typography>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Run Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Started</TableCell>
                <TableCell>Records</TableCell>
                <TableCell>Issues</TableCell>
                <TableCell>Rules Passed</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {runs.map((run) => (
                <TableRow
                  key={run.id}
                  hover
                  onClick={() => navigate(`/run/${run.id}`)}
                  sx={{ cursor: 'pointer' }}
                >
                  <TableCell>{run.name}</TableCell>
                  <TableCell>
                    <Chip
                      label={run.status.toUpperCase()}
                      color={
                        run.status === 'completed'
                          ? 'success'
                          : run.status === 'failed'
                          ? 'error'
                          : 'info'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(run.started_at).toLocaleString()}
                  </TableCell>
                  <TableCell>{run.total_records}</TableCell>
                  <TableCell>
                    <Chip
                      label={run.total_issues}
                      color={run.total_issues > 0 ? 'error' : 'success'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {run.rules_passed} / {run.rules_passed + run.rules_failed}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {runs.length === 0 && (
          <Alert severity="info" sx={{ mt: 2 }}>
            No runs yet. Upload a CSV file to get started!
          </Alert>
        )}
      </Paper>
    </Box>
  )
}
