export const API_BASE_URL = "https://zinbot-backend.onrender.com";

export function apiUrl(path) {
  return `${API_BASE_URL}${path}`;
}
