<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="modal-backdrop"
      style="display: flex; align-items: center; justify-content: center; padding: 1.5rem;"
      @click.self="closeModal"
      @keydown.esc="closeModal"
    >
      <div class="crud-modal-card" :class="{ 'wide-modal': showAiPanel }" role="dialog" aria-modal="true">
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
          <div style="display: flex; justify-content: flex-end; margin-bottom: 0.75rem;">
            <button
              type="button"
              class="btn-ai-toggle"
              :class="{ 'active': showAiPanel }"
              @click="toggleAiPanel"
              title="Dapatkan rekomendasi perumusan indikator yang SMART berbasis AI"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
              <span>{{ showAiPanel ? 'Sembunyikan Rekomendasi AI' : '🤖 Rekomendasi AI (SMART)' }}</span>
            </button>
          </div>

          <SmartAiAssistant
            v-if="showAiPanel"
            :level="aiContextLevel"
            :parent-uraian="aiParentUraian"
            :entity-uraian="aiEntityUraian"
            :kinerja="formData.kinerja || props.itemData?.kinerja"
            :opd-name="props.itemData?.opd_name"
            :subkegiatan-list="props.itemData?.subkegiatan"
            :is-edit-mode="isEditMode"
            @apply="handleApplySmartRecommendation"
            @close="showAiPanel = false"
          />

          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label class="form-label">
                Uraian {{ isTujuan ? 'Tujuan' : 'Sasaran' }} <span style="color: #ef4444;">*</span>
              </label>
              <textarea
                class="form-textarea"
                v-model="formData.uraian"
                rows="3"
                required
                :placeholder="`Masukkan rumusan uraian ${isTujuan ? 'Tujuan' : 'Sasaran'} RENSTRA...`"
              ></textarea>
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
          <!-- Tombol AI Assistant SMART -->
          <div style="display: flex; justify-content: flex-end; margin-bottom: 0.75rem;">
            <button
              type="button"
              class="btn-ai-toggle"
              :class="{ 'active': showAiPanel }"
              @click="toggleAiPanel"
              title="Dapatkan rekomendasi perumusan indikator yang SMART berbasis AI"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
              <span>{{ showAiPanel ? 'Sembunyikan Rekomendasi AI' : '🤖 Rekomendasi AI (SMART)' }}</span>
            </button>
          </div>

          <!-- Smart AI Assistant Panel -->
          <SmartAiAssistant
            v-if="showAiPanel"
            :level="aiContextLevel"
            :parent-uraian="aiParentUraian"
            :entity-uraian="aiEntityUraian"
            :kinerja="formData.kinerja || props.itemData?.kinerja"
            :opd-name="props.itemData?.opd_name"
            :subkegiatan-list="props.itemData?.subkegiatan"
            :is-edit-mode="isEditMode"
            @apply="handleApplySmartRecommendation"
            @close="showAiPanel = false"
          />

          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label class="form-label">
                Uraian Indikator Kinerja <span style="color: #ef4444;">*</span>
              </label>
              <textarea
                class="form-textarea"
                v-model="formData.uraian"
                rows="2"
                required
                placeholder="Contoh: Rata-Rata Lama Sekolah, Indeks Kepuasan Masyarakat..."
              ></textarea>
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
                <label class="form-label" style="font-weight: 700; color: #1e3a8a; margin-bottom: 0;">
                  Target Capaian Kinerja (Murni)
                </label>
              </div>
              <div class="targets-form-grid">
                <div class="form-group">
                  <label class="form-label sub">Target Awal <span style="font-size: 0.72rem; opacity: 0.85;">(Baseline)</span></label>
                  <input type="text" class="form-input mono" v-model="formData.target_awal" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub">Target 2026</label>
                  <input type="text" class="form-input mono" v-model="formData.target2026" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub">Target 2027</label>
                  <input type="text" class="form-input mono" v-model="formData.target2027" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub">Target 2028</label>
                  <input type="text" class="form-input mono" v-model="formData.target2028" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub">Target 2029</label>
                  <input
                    type="text"
                    class="form-input mono"
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
            </div>

            <!-- Realisasi Capaian Tahunan Grid -->
            <div style="margin-top: 1.25rem;">
              <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 0.5rem;">
                <label class="form-label" style="font-weight: 700; color: #047857; margin-bottom: 0; display: flex; align-items: center; gap: 0.45rem;">
                  <span class="badge-realisasi">Realisasi</span>
                  Realisasi Capaian Tahunan (2025 - 2030)
                </label>
                <span style="font-size: 0.75rem; color: #059669; font-weight: 600;">
                  * Masukkan angka atau capaian realisasi tahunan
                </span>
              </div>
              <div class="targets-form-grid targets-realisasi-grid" style="grid-template-columns: repeat(6, 1fr);">
                <div class="form-group">
                  <label class="form-label sub r-label">2025</label>
                  <input type="text" class="form-input mono r-input" v-model="formData.realisasi2025" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub r-label">2026</label>
                  <input type="text" class="form-input mono r-input" v-model="formData.realisasi2026" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub r-label">2027</label>
                  <input type="text" class="form-input mono r-input" v-model="formData.realisasi2027" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub r-label">2028</label>
                  <input type="text" class="form-input mono r-input" v-model="formData.realisasi2028" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub r-label">2029</label>
                  <input type="text" class="form-input mono r-input" v-model="formData.realisasi2029" placeholder="-" />
                </div>
                <div class="form-group">
                  <label class="form-label sub r-label">2030</label>
                  <input type="text" class="form-input mono r-input" v-model="formData.realisasi2030" placeholder="-" />
                </div>
              </div>
            </div>
          </form>
        </div>

        <!-- Modal Body: FORM (PROGRAM) -->
        <div v-else-if="isProgramForm" class="crud-modal-body">
          <div style="display: flex; justify-content: flex-end; margin-bottom: 0.75rem;">
            <button
              type="button"
              class="btn-ai-toggle"
              :class="{ 'active': showAiPanel }"
              @click="toggleAiPanel"
              title="Dapatkan rekomendasi kinerja/indikator SMART berbasis AI"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
              <span>{{ showAiPanel ? 'Sembunyikan AI' : '🤖 Rekomendasi AI SMART' }}</span>
            </button>
          </div>

          <SmartAiAssistant
            v-if="showAiPanel"
            :level="aiContextLevel"
            :parent-uraian="aiParentUraian"
            :entity-uraian="aiEntityUraian"
            :kinerja="formData.kinerja || props.itemData?.kinerja"
            :opd-name="props.itemData?.opd_name"
            :subkegiatan-list="props.itemData?.subkegiatan"
            :is-edit-mode="isEditMode"
            @apply="handleApplySmartRecommendation"
            @close="showAiPanel = false"
          />

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

            <!-- Tagging Keterkaitan dengan Sasaran RENSTRA -->
            <div class="sasaran-tagger-card" style="margin-top: 1rem;">
              <div class="sasaran-tagger-header">
                <div class="sasaran-tagger-title">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <circle cx="12" cy="12" r="10"/>
                    <circle cx="12" cy="6" r="1"/>
                    <circle cx="12" cy="12" r="2"/>
                  </svg>
                  <span>Keterkaitan dengan Sasaran RENSTRA (Tagging Sasaran)</span>
                </div>
                <span v-if="loadingRefSasaran" class="ref-loading-badge">Memuat sasaran...</span>
                <span v-else class="sasaran-tagger-count">
                  {{ selectedSasaranIds.length }} dari {{ refSasaranList.length }} Sasaran dipilih
                </span>
              </div>
              <p class="sasaran-tagger-desc">
                Pilih satu atau lebih Sasaran RENSTRA yang didukung oleh program ini (satu program dapat mendukung lebih dari satu sasaran).
              </p>

              <div v-if="loadingRefSasaran" style="padding: 0.85rem; text-align: center; color: #64748b; font-size: 0.85rem;">
                Memuat daftar sasaran...
              </div>
              <div v-else-if="!refSasaranList.length" style="padding: 0.85rem; color: #64748b; font-size: 0.82rem; font-style: italic;">
                Belum ada data Sasaran yang terdaftar pada Perangkat Daerah ini.
              </div>
              <div v-else class="sasaran-checkbox-list">
                <label
                  v-for="s in refSasaranList"
                  :key="s.idsasaran"
                  class="sasaran-checkbox-item"
                  :class="{ 'selected': selectedSasaranIds.includes(s.idsasaran) }"
                >
                  <input
                    type="checkbox"
                    :value="s.idsasaran"
                    v-model="selectedSasaranIds"
                    class="sasaran-checkbox-input"
                  />
                  <div class="sasaran-checkbox-content">
                    <div class="sasaran-checkbox-main">
                      <span class="sasaran-number-badge">Sasaran {{ s.no }}</span>
                      <span class="sasaran-uraian-text">{{ s.uraisasaran }}</span>
                    </div>
                    <div v-if="s.uraitujuan && s.uraitujuan !== '-'" class="sasaran-tujuan-text">
                      🎯 Tujuan: {{ s.uraitujuan }}
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </form>
        </div>

        <!-- Modal Body: FORM (KEGIATAN) -->
        <div v-else-if="isKegiatanForm" class="crud-modal-body">
          <div style="display: flex; justify-content: flex-end; margin-bottom: 0.75rem;">
            <button
              type="button"
              class="btn-ai-toggle"
              :class="{ 'active': showAiPanel }"
              @click="toggleAiPanel"
              title="Dapatkan rekomendasi kinerja/indikator SMART berbasis AI"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
              <span>{{ showAiPanel ? 'Sembunyikan AI' : '🤖 Rekomendasi AI SMART' }}</span>
            </button>
          </div>

          <SmartAiAssistant
            v-if="showAiPanel"
            :level="aiContextLevel"
            :parent-uraian="aiParentUraian"
            :entity-uraian="aiEntityUraian"
            :kinerja="formData.kinerja || props.itemData?.kinerja"
            :opd-name="props.itemData?.opd_name"
            :subkegiatan-list="props.itemData?.subkegiatan"
            :is-edit-mode="isEditMode"
            @apply="handleApplySmartRecommendation"
            @close="showAiPanel = false"
          />

          <form @submit.prevent="handleSubmit">
            <!-- Ref Picker Kegiatan -->
            <div class="ref-picker-card">
              <div class="ref-picker-header">
                <div class="ref-picker-title">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                  <span>Referensi Kegiatan (SIPD-RI / Permendagri)</span>
                </div>
                <span v-if="loadingRefKegiatan" class="ref-loading-badge">Memuat referensi...</span>
                <span v-else-if="refKegiatanList.length" class="ref-count-badge">{{ refKegiatanList.length }} referensi</span>
              </div>
              <div class="ref-picker-body">
                <select
                  v-model="selectedRefKegiatan"
                  class="ref-select"
                  @change="onSelectRefKegiatan"
                  :disabled="loadingRefKegiatan"
                >
                  <option value="">-- Pilih dari Referensi SIPD-RI (Otomatis Isi) --</option>
                  <option
                    v-for="item in refKegiatanList"
                    :key="item.kodekegiatan"
                    :value="item.kodekegiatan"
                  >
                    {{ item.kodekegiatan }} - {{ item.uraikegiatan }}
                  </option>
                </select>
                <div class="ref-hint" v-if="refKegiatanList.length">
                  💡 Memilih referensi akan otomatis mengisi Kode dan Nama Kegiatan.
                </div>
                <div class="ref-hint" v-else-if="!loadingRefKegiatan">
                  ℹ️ Tidak ada referensi khusus untuk program ini, silakan isi formulir secara manual.
                </div>
              </div>
            </div>

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
            <!-- Ref Picker Subkegiatan -->
            <div class="ref-picker-card">
              <div class="ref-picker-header">
                <div class="ref-picker-title">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
                  <span>Referensi Sub Kegiatan (SIPD-RI / Permendagri)</span>
                </div>
                <span v-if="loadingRefSubkegiatan" class="ref-loading-badge">Memuat referensi...</span>
                <span v-else-if="refSubkegiatanList.length" class="ref-count-badge">{{ refSubkegiatanList.length }} referensi</span>
              </div>
              <div class="ref-picker-body">
                <select
                  v-model="selectedRefSubkegiatan"
                  class="ref-select"
                  @change="onSelectRefSubkegiatan"
                  :disabled="loadingRefSubkegiatan"
                >
                  <option value="">-- Pilih dari Referensi SIPD-RI (Otomatis Isi) --</option>
                  <option
                    v-for="item in refSubkegiatanList"
                    :key="item.kodesubkegiatan"
                    :value="item.kodesubkegiatan"
                  >
                    {{ item.kodesubkegiatan }} - {{ item.uraisubkegiatan }}
                  </option>
                </select>
                <div class="ref-hint" v-if="refSubkegiatanList.length">
                  💡 Memilih referensi akan otomatis mengisi Kode, Uraian, Kinerja, Indikator, dan Satuan.
                </div>
                <div class="ref-hint" v-else-if="!loadingRefSubkegiatan">
                  ℹ️ Tidak ada referensi khusus untuk kegiatan ini, silakan isi formulir secara manual.
                </div>
              </div>
            </div>

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
              <div style="font-weight: 700; font-size: 0.88rem; color: #1e3a8a; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 0.4rem;">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
                  <span>Indikator Kinerja Subkegiatan</span>
                </div>
                <button
                  type="button"
                  class="btn-ai-toggle"
                  :class="{ 'active': showAiPanel }"
                  @click="toggleAiPanel"
                  title="Dapatkan rekomendasi perumusan indikator yang SMART berbasis AI"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                  </svg>
                  <span>{{ showAiPanel ? 'Sembunyikan AI' : '🤖 Rekomendasi AI SMART' }}</span>
                </button>
              </div>

              <!-- SMART AI Assistant Panel Component -->
              <SmartAiAssistant
                v-if="showAiPanel"
                :level="aiContextLevel"
                :parent-uraian="aiParentUraian"
                :entity-uraian="aiEntityUraian"
                :kinerja="formData.kinerja || props.itemData?.kinerja"
                :opd-name="props.itemData?.opd_name"
                :subkegiatan-list="props.itemData?.subkegiatan"
                :is-edit-mode="isEditMode"
                @apply="handleApplySmartRecommendation"
                @close="showAiPanel = false"
              />
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
                  Target (Murni)
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

              <!-- Grid Realisasi Volume Subkegiatan -->
              <div style="margin-top: 0.85rem;">
                <label class="form-label" style="font-weight: 600; color: #047857; font-size: 0.8rem; display: flex; align-items: center; gap: 0.35rem;">
                  <span class="badge-realisasi">Realisasi</span>
                  Realisasi Capaian Tahunan (2025 - 2030)
                </label>
                <div class="targets-form-grid targets-realisasi-grid" style="grid-template-columns: repeat(6, 1fr);">
                  <div class="form-group">
                    <label class="form-label sub r-label">2025</label>
                    <input type="text" class="form-input mono r-input" v-model="formData.realisasi2025" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub r-label">2026</label>
                    <input type="text" class="form-input mono r-input" v-model="formData.realisasi2026" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub r-label">2027</label>
                    <input type="text" class="form-input mono r-input" v-model="formData.realisasi2027" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub r-label">2028</label>
                    <input type="text" class="form-input mono r-input" v-model="formData.realisasi2028" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub r-label">2029</label>
                    <input type="text" class="form-input mono r-input" v-model="formData.realisasi2029" placeholder="-" />
                  </div>
                  <div class="form-group">
                    <label class="form-label sub r-label">2030</label>
                    <input type="text" class="form-input mono r-input" v-model="formData.realisasi2030" placeholder="-" />
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
import SmartAiAssistant from './SmartAiAssistant.vue';

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
const showAiPanel = ref(false);

