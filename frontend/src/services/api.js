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

export async function checkPDF(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/api/check-pdf`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to process PDF')
  }

  return response.json()
}

export async function checkImageAlignment(logo, background) {
  const formData = new FormData()
  formData.append('logo', logo)
  formData.append('background', background)

  const response = await fetch(`${API_BASE_URL}/api/check-image-alignment`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to check image alignment')
  }

  return response.json()
}