<template>
  <el-dropdown trigger="click" @command="handleLanguageChange" class="language-switcher">
    <div class="language-button">
      <el-icon><Globe /></el-icon>
      <span class="current-language">{{ currentLanguageName }}</span>
      <el-icon class="el-icon--right"><ArrowDown /></el-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item 
          v-for="lang in availableLanguages" 
          :key="lang.code"
          :command="lang.code"
          :disabled="lang.code === currentLocale"
        >
          <span class="flag">{{ lang.flag }}</span>
          <el-icon v-if="lang.code === currentLocale"><Check /></el-icon>
          <span v-else style="width: 16px; display: inline-block;"></span>
          {{ lang.name }}
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { saveLanguage } from '@/i18n'
import { ElMessage } from 'element-plus'

const emit = defineEmits<{
  'language-change': [langCode: string]
}>()

const { locale, t } = useI18n()

// 可用语言列表
const availableLanguages = ref([
  { code: 'zh-CN', name: '中文（简体）', flag: '🇨🇳' },
  { code: 'en-US', name: 'English', flag: '🇺🇸' }
])

// 当前语言
const currentLocale = computed(() => locale.value)

// 当前语言名称
const currentLanguageName = computed(() => {
  const lang = availableLanguages.value.find(l => l.code === locale.value)
  return lang ? lang.name : '中文'
})

// 切换语言
const handleLanguageChange = (langCode: string) => {
  if (langCode !== locale.value) {
    locale.value = langCode
    saveLanguage(langCode)
    
    // 显示切换成功提示
    const lang = availableLanguages.value.find(l => l.code === langCode)
    ElMessage.success(`${t('language.switch')}：${lang?.name}`)
    
    // 触发语言切换事件，供父组件处理业务逻辑
    emit('language-change', langCode)
  }
}
</script>

<style scoped>
.language-switcher {
  cursor: pointer;
}

.language-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
  color: inherit;
}

.language-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.current-language {
  font-size: 14px;
  font-weight: 500;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-dropdown-menu__item.is-disabled) {
  cursor: default;
}

.flag {
  font-size: 16px;
  margin-right: 4px;
}
</style>
