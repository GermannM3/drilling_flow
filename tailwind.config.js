module.exports = {
    content: ["./public/**/*.{html,js}", "./api/**/*.{html,js}"],
    theme: {
        "name": "Custom",
        "fontFamily": {
            "sans": ["Oswald", "ui-sans-serif", "system-ui", "sans-serif", "\"Apple Color Emoji\"", "\"Segoe UI Emoji\"", "\"Segoe UI Symbol\"", "\"Noto Color Emoji\""]
        },
        "extend": {
            "fontFamily": {
                "title": ["Roboto", "ui-sans-serif", "system-ui", "sans-serif", "\"Apple Color Emoji\"", "\"Segoe UI Emoji\"", "\"Segoe UI Symbol\"", "\"Noto Color Emoji\""],
                "body": ["Inter", "ui-sans-serif", "system-ui", "sans-serif", "\"Apple Color Emoji\"", "\"Segoe UI Emoji\"", "\"Segoe UI Symbol\"", "\"Noto Color Emoji\""]
            },
            "colors": {
                "neutral": {
                    "50": "#1D232A",
                    "100": "#1C2229",
                    "200": "#1B2127",
                    "300": "#1A2026",
                    "400": "#1A1F25",
                    "500": "#191E24",
                    "600": "#0C0E11",
                    "700": "#090B0D",
                    "800": "#060708",
                    "900": "#030304",
                    "DEFAULT": "#1D232A"
                },
                "primary": {
                    "50": "#f1fcf2",
                    "100": "#defae2",
                    "200": "#bef4c7",
                    "300": "#8bea9c",
                    "400": "#51d76a",
                    "500": "#2abd46",
                    "600": "#1d9c35",
                    "700": "#1a7b2d",
                    "800": "#1a6128",
                    "900": "#175024",
                    "950": "#072c0f",
                    "DEFAULT": "#2abd46"
                }
            }
        },
        "fontSize": {
            "xs": ["13.5px", {"lineHeight": "21.6px"}],
            "sm": ["15.75px", {"lineHeight": "23.625px"}],
            "base": ["18px", {"lineHeight": "28.8px"}],
            "lg": ["20.25px", {"lineHeight": "30.375px"}],
            "xl": ["22.5px", {"lineHeight": "31.499999999999996px"}],
            "2xl": ["27px", {"lineHeight": "35.1px"}],
            "3xl": ["33.75px", {"lineHeight": "40.5px"}],
            "4xl": ["40.5px", {"lineHeight": "46.574999999999996px"}],
            "5xl": ["54px", {"lineHeight": "59.400000000000006px"}],
            "6xl": ["67.5px", {"lineHeight": "74.25px"}],
            "7xl": ["81px", {"lineHeight": "85.05px"}],
            "8xl": ["108px", {"lineHeight": "113.4px"}],
            "9xl": ["144px", {"lineHeight": "151.20000000000002px"}]
        },
        "borderRadius": {
            "none": "0px",
            "sm": "2px",
            "DEFAULT": "4px",
            "md": "6px",
            "lg": "8px",
            "xl": "12px",
            "2xl": "16px",
            "3xl": "24px",
            "full": "9999px"
        },
        "spacing": {
            "0": "0px",
            "1": "4px",
            "2": "8px",
            "3": "12px",
            "4": "16px",
            "5": "20px",
            "6": "24px",
            "7": "28px",
            "8": "32px",
            "9": "36px",
            "10": "40px",
            "11": "44px",
            "12": "48px",
            "14": "56px",
            "16": "64px",
            "20": "80px",
            "24": "96px",
            "28": "112px",
            "32": "128px",
            "36": "144px",
            "40": "160px",
            "44": "176px",
            "48": "192px",
            "52": "208px",
            "56": "224px",
            "60": "240px",
            "64": "256px",
            "72": "288px",
            "80": "320px",
            "96": "384px",
            "px": "1px",
            "0.5": "2px",
            "1.5": "6px",
            "2.5": "10px",
            "3.5": "14px"
        }
    },
    plugins: [],
    important: '#webcrumbs'
} 