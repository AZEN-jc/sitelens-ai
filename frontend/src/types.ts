export interface Evidence {
  source: string
  matched: string
  kind: 'direct' | 'indirect'
  weight: number
}

export interface Technology {
  name: string
  category: string
  category_label: string
  score: number
  confidence: 'high' | 'medium' | 'low'
  evidence: Evidence[]
}

export interface AIReport {
  id: number
  model: string
  content: string
  created_at: string
}

export interface Scan {
  id: number
  url: string
  final_url: string
  status_code: number
  content_type: string
  title: string
  headers: Record<string, string>
  meta: { name: string; content: string }[]
  scripts: string[]
  styles: string[]
  duration_ms?: number
  page_bytes?: number
  created_at: string
  technologies: Technology[]
  ai_report_count: number
  ai_reports: AIReport[]
}
