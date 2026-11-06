<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="modal-backdrop"
      style="display: flex; align-items: center; justify-content: center; padding: 1.5rem;"
      @click.self="closeModal"
      @keydown.esc="closeModal"
    >
      <div class="crud-modal-card" role="dialog" aria-modal="true">
        <!-- Modal Header -->
        <div class="crud-modal-header" :class="{ 'delete-header': isDeleteMode }">
          <div class="crud-modal-title-group">
            <span class="badge-tag" style="align-self: flex-start; margin-bottom: 0.25rem;">
              {{ modalCategoryLabel }}
            </span>
            <h3>{{ modalTitle }}</h3>
          </div>
          <button class="btn-close-drawer" @click="closeModal" title="Tutup">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Modal Body: DELETE CONFIRMATION -->
        <div v-if="isDeleteMode" class="crud-modal-body">
          <div style="display: flex; gap: 1rem; align-items: flex-start;">
            <div style="width: 48px; height: 48px; border-radius: 50%; background: #fee2e2; color: #dc2626; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <div>
              <h4 style="font-size: 1.05rem; font-weight: 700; color: #991b1b; margin-bottom: 0.35rem;">
                Konfirmasi Hapus Data
              </h4>
              <p style="font-size: 0.88rem; color: #4b5563; line-height: 1.5;">
                Apakah Anda yakin ingin menghapus <strong>{{ deleteItemLabel }}</strong>?
              </p>
              <div v-if="deleteItemType === 'tujuan'" style="margin-top: 0.75rem; padding: 0.65rem 0.85rem; background: #fff1f2; border: 1px solid #fecdd3; border-radius: var(--radius-sm); font-size: 0.8rem; color: #be123c;">
                <strong>Perhatian:</strong> Menghapus Tujuan akan menghapus seluruh <strong>Indikator Tujuan, Sasaran, dan Indikator Sasaran</strong> di bawahnya secara permanen!
              </div>
              <div v-else-if="deleteItemType === 'sasaran'" style="margin-top: 0.75rem; padding: 0.65rem 0.85rem; background: #fff1f2; border: 1px solid #fecdd3; border-radius: var(--radius-sm); font-size: 0.8rem; color: #be123c;">
                <strong>Perhatian:</strong> Menghapus Sasaran akan menghapus seluruh <strong>Indikator Sasaran</strong> di bawahnya secara permanen!
              </div>
              <div v-else-if="deleteItemType === 'program'" style="margin-top: 0.75rem; padding: 0.65rem 0.85rem; background: #fff1f2; border: 1px solid #fecdd3; border-radius: var(--radius-sm); font-size: 0.8rem; color: #be123c;">
                <strong>Perhatian:</strong> Menghapus Program akan menghapus seluruh <strong>Kegiatan dan Subkegiatan</strong> di bawahnya secara permanen!
              </div>
              <div v-else-if="deleteItemType === 'kegiatan'" style="margin-top: 0.75rem; padding: 0.65rem 0.85rem; background: #fff1f2; border: 1px solid #fecdd3; border-radius: var(--radius-sm); font-size: 0.8rem; color: #be123c;">
                <strong>Perhatian:</strong> Menghapus Kegiatan akan menghapus seluruh <strong>Subkegiatan dan Indikator Kegiatan</strong> di bawahnya secara permanen!
              </div>
              <div v-else-if="deleteItemType === 'subkegiatan'" style="margin-top: 0.75rem; padding: 0.65rem 0.85rem; background: #fff1f2; border: 1px solid #fecdd3; border-radius: var(--radius-sm); font-size: 0.8rem; color: #be123c;">
                <strong>Perhatian:</strong> Subkegiatan ini beserta indikator dan target volumenya akan dihapus secara permanen!
              </div>
              <div style="margin-top: 0.75rem; font-family: var(--font-sans); font-size: 0.85rem; color: #1e293b; background: #f8fafc; padding: 0.6rem; border-radius: 6px; border: 1px solid #e2e8f0;">
                <em>"{{ deleteItemText }}"</em>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Body: FORM (TUJUAN / SASARAN) -->
        <div v-else-if="isTujuanSasaranForm" class="crud-modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                <label class="form-label" style="margin-bottom: 0;">
                  Uraian {{ isTujuan ? 'Tujuan' : 'Sasaran' }} <span v-if="!isEditMode" style="color: #ef4444;">*</span>
                </label>
                <span v-if="isEditMode" class="badge-locked" title="Rumusan kalimat terkunci sesuai ketentuan RENSTRA Perubahan">
                  🔒 Kalimat Terkunci
                </span>
              </div>
              <textarea
                class="form-textarea"
                :class="{ 'readonly-locked': isEditMode }"
                v-model="formData.uraian"
                rows="3"
                :required="!isEditMode"
                :readonly="isEditMode"
                :disabled="isEditMode"
                :placeholder="`Masukkan rumusan uraian ${isTujuan ? 'Tujuan' : 'Sasaran'} RENSTRA...`"
              ></textarea>
              <div v-if="isEditMode" class="form-helper-locked">
                Kalimat rumusan tidak dapat diedit pada RENSTRA Perubahan. Anda hanya dapat menyesuaikan nomor urut dan status data.
              </div>
            </div>

            <div style="display: flex; gap: 0.85rem; align-items: flex-start; margin-top: 0.75rem;">
              <div class="form-group" style="width: 140px;">
                <label class="form-label">Nomor Urut</label>
                <input
                  type="number"
                  class="form-input"
                  v-model.number="formData.no_urut"
                  min="1"
                />
              </div>
              <div class="form-group" style="flex: 1;">
                <label class="form-label">Status Data (Renstra Perubahan)</label>
                <select class="form-input" v-model="formData.perubahan_status" style="cursor: pointer;">
                  <option value="otomatis">Otomatis</option>
                  <option value="baru">Data Baru</option>
                  <option value="perubahan">Ada Perubahan</option>
                  <option value="tetap">Tetap</option>
                </select>
              </div>
            </div>
          </form>
        </div>

        <!-- Modal Body: FORM (INDIKATOR TUJUAN / INDIKATOR SASARAN) -->
        <div v-else-if="isIndikatorForm" class="crud-modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                <label class="form-label" style="margin-bottom: 0;">
                  Uraian Indikator Kinerja <span v-if="!isEditMode" style="color: #ef4444;">*</span>
                </label>
                <span v-if="isEditMode" class="badge-locked" title="Rumusan kalimat indikator terkunci sesuai ketentuan RENSTRA Perubahan">
                  🔒 Kalimat Terkunci
                </span>
              </div>
              <textarea
                class="form-textarea"
                :class="{ 'readonly-locked': isEditMode }"
                v-model="formData.uraian"
                rows="2"
                :required="!isEditMode"
                :readonly="isEditMode"
                :disabled="isEditMode"
                placeholder="Contoh: Rata-Rata Lama Sekolah, Indeks Kepuasan Masyarakat..."
              ></textarea>
              <div v-if="isEditMode" class="form-helper-locked">
                Rumusan kalimat indikator tidak dapat diubah pada RENSTRA Perubahan.
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1.1fr 1.2fr 0.7fr; gap: 0.85rem; margin-top: 0.75rem;">
              <div class="form-group">
                <label class="form-label">Satuan <span style="color: #ef4444;">*</span></label>
                <input
                  type="text"
                  class="form-input"
                  v-model="formData.satuan"
                  required
                  placeholder="Contoh: %, Nilai, Poin, Dokumen"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Status <span style="color: #ef4444;">*</span></label>
                <select class="form-input" v-model="formData.status" required style="cursor: pointer;">
                  <option value="positif">positif</option>
                  <option value="negatif">negatif</option>
                  <option value="akumulatif">akumulatif</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Nomor Urut</label>
                <input
                  type="number"
                  class="form-input"
                  v-model.number="formData.no_urut"
                  min="1"
                />
              </div>
            </div>

            <!-- IKU (Indikator Kinerja Utama) -->
            <div style="margin-top: 0.75rem; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 0.65rem 0.85rem; display: flex; align-items: center; justify-content: space-between;">
              <div style="display: flex; align-items: center; gap: 0.6rem;">
                <input
                  type="checkbox"
                  id="checkbox-iku"
                  :checked="formData.iku === '1'"
                  @change="formData.iku = $event.target.checked ? '1' : '0'"
                  style="width: 18px; height: 18px; cursor: pointer; accent-color: #16a34a;"
                />
                <label for="checkbox-iku" style="cursor: pointer; font-size: 0.85rem; font-weight: 600; color: #166534; user-select: none;">
                  Tandai sebagai Indikator Kinerja Utama (IKU)
                </label>
              </div>
              <span v-if="formData.iku === '1'" style="font-size: 0.72rem; font-weight: 700; color: #15803d; background: #dcfce7; padding: 0.15rem 0.5rem; border-radius: 9999px;">
                ✓ IKU AKTIF
              </span>
            </div>

            <!-- Penandaan Status Perubahan Data -->
            <div style="margin-top: 0.75rem;">
              <label class="form-label">
                Penandaan Status (Renstra Perubahan)
              </label>
              <select class="form-input" v-model="formData.perubahan_status" style="cursor: pointer;">
                <option value="otomatis">Otomatis (Sistem Mendeteksi Perbandingan Target)</option>
                <option value="perubahan">Ada Perubahan Target</option>
                <option value="baru">Data Baru (Usulan Baru)</option>
                <option value="tetap">Tetap (Tidak Ada Perubahan)</option>
              </select>
            </div>

            <!-- Live Alert Terdeteksi Target Berubah -->
            <div
              v-if="detectedChanges.length > 0"
              style="margin-top: 0.65rem; background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 0.55rem 0.85rem; font-size: 0.78rem; color: #b45309; display: flex; align-items: center; gap: 0.5rem;"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              <span>Terdeteksi penyesuaian target pada tahun: <strong>{{ detectedChanges.join(', ') }}</strong></span>
            </div>

            <!-- Definisi Operasional / Metadata -->
            <div class="form-group" style="margin-top: 0.75rem;">
              <label class="form-label">
                Definisi Operasional / Metadata
              </label>
              <textarea
                class="form-textarea"
                v-model="formData.definisi_operasional"
                rows="2"
                placeholder="Penjelasan definisi operasional, formula perhitungan, atau metadata indikator..."
              ></textarea>
            </div>

            <!-- Target Capaian Grid (Murni / Sebelum Perubahan) -->
            <div style="margin-top: 1.25rem;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 0.5rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  <label class="form-label" style="font-weight: 700; color: #1e3a8a; margin-bottom: 0;">
                    Target Capaian Kinerja (Murni)
                  </label>
                  <span v-if="isEditMode" class="badge-locked" title="Target Murni adalah acuan penetapan awal dan tidak dapat diubah">
                    🔒 Terkunci
                  </span>
                </div>
                <span style="font-size: 0.75rem; color: #64748b; font-weight: 500;">
                  * Target Murni adalah acuan awal (tidak dapat diubah)
                </span>
              </div>
              <div class="targets-form-grid" :class="{ 'grid-locked': isEditMode }">
                <div class="form-group">
                  <label class="form-label sub">Target Awal <span style="font-size: 0.72rem; opacity: 0.85;">(Baseline)</span></label>
                  <input type="text" class="form-input mono" :class="{ 'readonly-locked': isEditMode }" :readonly="isEditMode" :disabled="isEditMode" v-model="formData.target_awal" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub">Target 2026</label>
                  <input type="text" class="form-input mono" :class="{ 'readonly-locked': isEditMode }" :readonly="isEditMode" :disabled="isEditMode" v-model="formData.target2026" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub">Target 2027</label>
                  <input type="text" class="form-input mono" :class="{ 'readonly-locked': isEditMode }" :readonly="isEditMode" :disabled="isEditMode" v-model="formData.target2027" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub">Target 2028</label>
                  <input type="text" class="form-input mono" :class="{ 'readonly-locked': isEditMode }" :readonly="isEditMode" :disabled="isEditMode" v-model="formData.target2028" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub">Target 2029</label>
                  <input
                    type="text"
                    class="form-input mono"
                    :class="{ 'readonly-locked': isEditMode }"
                    :readonly="isEditMode"
                    :disabled="isEditMode"
                    v-model="formData.target2029"
                    @input="onTarget2029Input"
                    placeholder="-"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label sub">Target 2030</label>
                  <input
                    type="text"
                    class="form-input mono"
                    :class="{ 'readonly-locked': isEditMode }"
                    :readonly="isEditMode"
                    :disabled="isEditMode"
                    v-model="formData.target2030"
                    placeholder="-"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label sub" style="color: #059669; font-weight: 700;">
                    Target Akhir
                  </label>
                  <input
                    type="text"
                    class="form-input mono"
                    :class="{ 'readonly-locked': isEditMode }"
                    :readonly="isEditMode"
                    :disabled="isEditMode"
                    v-model="formData.target_akhir"
                    placeholder="-"
                    style="border-color: #a7f3d0;"
                  />
                </div>
              </div>
            </div>

            <!-- Target Perubahan Grid -->
            <div style="margin-top: 1.25rem;">
              <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 0.5rem;">
                <label class="form-label" style="font-weight: 700; color: #b45309; margin-bottom: 0; display: flex; align-items: center; gap: 0.45rem;">
                  <span class="badge-perubahan">Perubahan</span>
                  Target Perubahan (Dapat Disesuaikan)
                </label>
                <span style="font-size: 0.75rem; color: #d97706; font-weight: 600;">
                  * Target Akhir setelah perubahan memakai tahun 2029 perubahan
                </span>
              </div>
              <div class="targets-form-grid targets-perubahan-grid">
                <div class="form-group">
                  <label class="form-label sub p-label">Tahun 2025</label>
                  <input type="text" class="form-input mono p-input" v-model="formData.p_target2025" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub p-label">Tahun 2026</label>
                  <input type="text" class="form-input mono p-input" v-model="formData.p_target2026" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub p-label">Tahun 2027</label>
                  <input type="text" class="form-input mono p-input" v-model="formData.p_target2027" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub p-label">Tahun 2028</label>
                  <input type="text" class="form-input mono p-input" v-model="formData.p_target2028" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub p-label">Tahun 2029</label>
                  <input
                    type="text"
                    class="form-input mono p-input"
                    v-model="formData.p_target2029"
                    @input="onTarget2029PerubahanInput"
                    placeholder="-"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label sub p-label">Tahun 2030</label>
                  <input
                    type="text"
                    class="form-input mono p-input"
                    v-model="formData.p_target2030"
                    placeholder="-"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label sub" style="color: #b45309; font-weight: 700;">
                    Target Akhir Perubahan
                  </label>
                  <input
                    type="text"
                    class="form-input mono"
                    v-model="formData.p_target_akhir"
                    placeholder="-"
                    style="border-color: #fcd34d; background: #fffbeb;"
                  />
                </div>
              </div>

              <!-- Grid Pagu Anggaran Murni & Perubahan jika Indikator Kegiatan -->
              <div v-if="props.mode.includes('ind_kegiatan')" style="margin-top: 1rem;">
                <div class="form-section-header">
                  <label class="form-label" style="font-weight: 600; color: #1e293b;">
                    Pagu Anggaran Indikator Kegiatan (Murni)
                  </label>
                </div>
                <div class="targets-form-grid" style="grid-template-columns: repeat(5, 1fr);">
                  <div class="form-group">
                    <label class="form-label sub">Pagu 2026</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu1" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">Pagu 2027</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu2" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">Pagu 2028</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu3" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">Pagu 2029</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu4" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">Pagu 2030</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu5" placeholder="0" />
                  </div>
                </div>

                <div class="form-section-header" style="margin-top: 0.85rem;">
                  <label class="form-label" style="font-weight: 600; color: #b45309; display: flex; align-items: center; gap: 0.35rem;">
                    <span class="badge-perubahan">Perubahan</span>
                    Pagu Anggaran Indikator Kegiatan (Perubahan)
                  </label>
                </div>
                <div class="targets-form-grid targets-perubahan-grid" style="grid-template-columns: repeat(5, 1fr);">
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2026</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu1" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2027</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu2" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2028</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu3" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2029</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu4" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2030</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu5" placeholder="0" />
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>

        <!-- Modal Body: FORM (PROGRAM) -->
        <div v-else-if="isProgramForm" class="crud-modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label class="form-label">Kode Program <span style="color: #ef4444;">*</span></label>
              <input
                type="text"
                class="form-input mono"
                v-model="formData.kodeprogram"
                required
                placeholder="Contoh: 1.01.01"
              />
            </div>
            <div class="form-group" style="margin-top: 0.75rem;">
              <label class="form-label">Nama / Uraian Program <span style="color: #ef4444;">*</span></label>
              <textarea
                class="form-textarea"
                v-model="formData.uraiprogram"
                rows="2"
                required
                placeholder="Contoh: PROGRAM PENUNJANG URUSAN PEMERINTAHAN DAERAH..."
              ></textarea>
            </div>
            <div class="form-group" style="margin-top: 0.75rem;">
              <label class="form-label">Kinerja Program / Outcome </label>
              <textarea
                class="form-textarea"
                v-model="formData.kinerja"
                rows="2"
                placeholder="Rumusan kinerja/outcome program, misal: Meningkatnya Tata Kelola Organisasi Pemerintah Daerah..."
              ></textarea>
            </div>
          </form>
        </div>

        <!-- Modal Body: FORM (KEGIATAN) -->
        <div v-else-if="isKegiatanForm" class="crud-modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label class="form-label">Kode Kegiatan <span style="color: #ef4444;">*</span></label>
              <input
                type="text"
                class="form-input mono"
                v-model="formData.kodekegiatan"
                required
                placeholder="Contoh: 1.01.01.2.01"
              />
            </div>
            <div class="form-group" style="margin-top: 0.75rem;">
              <label class="form-label">Nama / Uraian Kegiatan <span style="color: #ef4444;">*</span></label>
              <textarea
                class="form-textarea"
                v-model="formData.uraikegiatan"
                rows="2"
                required
                placeholder="Contoh: Perencanaan, Penganggaran, dan Evaluasi Kinerja..."
              ></textarea>
            </div>
            <div class="form-group" style="margin-top: 0.75rem;">
              <label class="form-label">Kinerja Kegiatan (Output)</label>
              <textarea
                class="form-textarea"
                v-model="formData.kinerja"
                rows="2"
                placeholder="Rumusan kinerja kegiatan..."
              ></textarea>
            </div>
          </form>
        </div>

        <!-- Modal Body: FORM (SUBKEGIATAN) -->
        <div v-else-if="isSubkegiatanForm" class="crud-modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label class="form-label">Kode Subkegiatan <span style="color: #ef4444;">*</span></label>
              <input
                type="text"
                class="form-input mono"
                v-model="formData.kodesubkegiatan"
                required
                placeholder="Contoh: 1.01.01.2.01.0001"
              />
            </div>
            <div class="form-group" style="margin-top: 0.75rem;">
              <label class="form-label">Nama / Uraian Subkegiatan <span style="color: #ef4444;">*</span></label>
              <textarea
                class="form-textarea"
                v-model="formData.uraisubkegiatan"
                rows="2"
                required
                placeholder="Contoh: Penyusunan Dokumen Perencanaan Perangkat Daerah..."
              ></textarea>
            </div>
            <div class="form-group" style="margin-top: 0.75rem;">
              <label class="form-label">Kinerja Subkegiatan</label>
              <textarea
                class="form-textarea"
                v-model="formData.kinerja"
                rows="2"
                placeholder="Rumusan kinerja subkegiatan, misal: Tersusunnya Dokumen Perencanaan..."
              ></textarea>
            </div>

            <!-- Bagian Indikator Subkegiatan & Target Volume -->
            <div style="margin-top: 1.25rem; padding: 0.85rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
              <div style="font-weight: 700; font-size: 0.88rem; color: #1e3a8a; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem;">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
                <span>Indikator Kinerja Subkegiatan</span>
              </div>
              <div class="form-group">
                <label class="form-label">Uraian Indikator (uraisubkegiatan_indikator)</label>
                <input
                  type="text"
                  class="form-input"
                  v-model="formData.uraisubkegiatan_indikator"
                  placeholder="Contoh: Jumlah Dokumen Perencanaan Perangkat Daerah"
                />
              </div>
              <div class="form-group" style="margin-top: 0.65rem;">
                <label class="form-label">Satuan</label>
                <input
                  type="text"
                  class="form-input"
                  v-model="formData.satuan"
                  placeholder="Contoh: Dokumen, Unit, Orang, %"
                />
              </div>

              <!-- Grid Target Volume (volume_0, volume_1, dst) -->
              <div style="margin-top: 0.85rem;">
                <label class="form-label" style="font-weight: 600; color: #475569; font-size: 0.8rem;">
                  Target Volume Capaian (volume_0, volume_1 .. volume_5)
                </label>
                <div class="targets-form-grid" style="grid-template-columns: repeat(7, 1fr);">
                  <div class="form-group">
                    <label class="form-label sub">Awal</label>
                    <input type="text" class="form-input mono" v-model="formData.volume_awal" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2025</label>
                    <input type="text" class="form-input mono" v-model="formData.volume_0" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2026</label>
                    <input type="text" class="form-input mono" v-model="formData.volume_1" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2027</label>
                    <input type="text" class="form-input mono" v-model="formData.volume_2" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2028</label>
                    <input type="text" class="form-input mono" v-model="formData.volume_3" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2029</label>
                    <input type="text" class="form-input mono" v-model="formData.volume_4" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2030</label>
                    <input type="text" class="form-input mono" v-model="formData.volume_5" placeholder="-" />
                  </div>
                </div>
              </div>

              <!-- Grid Target Volume Perubahan -->
              <div style="margin-top: 0.85rem;">
                <label class="form-label" style="font-weight: 600; color: #b45309; font-size: 0.8rem; display: flex; align-items: center; gap: 0.35rem;">
                  <span class="badge-perubahan">Perubahan</span>
                  Target Perubahan
                </label>
                <div class="targets-form-grid targets-perubahan-grid" style="grid-template-columns: repeat(7, 1fr);">
                  <div class="form-group">
                    <label class="form-label sub p-label">2025</label>
                    <input type="text" class="form-input mono p-input" v-model="formData.p_volume_0" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">2026</label>
                    <input type="text" class="form-input mono p-input" v-model="formData.p_volume_1" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">2027</label>
                    <input type="text" class="form-input mono p-input" v-model="formData.p_volume_2" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">2028</label>
                    <input type="text" class="form-input mono p-input" v-model="formData.p_volume_3" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">2029</label>
                    <input type="text" class="form-input mono p-input" v-model="formData.p_volume_4" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">2030</label>
                    <input type="text" class="form-input mono p-input" v-model="formData.p_volume_5" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub" style="color: #b45309; font-weight: 700;">Akhir (P)</label>
                    <input type="text" class="form-input mono" v-model="formData.p_volume_akhir" placeholder="-" style="border-color: #fcd34d; background: #fffbeb;" />
                  </div>
                </div>
              </div>

              <!-- Grid Pagu Anggaran Murni (pagu1..pagu5) -->
              <div style="margin-top: 0.85rem;">
                <label class="form-label" style="font-weight: 600; color: #475569; font-size: 0.8rem;">
                  Pagu Anggaran Subkegiatan (Murni)
                </label>
                <div class="targets-form-grid" style="grid-template-columns: repeat(5, 1fr);">
                  <div class="form-group">
                    <label class="form-label sub">2026</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu1" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2027</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu2" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2028</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu3" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2029</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu4" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub">2030</label>
                    <input type="number" class="form-input mono" v-model.number="formData.pagu5" placeholder="0" />
                  </div>
                </div>
              </div>

              <!-- Grid Pagu Anggaran Perubahan (p_pagu1..p_pagu5) -->
              <div style="margin-top: 0.85rem;">
                <label class="form-label" style="font-weight: 600; color: #b45309; font-size: 0.8rem; display: flex; align-items: center; gap: 0.35rem;">
                  <span class="badge-perubahan">Perubahan</span>
                  Pagu Anggaran Subkegiatan (Perubahan)
                </label>
                <div class="targets-form-grid targets-perubahan-grid" style="grid-template-columns: repeat(5, 1fr);">
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2026</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu1" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2027</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu2" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2028</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu3" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2029</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu4" placeholder="0" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub p-label">Pagu (P) 2030</label>
                    <input type="number" class="form-input mono p-input" v-model.number="formData.p_pagu5" placeholder="0" />
                  </div>
                </div>
              </div>
            </div>
          </form>
        </div>

        <!-- Modal Footer -->
        <div class="crud-modal-footer">
          <button class="btn-action-secondary" @click="closeModal" :disabled="submitting">
            Batal
          </button>
          <button
            v-if="isDeleteMode"
            class="btn-delete-confirm"
            @click="handleDeleteConfirm"
            :disabled="submitting"
          >
            <span v-if="submitting">Menghapus...</span>
            <span v-else>Ya, Hapus Data</span>
          </button>
          <button
            v-else
            class="btn-action-view"
            @click="handleSubmit"
            :disabled="submitting"
          >
            <span v-if="submitting">Menyimpan...</span>
            <span v-else>{{ isEditMode ? 'Simpan Perubahan Target & Metadata' : 'Simpan Data' }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import api from '../services/api';

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  mode: {
    type: String,
    default: 'create_tujuan', // 'create_tujuan', 'edit_tujuan', 'create_sasaran', 'edit_sasaran', 'create_ind_tujuan', 'edit_ind_tujuan', 'create_ind_sasaran', 'edit_ind_sasaran', 'delete'
  },
  itemData: {
    type: Object,
    default: null,
  },
  idSkpd: {
    type: Number,
    default: null,
  },
});