// SIPD-RI Database References for Kegiatan & Subkegiatan
const refKegiatanList = ref([]);
const loadingRefKegiatan = ref(false);
const selectedRefKegiatan = ref('');

const refSubkegiatanList = ref([]);
const loadingRefSubkegiatan = ref(false);
const selectedRefSubkegiatan = ref('');

// Referensi Sasaran untuk Tagging Program
const refSasaranList = ref([]);
const loadingRefSasaran = ref(false);
const selectedSasaranIds = ref([]);

const aiContextLevel = computed(() => {
  if (props.mode.includes('ind_tujuan')) return 'tujuan';
  if (props.mode.includes('ind_sasaran')) return 'sasaran';
  if (props.mode.includes('ind_program')) return 'program';
  if (props.mode.includes('ind_kegiatan')) return 'kegiatan';
  if (isSubkegiatanForm.value) return 'subkegiatan';
  if (isKegiatanForm.value) return 'kegiatan';
  if (isProgramForm.value) return 'program';
  if (isSasaran.value) return 'sasaran';
  if (isTujuan.value) return 'tujuan';
  return 'kegiatan';
});

const aiParentUraian = computed(() => {
  return props.itemData?.parent_uraian || props.itemData?.uraiprogram || props.itemData?.uraikegiatan || props.itemData?.uraitujuan || '';
});

