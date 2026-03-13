// API helper module for making requests to the backend
// Uses session cookies automatically - no need to manually set headers

const api = {
    async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
        };

        const mergedOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, mergedOptions);

            // Handle 401 Unauthorized - redirect to login
            if (response.status === 401) {
                window.location.href = '/login';
                throw new Error('Unauthorized');
            }

            // Handle 403 Forbidden
            if (response.status === 403) {
                throw new Error('Forbidden - You do not have permission to perform this action');
            }

            // Handle 204 No Content
            if (response.status === 204) {
                return null;
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            if (error.message === 'Failed to fetch') {
                throw new Error('Network error - unable to connect to the server');
            }
            throw error;
        }
    },

    get(url) {
        return this.request(url, { method: 'GET' });
    },

    post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete(url) {
        return this.request(url, { method: 'DELETE' });
    },

    // Form data submission (for file uploads or multipart forms)
    postForm(url, formData) {
        return this.request(url, {
            method: 'POST',
            headers: {}, // Let browser set Content-Type for FormData
            body: formData,
        });
    },
};

// Make api available globally
window.api = api;