const emit = defineEmits(['close', 'saved', 'deleted']);

const submitting = ref(false);

const formData = ref({
  uraian: '',
  satuan: '',
  status: 'positif',
  iku: '0',
  perubahan_status: 'otomatis',
  definisi_operasional: '',
  no_urut: 1,
  target_awal: '-',
  target2026: '-',
  target2027: '-',
  target2028: '-',
  target2029: '-',
  target2030: '-',
  target_akhir: '-',
  p_target2025: '-',
  p_target2026: '-',
  p_target2027: '-',
  p_target2028: '-',
  p_target2029: '-',
  p_target2030: '-',
  p_target_akhir: '-',

  // Program, Kegiatan, Subkegiatan fields
  kodeprogram: '',
  uraiprogram: '',
  kodekegiatan: '',
  uraikegiatan: '',
  kodesubkegiatan: '',
  uraisubkegiatan: '',
  kinerja: '',
  uraisubkegiatan_indikator: '',
  volume_awal: '-',
  volume_0: '-',
  volume_1: '-',
  volume_2: '-',
  volume_3: '-',
  volume_4: '-',
  volume_5: '-',
  p_volume_0: '-',
  p_volume_1: '-',
  p_volume_2: '-',
  p_volume_3: '-',
  p_volume_4: '-',
  p_volume_5: '-',
  p_volume_akhir: '-',
  pagu1: 0,
  pagu2: 0,
  pagu3: 0,
  pagu4: 0,
  pagu5: 0,
  p_pagu1: 0,
  p_pagu2: 0,
  p_pagu3: 0,
  p_pagu4: 0,
  p_pagu5: 0,
});