const aiEntityUraian = computed(() => {
  if (props.mode.includes('ind_kegiatan')) {
    return props.itemData?.uraikegiatan || formData.value.uraikegiatan || '';
  }
  if (props.mode.includes('ind_tujuan')) {
    return props.itemData?.uraitujuan || '';
  }
  if (props.mode.includes('ind_sasaran')) {
    return props.itemData?.uraisasaran || '';
  }
  if (props.mode.includes('ind_program')) {
    return props.itemData?.uraiprogram || formData.value.uraiprogram || '';
  }
  if (isSubkegiatanForm.value) {
    return formData.value.uraisubkegiatan || props.itemData?.uraisubkegiatan || '';
  }
  if (isKegiatanForm.value) {
    return formData.value.uraikegiatan || props.itemData?.uraikegiatan || '';
  }
  if (isProgramForm.value) {
    return formData.value.uraiprogram || props.itemData?.uraiprogram || '';
  }
  if (isTujuanSasaranForm.value) {
    return formData.value.uraian || props.itemData?.uraian || '';
  }
  return formData.value.uraian || '';
});

function toggleAiPanel() {
  showAiPanel.value = !showAiPanel.value;
}

function handleApplySmartRecommendation(rec) {
  if (isSubkegiatanForm.value) {
    formData.value.uraisubkegiatan_indikator = rec.uraian;
    if (rec.satuan) formData.value.satuan = rec.satuan;
    if (rec.target_awal && (!formData.value.volume_awal || formData.value.volume_awal === '-')) formData.value.volume_awal = rec.target_awal;
    if (rec.target2026 && (!formData.value.volume_1 || formData.value.volume_1 === '-')) formData.value.volume_1 = rec.target2026;
    if (rec.target2027 && (!formData.value.volume_2 || formData.value.volume_2 === '-')) formData.value.volume_2 = rec.target2027;
    if (rec.target2028 && (!formData.value.volume_3 || formData.value.volume_3 === '-')) formData.value.volume_3 = rec.target2028;
    if (rec.target2029 && (!formData.value.volume_4 || formData.value.volume_4 === '-')) formData.value.volume_4 = rec.target2029;
    if (rec.target2030 && (!formData.value.volume_5 || formData.value.volume_5 === '-')) formData.value.volume_5 = rec.target2030;
  } else if (isKegiatanForm.value || isProgramForm.value) {
    formData.value.kinerja = rec.uraian;
  } else if (isTujuanSasaranForm.value) {
    if (!isEditMode.value) {
      formData.value.uraian = rec.uraian;
    }
  } else {
    if (!isEditMode.value) {
      formData.value.uraian = rec.uraian;
    }
    if (rec.satuan) formData.value.satuan = rec.satuan;
    if (rec.status) formData.value.status = rec.status;
    if (rec.definisi_operasional) {
      formData.value.definisi_operasional = rec.definisi_operasional;
    }
    if (!isEditMode.value) {
      if (rec.target_awal) formData.value.target_awal = rec.target_awal;
      if (rec.target2026) formData.value.target2026 = rec.target2026;
      if (rec.target2027) formData.value.target2027 = rec.target2027;
      if (rec.target2028) formData.value.target2028 = rec.target2028;
      if (rec.target2029) formData.value.target2029 = rec.target2029;
      if (rec.target2030) formData.value.target2030 = rec.target2030;
      if (rec.target2029) formData.value.target_akhir = rec.target2029;
    } else {
      if (rec.target2026 && (!formData.value.p_target2026 || formData.value.p_target2026 === '-')) formData.value.p_target2026 = rec.target2026;
      if (rec.target2027 && (!formData.value.p_target2027 || formData.value.p_target2027 === '-')) formData.value.p_target2027 = rec.target2027;
      if (rec.target2028 && (!formData.value.p_target2028 || formData.value.p_target2028 === '-')) formData.value.p_target2028 = rec.target2028;
      if (rec.target2029 && (!formData.value.p_target2029 || formData.value.p_target2029 === '-')) formData.value.p_target2029 = rec.target2029;
      if (rec.target2030 && (!formData.value.p_target2030 || formData.value.p_target2030 === '-')) formData.value.p_target2030 = rec.target2030;
      if (rec.target2029) formData.value.p_target_akhir = rec.target2029;
    }
  }
}

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
  realisasi2025: '-',
  realisasi2026: '-',
  realisasi2027: '-',
  realisasi2028: '-',
  realisasi2029: '-',
  realisasi2030: '-',

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
    case 'ind_program': return 'Indikator Program';
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
    case 'edit_tujuan': return 'Ubah Tujuan RENSTRA';
    case 'create_sasaran': return 'Tambah Sasaran RENSTRA Baru';
    case 'edit_sasaran': return 'Ubah Sasaran RENSTRA';
    case 'create_ind_tujuan': return 'Tambah Indikator Tujuan';
    case 'edit_ind_tujuan': return 'Ubah Indikator Tujuan';
    case 'create_ind_sasaran': return 'Tambah Indikator Sasaran';
    case 'edit_ind_sasaran': return 'Ubah Indikator Sasaran';
    case 'create_ind_program': return 'Tambah Indikator Program';
    case 'edit_ind_program': return 'Ubah Indikator Program';
    case 'create_ind_kegiatan': return 'Tambah Indikator Kegiatan';
    case 'edit_ind_kegiatan': return 'Ubah Indikator Kegiatan';
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

