import { createRouter, createWebHistory } from 'vue-router';
import OpdListView from '../views/OpdListView.vue';
import OpdRenstraView from '../views/OpdRenstraView.vue';
import SubOpdTableView from '../views/SubOpdTableView.vue';
import RenstraSubOpdView from '../views/RenstraSubOpdView.vue';

const routes = [
  {
    path: '/',
    name: 'OpdList',
    component: OpdListView,
    meta: { title: 'Daftar Perangkat Daerah - RENSTRA Kota Tegal' }
  },
  {
    path: '/opd/:id',
    name: 'OpdRenstra',
    component: OpdRenstraView,
    props: true,
    meta: { title: 'RENSTRA Perangkat Daerah - Kota Tegal' }
  },
  {
    path: '/sub-opd/:subId',
    name: 'RenstraSubOpd',
    component: RenstraSubOpdView,
    props: true,
    meta: { title: 'Dokumen RENSTRA - Pemerintah Kota Tegal' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title;
  }
  next();
});

export default router;
