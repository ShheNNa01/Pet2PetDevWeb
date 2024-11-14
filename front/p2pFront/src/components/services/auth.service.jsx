import axiosInstance from './config/axios';

export const AuthService = {
    async register(userData) {
        try {
            const response = await axiosInstance.post('/auth/register', {
                user_name: userData.ownerName,
                user_last_name: userData.ownerLastName,
                user_email: userData.correo,
                password: userData.contrasena,
                user_city: userData.city || '',
                user_country: userData.country || '',
                user_number: userData.phoneNumber || '',
                user_bio: userData.bio || ''
            });

            localStorage.setItem('pendingVerificationEmail', userData.correo);

            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    async verifyEmail(token) {
        try {
            // Enviamos el token como query parameter
            const response = await axiosInstance.post(`/auth/verify-email?token=${token}`);
            return response.data;
        } catch (error) {
            console.log('Error completo:', error.response);
            throw error.response?.data || error.message;
        }
    },

    async login(credentials) {
        try {
            const formData = new URLSearchParams();
            formData.append('username', credentials.username);
            formData.append('password', credentials.password);

            const response = await axiosInstance.post('/auth/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            if (response.data.access_token) {
                localStorage.setItem('token', response.data.access_token);
                localStorage.setItem('user', JSON.stringify(response.data.user));
            }

            return response.data;
        } catch (error) {
            throw error.response?.data || error.message;
        }
    },

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('currentPet');
    },

    getCurrentUser() {
        return JSON.parse(localStorage.getItem('user'));
    },

    isAuthenticated() {
        return !!localStorage.getItem('token');
    }
};

export default AuthService;