async function fetchRefKegiatan(kodeprogram) {
  if (!kodeprogram) {
    refKegiatanList.value = [];
    return;
  }
  loadingRefKegiatan.value = true;
  try {
    const res = await api.getRefKegiatan(String(kodeprogram).trim());
    const list = Array.isArray(res) ? res : (res?.data || []);
    refKegiatanList.value = list;
    if (formData.value.kodekegiatan) {
      const match = list.find(k => k.kodekegiatan === formData.value.kodekegiatan);
      if (match) {
        selectedRefKegiatan.value = formData.value.kodekegiatan;
      }
    }
  } catch (err) {
    console.error('Failed to load ref kegiatan:', err);
    refKegiatanList.value = [];
  } finally {
    loadingRefKegiatan.value = false;
  }
}

async function fetchRefSubkegiatan(kodekegiatan) {
  if (!kodekegiatan) {
    refSubkegiatanList.value = [];
    return;
  }
  loadingRefSubkegiatan.value = true;
  try {
    const res = await api.getRefSubkegiatan(String(kodekegiatan).trim());
    const list = Array.isArray(res) ? res : (res?.data || []);
    refSubkegiatanList.value = list;
    if (formData.value.kodesubkegiatan) {
      const match = list.find(s => s.kodesubkegiatan === formData.value.kodesubkegiatan);
      if (match) {
        selectedRefSubkegiatan.value = formData.value.kodesubkegiatan;
      }
    }
  } catch (err) {
    console.error('Failed to load ref subkegiatan:', err);
    refSubkegiatanList.value = [];
  } finally {
    loadingRefSubkegiatan.value = false;
  }
}

