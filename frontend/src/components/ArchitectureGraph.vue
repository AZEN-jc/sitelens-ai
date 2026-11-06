<script setup lang="ts">
import { computed } from 'vue'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { VueFlow } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import type { Technology } from '../types'

const props = defineProps<{ technologies: Technology[] }>()
const nodes = computed(() => [
  { id: 'response', position: { x: 0, y: 80 }, data: { label: '公开响应' }, class: 'flow-node flow-origin' },
  ...props.technologies.map((tech, index) => ({
    id: `tech-${index}`, position: { x: 230 + (index % 2) * 230, y: Math.floor(index / 2) * 100 }, data: { label: `${tech.name} · ${{ high: '高', medium: '中', low: '低' }[tech.confidence]}置信` }, class: 'flow-node',
  })),
])
const edges = computed(() => props.technologies.map((_, index) => ({ id: `edge-${index}`, source: 'response', target: `tech-${index}`, label: '观察到', animated: false, style: { stroke: '#8a8a8a' } })))
</script>

<template>
  <div class="flow-wrap"><VueFlow :nodes="nodes" :edges="edges" fit-view-on-init :nodes-draggable="false" :zoom-on-scroll="false"><Background pattern-color="#2a2a2a" :gap="24" /><Controls /></VueFlow></div>
</template>
