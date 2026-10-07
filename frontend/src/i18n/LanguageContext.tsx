import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'
import { Language, t as translate, TranslationKey, LANGUAGE_LABELS } from './translations'

interface LanguageContextValue {
  lang: Language
  setLang: (lang: Language) => void
  t: (key: TranslationKey) => string
}

const LanguageContext = createContext<LanguageContextValue>({
  lang: 'en',
  setLang: () => {},
  t: (key) => key,
})

const STORAGE_KEY = 'udyamniti_language'

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [lang, setLangState] = useState<Language>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored === 'en' || stored === 'hi' || stored === 'gu') return stored
    } catch {}
    return 'en'
  })

  const setLang = useCallback((newLang: Language) => {
    setLangState(newLang)
    try {
      localStorage.setItem(STORAGE_KEY, newLang)
    } catch {}
  }, [])

  useEffect(() => {
    // Set html lang attribute for accessibility
    document.documentElement.lang = lang === 'en' ? 'en' : lang === 'hi' ? 'hi' : 'gu'
  }, [lang])

  const tFn = useCallback((key: TranslationKey) => translate(key, lang), [lang])

  return (
    <LanguageContext.Provider value={{ lang, setLang, t: tFn }}>
      {children}
    </LanguageContext.Provider>
  )
}

export const useLanguage = () => useContext(LanguageContext)
export { LANGUAGE_LABELS }
export type { Language, TranslationKey }
