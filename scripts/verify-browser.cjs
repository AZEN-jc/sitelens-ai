const http = require('node:http')
const fs = require('node:fs')

const CDP = 'http://127.0.0.1:9223'
const TARGET = 'http://127.0.0.1:8000/scans/1'

const fixture = {
  id: 1,
  url: 'https://fixture.test',
  final_url: 'https://fixture.test',
  status_code: 200,
  content_type: 'text/html',
  title: '受控图表验收样本',
  headers: { 'content-type': 'text/html', server: 'nginx' },
  meta: [{ name: 'generator', content: 'WordPress 6.4' }],
  scripts: ['/wp-includes/js/jquery.js'],
  styles: ['/wp-content/themes/demo/style.css'],
  created_at: '2026-11-05T00:00:00Z',
  technologies: [
    { name: 'WordPress', category: 'CMS', score: 90, confidence: 'high', evidence: [{ source: 'meta_generator', matched: 'WordPress 6.4', kind: 'direct', weight: 90 }] },
    { name: 'jQuery', category: 'JavaScript library', score: 60, confidence: 'medium', evidence: [{ source: 'script_src', matched: '/wp-includes/js/jquery.js', kind: 'direct', weight: 60 }] },
    { name: 'Nginx', category: 'Web server', score: 70, confidence: 'medium', evidence: [{ source: 'header_server', matched: 'nginx', kind: 'direct', weight: 70 }] },
  ],
  ai_report_count: 0,
  ai_reports: [],
}

function httpJSON(path) {
  return new Promise((resolve, reject) => {
    http.get(CDP + path, r => {
      let d = ''
      r.on('data', c => { d += c })
      r.on('end', () => { try { resolve(JSON.parse(d)) } catch (e) { reject(e) } })
    }).on('error', reject)
  })
}

const sleep = ms => new Promise(r => setTimeout(r, ms))

async function main() {
  const targets = await httpJSON('/json/list')
  const page = targets.find(t => t.type === 'page')
  if (!page) throw new Error('没有可用页面 target')
  const ws = new WebSocket(page.webSocketDebuggerUrl)
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej })

  let seq = 0
  const pending = new Map()
  const send = (method, params = {}) => new Promise(resolve => {
    const id = ++seq
    pending.set(id, resolve)
    ws.send(JSON.stringify({ id, method, params }))
  })
  ws.onmessage = e => {
    const m = JSON.parse(e.data)
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); return }
    if (m.method === 'Fetch.requestPaused') {
      const { requestId, request } = m.params
      if (request.url.includes('/api/scans/1')) {
        const body = Buffer.from(JSON.stringify(fixture)).toString('base64')
        send('Fetch.fulfillRequest', {
          requestId, responseCode: 200,
          responseHeaders: [{ name: 'Content-Type', value: 'application/json' }],
          body,
        })
      } else {
        send('Fetch.continueRequest', { requestId })
      }
    }
  }

  const evaluate = async expression => {
    const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })
    if (r.exceptionDetails) return { error: r.exceptionDetails.text }
    return r.result.value
  }

  await send('Page.enable')
  await send('Runtime.enable')
  await send('Network.enable')
  await send('Fetch.enable', { patterns: [{ urlPattern: '*api/scans/1*', requestStage: 'Request' }] })
  await send('Page.navigate', { url: TARGET })

  for (let i = 0; i < 40; i++) {
    await sleep(250)
    const ready = await evaluate("!!document.querySelector('.scan-page')")
    if (ready === true) break
  }

  for (let i = 0; i < 30; i++) {
    const n = await evaluate("document.querySelectorAll('canvas').length")
    if (n > 0) break
    await sleep(200)
  }

  const overview = await evaluate(`(() => {
    const c = document.querySelector('.side-panel canvas')
    let dataLen = 0
    try { dataLen = c ? c.toDataURL().length : 0 } catch (e) { dataLen = -1 }
    return {
      title: document.title,
      h1: document.querySelector('.scan-header h1')?.textContent?.trim(),
      tabs: [...document.querySelectorAll('.result-tabs button')].map(b => b.textContent.trim()),
      techCards: document.querySelectorAll('.technology-card').length,
      canvasCount: document.querySelectorAll('canvas').length,
      canvasSize: c ? [c.width, c.height] : null,
      canvasDataUrlLen: dataLen,
      chartEmpty: document.querySelector('.chart-empty')?.textContent?.trim() || null,
    }
  })()`)

  const resourcesBefore = await evaluate("performance.getEntriesByType('resource').map(e => e.name.split('/').pop())")

  await evaluate("[...document.querySelectorAll('.result-tabs button')].find(b => b.textContent.includes('架构')).click()")
  await sleep(1500)
  const architecture = await evaluate(`(() => ({
    flowNodes: document.querySelectorAll('.vue-flow__node').length,
    svgCount: document.querySelectorAll('.tab-content svg').length,
    methodNote: document.querySelector('.method-note')?.textContent?.trim().slice(0, 60),
    resources: performance.getEntriesByType('resource').map(e => e.name.split('/').pop()),
  }))()`)

  const shot = await send('Page.captureScreenshot', { format: 'png' })
  fs.writeFileSync('/tmp/sitelens-architecture.png', Buffer.from(shot.data, 'base64'))

  const result = {
    chrome: (await httpJSON('/json/version')).Browser,
    target: TARGET,
    fixtureNote: 'CDP Fetch 拦截 /api/scans/1 返回受控数据，未修改数据库与源码',
    overview,
    resourcesBefore: resourcesBefore.filter(n => /TechnologyChart|ArchitectureGraph|charts-/.test(n)),
    architecture: {
      flowNodes: architecture.flowNodes,
      svgCount: architecture.svgCount,
      methodNote: architecture.methodNote,
      lazyChunks: architecture.resources.filter(n => /TechnologyChart|ArchitectureGraph/.test(n)),
    },
    screenshot: '/tmp/sitelens-architecture.png',
  }
  console.log(JSON.stringify(result, null, 2))
  ws.close()
}

main().catch(e => { console.error('CDP_FAIL', e); process.exit(1) })
