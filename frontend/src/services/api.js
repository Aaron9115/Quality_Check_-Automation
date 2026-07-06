const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function checkText(text) {
  const response = await fetch(`${API_BASE_URL}/api/check-text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to check text')
  }

  return response.json()
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`)
  return response.json()
}