import { createRouter, createWebHashHistory } from 'vue-router'
import SeoView from '@/views/SeoView.vue'
import SettingsView from '@/views/SettingsView.vue'
import StubView from '@/views/StubView.vue'

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
      component: StubView,
      meta: { title: 'Oversigt', heading: 'Oversigt', icon: 'Dashboard', sidebarKey: 'oversigt' },
    },
    {
      path: '/bookinger',
      component: StubView,
      meta: { title: 'Bookinger', heading: 'Bookinger', icon: 'Calendar', sidebarKey: 'bookinger' },
    },
    {
      path: '/statistik',
      component: StubView,
      meta: { title: 'Statistik', heading: 'Bookingstatistik', icon: 'Chart', sidebarKey: 'statistik' },
    },
    {
      path: '/behandlinger',
      component: StubView,
      meta: { title: 'Behandlinger', heading: 'Behandlinger', icon: 'Scissors', sidebarKey: 'behandlinger' },
    },
  ],
})
