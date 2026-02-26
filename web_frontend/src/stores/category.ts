import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { categoryApi, type Category, type CategoryCreate, type CategoryUpdate } from '@/api/category'

export const useCategoryStore = defineStore('category', () => {
  const categories = ref<Category[]>([])
  const categoryTree = ref<Category[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 获取所有分类
  const fetchCategories = async () => {
    loading.value = true
    error.value = null
    try {
      categories.value = await categoryApi.getCategories()
      categoryTree.value = categoryApi.buildCategoryTree(categories.value)
    } catch (err: any) {
      error.value = err.message || '获取分类失败'
      console.error('获取分类失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 创建分类
  const createCategory = async (data: CategoryCreate) => {
    loading.value = true
    error.value = null
    try {
      const newCategory = await categoryApi.createCategory(data)
      await fetchCategories() // 重新获取分类列表
      return newCategory
    } catch (err: any) {
      error.value = err.message || '创建分类失败'
      console.error('创建分类失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新分类
  const updateCategory = async (id: string, data: CategoryUpdate) => {
    loading.value = true
    error.value = null
    try {
      const updatedCategory = await categoryApi.updateCategory(id, data)
      await fetchCategories() // 重新获取分类列表
      return updatedCategory
    } catch (err: any) {
      error.value = err.message || '更新分类失败'
      console.error('更新分类失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除分类
  const deleteCategory = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      const success = await categoryApi.deleteCategory(id)
      if (success) {
        await fetchCategories() // 重新获取分类列表
      }
      return success
    } catch (err: any) {
      error.value = err.message || '删除分类失败'
      console.error('删除分类失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 根据ID获取分类
  const getCategoryById = computed(() => (id: string) => {
    return categories.value.find(category => category.id === id)
  })

  // 获取面包屑导航
  const getBreadcrumbs = computed(() => (categoryId: string) => {
    return categoryApi.getBreadcrumbs(categoryTree.value, categoryId)
  })

  // 获取子分类
  const getChildCategories = computed(() => (parentId?: string) => {
    if (!parentId) {
      return categoryTree.value
    }
    
    const findCategory = (nodes: Category[]): Category | undefined => {
      for (const node of nodes) {
        if (node.id === parentId) {
          return node
        }
        if (node.children && node.children.length > 0) {
          const found = findCategory(node.children)
          if (found) return found
        }
      }
      return undefined
    }
    
    const parent = findCategory(categoryTree.value)
    return parent?.children || []
  })

  // 获取所有分类的扁平列表
  const getAllCategoriesFlat = computed(() => {
    const flatten = (nodes: Category[]): Category[] => {
      let result: Category[] = []
      nodes.forEach(node => {
        result.push(node)
        if (node.children && node.children.length > 0) {
          result = result.concat(flatten(node.children))
        }
      })
      return result
    }
    
    return flatten(categoryTree.value)
  })

  // 初始化时获取分类
  fetchCategories()

  return {
    categories,
    categoryTree,
    loading,
    error,
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    getCategoryById,
    getBreadcrumbs,
    getChildCategories,
    getAllCategoriesFlat
  }
})