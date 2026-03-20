// 翻译工具服务
import { useI18n } from 'vue-i18n'

// 翻译 API 配置（可选：集成外部翻译服务）
const TRANSLATION_API = {
  enabled: false, // 是否启用外部翻译 API
  endpoint: '', // 翻译 API 端点
  apiKey: '' // API 密钥
}

/**
 * 使用外部翻译 API 翻译文本
 * @param text 要翻译的文本
 * @param targetLang 目标语言
 * @returns 翻译后的文本
 */
export async function translateText(text: string, targetLang: string): Promise<string> {
  if (!TRANSLATION_API.enabled || !text.trim()) {
    return text
  }

  try {
    const response = await fetch(TRANSLATION_API.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${TRANSLATION_API.apiKey}`
      },
      body: JSON.stringify({
        q: text,
        source: 'auto',
        target: targetLang.split('-')[0],
        format: 'text'
      })
    })

    if (!response.ok) {
      throw new Error('Translation API error')
    }

    const data = await response.json()
    return data.translatedText || text
  } catch (error) {
    console.error('Translation failed:', error)
    return text
  }
}

/**
 * 批量翻译文本
 * @param texts 要翻译的文本数组
 * @param targetLang 目标语言
 * @returns 翻译后的文本数组
 */
export async function translateBatch(
  texts: string[], 
  targetLang: string
): Promise<string[]> {
  if (!TRANSLATION_API.enabled) {
    return texts
  }

  const results = await Promise.all(
    texts.map(text => translateText(text, targetLang))
  )
  
  return results
}

/**
 * 翻译题目内容（题干、选项、答案、解析）
 * @param question 题目对象
 * @param i18n vue-i18n 实例
 * @param targetLang 目标语言
 * @returns 翻译后的题目对象
 */
export async function translateQuestion(
  question: any,
  targetLang: string
): Promise<any> {
  if (!TRANSLATION_API.enabled) {
    return question
  }

  const translated = { ...question }
  
  // 翻译题干
  if (question.content) {
    translated.content = await translateText(question.content, targetLang)
  }

  // 翻译选项
  if (question.options && question.options.length > 0) {
    translated.options = await translateBatch(question.options, targetLang)
  }

  // 翻译答案
  if (question.answer) {
    translated.answer = await translateText(question.answer, targetLang)
  }

  // 翻译解析
  if (question.explanation) {
    translated.explanation = await translateText(question.explanation, targetLang)
  }

  return translated
}

/**
 * 创建翻译助手（在组件中使用）
 */
export function useTranslator() {
  const { t, locale } = useI18n()

  /**
   * 翻译单个文本
   */
  const translate = async (text: string): Promise<string> => {
    return translateText(text, locale.value)
  }

  /**
   * 翻译题目
   */
  const translateQuestionContent = async (question: any): Promise<any> => {
    return translateQuestion(question, locale.value)
  }

  /**
   * 获取当前语言
   */
  const getCurrentLanguage = (): string => {
    return locale.value
  }

  /**
   * 切换语言
   */
  const setLanguage = (lang: string): void => {
    locale.value = lang
  }

  return {
    translate,
    translateQuestionContent,
    getCurrentLanguage,
    setLanguage
  }
}

/**
 * 检测文本语言（简单实现）
 * @param text 要检测的文本
 * @returns 语言代码
 */
export function detectLanguage(text: string): string {
  if (!text) return 'zh-CN'

  // 检测是否包含中文字符
  const hasChinese = /[\u4e00-\u9fa5]/.test(text)
  
  if (hasChinese) {
    return 'zh-CN'
  }
  
  return 'en-US'
}

/**
 * 自动翻译页面内容（实验性功能）
 * @param container 容器元素
 * @param targetLang 目标语言
 */
export async function translatePageContent(
  container: HTMLElement,
  targetLang: string
): Promise<void> {
  if (!TRANSLATION_API.enabled) {
    return
  }

  // 查找所有需要翻译的文本元素
  const textElements = container.querySelectorAll('[data-translate]')
  
  for (const element of textElements) {
    const originalText = element.getAttribute('data-original-text') || element.textContent
    if (originalText && originalText.trim()) {
      const translated = await translateText(originalText, targetLang)
      element.textContent = translated
    }
  }
}

export default {
  translateText,
  translateBatch,
  translateQuestion,
  useTranslator,
  detectLanguage,
  translatePageContent
}
