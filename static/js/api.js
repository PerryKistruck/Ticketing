// Unified API helper
(function(global){
  if (global.apiRequest) { return; }
  async function apiRequest(url, options = {}) {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      if (window.location.protocol === 'https:' && url.startsWith('http://')) {
        url = url.replace('http://', 'https://');
      }
    }
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'same-origin'
    };
    const finalOptions = {
      ...defaultOptions,
      ...options,
      headers: { ...defaultOptions.headers, ...(options.headers || {}) }
    };
    let response;
    try {
      response = await fetch(url, finalOptions);
    } catch (e) {
      throw new Error('Network error: Unable to connect to server.');
    }
    const contentType = response.headers.get('content-type') || '';
    let data = null;
    if (contentType.includes('application/json')) {
      data = await response.json().catch(()=>({ error: 'Invalid JSON response'}));
    } else {
      data = { error: 'Non-JSON response', status: response.status };
    }
    if (!response.ok) {
      throw new Error(data && data.error ? data.error : `HTTP ${response.status}`);
    }
    return data;
  }
  global.apiRequest = apiRequest;
})(window);
