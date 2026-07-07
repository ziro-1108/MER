<script setup>
import { computed, ref } from 'vue'
import { FileArchive, FileSpreadsheet, ImagePlus, X } from 'lucide-vue-next'

const props = defineProps({
  tifFiles: {
    type: Array,
    required: true,
  },
  xlsxFile: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['update:tifFiles', 'update:xlsxFile'])
const isDragging = ref(false)
const fileInput = ref(null)

const tifCountLabel = computed(() => `${props.tifFiles.length}개 이미지`)

function openPicker() {
  fileInput.value?.click()
}

function handleInput(event) {
  addFiles(Array.from(event.target.files || []))
  event.target.value = ''
}

function handleDrop(event) {
  isDragging.value = false
  addFiles(Array.from(event.dataTransfer.files || []))
}

function addFiles(files) {
  const tifFiles = []
  let xlsxFile = props.xlsxFile

  files.forEach((file) => {
    const name = file.name.toLowerCase()
    if (name.endsWith('.tif') || name.endsWith('.tiff')) tifFiles.push(file)
    if (name.endsWith('.xlsx')) xlsxFile = file
  })

  if (tifFiles.length) emit('update:tifFiles', [...props.tifFiles, ...tifFiles])
  if (xlsxFile !== props.xlsxFile) emit('update:xlsxFile', xlsxFile)
}

function removeTif(index) {
  emit('update:tifFiles', props.tifFiles.filter((_, fileIndex) => fileIndex !== index))
}
</script>

<template>
  <section
    class="drop-zone"
    :class="{ 'is-dragging': isDragging }"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="handleDrop"
  >
    <input
      ref="fileInput"
      class="visually-hidden"
      type="file"
      multiple
      accept=".tif,.tiff,.xlsx"
      @change="handleInput"
    />

    <div class="drop-zone__icon" aria-hidden="true">
      <ImagePlus :size="30" />
    </div>
    <div class="drop-zone__copy">
      <h2>tif 이미지를 여기에 놓아주세요</h2>
      <p>tif, tiff 파일을 여러 개 등록할 수 있고 xlsx는 선택 사항입니다.</p>
    </div>
    <button class="button button--primary" type="button" @click="openPicker">
      <FileArchive :size="18" />
      파일 선택
    </button>
  </section>

  <div class="file-summary">
    <div class="summary-pill">
      <ImagePlus :size="17" />
      <span>{{ tifCountLabel }}</span>
    </div>
    <div class="summary-pill" :class="{ 'is-empty': !xlsxFile }">
      <FileSpreadsheet :size="17" />
      <span>{{ xlsxFile ? xlsxFile.name : 'xlsx 없음' }}</span>
      <button v-if="xlsxFile" class="icon-button" type="button" aria-label="xlsx 제거" @click="$emit('update:xlsxFile', null)">
        <X :size="14" />
      </button>
    </div>
  </div>

  <ul v-if="tifFiles.length" class="file-list" aria-label="등록된 tif 파일">
    <li v-for="(file, index) in tifFiles" :key="`${file.name}-${index}`">
      <span>{{ file.name }}</span>
      <button class="icon-button" type="button" :aria-label="`${file.name} 제거`" @click="removeTif(index)">
        <X :size="14" />
      </button>
    </li>
  </ul>
</template>
