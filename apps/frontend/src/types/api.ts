export interface ApiList<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}