function onSelectRefKegiatan() {
  if (!selectedRefKegiatan.value) return;
  const match = refKegiatanList.value.find(k => k.kodekegiatan === selectedRefKegiatan.value);
  if (match) {
    formData.value.kodekegiatan = match.kodekegiatan;
    formData.value.uraikegiatan = match.uraikegiatan;
  }
}

function onSelectRefSubkegiatan() {
  if (!selectedRefSubkegiatan.value) return;
  const match = refSubkegiatanList.value.find(s => s.kodesubkegiatan === selectedRefSubkegiatan.value);
  if (match) {
    formData.value.kodesubkegiatan = match.kodesubkegiatan;
    formData.value.uraisubkegiatan = match.uraisubkegiatan;
    if (match.kinerja && match.kinerja !== '-') {
      formData.value.kinerja = match.kinerja;
    }
    if (match.indikator && match.indikator !== '-') {
      formData.value.uraisubkegiatan_indikator = match.indikator;
    }
    if (match.satuan && match.satuan !== '-') {
      formData.value.satuan = match.satuan;
    }
  }
}

async function fetchRefSasaran(kodeskpd, id_skpd, id_sub_skpd) {
  loadingRefSasaran.value = true;
  try {
    const res = await api.getRefSasaran({
      kodeskpd: kodeskpd || '',
      id_skpd: id_skpd || '',
      id_sub_skpd: id_sub_skpd || '',
    });
    refSasaranList.value = Array.isArray(res) ? res : (res?.data || []);
  } catch (err) {
    console.error('Failed to load ref sasaran:', err);
    refSasaranList.value = [];
  } finally {
    loadingRefSasaran.value = false;
  }
}

