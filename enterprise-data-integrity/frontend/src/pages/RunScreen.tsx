import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Grid,
  Card,
  CardContent,
} from '@mui/material'
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  PictureAsPdf as PdfIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material'
import { getRun, getRunIssues, generateReport, Run, Issue } from '../services/api'

export default function RunScreen() {
  const { runId } = useParams<{ runId: string }>()
  const [run, setRun] = useState<Run | null>(null)
  const [issues, setIssues] = useState<Issue[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generatingReport, setGeneratingReport] = useState(false)
  const [reportUrl, setReportUrl] = useState<string | null>(null)

  const loadRunData = async () => {
    try {
      setLoading(true)
      const runData = await getRun(Number(runId))
      setRun(runData)

      if (runData.status === 'completed' || runData.status === 'failed') {
        const issuesData = await getRunIssues(Number(runId))
        setIssues(issuesData)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load run data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRunData()

    // Poll for updates if run is pending or running
    const interval = setInterval(() => {
      if (run?.status === 'pending' || run?.status === 'running') {
        loadRunData()
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [runId, run?.status])

  const handleGenerateReport = async () => {
    setGeneratingReport(true)
    try {
      const result = await generateReport(Number(runId))
      setReportUrl(result.download_url)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate report')
    } finally {
      setGeneratingReport(false)
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />
      case 'high':
        return <WarningIcon color="warning" />
      case 'medium':
        return <WarningIcon color="info" />
      default:
        return <CheckCircleIcon color="success" />
    }
  }

  const getSeverityColor = (severity: string): any => {
    switch (severity) {
      case 'critical':
        return 'error'
      case 'high':
        return 'warning'
      case 'medium':
        return 'info'
      default:
        return 'default'
    }
  }

  if (loading && !run) {
    return (
      <Box>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading run data...</Typography>
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>
  }

  if (!run) {
    return <Alert severity="info">Run not found</Alert>
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">{run.name}</Typography>
        <Box>
          <Button
            startIcon={<RefreshIcon />}
            onClick={loadRunData}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          {run.status === 'completed' && (
            <Button
              variant="contained"
              startIcon={<PdfIcon />}
              onClick={handleGenerateReport}
              disabled={generatingReport}
            >
              {generatingReport ? 'Generating...' : 'Generate PDF Report'}
            </Button>
          )}
        </Box>
      </Box>

      {reportUrl && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Report generated successfully!{' '}
          <a href={reportUrl} target="_blank" rel="noopener noreferrer">
            Download PDF
          </a>
        </Alert>
      )}

      {/* Run Status */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Status
              </Typography>
              <Chip
                label={run.status.toUpperCase()}
                color={
                  run.status === 'completed'
                    ? 'success'
                    : run.status === 'failed'
                    ? 'error'
                    : 'info'
                }
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Records
              </Typography>
              <Typography variant="h4">{run.total_records}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Issues Found
              </Typography>
              <Typography variant="h4" color="error">
                {run.total_issues}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Rules Passed
              </Typography>
              <Typography variant="h4" color="success.main">
                {run.rules_passed} / {run.rules_passed + run.rules_failed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {(run.status === 'pending' || run.status === 'running') && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress />
          <Typography sx={{ mt: 1 }}>
            Data quality check is {run.status}...
          </Typography>
        </Box>
      )}

      {/* Issues Table */}
      {issues.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Issues Detected ({issues.length})
          </Typography>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Severity</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Rule</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Recommendation</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {issues.map((issue) => (
                  <TableRow key={issue.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getSeverityIcon(issue.severity)}
                        <Chip
                          label={issue.severity.toUpperCase()}
                          color={getSeverityColor(issue.severity)}
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>{issue.title}</TableCell>
                    <TableCell>{issue.rule_name}</TableCell>
                    <TableCell>
                      <Chip label={issue.status} size="small" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {issue.recommendation || 'No recommendation'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {run.status === 'completed' && issues.length === 0 && (
        <Alert severity="success">
          No issues found! Your data quality is excellent.
        </Alert>
      )}
    </Box>
  )
}
