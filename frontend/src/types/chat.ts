export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  stream?: boolean
}

export interface ChatResponse {
  message: ChatMessage
  model: string
}

export interface ChatChunk {
  delta: string
  done: boolean
  tool?: string
  error?: string
  detail?: string
}
