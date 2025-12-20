import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Grid,
  Card,
  CardContent,
} from '@mui/material'
import {
  CloudUpload as CloudUploadIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material'
import { uploadCSV, getAvailableRules, createRun, Rule } from '../services/api'

export default function UploadScreen() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [rules, setRules] = useState<Rule[]>([])
  const [selectedRules, setSelectedRules] = useState<string[]>([])
  const [running, setRunning] = useState(false)

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (!selectedFile) return

    setFile(selectedFile)
    setError(null)
    setUploading(true)

    try {
      const result = await uploadCSV(selectedFile)
      setUploadResult(result)

      // Load available rules
      const availableRules = await getAvailableRules()
      setRules(availableRules)

      // Select all rules by default
      setSelectedRules(availableRules.map((r) => r.id))
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload file')
    } finally {
      setUploading(false)
    }
  }

  const handleRuleToggle = (ruleId: string) => {
    setSelectedRules((prev) =>
      prev.includes(ruleId)
        ? prev.filter((id) => id !== ruleId)
        : [...prev, ruleId]
    )
  }

  const handleRun = async () => {
    if (!uploadResult || selectedRules.length === 0) return

    setRunning(true)
    setError(null)

    try {
      const run = await createRun(uploadResult.file_path, selectedRules)
      navigate(`/run/${run.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start data quality check')
      setRunning(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload & Configure Data Quality Check
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload your CSV file and select the data quality rules to execute
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Step 1: Upload CSV */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Step 1: Upload CSV File
        </Typography>

        <Button
          variant="contained"
          component="label"
          startIcon={<CloudUploadIcon />}
          disabled={uploading}
        >
          Choose File
          <input
            type="file"
            hidden
            accept=".csv"
            onChange={handleFileChange}
          />
        </Button>

        {file && (
          <Box sx={{ mt: 2 }}>
            <Chip label={file.name} color="primary" />
          </Box>
        )}

        {uploading && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress />
            <Typography variant="body2" sx={{ mt: 1 }}>
              Uploading and analyzing file...
            </Typography>
          </Box>
        )}

        {uploadResult && (
          <Box sx={{ mt: 2 }}>
            <Alert severity="success">
              File uploaded successfully! Found {uploadResult.rows} rows and{' '}
              {uploadResult.columns.length} columns.
            </Alert>

            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Columns Found
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {uploadResult.columns.map((col: string) => (
                        <Chip key={col} label={col} size="small" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Step 2: Select Rules */}
      {uploadResult && rules.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Step 2: Select Data Quality Rules
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Choose which rules to execute on your data
          </Typography>

          <FormGroup>
            {rules.map((rule) => (
              <FormControlLabel
                key={rule.id}
                control={
                  <Checkbox
                    checked={selectedRules.includes(rule.id)}
                    onChange={() => handleRuleToggle(rule.id)}
                  />
                }
                label={
                  <Box>
                    <Typography variant="body1">{rule.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {rule.description} - Severity: {rule.severity}
                    </Typography>
                  </Box>
                }
              />
            ))}
          </FormGroup>
        </Paper>
      )}

      {/* Step 3: Run */}
      {uploadResult && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            size="large"
            startIcon={<PlayArrowIcon />}
            onClick={handleRun}
            disabled={running || selectedRules.length === 0}
          >
            {running ? 'Running...' : 'Run Data Quality Check'}
          </Button>
        </Box>
      )}
    </Box>
  )
}