// Initialize form values when modal opens or itemData changes
watch(
  () => [props.isOpen, props.mode, props.itemData],
  ([open]) => {
    if (open) {
      showAiPanel.value = false;
      selectedRefKegiatan.value = '';
      selectedRefSubkegiatan.value = '';
      refKegiatanList.value = [];
      refSubkegiatanList.value = [];
      selectedSasaranIds.value = [];
      refSasaranList.value = [];
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
          realisasi2025: props.itemData.indikator?.realisasi2025 || props.itemData.realisasi2025 || '-',
          realisasi2026: props.itemData.indikator?.realisasi2026 || props.itemData.realisasi2026 || '-',
          realisasi2027: props.itemData.indikator?.realisasi2027 || props.itemData.realisasi2027 || '-',
          realisasi2028: props.itemData.indikator?.realisasi2028 || props.itemData.realisasi2028 || '-',
          realisasi2029: props.itemData.indikator?.realisasi2029 || props.itemData.realisasi2029 || '-',
          realisasi2030: props.itemData.indikator?.realisasi2030 || props.itemData.realisasi2030 || '-',

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
          realisasi2025: '-',
          realisasi2026: '-',
          realisasi2027: '-',
          realisasi2028: '-',
          realisasi2029: '-',
          realisasi2030: '-',

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

      // Fetch references from database if applicable
      if (isProgramForm.value) {
        const rawSasaran = [
          ...(props.itemData?.sasaran_ids || []),
          ...(props.itemData?.renstra_sasaran || []),
        ];
        selectedSasaranIds.value = [...new Set(rawSasaran.map(id => {
          const s = String(id).trim();
          return s.length > 36 ? s.slice(-36) : s;
        }))];

        const kpd = props.itemData?.kodeskpd || formData.value.kodeskpd;
        const idSkpd = props.itemData?.id_skpd || props.idSkpd;
        const idSubSkpd = props.itemData?.id_sub_skpd;
        fetchRefSasaran(kpd, idSkpd, idSubSkpd);
      }

      if (isKegiatanForm.value) {
        let kodeProg = props.itemData?.kodeprogram || formData.value.kodeprogram;
        if (!kodeProg && (props.itemData?.kodekegiatan || formData.value.kodekegiatan)) {
          const rawKeg = props.itemData?.kodekegiatan || formData.value.kodekegiatan;
          const parts = String(rawKeg).split('.');
          if (parts.length >= 3) {
            kodeProg = parts.slice(0, 3).join('.');
          }
        }
        if (kodeProg) {
          fetchRefKegiatan(kodeProg);
        }
      }

      if (isSubkegiatanForm.value) {
        let kodeKeg = props.itemData?.kodekegiatan || formData.value.kodekegiatan;
        if (!kodeKeg && (props.itemData?.kodesubkegiatan || formData.value.kodesubkegiatan)) {
          const rawSub = props.itemData?.kodesubkegiatan || formData.value.kodesubkegiatan;
          const parts = String(rawSub).split('.');
          if (parts.length >= 5) {
            kodeKeg = parts.slice(0, 5).join('.');
          }
        }
        if (kodeKeg) {
          fetchRefSubkegiatan(kodeKeg);
        }
      }
    }
  },
  { immediate: true, deep: true }
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
        no_urut: formData.value.no_urut,
      });
    } else if (props.mode === 'create_ind_program') {
      await api.createIndikatorProgram({
        kodeskpd: props.itemData.kodeskpd,
        kodeprogram: props.itemData.kodeprogram,
        uraiprogram: props.itemData.uraiprogram,
        kodebidang: props.itemData.kodebidang,
        uraian: formData.value.uraian,
        satuan: formData.value.satuan,
        status: formData.value.status,
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
        no_urut: formData.value.no_urut,
      });
    } else if (props.mode === 'edit_ind_program') {
      await api.updateIndikatorProgram(props.itemData.id, {
        uraian: formData.value.uraian,
        satuan: formData.value.satuan,
        status: formData.value.status,
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
        no_urut: formData.value.no_urut,
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
        no_urut: formData.value.no_urut,
      });
    } else if (props.mode === 'create_program') {
      await api.createProgram({
        kodeskpd: props.itemData.kodeskpd,
        kodebidang: props.itemData.kodebidang,
        kodeprogram: formData.value.kodeprogram,
        uraiprogram: formData.value.uraiprogram,
        kinerja: formData.value.kinerja,
        sasaran_ids: selectedSasaranIds.value,
      });
    } else if (props.mode === 'edit_program') {
      await api.updateProgram(props.itemData.id, {
        kodeprogram: formData.value.kodeprogram,
        uraiprogram: formData.value.uraiprogram,
        kinerja: formData.value.kinerja,
        sasaran_ids: selectedSasaranIds.value,
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
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
        realisasi2025: formData.value.realisasi2025,
        realisasi2026: formData.value.realisasi2026,
        realisasi2027: formData.value.realisasi2027,
        realisasi2028: formData.value.realisasi2028,
        realisasi2029: formData.value.realisasi2029,
        realisasi2030: formData.value.realisasi2030,
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
      case 'ind_program':
        await api.deleteIndikatorProgram(props.itemData.id);
        break;
      case 'ind_kegiatan':
        await api.deleteIndikatorKegiatan(props.itemData.id);
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
  transition: max-width 0.25s ease;
}

.crud-modal-card.wide-modal {
  max-width: 900px;
}

.btn-ai-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: #ffffff;
  border: 1px solid transparent;
  padding: 0.4rem 0.85rem;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 9999px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(79, 70, 229, 0.25);
  transition: all 0.2s ease;
}

.btn-ai-toggle:hover {
  background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%);
  box-shadow: 0 4px 10px rgba(79, 70, 229, 0.35);
  transform: translateY(-1px);
}

