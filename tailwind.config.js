module.exports = {
    content: [
        "./app/templates/**/*.html",
        "./app/static/webapp/js/**/*.js"
    ],
    important: '#webcrumbs',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif']
            },
            colors: {
                emerald: {
                    400: '#34D399',
                    500: '#10B981',
                    600: '#059669',
                    700: '#047857'
                },
                slate: {
                    800: '#1E293B',
                    900: '#0F172A'
                }
            }
        }
    }
} 