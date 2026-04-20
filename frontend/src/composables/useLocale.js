import { useI18n } from 'vue-i18n'

export function useLocale() {
  const { locale, availableLocales, t } = useI18n()

  function setLocale(code) {
    locale.value = code
    try { localStorage.setItem('co.locale', code) } catch (_) {}
  }

  function hydrate() {
    try {
      const saved = localStorage.getItem('co.locale')
      if (saved && availableLocales.includes(saved)) locale.value = saved
    } catch (_) {}
  }

  return { locale, availableLocales, t, setLocale, hydrate }
}
