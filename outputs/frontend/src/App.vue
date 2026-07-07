<script setup>
import { computed, onMounted, ref } from 'vue'
import { Download, Loader2, Search, Sparkles, UploadCloud } from 'lucide-vue-next'
import DropZone from './components/DropZone.vue'
import JobCard from './components/JobCard.vue'
import { absoluteDownloadUrl, createJob, searchJobs } from './services/api'

const activeView = ref('create')
const requestNumber = ref('')
const sampleNumber = ref('')
const tifFiles = ref([])
const xlsxFile = ref(null)
const createdJob = ref(null)
const jobs = ref([])
const query = ref('')
const isSubmitting = ref(false)
const isSearching = ref(false)
const errorMessage = ref('')

const canSubmit = computed(() => requestNumber.value.trim() && sampleNumber.value.trim() && tifFiles.value.length)

async function submitJob() {
  if (!canSubmit.value || isSubmitting.value) return

  isSubmitting.value = true
  errorMessage.value = ''
  createdJob.value = null

  try {
    createdJob.value = await createJob({
      requestNumber: requestNumber.value,
      sampleNumber: sampleNumber.value,
      tifFiles: tifFiles.value,
      xlsxFile: xlsxFile.value,
    })
    activeView.value = 'create'
    await loadJobs(createdJob.value.combined_key)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isSubmitting.value = false
  }
}

async function loadJobs(nextQuery = query.value) {
  isSearching.value = true
  errorMessage.value = ''
  query.value = nextQuery
  try {
    jobs.value = await searchJobs(nextQuery)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isSearching.value = false
  }
}

function resetForm() {
  requestNumber.value = ''
  sampleNumber.value = ''
  tifFiles.value = []
  xlsxFile.value = null
  createdJob.value = null
  errorMessage.value = ''
}

onMounted(() => {
  loadJobs('')
})
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="brand__mark"><Sparkles :size="22" /></span>
        <div>
          <p class="brand__name">TIF PPTX 생성</p>
          <p class="brand__sub">이미지 묶음을 PPTX로 정리합니다</p>
        </div>
      </div>
      <nav class="view-tabs" aria-label="페이지 선택">
        <button :class="{ active: activeView === 'create' }" type="button" @click="activeView = 'create'">
          <UploadCloud :size="17" />
          생성
        </button>
        <button :class="{ active: activeView === 'search' }" type="button" @click="activeView = 'search'">
          <Search :size="17" />
          조회
        </button>
      </nav>
    </header>

    <p v-if="errorMessage" class="alert">{{ errorMessage }}</p>

    <section v-if="activeView === 'create'" class="workspace workspace--create">
      <div class="panel form-panel">
        <div class="section-heading">
          <p>생성 페이지</p>
          <h1>의뢰 정보와 tif 이미지를 등록하세요</h1>
        </div>

        <div class="field-grid">
          <label>
            <span>의뢰번호</span>
            <input v-model="requestNumber" type="text" placeholder="예: REQ-2026-001" />
          </label>
          <label>
            <span>시료번호</span>
            <input v-model="sampleNumber" type="text" placeholder="예: SAMPLE-A12" />
          </label>
        </div>

        <DropZone v-model:tif-files="tifFiles" v-model:xlsx-file="xlsxFile" />

        <div class="form-actions">
          <button class="button button--ghost" type="button" @click="resetForm">초기화</button>
          <button class="button button--primary button--large" type="button" :disabled="!canSubmit || isSubmitting" @click="submitJob">
            <Loader2 v-if="isSubmitting" class="spin" :size="18" />
            <UploadCloud v-else :size="18" />
            PPTX 생성
          </button>
        </div>
      </div>

      <aside class="panel result-panel">
        <div class="section-heading">
          <p>다운로드</p>
          <h2>생성이 완료되면 버튼이 표시됩니다</h2>
        </div>

        <div v-if="createdJob" class="complete-box">
          <p class="complete-box__key">{{ createdJob.combined_key }}</p>
          <p class="complete-box__status">PPTX 생성이 완료되었습니다.</p>
          <a class="button button--primary button--wide" :href="absoluteDownloadUrl(createdJob.pptx_download_url)" download>
            <Download :size="18" />
            PPTX 다운로드
          </a>
          <a
            v-if="createdJob.xlsx_download_url"
            class="button button--light button--wide"
            :href="absoluteDownloadUrl(createdJob.xlsx_download_url)"
            download
          >
            XLSX 다운로드
          </a>
        </div>
        <div v-else class="empty-state">
          <UploadCloud :size="34" />
          <p>아직 생성된 PPTX가 없습니다.</p>
        </div>
      </aside>
    </section>

    <section v-else class="workspace workspace--search">
      <div class="panel search-panel">
        <div class="section-heading">
          <p>Main Page</p>
          <h1>의뢰번호_시료번호로 결과를 조회하세요</h1>
        </div>
        <div class="search-row">
          <Search :size="20" />
          <input v-model="query" type="search" placeholder="예: REQ-2026-001_SAMPLE-A12" @keyup.enter="loadJobs()" />
          <button class="button button--primary" type="button" @click="loadJobs()">
            <Loader2 v-if="isSearching" class="spin" :size="17" />
            <Search v-else :size="17" />
            검색
          </button>
        </div>
      </div>

      <div class="results-grid">
        <JobCard v-for="job in jobs" :key="job.id" :job="job" />
        <div v-if="!jobs.length && !isSearching" class="panel empty-search">
          <Search :size="32" />
          <p>조회된 건이 없습니다.</p>
        </div>
      </div>
    </section>
  </main>
</template>
