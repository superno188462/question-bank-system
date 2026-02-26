import api from './index'

export interface Category {
  id: string
  name: string
  description?: string
  parent_id?: string
  children?: Category[]
  created_at: string
  updated_at: string
}

export interface CategoryCreate {
  name: string
  description?: string
  parent_id?: string
}

export interface CategoryUpdate {
  name?: string
  description?: string
  parent_id?: string
}

export const categoryApi = {
  // 获取所有分类（树形结构）
  async getCategories(): Promise<Category[]> {
    return api.get('/categories')
  },

  // 获取单个分类
  async getCategory(id: string): Promise<Category> {
    return api.get(`/categories/${id}`)
  },

  // 创建分类
  async createCategory(data: CategoryCreate): Promise<Category> {
    return api.post('/categories', data)
  },

  // 更新分类
  async updateCategory(id: string, data: CategoryUpdate): Promise<Category> {
    return api.put(`/categories/${id}`, data)
  },

  // 删除分类
  async deleteCategory(id: string): Promise<boolean> {
    return api.delete(`/categories/${id}`)
  },

  // 获取分类树
  async getCategoryTree(): Promise<Category[]> {
    const categories = await this.getCategories()
    return this.buildCategoryTree(categories)
  },

  // 构建分类树
  buildCategoryTree(categories: Category[]): Category[] {
    const categoryMap = new Map<string, Category>()
    const tree: Category[] = []

    // 创建映射
    categories.forEach(category => {
      categoryMap.set(category.id, { ...category, children: [] })
    })

    // 构建树
    categories.forEach(category => {
      const node = categoryMap.get(category.id)!
      if (category.parent_id && categoryMap.has(category.parent_id)) {
        const parent = categoryMap.get(category.parent_id)!
        parent.children!.push(node)
      } else {
        tree.push(node)
      }
    })

    return tree
  },

  // 获取面包屑导航
  getBreadcrumbs(categories: Category[], categoryId: string): Category[] {
    const breadcrumbs: Category[] = []
    const findPath = (node: Category, path: Category[] = []): boolean => {
      if (node.id === categoryId) {
        breadcrumbs.push(...path, node)
        return true
      }
      
      if (node.children) {
        for (const child of node.children) {
          if (findPath(child, [...path, node])) {
            return true
          }
        }
      }
      
      return false
    }

    categories.forEach(category => {
      findPath(category)
    })

    return breadcrumbs
  }
}