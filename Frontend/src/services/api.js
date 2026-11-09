const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/renstra/api' : 'http://localhost:7878/api');

/**
 * Helper function for HTTP requests with error handling
 */
async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorDetail = `HTTP error! status: ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  /**
   * Health check
   */
  async checkHealth() {
    return fetchJson(`${API_BASE_URL}/health`);
  },

  /**
   * Mengambil statistik dashboard eksekutif
   */
  async getStats() {
    return fetchJson(`${API_BASE_URL}/opd/stats`);
  },

  /**
   * Mengambil daftar seluruh Perangkat Daerah (ta_opd)
   * @param {Object} params - { search: string, has_sub: boolean }
   */
  async getOpdList(params = {}) {
    const query = new URLSearchParams();
    if (params.search && params.search.trim()) {
      query.append('search', params.search.trim());
    }
    if (params.has_sub !== undefined && params.has_sub !== null) {
      query.append('has_sub', params.has_sub);
    }

    const qs = query.toString();
    const url = `${API_BASE_URL}/opd${qs ? `?${qs}` : ''}`;
    return fetchJson(url);
  },

  /**
   * Mengambil detail OPD beserta daftar Sub SKPD
   * @param {number|string} idSkpd
   */
  async getOpdDetail(idSkpd) {
    return fetchJson(`${API_BASE_URL}/opd/${idSkpd}`);
  },

  /**
   * Mengambil daftar Sub SKPD milik OPD tertentu
   * @param {number|string} idSkpd
   * @param {string} search
   */
  async getSubOpdList(idSkpd, search = '') {
    const query = new URLSearchParams();
    if (search && search.trim()) {
      query.append('search', search.trim());
    }
    const qs = query.toString();
    const url = `${API_BASE_URL}/opd/${idSkpd}/sub${qs ? `?${qs}` : ''}`;
    return fetchJson(url);
  },

  /**
   * Mengambil detail satu Sub SKPD beserta data SKPD induknya
   * @param {number|string} idSubSkpd
   */
  async getSubOpdDetail(idSubSkpd) {
    return fetchJson(`${API_BASE_URL}/opd/sub/${idSubSkpd}`);
  },

  /**
   * Mengambil data cascading RENSTRA (Tujuan, Indikator Tujuan, Sasaran, Indikator Sasaran)
   * @param {number|string} idSkpd
   */
  async getOpdRenstraCascading(idSkpd) {
    return fetchJson(`${API_BASE_URL}/opd/${idSkpd}/renstra-cascading`);
  },

  /**
   * Mengambil data cascading Program / Kegiatan / Subkegiatan untuk Sub SKPD
   * @param {number|string} idSubSkpd
   */
  async getSubSkpdCascading(idSubSkpd) {
    return fetchJson(`${API_BASE_URL}/opd/sub/${idSubSkpd}/cascading`);
  },

  // ==========================================
  // CRUD RENSTRA
  // ==========================================

  // Tujuan
  async createTujuan(payload) {
    return fetchJson(`${API_BASE_URL}/renstra/tujuan`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateTujuan(idtujuan, payload) {
    return fetchJson(`${API_BASE_URL}/renstra/tujuan/${idtujuan}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
  async deleteTujuan(idtujuan) {
    return fetchJson(`${API_BASE_URL}/renstra/tujuan/${idtujuan}`, {
      method: 'DELETE',
    });
  },

  // Indikator Tujuan
  async createIndikatorTujuan(payload) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-tujuan`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateIndikatorTujuan(id, payload) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-tujuan/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
  async deleteIndikatorTujuan(id) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-tujuan/${id}`, {
      method: 'DELETE',
    });
  },

  // Sasaran
  async createSasaran(payload) {
    return fetchJson(`${API_BASE_URL}/renstra/sasaran`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateSasaran(idsasaran, payload) {
    return fetchJson(`${API_BASE_URL}/renstra/sasaran/${idsasaran}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
  async deleteSasaran(idsasaran) {
    return fetchJson(`${API_BASE_URL}/renstra/sasaran/${idsasaran}`, {
      method: 'DELETE',
    });
  },

  // Indikator Sasaran
  async createIndikatorSasaran(payload) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-sasaran`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateIndikatorSasaran(id, payload) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-sasaran/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
  async deleteIndikatorSasaran(id) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-sasaran/${id}`, {
      method: 'DELETE',
    });
  },

  // Indikator Kegiatan
  async createIndikatorKegiatan(payload) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-kegiatan`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateIndikatorKegiatan(id, payload) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-kegiatan/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
  async deleteIndikatorKegiatan(id) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-kegiatan/${id}`, {
      method: 'DELETE',
    });
  },

  // Indikator Program
  async updateIndikatorProgram(id, payload) {
    return fetchJson(`${API_BASE_URL}/renstra/indikator-program/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  // Program
  async createProgram(payload) {
    return fetchJson(`${API_BASE_URL}/renstra/program`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateProgram(id, payload) {
    return fetchJson(`${API_BASE_URL}/renstra/program/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
  async deleteProgram(id) {
    return fetchJson(`${API_BASE_URL}/renstra/program/${id}`, {
      method: 'DELETE',
    });
  },

  // Kegiatan
  async createKegiatan(payload) {
    return fetchJson(`${API_BASE_URL}/renstra/kegiatan`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateKegiatan(id, payload) {
    return fetchJson(`${API_BASE_URL}/renstra/kegiatan/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
  async deleteKegiatan(id) {
    return fetchJson(`${API_BASE_URL}/renstra/kegiatan/${id}`, {
      method: 'DELETE',
    });
  },

  // Subkegiatan
  async createSubkegiatan(payload) {
    return fetchJson(`${API_BASE_URL}/renstra/subkegiatan`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
  async updateSubkegiatan(id, payload) {
    return fetchJson(`${API_BASE_URL}/renstra/subkegiatan/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },
  async deleteSubkegiatan(id) {
    return fetchJson(`${API_BASE_URL}/renstra/subkegiatan/${id}`, {
      method: 'DELETE',
    });
  },

  // Referensi dari ref_subkegiatan & Sasaran OPD
  async getRefKegiatan(kodeProgram) {
    return fetchJson(`${API_BASE_URL}/renstra/ref/kegiatan?kode_program=${encodeURIComponent(kodeProgram || '')}`);
  },
  async getRefSubkegiatan(kodeKegiatan) {
    return fetchJson(`${API_BASE_URL}/renstra/ref/subkegiatan?kode_kegiatan=${encodeURIComponent(kodeKegiatan || '')}`);
  },
  async getRefSasaran(params = {}) {
    const query = new URLSearchParams();
    if (params.kodeskpd) query.append('kodeskpd', params.kodeskpd);
    if (params.id_skpd) query.append('id_skpd', params.id_skpd);
    if (params.id_sub_skpd) query.append('id_sub_skpd', params.id_sub_skpd);
    const qs = query.toString();
    return fetchJson(`${API_BASE_URL}/renstra/ref/sasaran${qs ? `?${qs}` : ''}`);
  },

  // AI Assistant SMART Indicator Recommendations
  async getSmartIndicatorRecommendations(payload) {
    return fetchJson(`${API_BASE_URL}/ai/smart-indicator-recommendation`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Laporan RENSTRA
  async getLaporanOpdList() {
    return fetchJson(`${API_BASE_URL}/laporan/opd-list`);
  },
  async getLaporanTujuanSasaran(idSkpd, tipe = 'murni') {
    return fetchJson(`${API_BASE_URL}/laporan/tujuan-sasaran/${idSkpd}?tipe=${encodeURIComponent(tipe)}`);
  },
  getLaporanTujuanSasaranExcelUrl(idSkpd, tipe = 'murni') {
    return `${API_BASE_URL}/laporan/tujuan-sasaran/${idSkpd}/export-excel?tipe=${encodeURIComponent(tipe)}`;
  },
  async downloadLaporanTujuanSasaranExcel(idSkpd, tipe = 'murni') {
    const url = this.getLaporanTujuanSasaranExcelUrl(idSkpd, tipe);
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Gagal mengunduh Excel: HTTP ${res.status}`);
    }
    const blob = await res.blob();
    const disposition = res.headers.get('content-disposition');
    let filename = `Tabel_3.1_Tujuan_dan_Sasaran_OPD_${idSkpd}.xlsx`;
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename=["']?([^"']+)["']?/);
      if (match && match[1]) filename = match[1];
    }
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },

  // Laporan IKU (Indikator Kinerja Utama)
  async getLaporanIku(idSkpd, tipe = 'murni') {
    return fetchJson(`${API_BASE_URL}/laporan/iku/${idSkpd}?tipe=${encodeURIComponent(tipe)}`);
  },
  getLaporanIkuExcelUrl(idSkpd, tipe = 'murni') {
    return `${API_BASE_URL}/laporan/iku/${idSkpd}/export-excel?tipe=${encodeURIComponent(tipe)}`;
  },
  async downloadLaporanIkuExcel(idSkpd, tipe = 'murni') {
    const url = this.getLaporanIkuExcelUrl(idSkpd, tipe);
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Gagal mengunduh Excel IKU: HTTP ${res.status}`);
    }
    const blob = await res.blob();
    const disposition = res.headers.get('content-disposition');
    let filename = `IKU_OPD_${idSkpd}.xlsx`;
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename=["']?([^"']+)["']?/);
      if (match && match[1]) filename = match[1];
    }
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },
  // Laporan Tabel 4.1: Program, Kegiatan, Sub Kegiatan & Pendanaan
  async getLaporanProgramKegiatan(idSkpd, params = {}) {
    const { idSubSkpd = null, tipe = 'murni' } = params;
    let url = `${API_BASE_URL}/laporan/program-kegiatan/${idSkpd}?tipe=${encodeURIComponent(tipe)}`;
    if (idSubSkpd) url += `&id_sub_skpd=${encodeURIComponent(idSubSkpd)}`;
    return fetchJson(url);
  },
  getLaporanProgramKegiatanExcelUrl(idSkpd, params = {}) {
    const { idSubSkpd = null, tipe = 'murni' } = params;
    let url = `${API_BASE_URL}/laporan/program-kegiatan/${idSkpd}/export-excel?tipe=${encodeURIComponent(tipe)}`;
    if (idSubSkpd) url += `&id_sub_skpd=${encodeURIComponent(idSubSkpd)}`;
    return url;
  },
  async downloadLaporanProgramKegiatanExcel(idSkpd, params = {}) {
    const url = this.getLaporanProgramKegiatanExcelUrl(idSkpd, params);
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Gagal mengunduh Excel Program Kegiatan: HTTP ${res.status}`);
    }
    const blob = await res.blob();
    const disposition = res.headers.get('content-disposition');
    let filename = `Tabel_4.1_Program_Kegiatan_OPD_${idSkpd}.xlsx`;
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename=["']?([^"']+)["']?/);
      if (match && match[1]) filename = match[1];
    }
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },

  // Laporan Evaluasi Hasil Renstra (Permendagri 86/2017)
  async getLaporanEvaluasiRenstra(idSkpd, params = {}) {
    const { idSubSkpd = null, tipe = 'murni' } = params;
    let url = `${API_BASE_URL}/laporan/evaluasi-renstra/${idSkpd}?tipe=${encodeURIComponent(tipe)}`;
    if (idSubSkpd) url += `&id_sub_skpd=${encodeURIComponent(idSubSkpd)}`;
    return fetchJson(url);
  },
  getLaporanEvaluasiRenstraExcelUrl(idSkpd, params = {}) {
    const { idSubSkpd = null, tipe = 'murni' } = params;
    let url = `${API_BASE_URL}/laporan/evaluasi-renstra/${idSkpd}/export-excel?tipe=${encodeURIComponent(tipe)}`;
    if (idSubSkpd) url += `&id_sub_skpd=${encodeURIComponent(idSubSkpd)}`;
    return url;
  },
  async downloadLaporanEvaluasiRenstraExcel(idSkpd, params = {}) {
    const url = this.getLaporanEvaluasiRenstraExcelUrl(idSkpd, params);
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Gagal mengunduh Excel Evaluasi Renstra: HTTP ${res.status}`);
    }
    const blob = await res.blob();
    const disposition = res.headers.get('content-disposition');
    let filename = `Evaluasi_Hasil_Renstra_OPD_${idSkpd}.xlsx`;
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename=["']?([^"']+)["']?/);
      if (match && match[1]) filename = match[1];
    }
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },
};

export default api;



