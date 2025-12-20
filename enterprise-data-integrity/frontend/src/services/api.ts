import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface UploadResult {
  success: boolean
  file_path: string
  filename: string
  rows: number
  columns: string[]
  preview: any[]
}

export interface Rule {
  id: string
  name: string
  description: string
  severity: string
}

export interface Run {
  id: number
  name: string
  run_type: string
  status: string
  started_at: string
  completed_at: string | null
  total_records: number
  total_issues: number
  rules_passed: number
  rules_failed: number
}

export interface Issue {
  id: number
  title: string
  description: string
  severity: string
  status: string
  rule_name: string
  recommendation: string
}

export const uploadCSV = async (file: File): Promise<UploadResult> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/connectors/upload-csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const getAvailableRules = async (): Promise<Rule[]> => {
  const response = await api.get('/rules/available')
  return response.data
}

export const createRun = async (
  filePath: string,
  ruleIds: string[]
): Promise<Run> => {
  const response = await api.post('/runs/', {
    connector_id: 1, // Default connector
    file_path: filePath,
    rule_ids: ruleIds,
  })
  return response.data
}

export const getRun = async (runId: number): Promise<Run> => {
  const response = await api.get(`/runs/${runId}`)
  return response.data
}

export const getRunIssues = async (runId: number): Promise<Issue[]> => {
  const response = await api.get(`/runs/${runId}/issues`)
  return response.data
}

export const generateReport = async (runId: number): Promise<any> => {
  const response = await api.post('/reports/generate', {
    run_id: runId,
    report_type: 'executive_summary',
    format: 'pdf',
  })
  return response.data
}

export const getHealthDashboard = async (): Promise<any> => {
  const response = await api.get('/health-monitor/dashboard')
  return response.data
}

export const getRecentRuns = async (): Promise<Run[]> => {
  const response = await api.get('/runs/', { params: { limit: 20 } })
  return response.data
}
