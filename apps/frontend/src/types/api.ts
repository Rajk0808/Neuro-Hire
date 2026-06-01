export interface ApiResponse<T = unknown> {
  data: T
  status: number
  message?: string
}

export interface ApiError {
  status: number
  message: string
  code?: string
}

export interface PaginationParams {
  page: number
  limit: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface ListResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  hasMore: boolean
}
