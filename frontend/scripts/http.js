/** Requests use the same-origin Nginx API proxy. */
export async function request(path, { method = 'GET', body, session } = {}) {
  const headers = {};
  if (session) headers['X-Session-Code'] = session;
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const response = await fetch(`/api${path}`, { method, headers, ...(body !== undefined ? { body: JSON.stringify(body) } : {}) });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const message = payload?.message || `Request failed (${response.status}).`;
    const error = new Error(message);
    error.code = payload?.error_code || 'REQUEST_FAILED';
    error.status = response.status;
    error.serverMessage = payload?.message || null;
    throw error;
  }
  return payload;
}