const isDeleteMode = computed(() => props.mode === 'delete');
const isEditMode = computed(() => props.mode.startsWith('edit_'));
const isTujuan = computed(() => props.mode.includes('tujuan') && !props.mode.includes('ind_'));
const isSasaran = computed(() => props.mode.includes('sasaran') && !props.mode.includes('ind_'));
const isTujuanSasaranForm = computed(() => isTujuan.value || isSasaran.value);
const isIndikatorForm = computed(() => props.mode.includes('ind_'));

const isProgramForm = computed(() => props.mode.includes('program') && !props.mode.includes('ind_'));
const isKegiatanForm = computed(() => props.mode.includes('kegiatan') && !props.mode.includes('ind_') && !props.mode.includes('subkegiatan'));
const isSubkegiatanForm = computed(() => props.mode.includes('subkegiatan') && !props.mode.includes('ind_'));

const deleteItemType = computed(() => props.itemData?.type || '');
const deleteItemLabel = computed(() => {
  switch (deleteItemType.value) {
    case 'tujuan': return 'Tujuan RENSTRA';
    case 'sasaran': return 'Sasaran RENSTRA';
    case 'ind_tujuan': return 'Indikator Tujuan';
    case 'ind_sasaran': return 'Indikator Sasaran';
    case 'ind_kegiatan': return 'Indikator Kegiatan';
    case 'program': return 'Program RENSTRA';
    case 'kegiatan': return 'Kegiatan RENSTRA';
    case 'subkegiatan': return 'Subkegiatan RENSTRA';
    default: return 'Data';
  }
});
const deleteItemText = computed(() => {
  return (
    props.itemData?.uraian ||
    props.itemData?.uraitujuan ||
    props.itemData?.uraisasaran ||
    props.itemData?.uraiprogram ||
    props.itemData?.uraikegiatan ||
    props.itemData?.uraisubkegiatan ||
    '-'
  );
});

