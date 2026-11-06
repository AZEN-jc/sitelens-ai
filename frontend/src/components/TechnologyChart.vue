<script setup lang="ts">
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

use([PieChart, LegendComponent, TooltipComponent, CanvasRenderer])
defineProps<{ categories: { name: string; value: number }[] }>()
const colors = ['#e61919', '#ff5c4d', '#8a8a8a', '#5a5a5a', '#c41414']
</script>

<template>
  <VChart class="chart" :option="{
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, textStyle: { color: '#8a8a8a' } },
    series: [{ type: 'pie', radius: ['58%', '78%'], center: ['50%', '43%'], label: { show: false }, itemStyle: { borderColor: '#0a0a0a', borderWidth: 3 }, data: categories.map((item, index) => ({ ...item, itemStyle: { color: colors[index % colors.length] } })) }],
  }" autoresize />
</template>
