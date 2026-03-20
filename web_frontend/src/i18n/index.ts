// i18n 配置
import { createI18n } from 'vue-i18n'
import zhCN from '../locales/zh-CN'
import enUS from '../locales/en-US'

// 获取浏览器语言
const getBrowserLanguage = (): string => {
  if (typeof navigator !== 'undefined') {
    const browserLang = navigator.language.toLowerCase()
    if (browserLang.startsWith('zh')) {
      return 'zh-CN'
    } else if (browserLang.startsWith('en')) {
      return 'en-US'
    }
  }
  return 'zh-CN'
}

// 从 localStorage 获取保存的语言设置
const getSavedLanguage = (): string => {
  if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem('app-language')
    if (saved && ['zh-CN', 'en-US'].includes(saved)) {
      return saved
    }
  }
  return getBrowserLanguage()
}

// 保存语言设置到 localStorage
export const saveLanguage = (lang: string): void => {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('app-language', lang)
  }
}

const i18n = createI18n({
  legacy: false, // 使用 Composition API
  locale: getSavedLanguage(), // 默认语言
  fallbackLocale: 'zh-CN', // 回退语言
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  },
  globalInjection: true // 全局注入 $t
})

export default i18n