const modalCategoryLabel = computed(() => {
  if (isDeleteMode.value) return 'HAPUS DATA';
  if (isTujuan.value) return 'TUJUAN RENSTRA';
  if (isSasaran.value) return 'SASARAN RENSTRA';
  if (props.mode.includes('ind_tujuan')) return 'INDIKATOR TUJUAN';
  if (props.mode.includes('ind_sasaran')) return 'INDIKATOR SASARAN';
  if (props.mode.includes('ind_kegiatan')) return 'INDIKATOR KEGIATAN';
  if (props.mode.includes('ind_program')) return 'INDIKATOR PROGRAM';
  if (isProgramForm.value) return 'PROGRAM RENSTRA';
  if (isKegiatanForm.value) return 'KEGIATAN RENSTRA';
  if (isSubkegiatanForm.value) return 'SUBKEGIATAN RENSTRA';
  return 'FORM RENSTRA';
});

const modalTitle = computed(() => {
  switch (props.mode) {
    case 'create_tujuan': return 'Tambah Tujuan RENSTRA Baru';
    case 'edit_tujuan': return 'Ubah Metadata Tujuan RENSTRA';
    case 'create_sasaran': return 'Tambah Sasaran RENSTRA Baru';
    case 'edit_sasaran': return 'Ubah Metadata Sasaran RENSTRA';
    case 'create_ind_tujuan': return 'Tambah Indikator Tujuan';
    case 'edit_ind_tujuan': return 'Ubah Metadata & Target Perubahan';
    case 'create_ind_sasaran': return 'Tambah Indikator Sasaran';
    case 'edit_ind_sasaran': return 'Ubah Metadata & Target Perubahan';
    case 'edit_ind_program': return 'Ubah Metadata & Target Perubahan Indikator Program';
    case 'create_ind_kegiatan': return 'Tambah Indikator Kegiatan';
    case 'edit_ind_kegiatan': return 'Ubah Metadata & Target Perubahan Indikator Kegiatan';
    case 'create_program': return 'Tambah Program RENSTRA Baru';
    case 'edit_program': return 'Ubah Data & Kinerja Program';
    case 'create_kegiatan': return 'Tambah Kegiatan RENSTRA Baru';
    case 'edit_kegiatan': return 'Ubah Data & Kinerja Kegiatan';
    case 'create_subkegiatan': return 'Tambah Subkegiatan RENSTRA Baru';
    case 'edit_subkegiatan': return 'Ubah Data, Kinerja & Target Subkegiatan';
    case 'delete': return `Hapus ${deleteItemLabel.value}`;
    default: return 'Form RENSTRA';
  }
});

