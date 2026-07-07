<script setup>
import { Download, FileSpreadsheet, Images } from 'lucide-vue-next'
import { absoluteDownloadUrl } from '../services/api'

defineProps({
  job: {
    type: Object,
    required: true,
  },
})

function formatDate(value) {
  return new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}
</script>

<template>
  <article class="job-card">
    <div>
      <p class="job-card__key">{{ job.combined_key }}</p>
      <div class="job-card__meta">
        <span><Images :size="15" /> tif {{ job.image_count }}개</span>
        <span>{{ formatDate(job.created_at) }}</span>
      </div>
    </div>
    <div class="job-card__actions">
      <a
        v-if="job.pptx_download_url"
        class="button button--primary"
        :href="absoluteDownloadUrl(job.pptx_download_url)"
        download
      >
        <Download :size="17" />
        PPTX
      </a>
      <a
        v-if="job.xlsx_download_url"
        class="button button--light"
        :href="absoluteDownloadUrl(job.xlsx_download_url)"
        download
      >
        <FileSpreadsheet :size="17" />
        XLSX
      </a>
      <button v-else class="button button--disabled" type="button" disabled>
        <FileSpreadsheet :size="17" />
        XLSX
      </button>
    </div>
  </article>
</template>
