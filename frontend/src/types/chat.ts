export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  context?: string
  stream?: boolean
}

export interface ChatResponse {
  message: ChatMessage
  model: string
}

export interface ChatChunk {
  delta: string
  done: boolean
  error?: string
  detail?: string
}