const detectedChanges = computed(() => {
  if (!isIndikatorForm.value) return [];
  const years = [];
  const pairs = [
    { label: '2025', m: formData.value.target_awal, p: formData.value.p_target2025 },
    { label: '2026', m: formData.value.target2026, p: formData.value.p_target2026 },
    { label: '2027', m: formData.value.target2027, p: formData.value.p_target2027 },
    { label: '2028', m: formData.value.target2028, p: formData.value.p_target2028 },
    { label: '2029', m: formData.value.target2029, p: formData.value.p_target2029 },
    { label: '2030', m: formData.value.target2030, p: formData.value.p_target2030 },
    { label: 'Akhir', m: formData.value.target_akhir, p: formData.value.p_target_akhir },
  ];
  for (const item of pairs) {
    const pVal = (item.p || '').trim();
    const mVal = (item.m || '').trim();
    if (pVal && pVal !== '-' && pVal !== mVal) {
      years.push(item.label);
    }
  }
  return years;
});

// Initialize form values when modal opens or itemData changes
watch(
  () => [props.isOpen, props.mode, props.itemData],
  ([open]) => {
    if (open) {
      if (props.mode.startsWith('edit_') && props.itemData) {
        formData.value = {
          uraian: props.itemData.uraian || props.itemData.uraitujuan || props.itemData.uraisasaran || '',
          satuan: props.itemData.indikator?.satuan || props.itemData.satuan || '-',
          status: props.itemData.status && props.itemData.status !== '-' ? props.itemData.status : 'positif',
          iku: props.itemData.iku === '1' || props.itemData.iku === 1 ? '1' : '0',
          perubahan_status: props.itemData.perubahan_status || 'otomatis',
          definisi_operasional: props.itemData.definisi_operasional && props.itemData.definisi_operasional !== '-' ? props.itemData.definisi_operasional : '',
          no_urut: props.itemData.no_urut || 1,
          target_awal: props.itemData.target_awal || '-',
          target2026: props.itemData.target2026 || '-',
          target2027: props.itemData.target2027 || '-',
          target2028: props.itemData.target2028 || '-',
          target2029: props.itemData.target2029 || '-',
          target2030: props.itemData.target2030 || '-',
          target_akhir: props.itemData.target_akhir || '-',
          p_target2025: props.itemData.p_target2025 || '-',
          p_target2026: props.itemData.p_target2026 || '-',
          p_target2027: props.itemData.p_target2027 || '-',
          p_target2028: props.itemData.p_target2028 || '-',
          p_target2029: props.itemData.p_target2029 || '-',
          p_target2030: props.itemData.p_target2030 || '-',
          p_target_akhir: props.itemData.p_target_akhir || '-',

          // Program, Kegiatan, Subkegiatan fields
          kodeprogram: props.itemData.kodeprogram || '',
          uraiprogram: props.itemData.uraiprogram || '',
          kodekegiatan: props.itemData.kodekegiatan || '',
          uraikegiatan: props.itemData.uraikegiatan || '',
          kodesubkegiatan: props.itemData.kodesubkegiatan || '',
          uraisubkegiatan: props.itemData.uraisubkegiatan || '',
          kinerja: props.itemData.kinerja && props.itemData.kinerja !== '-' ? props.itemData.kinerja : '',
          uraisubkegiatan_indikator: props.itemData.indikator?.uraian || props.itemData.uraisubkegiatan_indikator || '',
          volume_awal: props.itemData.indikator?.volume_awal || props.itemData.volume_awal || '-',
          volume_0: props.itemData.indikator?.volume_0 || props.itemData.volume_0 || '-',
          volume_1: props.itemData.indikator?.volume_1 || props.itemData.volume_1 || '-',
          volume_2: props.itemData.indikator?.volume_2 || props.itemData.volume_2 || '-',
          volume_3: props.itemData.indikator?.volume_3 || props.itemData.volume_3 || '-',
          volume_4: props.itemData.indikator?.volume_4 || props.itemData.volume_4 || '-',
          volume_5: props.itemData.indikator?.volume_5 || props.itemData.volume_5 || '-',
          p_volume_0: props.itemData.indikator?.p_volume_0 || props.itemData.p_volume_0 || '-',
          p_volume_1: props.itemData.indikator?.p_volume_1 || props.itemData.p_volume_1 || '-',
          p_volume_2: props.itemData.indikator?.p_volume_2 || props.itemData.p_volume_2 || '-',
          p_volume_3: props.itemData.indikator?.p_volume_3 || props.itemData.p_volume_3 || '-',
          p_volume_4: props.itemData.indikator?.p_volume_4 || props.itemData.p_volume_4 || '-',
          p_volume_5: props.itemData.indikator?.p_volume_5 || props.itemData.p_volume_5 || '-',
          p_volume_akhir: props.itemData.indikator?.p_volume_akhir || props.itemData.p_volume_akhir || '-',
          pagu1: props.itemData.pagu1 || 0,
          pagu2: props.itemData.pagu2 || 0,
          pagu3: props.itemData.pagu3 || 0,
          pagu4: props.itemData.pagu4 || 0,
          pagu5: props.itemData.pagu5 || 0,
          p_pagu1: props.itemData.p_pagu1 !== undefined ? props.itemData.p_pagu1 : (props.itemData.pagu1 || 0),
          p_pagu2: props.itemData.p_pagu2 !== undefined ? props.itemData.p_pagu2 : (props.itemData.pagu2 || 0),
          p_pagu3: props.itemData.p_pagu3 !== undefined ? props.itemData.p_pagu3 : (props.itemData.pagu3 || 0),
          p_pagu4: props.itemData.p_pagu4 !== undefined ? props.itemData.p_pagu4 : (props.itemData.pagu4 || 0),
          p_pagu5: props.itemData.p_pagu5 !== undefined ? props.itemData.p_pagu5 : (props.itemData.pagu5 || 0),
        };
      } else {
        // Reset defaults for create
        formData.value = {
          uraian: '',
          satuan: '%',
          status: 'positif',
          iku: '0',
          perubahan_status: 'baru',
          definisi_operasional: '',
          no_urut: props.itemData?.suggested_no || 1,
          target_awal: '-',
          target2026: '-',
          target2027: '-',
          target2028: '-',
          target2029: '-',
          target2030: '-',
          target_akhir: '-',
          p_target2025: '-',
          p_target2026: '-',
          p_target2027: '-',
          p_target2028: '-',
          p_target2029: '-',
          p_target2030: '-',
          p_target_akhir: '-',

          // Program, Kegiatan, Subkegiatan fields
          kodeprogram: props.itemData?.kodeprogram || '',
          uraiprogram: '',
          kodekegiatan: props.itemData?.kodekegiatan || '',
          uraikegiatan: '',
          kodesubkegiatan: props.itemData?.suggested_kodesubkegiatan || '',
          uraisubkegiatan: '',
          kinerja: '',
          uraisubkegiatan_indikator: '',
          volume_awal: '-',
          volume_0: '-',
          volume_1: '-',
          volume_2: '-',
          volume_3: '-',
          volume_4: '-',
          volume_5: '-',
          p_volume_0: '-',
          p_volume_1: '-',
          p_volume_2: '-',
          p_volume_3: '-',
          p_volume_4: '-',
          p_volume_5: '-',
          p_volume_akhir: '-',
          pagu1: 0,
          pagu2: 0,
          pagu3: 0,
          pagu4: 0,
          pagu5: 0,
          p_pagu1: 0,
          p_pagu2: 0,
          p_pagu3: 0,
          p_pagu4: 0,
          p_pagu5: 0,
        };
      }
    }
  },
  { immediate: true }
);

