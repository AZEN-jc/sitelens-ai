<script setup lang="ts">
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

use([PieChart, LegendComponent, TooltipComponent, CanvasRenderer])
defineProps<{ categories: { name: string; value: number }[] }>()
const colors = ['#c9e57a', '#89b8a8', '#9ca9dc', '#d5a977', '#cf8c79']
</script>

<template>
  <VChart class="chart" :option="{
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, textStyle: { color: '#9ca5a4' } },
    series: [{ type: 'pie', radius: ['58%', '78%'], center: ['50%', '43%'], label: { show: false }, itemStyle: { borderColor: '#171b1b', borderWidth: 3 }, data: categories.map((item, index) => ({ ...item, itemStyle: { color: colors[index % colors.length] } })) }],
  }" autoresize />
</template>
