/**
 * Google Identity Services (GIS) OAuth2 Integration
 * Enables real Google Sign-In with client credentials.
 */

declare global {
  interface Window {
    google?: any
  }
}

export interface GoogleUserProfile {
  sub: string
  name: string
  given_name?: string
  family_name?: string
  picture?: string
  email: string
  email_verified: boolean
}

/**
 * Ensures Google Identity Services script is loaded and ready
 */
export const loadGoogleScript = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (window.google?.accounts?.oauth2) {
      resolve()
      return
    }

    const existingScript = document.getElementById('google-gsi-client')
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve())
      existingScript.addEventListener('error', () => reject(new Error('Failed to load Google SDK script')))
      return
    }

    const script = document.createElement('script')
    script.id = 'google-gsi-client'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load Google SDK script'))
    document.head.appendChild(script)
  })
}

/**
 * Retrieves Google Client ID from environment or local cache
 */
export const getGoogleClientId = (): string => {
  const envId = import.meta.env.VITE_GOOGLE_CLIENT_ID
  if (envId && envId.trim() && !envId.includes('YOUR_GOOGLE_CLIENT_ID')) {
    return envId.trim()
  }
  const cached = localStorage.getItem('udyamniti_google_client_id')
  if (cached && cached.trim()) {
    return cached.trim()
  }
  return ''
}

/**
 * Triggers Google OAuth2 popup and retrieves verified user profile
 */
export const initiateGoogleSignIn = async (customClientId?: string): Promise<GoogleUserProfile> => {
  const clientId = (customClientId || getGoogleClientId()).trim()

  if (!clientId || clientId.includes('YOUR_GOOGLE_CLIENT_ID')) {
    throw new Error('MISSING_CLIENT_ID')
  }

  await loadGoogleScript()

  if (!window.google?.accounts?.oauth2) {
    throw new Error('Google Identity Services SDK is not ready. Please refresh the page.')
  }

  return new Promise((resolve, reject) => {
    try {
      const tokenClient = window.google.accounts.oauth2.initTokenClient({
        client_id: clientId.trim(),
        scope: 'openid email profile',
        callback: async (tokenResponse: any) => {
          if (tokenResponse.error) {
            reject(new Error(tokenResponse.error_description || tokenResponse.error))
            return
          }

          if (!tokenResponse.access_token) {
            reject(new Error('No access token received from Google.'))
            return
          }

          try {
            // Fetch verified user profile from Google's official userinfo API
            const response = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
              headers: {
                Authorization: `Bearer ${tokenResponse.access_token}`,
              },
            })

            if (!response.ok) {
              throw new Error(`Failed to fetch Google profile (status ${response.status})`)
            }

            const profile: GoogleUserProfile = await response.json()
            resolve(profile)
          } catch (fetchError) {
            reject(fetchError)
          }
        },
      })

      // Open Google OAuth consent popup
      tokenClient.requestAccessToken({ prompt: 'consent' })
    } catch (err) {
      reject(err)
    }
  })
}
