export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function readJson(response) {
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || '요청을 처리하지 못했습니다.')
  }
  return payload
}

export async function createJob({ requestNumber, sampleNumber, tifFiles, xlsxFile }) {
  const formData = new FormData()
  formData.append('request_number', requestNumber)
  formData.append('sample_number', sampleNumber)
  tifFiles.forEach((file) => formData.append('tif_files', file))
  if (xlsxFile) formData.append('xlsx_file', xlsxFile)

  const response = await fetch(`${API_BASE_URL}/api/jobs`, {
    method: 'POST',
    body: formData,
  })
  return readJson(response)
}

export async function searchJobs(query = '') {
  const params = new URLSearchParams()
  if (query.trim()) params.set('query', query.trim())
  const response = await fetch(`${API_BASE_URL}/api/jobs?${params.toString()}`)
  return readJson(response)
}

export function absoluteDownloadUrl(path) {
  if (!path) return '#'
  return path.startsWith('http') ? path : `${API_BASE_URL}${path}`
}