.btn-ai-toggle.active {
  background: #f1f5f9;
  color: #475569;
  border-color: #cbd5e1;
  box-shadow: none;
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

.badge-realisasi {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
  padding: 0.12rem 0.45rem;
  border-radius: 4px;
  font-size: 0.68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.targets-realisasi-grid {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
}

.r-label {
  color: #065f46 !important;
}

.r-input:focus {
  border-color: #059669 !important;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15) !important;
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

/* Reference Picker Card */
.ref-picker-card {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  padding: 0.85rem;
  margin-bottom: 1rem;
}

.ref-picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.ref-picker-title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 700;
  font-size: 0.84rem;
  color: #166534;
}

.ref-count-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: #15803d;
  background: #dcfce7;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  border: 1px solid #86efac;
}

.ref-loading-badge {
  font-size: 0.72rem;
  font-weight: 600;
  color: #0369a1;
  background: #e0f2fe;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  border: 1px solid #7dd3fc;
}

.ref-select {
  width: 100%;
  padding: 0.55rem 0.75rem;
  font-size: 0.84rem;
  border: 1px solid #86efac;
  border-radius: 6px;
  background-color: #ffffff;
  color: #14532d;
  font-weight: 500;
  cursor: pointer;
}

.ref-select:focus {
  outline: none;
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.15);
}

