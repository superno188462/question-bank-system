import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/HomeView.vue'),
      redirect: '/categories',
      children: [
        {
          path: 'categories',
          name: 'Categories',
          component: () => import('@/views/CategoryView.vue')
        },
        {
          path: 'questions',
          name: 'Questions',
          component: () => import('@/views/QuestionView.vue')
        },
        {
          path: 'questions/create',
          name: 'CreateQuestion',
          component: () => import('@/views/CreateQuestionView.vue')
        },
        {
          path: 'questions/:id/edit',
          name: 'EditQuestion',
          component: () => import('@/views/EditQuestionView.vue'),
          props: true
        },
        {
          path: 'ai-ask',
          name: 'AIAsk',
          component: () => import('@/views/AIAskView.vue')
        },
        {
          path: 'pending-questions',
          name: 'PendingQuestions',
          component: () => import('@/views/PendingQuestionsView.vue')
        }
      ]
    }
  ]
})

export default router