function closeModal() {
  emit('close');
}

function onTarget2029Input() {
  formData.value.target_akhir = formData.value.target2029;
}

function onTarget2029PerubahanInput() {
  formData.value.p_target_akhir = formData.value.p_target2029;
}

async function handleSubmit() {
  // Validate according to form mode
  if (isTujuanSasaranForm.value || isIndikatorForm.value) {
    if (!formData.value.uraian.trim()) return;
  } else if (isProgramForm.value) {
    if (!formData.value.kodeprogram?.trim() || !formData.value.uraiprogram?.trim()) {
      alert('Kode Program dan Nama Program wajib diisi');
      return;
    }
  } else if (isKegiatanForm.value) {
    if (!formData.value.kodekegiatan?.trim() || !formData.value.uraikegiatan?.trim()) {
      alert('Kode Kegiatan dan Nama Kegiatan wajib diisi');
      return;
    }
  } else if (isSubkegiatanForm.value) {
    if (!formData.value.kodesubkegiatan?.trim() || !formData.value.uraisubkegiatan?.trim()) {
      alert('Kode Subkegiatan dan Nama Subkegiatan wajib diisi');
      return;
    }
  }

  submitting.value = true;
  const statusToSend = formData.value.perubahan_status === 'otomatis' ? null : formData.value.perubahan_status;
  try {
    if (props.mode === 'create_tujuan') {
      await api.createTujuan({
        id_skpd: props.idSkpd,
        uraitujuan: formData.value.uraian,
        no_urut: formData.value.no_urut,
        perubahan_status: statusToSend || 'baru',
      });
    } else if (props.mode === 'edit_tujuan') {
      await api.updateTujuan(props.itemData.id, {
        uraitujuan: formData.value.uraian,
        no_urut: formData.value.no_urut,
        perubahan_status: statusToSend,
      });
    } else if (props.mode === 'create_sasaran') {
      await api.createSasaran({
        idtujuan: props.itemData.idtujuan,
        uraisasaran: formData.value.uraian,
        no_urut: formData.value.no_urut,
        perubahan_status: statusToSend || 'baru',
      });
    } else if (props.mode === 'edit_sasaran') {
      await api.updateSasaran(props.itemData.id, {
        uraisasaran: formData.value.uraian,
        no_urut: formData.value.no_urut,
        perubahan_status: statusToSend,
      });
    } else if (props.mode === 'create_ind_tujuan') {
      await api.createIndikatorTujuan({
        parent_id: props.itemData.idtujuan,
        uraian: formData.value.uraian,
        satuan: formData.value.satuan,
        status: formData.value.status,
        iku: formData.value.iku,
        perubahan_status: statusToSend || 'baru',
        definisi_operasional: formData.value.definisi_operasional,
        target_awal: formData.value.target_awal,
        target2026: formData.value.target2026,
        target2027: formData.value.target2027,
        target2028: formData.value.target2028,
        target2029: formData.value.target2029,
        target2030: formData.value.target2030,
        target_akhir: formData.value.target_akhir,
        p_target2025: formData.value.p_target2025,
        p_target2026: formData.value.p_target2026,
        p_target2027: formData.value.p_target2027,
        p_target2028: formData.value.p_target2028,
        p_target2029: formData.value.p_target2029,
        p_target2030: formData.value.p_target2030,
        p_target_akhir: formData.value.p_target_akhir,
        no_urut: formData.value.no_urut,
      });
    } else if (props.mode === 'edit_ind_tujuan') {
      await api.updateIndikatorTujuan(props.itemData.id, {
        uraian: formData.value.uraian,
        satuan: formData.value.satuan,
        status: formData.value.status,
        iku: formData.value.iku,
        perubahan_status: statusToSend,
        definisi_operasional: formData.value.definisi_operasional,
        target_awal: formData.value.target_awal,
        target2026: formData.value.target2026,
        target2027: formData.value.target2027,
        target2028: formData.value.target2028,
        target2029: formData.value.target2029,
        target2030: formData.value.target2030,
        target_akhir: formData.value.target_akhir,
        p_target2025: formData.value.p_target2025,
        p_target2026: formData.value.p_target2026,
        p_target2027: formData.value.p_target2027,
        p_target2028: formData.value.p_target2028,
        p_target2029: formData.value.p_target2029,
        p_target2030: formData.value.p_target2030,
        p_target_akhir: formData.value.p_target_akhir,
        no_urut: formData.value.no_urut,
      });
    } else if (props.mode === 'create_ind_sasaran') {
      await api.createIndikatorSasaran({
        parent_id: props.itemData.idsasaran,
        uraian: formData.value.uraian,
        satuan: formData.value.satuan,
        status: formData.value.status,
        iku: formData.value.iku,
        perubahan_status: statusToSend || 'baru',
        definisi_operasional: formData.value.definisi_operasional,
        target_awal: formData.value.target_awal,
        target2026: formData.value.target2026,
        target2027: formData.value.target2027,
        target2028: formData.value.target2028,
        target2029: formData.value.target2029,
        target2030: formData.value.target2030,
        target_akhir: formData.value.target_akhir,
        p_target2025: formData.value.p_target2025,
        p_target2026: formData.value.p_target2026,
        p_target2027: formData.value.p_target2027,
        p_target2028: formData.value.p_target2028,
        p_target2029: formData.value.p_target2029,
        p_target2030: formData.value.p_target2030,
        p_target_akhir: formData.value.p_target_akhir,
        no_urut: formData.value.no_urut,
      });
    } else if (props.mode === 'edit_ind_sasaran') {
      await api.updateIndikatorSasaran(props.itemData.id, {
        uraian: formData.value.uraian,
        satuan: formData.value.satuan,
        status: formData.value.status,
        iku: formData.value.iku,
        perubahan_status: statusToSend,
        definisi_operasional: formData.value.definisi_operasional,
        target_awal: formData.value.target_awal,
        target2026: formData.value.target2026,
        target2027: formData.value.target2027,
        target2028: formData.value.target2028,
        target2029: formData.value.target2029,
        target2030: formData.value.target2030,
        target_akhir: formData.value.target_akhir,
        p_target2025: formData.value.p_target2025,
        p_target2026: formData.value.p_target2026,
        p_target2027: formData.value.p_target2027,
        p_target2028: formData.value.p_target2028,
        p_target2029: formData.value.p_target2029,
        p_target2030: formData.value.p_target2030,
        p_target_akhir: formData.value.p_target_akhir,
        no_urut: formData.value.no_urut,
      });
    } else if (props.mode === 'edit_ind_program') {
      await api.updateIndikatorProgram(props.itemData.id, {
        satuan: formData.value.satuan,
        status: formData.value.status,
        perubahan_status: statusToSend,
        p_target2025: formData.value.p_target2025,
        p_target2026: formData.value.p_target2026,
        p_target2027: formData.value.p_target2027,
        p_target2028: formData.value.p_target2028,
        p_target2029: formData.value.p_target2029,
        p_target2030: formData.value.p_target2030,
        p_target_akhir: formData.value.p_target_akhir,
      });
    } else if (props.mode === 'create_ind_kegiatan') {
      await api.createIndikatorKegiatan({
        kodeskpd: props.itemData.kodeskpd,
        kodekegiatan: props.itemData.kodekegiatan,
        kodeprogram: props.itemData.kodeprogram,
        uraikegiatan: props.itemData.uraikegiatan,
        uraian: formData.value.uraian,
        satuan: formData.value.satuan,
        status: formData.value.status,
        iku: formData.value.iku,
        perubahan_status: statusToSend || 'baru',
        definisi_operasional: formData.value.definisi_operasional,
        target_awal: formData.value.target_awal,
        target2026: formData.value.target2026,
        target2027: formData.value.target2027,
        target2028: formData.value.target2028,
        target2029: formData.value.target2029,
        target2030: formData.value.target2030,
        target_akhir: formData.value.target_akhir,
        p_target2025: formData.value.p_target2025,
        p_target2026: formData.value.p_target2026,
        p_target2027: formData.value.p_target2027,
        p_target2028: formData.value.p_target2028,
        p_target2029: formData.value.p_target2029,
        p_target2030: formData.value.p_target2030,
        p_target_akhir: formData.value.p_target_akhir,
        pagu1: formData.value.pagu1,
        pagu2: formData.value.pagu2,
        pagu3: formData.value.pagu3,
        pagu4: formData.value.pagu4,
        pagu5: formData.value.pagu5,
        p_pagu1: formData.value.p_pagu1,
        p_pagu2: formData.value.p_pagu2,
        p_pagu3: formData.value.p_pagu3,
        p_pagu4: formData.value.p_pagu4,
        p_pagu5: formData.value.p_pagu5,
        no_urut: formData.value.no_urut,
      });
    } else if (props.mode === 'edit_ind_kegiatan') {
      await api.updateIndikatorKegiatan(props.itemData.id, {
        uraian: formData.value.uraian,
        satuan: formData.value.satuan,
        status: formData.value.status,
        iku: formData.value.iku,
        perubahan_status: statusToSend,
        definisi_operasional: formData.value.definisi_operasional,
        target_awal: formData.value.target_awal,
        target2026: formData.value.target2026,
        target2027: formData.value.target2027,
        target2028: formData.value.target2028,
        target2029: formData.value.target2029,
        target2030: formData.value.target2030,
        target_akhir: formData.value.target_akhir,
        p_target2025: formData.value.p_target2025,
        p_target2026: formData.value.p_target2026,
        p_target2027: formData.value.p_target2027,
        p_target2028: formData.value.p_target2028,
        p_target2029: formData.value.p_target2029,
        p_target2030: formData.value.p_target2030,
        p_target_akhir: formData.value.p_target_akhir,
        pagu1: formData.value.pagu1,
        pagu2: formData.value.pagu2,
        pagu3: formData.value.pagu3,
        pagu4: formData.value.pagu4,
        pagu5: formData.value.pagu5,
        p_pagu1: formData.value.p_pagu1,
        p_pagu2: formData.value.p_pagu2,
        p_pagu3: formData.value.p_pagu3,
        p_pagu4: formData.value.p_pagu4,
        p_pagu5: formData.value.p_pagu5,
        no_urut: formData.value.no_urut,
      });
    } else if (props.mode === 'create_program') {
      await api.createProgram({
        kodeskpd: props.itemData.kodeskpd,
        kodebidang: props.itemData.kodebidang,
        kodeprogram: formData.value.kodeprogram,
        uraiprogram: formData.value.uraiprogram,
        kinerja: formData.value.kinerja,
      });
    } else if (props.mode === 'edit_program') {
      await api.updateProgram(props.itemData.id, {
        kodeprogram: formData.value.kodeprogram,
        uraiprogram: formData.value.uraiprogram,
        kinerja: formData.value.kinerja,
      });
    } else if (props.mode === 'create_kegiatan') {
      await api.createKegiatan({
        kodeskpd: props.itemData.kodeskpd,
        kodebidang: props.itemData.kodebidang,
        kodeprogram: props.itemData.kodeprogram,
        kodekegiatan: formData.value.kodekegiatan,
        uraikegiatan: formData.value.uraikegiatan,
        kinerja: formData.value.kinerja,
      });
    } else if (props.mode === 'edit_kegiatan') {
      await api.updateKegiatan(props.itemData.id, {
        kodekegiatan: formData.value.kodekegiatan,
        uraikegiatan: formData.value.uraikegiatan,
        kinerja: formData.value.kinerja,
      });
    } else if (props.mode === 'create_subkegiatan') {
      await api.createSubkegiatan({
        kodeskpd: props.itemData.kodeskpd,
        kodebidang: props.itemData.kodebidang,
        kodeprogram: props.itemData.kodeprogram,
        kodekegiatan: props.itemData.kodekegiatan,
        kodesubkegiatan: formData.value.kodesubkegiatan,
        uraisubkegiatan: formData.value.uraisubkegiatan,
        kinerja: formData.value.kinerja,
        uraisubkegiatan_indikator: formData.value.uraisubkegiatan_indikator,
        satuan: formData.value.satuan,
        volume_awal: formData.value.volume_awal,
        volume_0: formData.value.volume_0,
        volume_1: formData.value.volume_1,
        volume_2: formData.value.volume_2,
        volume_3: formData.value.volume_3,
        volume_4: formData.value.volume_4,
        volume_5: formData.value.volume_5,
        p_volume_0: formData.value.p_volume_0,
        p_volume_1: formData.value.p_volume_1,
        p_volume_2: formData.value.p_volume_2,
        p_volume_3: formData.value.p_volume_3,
        p_volume_4: formData.value.p_volume_4,
        p_volume_5: formData.value.p_volume_5,
        p_volume_akhir: formData.value.p_volume_akhir,
        pagu1: formData.value.pagu1,
        pagu2: formData.value.pagu2,
        pagu3: formData.value.pagu3,
        pagu4: formData.value.pagu4,
        pagu5: formData.value.pagu5,
        p_pagu1: formData.value.p_pagu1,
        p_pagu2: formData.value.p_pagu2,
        p_pagu3: formData.value.p_pagu3,
        p_pagu4: formData.value.p_pagu4,
        p_pagu5: formData.value.p_pagu5,
      });
    } else if (props.mode === 'edit_subkegiatan') {
      await api.updateSubkegiatan(props.itemData.id, {
        kodesubkegiatan: formData.value.kodesubkegiatan,
        uraisubkegiatan: formData.value.uraisubkegiatan,
        kinerja: formData.value.kinerja,
        uraisubkegiatan_indikator: formData.value.uraisubkegiatan_indikator,
        satuan: formData.value.satuan,
        volume_awal: formData.value.volume_awal,
        volume_0: formData.value.volume_0,
        volume_1: formData.value.volume_1,
        volume_2: formData.value.volume_2,
        volume_3: formData.value.volume_3,
        volume_4: formData.value.volume_4,
        volume_5: formData.value.volume_5,
        p_volume_0: formData.value.p_volume_0,
        p_volume_1: formData.value.p_volume_1,
        p_volume_2: formData.value.p_volume_2,
        p_volume_3: formData.value.p_volume_3,
        p_volume_4: formData.value.p_volume_4,
        p_volume_5: formData.value.p_volume_5,
        p_volume_akhir: formData.value.p_volume_akhir,
        pagu1: formData.value.pagu1,
        pagu2: formData.value.pagu2,
        pagu3: formData.value.pagu3,
        pagu4: formData.value.pagu4,
        pagu5: formData.value.pagu5,
        p_pagu1: formData.value.p_pagu1,
        p_pagu2: formData.value.p_pagu2,
        p_pagu3: formData.value.p_pagu3,
        p_pagu4: formData.value.p_pagu4,
        p_pagu5: formData.value.p_pagu5,
      });
    }

    emit('saved');
    closeModal();
  } catch (err) {
    alert('Gagal menyimpan data: ' + err.message);
  } finally {
    submitting.value = false;
  }
}