.ref-hint {
  font-size: 0.75rem;
  color: #15803d;
  margin-top: 0.35rem;
  line-height: 1.4;
}

/* Sasaran Tagger Card */
.sasaran-tagger-card {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 0.9rem;
}

.sasaran-tagger-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.35rem;
}

.sasaran-tagger-title {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-weight: 700;
  font-size: 0.85rem;
  color: #1e293b;
}

.sasaran-tagger-count {
  font-size: 0.74rem;
  font-weight: 700;
  color: #2563eb;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  padding: 0.15rem 0.55rem;
  border-radius: 9999px;
}

.sasaran-tagger-desc {
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.sasaran-checkbox-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 220px;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.sasaran-checkbox-item {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.sasaran-checkbox-item:hover {
  border-color: #93c5fd;
  background: #f0f7ff;
}

.sasaran-checkbox-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.1);
}

.sasaran-checkbox-input {
  margin-top: 0.25rem;
  cursor: pointer;
  accent-color: #2563eb;
  width: 16px;
  height: 16px;
}

.sasaran-checkbox-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.sasaran-checkbox-main {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.sasaran-number-badge {
  font-size: 0.7rem;
  font-weight: 700;
  color: #1e40af;
  background: #dbeafe;
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
  white-space: nowrap;
}

.sasaran-uraian-text {
  font-size: 0.82rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.35;
}

.sasaran-tujuan-text {
  font-size: 0.73rem;
  color: #64748b;
  line-height: 1.3;
}
</style>
