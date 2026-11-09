import { createRouter, createWebHistory } from 'vue-router';
import OpdListView from '../views/OpdListView.vue';
import OpdRenstraView from '../views/OpdRenstraView.vue';
import SubOpdTableView from '../views/SubOpdTableView.vue';
import RenstraSubOpdView from '../views/RenstraSubOpdView.vue';
import TujuanSasaranReportView from '../views/TujuanSasaranReportView.vue';
import IkuReportView from '../views/IkuReportView.vue';
import ProgramKegiatanReportView from '../views/ProgramKegiatanReportView.vue';
import EvaluasiRenstraReportView from '../views/EvaluasiRenstraReportView.vue';

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
    path: '/laporan/tujuan-sasaran/:id?',
    name: 'LaporanTujuanSasaran',
    component: TujuanSasaranReportView,
    props: true,
    meta: { title: 'Laporan Tabel 3.1: Tujuan dan Sasaran - RENSTRA Kota Tegal' }
  },
  {
    path: '/laporan/program-kegiatan/:id?',
    name: 'LaporanProgramKegiatan',
    component: ProgramKegiatanReportView,
    props: true,
    meta: { title: 'Laporan Tabel 4.1: Program & Pendanaan - RENSTRA Kota Tegal' }
  },
  {
    path: '/laporan/iku/:id?',
    name: 'LaporanIku',
    component: IkuReportView,
    props: true,
    meta: { title: 'Laporan Indikator Kinerja Utama (IKU) - RENSTRA Kota Tegal' }
  },
  {
    path: '/laporan/evaluasi-renstra/:id?',
    name: 'LaporanEvaluasiRenstra',
    component: EvaluasiRenstraReportView,
    props: true,
    meta: { title: 'Laporan Evaluasi Hasil Renstra - Pemerintah Kota Tegal' }
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
