import { createRouter, createWebHashHistory } from 'vue-router'
import SeoView from '@/views/SeoView.vue'
import SettingsView from '@/views/SettingsView.vue'
import OversigtsView from '@/views/OversigtsView.vue'
import BookingerView from '@/views/BookingerView.vue'
import BehandlingerView from '@/views/BehandlingerView.vue'
import PrislisteView from '@/views/PrislisteView.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/seo' },
    {
      path: '/seo',
      component: SeoView,
      meta: { title: 'SEO & Hjemmeside', breadcrumb: 'Crawl & analyse', sidebarKey: 'seo' },
    },
    {
      path: '/indstillinger',
      component: SettingsView,
      meta: { title: 'Indstillinger', sidebarKey: 'indstillinger' },
    },
    {
      path: '/oversigt',
      component: OversigtsView,
      meta: { title: 'Oversigt', sidebarKey: 'oversigt' },
    },
    {
      path: '/bookinger',
      component: BookingerView,
      meta: { title: 'Bookinger', sidebarKey: 'bookinger' },
    },
    {
      path: '/behandlinger',
      component: BehandlingerView,
      meta: { title: 'Behandlinger', sidebarKey: 'behandlinger' },
    },
    {
      path: '/prisliste',
      component: PrislisteView,
      meta: { title: 'Prisliste', sidebarKey: 'prisliste' },
    },
  ],
})
