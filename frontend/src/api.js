export const API_BASE_URL = "http://54.180.162.50:8000";

export function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}
