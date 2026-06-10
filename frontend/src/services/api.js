const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export async function analyzeApplication(payload) {
  const response = await fetch(`${API_BASE_URL}/applications/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    throw new Error('Application analysis failed. Please try again.')
  }

  return response.json()
}