async function handleDeleteConfirm() {
  if (!props.itemData?.id) return;

  submitting.value = true;
  try {
    switch (props.itemData.type) {
      case 'tujuan':
        await api.deleteTujuan(props.itemData.id);
        break;
      case 'sasaran':
        await api.deleteSasaran(props.itemData.id);
        break;
      case 'ind_tujuan':
        await api.deleteIndikatorTujuan(props.itemData.id);
        break;
      case 'ind_sasaran':
        await api.deleteIndikatorSasaran(props.itemData.id);
        break;
      case 'program':
        await api.deleteProgram(props.itemData.id);
        break;
      case 'kegiatan':
        await api.deleteKegiatan(props.itemData.id);
        break;
      case 'subkegiatan':
        await api.deleteSubkegiatan(props.itemData.id);
        break;
    }
    emit('deleted');
    closeModal();
  } catch (err) {
    alert('Gagal menghapus data: ' + err.message);
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.crud-modal-card {
  background: #ffffff;
  width: 100%;
  max-width: 760px;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalScale 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  border: 1px solid var(--border-subtle);
}

@keyframes modalScale {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.crud-modal-header {
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #091225 0%, #1e293b 100%);
  color: #ffffff;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.crud-modal-header.delete-header {
  background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
}

.crud-modal-title-group h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #ffffff;
}

.crud-modal-body {
  padding: 1.5rem 1.75rem;
  max-height: 75vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.82rem;
  font-weight: 600;
  color: #334155;
  margin-bottom: 0.35rem;
}

.form-label.sub {
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-muted);
}

.form-input {
  width: 100%;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
  font-size: 0.88rem;
  color: var(--text-main);
  background: #ffffff;
  transition: all var(--transition-fast);
}

.form-input.mono {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  text-align: center;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-600);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.form-textarea {
  width: 100%;
  padding: 0.65rem 0.85rem;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
  font-size: 0.88rem;
  color: var(--text-main);
  background: #ffffff;
  resize: vertical;
}

.targets-form-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  background: #f8fafc;
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.badge-perubahan {
  background: #fef3c7;
  color: #92400e;
  border: 1px solid #fde68a;
  padding: 0.12rem 0.45rem;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.targets-perubahan-grid {
  background: #fffdf5;
  border: 1px solid #fde68a;
}

.p-label {
  color: #92400e !important;
}

.p-input:focus {
  border-color: #d97706 !important;
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.15) !important;
}

.crud-modal-footer {
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-delete-confirm {
  padding: 0.55rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: 0.84rem;
  font-weight: 600;
  background: #dc2626;
  color: #ffffff;
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 2px 4px rgba(220, 38, 38, 0.25);
}

.btn-delete-confirm:hover {
  background: #b91c1c;
}

.badge-locked {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.7rem;
  font-weight: 700;
  color: #64748b;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  letter-spacing: 0.02em;
}

.readonly-locked {
  background: #f8fafc !important;
  color: #64748b !important;
  border: 1px dashed #cbd5e1 !important;
  cursor: not-allowed !important;
  user-select: none;
}

.grid-locked {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.form-helper-locked {
  font-size: 0.74rem;
  color: #64748b;
  margin-top: 0.35rem;
  font-style: italic;
}
</style>
