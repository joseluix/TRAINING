import axios from 'axios';

// 1. Create an Axios instance
// This pre-configures the base URL and headers so we don't have to repeat them.
const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
    timeout: 5000, // Wait for 5 seconds before giving up
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

// 2. Add Default Auth (for now)
// Since we are assuming Basic Auth with a test user (admin:admin) or similar.
// In a real app, you'd set this token after the user logs in.
// api.defaults.headers.common['Authorization'] = 'Basic YWRtaW46YWRtaW4='; // admin:admin in Base64

// 3. Export the client
export default api;

// 4. API Service Functions
// It's good practice to keep API calls here, not in the components.
export const fetchAccounts = () => api.get('accounts/');
export const deposit = (accountId, amount) => api.post(`accounts/${accountId}/deposit/`, { amount });
export const withdraw = (accountId, amount) => api.post(`accounts/${accountId}/withdraw/`, { amount });
export const executeTrade = (tradeData) => api.post('trading/', tradeData);
