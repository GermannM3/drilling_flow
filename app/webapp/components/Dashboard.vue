<template>
  <div id="webcrumbs"><div class="min-h-screen bg-gradient-to-br from-emerald-800 to-blue-900 flex items-center justify-center p-4 sm:p-8"> <div class="w-full max-w-[1200px] bg-slate-900 rounded-xl shadow-2xl p-4 sm:p-8 border-2 sm:border-4 border-emerald-500"> <header class="flex flex-col sm:flex-row justify-between items-center mb-8 gap-4"> <div class="flex items-center gap-4"> <span class="material-symbols-outlined text-3xl sm:text-4xl text-emerald-400">water_drop</span> <h1 class="text-2xl sm:text-3xl font-bold text-emerald-400">Панель Управления DrillFlow</h1> </div> <div class="flex items-center gap-4"> <details class="relative"> <summary class="flex items-center gap-2 cursor-pointer hover:bg-emerald-800 p-2 rounded-lg transition-all"> <span class="material-symbols-outlined text-emerald-400">notifications</span> <span class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">3</span> </summary> <div class="absolute right-0 mt-2 w-64 bg-slate-800 rounded-lg shadow-2xl p-4 z-10 border-2 border-emerald-500"> <div class="flex flex-col gap-2"> <div class="p-2 hover:bg-slate-700 rounded-lg transition-all text-emerald-400"> <p class="font-semibold">Новый Заказ #1234</p> <p class="text-sm text-emerald-300">Запрос на бурение скважины - 5км</p> </div> </div> </div> </details> <details class="relative"> <summary class="flex items-center gap-2 cursor-pointer hover:bg-emerald-800 p-2 rounded-lg transition-all text-emerald-400"> <span class="material-symbols-outlined">account_circle</span> <span>Администратор</span> </summary> </details> </div> </header> <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8"> <div class="bg-emerald-900 p-4 sm:p-6 rounded-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 border-2 border-emerald-500"> <div class="flex items-center gap-4"> <span class="material-symbols-outlined text-2xl sm:text-3xl text-emerald-400">engineering</span> <div class="text-emerald-400"> <p class="text-xl sm:text-2xl font-bold">247</p> <p class="text-sm sm:text-base">Активных Подрядчиков</p> </div> </div> </div> <div class="bg-blue-900 p-4 sm:p-6 rounded-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 border-2 border-emerald-500"> <div class="flex items-center gap-4"> <span class="material-symbols-outlined text-2xl sm:text-3xl text-emerald-400">assignment</span> <div class="text-emerald-400"> <p class="text-xl sm:text-2xl font-bold">1,893</p> <p class="text-sm sm:text-base">Выполненных Заказов</p> </div> </div> </div> <div class="bg-emerald-900 p-4 sm:p-6 rounded-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 border-2 border-emerald-500"> <div class="flex items-center gap-4"> <span class="material-symbols-outlined text-2xl sm:text-3xl text-emerald-400">pending</span> <div class="text-emerald-400"> <p class="text-xl sm:text-2xl font-bold">42</p> <p class="text-sm sm:text-base">Ожидающих Заказов</p> </div> </div> </div> <div class="bg-blue-900 p-4 sm:p-6 rounded-xl hover:shadow-2xl transition-all transform hover:-translate-y-1 border-2 border-emerald-500"> <div class="flex items-center gap-4"> <span class="material-symbols-outlined text-2xl sm:text-3xl text-emerald-400">stars</span> <div class="text-emerald-400"> <p class="text-xl sm:text-2xl font-bold">4.8</p> <p class="text-sm sm:text-base">Средний Рейтинг</p> </div> </div> </div> </div> <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6"> <div class="lg:col-span-2 bg-slate-800 rounded-xl border-2 sm:border-4 border-emerald-500 p-4 sm:p-6"> <h2 class="text-lg sm:text-xl font-bold mb-4 text-emerald-400">Последние Заказы</h2> <div class="space-y-4"> <div class="flex items-center justify-between p-2 sm:p-4 hover:bg-slate-700 rounded-lg transition-all"> <div class="flex items-center gap-4"> <span class="material-symbols-outlined text-emerald-400">drill</span> <div class="text-emerald-400"> <p class="font-semibold">Бурение Скважины</p> <p class="text-xs sm:text-sm text-emerald-300">ул. Главная 123, Город</p> </div> </div> <button class="bg-emerald-600 text-white px-3 py-1 sm:px-4 sm:py-2 rounded-lg hover:bg-emerald-700 transition-all transform hover:scale-105 border-2 border-emerald-400 text-sm sm:text-base"> Назначить </button> </div> </div> </div> <div class="bg-slate-800 rounded-xl border-2 sm:border-4 border-emerald-500 p-4 sm:p-6"> <h2 class="text-lg sm:text-xl font-bold mb-4 text-emerald-400">Лучшие Подрядчики</h2> <div class="space-y-4"> <div class="flex items-center justify-between p-2 hover:bg-slate-700 rounded-lg transition-all"> <div class="flex items-center gap-2"> <span class="material-symbols-outlined text-emerald-400">account_circle</span> <p class="font-semibold text-emerald-400 text-sm sm:text-base">Иван Иванов</p> </div> <div class="flex items-center text-emerald-400"> <span class="material-symbols-outlined text-yellow-500">star</span> <span class="text-sm sm:text-base">4.9</span> </div> </div> </div> </div> </div> </div> </div></div>
</template>

<style scoped>
  @import url(https://fonts.googleapis.com/css2?family=Roboto&display=swap);
  
  @import url(https://fonts.googleapis.com/css2?family=Inter&display=swap);
  
  @import url(https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200);
  
  /*! tailwindcss v3.4.11 | MIT License | https://tailwindcss.com*/
  *,
  :after,
  :before {
    border: 0 solid #e5e7eb;
    box-sizing: border-box;
  }
  :after,
  :before {
    --tw-content: "";
  }
  :host,
  html {
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
    font-family:
      Oswald,
      ui-sans-serif,
      system-ui,
      sans-serif,
      Apple Color Emoji,
      Segoe UI Emoji,
      Segoe UI Symbol,
      Noto Color Emoji;
    font-feature-settings: normal;
    font-variation-settings: normal;
    -moz-tab-size: 4;
    tab-size: 4;
    -webkit-tap-highlight-color: transparent;
  }
  body {
    line-height: inherit;
    margin: 0;
  }
  hr {
    border-top-width: 1px;
    color: inherit;
    height: 0;
  }
  abbr:where([title]) {
    text-decoration: underline dotted;
  }
  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    font-size: inherit;
    font-weight: inherit;
  }
  a {
    color: inherit;
    text-decoration: inherit;
  }
  b,
  strong {
    font-weight: bolder;
  }
  code,
  kbd,
  pre,
  samp {
    font-family:
      ui-monospace,
      SFMono-Regular,
      Menlo,
      Monaco,
      Consolas,
      Liberation Mono,
      Courier New,
      monospace;
    font-feature-settings: normal;
    font-size: 1em;
    font-variation-settings: normal;
  }
  small {
    font-size: 80%;
  }
  sub,
  sup {
    font-size: 75%;
    line-height: 0;
    position: relative;
    vertical-align: baseline;
  }
  sub {
    bottom: -0.25em;
  }
  sup {
    top: -0.5em;
  }
  table {
    border-collapse: collapse;
    border-color: inherit;
    text-indent: 0;
  }
  button,
  input,
  optgroup,
  select,
  textarea {
    color: inherit;
    font-family: inherit;
    font-feature-settings: inherit;
    font-size: 100%;
    font-variation-settings: inherit;
    font-weight: inherit;
    letter-spacing: inherit;
    line-height: inherit;
    margin: 0;
    padding: 0;
  }
  button,
  select {
    text-transform: none;
  }
  button,
  input:where([type="button"]),
  input:where([type="reset"]),
  input:where([type="submit"]) {
    -webkit-appearance: button;
    background-color: transparent;
    background-image: none;
  }
  :-moz-focusring {
    outline: auto;
  }
  :-moz-ui-invalid {
    box-shadow: none;
  }
  progress {
    vertical-align: baseline;
  }
  ::-webkit-inner-spin-button,
  ::-webkit-outer-spin-button {
    height: auto;
  }
  [type="search"] {
    -webkit-appearance: textfield;
    outline-offset: -2px;
  }
  ::-webkit-search-decoration {
    -webkit-appearance: none;
  }
  ::-webkit-file-upload-button {
    -webkit-appearance: button;
    font: inherit;
  }
  summary {
    display: list-item;
  }
  blockquote,
  dd,
  dl,
  figure,
  h1,
  h2,
  h3,
  h4,
  h5,
  h6,
  hr,
  p,
  pre {
    margin: 0;
  }
  fieldset {
    margin: 0;
  }
  fieldset,
  legend {
    padding: 0;
  }
  menu,
  ol,
  ul {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  dialog {
    padding: 0;
  }
  textarea {
    resize: vertical;
  }
  input::placeholder,
  textarea::placeholder {
    color: #9ca3af;
    opacity: 1;
  }
  [role="button"],
  button {
    cursor: pointer;
  }
  :disabled {
    cursor: default;
  }
  audio,
  canvas,
  embed,
  iframe,
  img,
  object,
  svg,
  video {
    display: block;
    vertical-align: middle;
  }
  img,
  video {
    height: auto;
    max-width: 100%;
  }
  [hidden] {
    display: none;
  }
  *,
  :after,
  :before {
    --tw-border-spacing-x: 0;
    --tw-border-spacing-y: 0;
    --tw-translate-x: 0;
    --tw-translate-y: 0;
    --tw-rotate: 0;
    --tw-skew-x: 0;
    --tw-skew-y: 0;
    --tw-scale-x: 1;
    --tw-scale-y: 1;
    --tw-pan-x: ;
    --tw-pan-y: ;
    --tw-pinch-zoom: ;
    --tw-scroll-snap-strictness: proximity;
    --tw-gradient-from-position: ;
    --tw-gradient-via-position: ;
    --tw-gradient-to-position: ;
    --tw-ordinal: ;
    --tw-slashed-zero: ;
    --tw-numeric-figure: ;
    --tw-numeric-spacing: ;
    --tw-numeric-fraction: ;
    --tw-ring-inset: ;
    --tw-ring-offset-width: 0px;
    --tw-ring-offset-color: #fff;
    --tw-ring-color: rgba(59, 130, 246, 0.5);
    --tw-ring-offset-shadow: 0 0 #0000;
    --tw-ring-shadow: 0 0 #0000;
    --tw-shadow: 0 0 #0000;
    --tw-shadow-colored: 0 0 #0000;
    --tw-blur: ;
    --tw-brightness: ;
    --tw-contrast: ;
    --tw-grayscale: ;
    --tw-hue-rotate: ;
    --tw-invert: ;
    --tw-saturate: ;
    --tw-sepia: ;
    --tw-drop-shadow: ;
    --tw-backdrop-blur: ;
    --tw-backdrop-brightness: ;
    --tw-backdrop-contrast: ;
    --tw-backdrop-grayscale: ;
    --tw-backdrop-hue-rotate: ;
    --tw-backdrop-invert: ;
    --tw-backdrop-opacity: ;
    --tw-backdrop-saturate: ;
    --tw-backdrop-sepia: ;
    --tw-contain-size: ;
    --tw-contain-layout: ;
    --tw-contain-paint: ;
    --tw-contain-style: ;
  }
  ::backdrop {
    --tw-border-spacing-x: 0;
    --tw-border-spacing-y: 0;
    --tw-translate-x: 0;
    --tw-translate-y: 0;
    --tw-rotate: 0;
    --tw-skew-x: 0;
    --tw-skew-y: 0;
    --tw-scale-x: 1;
    --tw-scale-y: 1;
    --tw-pan-x: ;
    --tw-pan-y: ;
    --tw-pinch-zoom: ;
    --tw-scroll-snap-strictness: proximity;
    --tw-gradient-from-position: ;
    --tw-gradient-via-position: ;
    --tw-gradient-to-position: ;
    --tw-ordinal: ;
    --tw-slashed-zero: ;
    --tw-numeric-figure: ;
    --tw-numeric-spacing: ;
    --tw-numeric-fraction: ;
    --tw-ring-inset: ;
    --tw-ring-offset-width: 0px;
    --tw-ring-offset-color: #fff;
    --tw-ring-color: rgba(59, 130, 246, 0.5);
    --tw-ring-offset-shadow: 0 0 #0000;
    --tw-ring-shadow: 0 0 #0000;
    --tw-shadow: 0 0 #0000;
    --tw-shadow-colored: 0 0 #0000;
    --tw-blur: ;
    --tw-brightness: ;
    --tw-contrast: ;
    --tw-grayscale: ;
    --tw-hue-rotate: ;
    --tw-invert: ;
    --tw-saturate: ;
    --tw-sepia: ;
    --tw-drop-shadow: ;
    --tw-backdrop-blur: ;
    --tw-backdrop-brightness: ;
    --tw-backdrop-contrast: ;
    --tw-backdrop-grayscale: ;
    --tw-backdrop-hue-rotate: ;
    --tw-backdrop-invert: ;
    --tw-backdrop-opacity: ;
    --tw-backdrop-saturate: ;
    --tw-backdrop-sepia: ;
    --tw-contain-size: ;
    --tw-contain-layout: ;
    --tw-contain-paint: ;
    --tw-contain-style: ;
  }
  #webcrumbs .absolute {
    position: absolute;
  }
  #webcrumbs .relative {
    position: relative;
  }
  #webcrumbs .-right-1 {
    right: -4px;
  }
  #webcrumbs .-top-1 {
    top: -4px;
  }
  #webcrumbs .right-0 {
    right: 0;
  }
  #webcrumbs .z-10 {
    z-index: 10;
  }
  #webcrumbs .mb-4 {
    margin-bottom: 16px;
  }
  #webcrumbs .mb-8 {
    margin-bottom: 32px;
  }
  #webcrumbs .mt-2 {
    margin-top: 8px;
  }
  #webcrumbs .flex {
    display: flex;
  }
  #webcrumbs .grid {
    display: grid;
  }
  #webcrumbs .h-5 {
    height: 20px;
  }
  #webcrumbs .min-h-screen {
    min-height: 100vh;
  }
  #webcrumbs .w-5 {
    width: 20px;
  }
  #webcrumbs .w-64 {
    width: 256px;
  }
  #webcrumbs .w-full {
    width: 100%;
  }
  #webcrumbs .max-w-\[1200px\] {
    max-width: 1200px;
  }
  #webcrumbs .transform {
    transform: translate(var(--tw-translate-x), var(--tw-translate-y))
      rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
      scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
  }
  #webcrumbs .cursor-pointer {
    cursor: pointer;
  }
  #webcrumbs .grid-cols-1 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  #webcrumbs .flex-row {
    flex-direction: row;
  }
  #webcrumbs .flex-col {
    flex-direction: column;
  }
  #webcrumbs .items-center {
    align-items: center;
  }
  #webcrumbs .justify-center {
    justify-content: center;
  }
  #webcrumbs .justify-between {
    justify-content: space-between;
  }
  #webcrumbs .gap-2 {
    gap: 8px;
  }
  #webcrumbs .gap-4 {
    gap: 16px;
  }
  #webcrumbs :is(.space-y-4 > :not([hidden]) ~ :not([hidden])) {
    --tw-space-y-reverse: 0;
    margin-bottom: calc(16px * var(--tw-space-y-reverse));
    margin-top: calc(16px * (1 - var(--tw-space-y-reverse)));
  }
  #webcrumbs .rounded-full {
    border-radius: 9999px;
  }
  #webcrumbs .rounded-lg {
    border-radius: 8px;
  }
  #webcrumbs .rounded-xl {
    border-radius: 12px;
  }
  #webcrumbs .border-2 {
    border-width: 2px;
  }
  #webcrumbs .border-emerald-400 {
    --tw-border-opacity: 1;
    border-color: rgb(52 211 153 / var(--tw-border-opacity));
  }
  #webcrumbs .border-emerald-500 {
    --tw-border-opacity: 1;
    border-color: rgb(16 185 129 / var(--tw-border-opacity));
  }
  #webcrumbs .bg-blue-900 {
    --tw-bg-opacity: 1;
    background-color: rgb(30 58 138 / var(--tw-bg-opacity));
  }
  #webcrumbs .bg-emerald-600 {
    --tw-bg-opacity: 1;
    background-color: rgb(5 150 105 / var(--tw-bg-opacity));
  }
  #webcrumbs .bg-emerald-900 {
    --tw-bg-opacity: 1;
    background-color: rgb(6 78 59 / var(--tw-bg-opacity));
  }
  #webcrumbs .bg-red-500 {
    --tw-bg-opacity: 1;
    background-color: rgb(239 68 68 / var(--tw-bg-opacity));
  }
  #webcrumbs .bg-slate-800 {
    --tw-bg-opacity: 1;
    background-color: rgb(30 41 59 / var(--tw-bg-opacity));
  }
  #webcrumbs .bg-slate-900 {
    --tw-bg-opacity: 1;
    background-color: rgb(15 23 42 / var(--tw-bg-opacity));
  }
  #webcrumbs .bg-gradient-to-br {
    background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
  }
  #webcrumbs .from-emerald-800 {
    --tw-gradient-from: #065f46 var(--tw-gradient-from-position);
    --tw-gradient-to: rgba(6, 95, 70, 0) var(--tw-gradient-to-position);
    --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
  }
  #webcrumbs .to-blue-900 {
    --tw-gradient-to: #1e3a8a var(--tw-gradient-to-position);
  }
  #webcrumbs .p-2 {
    padding: 8px;
  }
  #webcrumbs .p-4 {
    padding: 16px;
  }
  #webcrumbs .px-3 {
    padding-left: 12px;
    padding-right: 12px;
  }
  #webcrumbs .py-1 {
    padding-bottom: 4px;
    padding-top: 4px;
  }
  #webcrumbs .text-2xl {
    font-size: 27px;
    line-height: 35.1px;
  }
  #webcrumbs .text-3xl {
    font-size: 33.75px;
    line-height: 40.5px;
  }
  #webcrumbs .text-lg {
    font-size: 20.25px;
    line-height: 30.375px;
  }
  #webcrumbs .text-sm {
    font-size: 15.75px;
    line-height: 23.625px;
  }
  #webcrumbs .text-xl {
    font-size: 22.5px;
    line-height: 31.499999999999996px;
  }
  #webcrumbs .text-xs {
    font-size: 13.5px;
    line-height: 21.6px;
  }
  #webcrumbs .font-bold {
    font-weight: 700;
  }
  #webcrumbs .font-semibold {
    font-weight: 600;
  }
  #webcrumbs .text-emerald-300 {
    --tw-text-opacity: 1;
    color: rgb(110 231 183 / var(--tw-text-opacity));
  }
  #webcrumbs .text-emerald-400 {
    --tw-text-opacity: 1;
    color: rgb(52 211 153 / var(--tw-text-opacity));
  }
  #webcrumbs .text-white {
    --tw-text-opacity: 1;
    color: rgb(255 255 255 / var(--tw-text-opacity));
  }
  #webcrumbs .text-yellow-500 {
    --tw-text-opacity: 1;
    color: rgb(234 179 8 / var(--tw-text-opacity));
  }
  #webcrumbs .shadow-2xl {
    --tw-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    --tw-shadow-colored: 0 25px 50px -12px var(--tw-shadow-color);
    box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000),
      var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
  }
  #webcrumbs .transition-all {
    transition-duration: 0.15s;
    transition-property: all;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  }
  #webcrumbs {
    font-family: Inter !important;
    font-size: 18px !important;
  }
  #webcrumbs .hover\:-translate-y-1:hover {
    --tw-translate-y: -4px;
  }
  #webcrumbs .hover\:-translate-y-1:hover,
  #webcrumbs .hover\:scale-105:hover {
    transform: translate(var(--tw-translate-x), var(--tw-translate-y))
      rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
      scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
  }
  #webcrumbs .hover\:scale-105:hover {
    --tw-scale-x: 1.05;
    --tw-scale-y: 1.05;
  }
  #webcrumbs .hover\:bg-emerald-700:hover {
    --tw-bg-opacity: 1;
    background-color: rgb(4 120 87 / var(--tw-bg-opacity));
  }
  #webcrumbs .hover\:bg-emerald-800:hover {
    --tw-bg-opacity: 1;
    background-color: rgb(6 95 70 / var(--tw-bg-opacity));
  }
  #webcrumbs .hover\:bg-slate-700:hover {
    --tw-bg-opacity: 1;
    background-color: rgb(51 65 85 / var(--tw-bg-opacity));
  }
  #webcrumbs .hover\:shadow-2xl:hover {
    --tw-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    --tw-shadow-colored: 0 25px 50px -12px var(--tw-shadow-color);
    box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000),
      var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
  }
  @media (min-width: 640px) {
    #webcrumbs .sm\:grid-cols-2 {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    #webcrumbs .sm\:flex-row {
      flex-direction: row;
    }
    #webcrumbs .sm\:gap-6 {
      gap: 24px;
    }
    #webcrumbs .sm\:border-4 {
      border-width: 4px;
    }
    #webcrumbs .sm\:p-4 {
      padding: 16px;
    }
    #webcrumbs .sm\:p-6 {
      padding: 24px;
    }
    #webcrumbs .sm\:p-8 {
      padding: 32px;
    }
    #webcrumbs .sm\:px-4 {
      padding-left: 16px;
      padding-right: 16px;
    }
    #webcrumbs .sm\:py-2 {
      padding-bottom: 8px;
      padding-top: 8px;
    }
    #webcrumbs .sm\:text-2xl {
      font-size: 27px;
      line-height: 35.1px;
    }
    #webcrumbs .sm\:text-3xl {
      font-size: 33.75px;
      line-height: 40.5px;
    }
    #webcrumbs .sm\:text-4xl {
      font-size: 40.5px;
      line-height: 46.574999999999996px;
    }
    #webcrumbs .sm\:text-base {
      font-size: 18px;
      line-height: 28.8px;
    }
    #webcrumbs .sm\:text-sm {
      font-size: 15.75px;
      line-height: 23.625px;
    }
    #webcrumbs .sm\:text-xl {
      font-size: 22.5px;
      line-height: 31.499999999999996px;
    }
  }
  @media (min-width: 1024px) {
    #webcrumbs .lg\:col-span-2 {
      grid-column: span 2 / span 2;
    }
    #webcrumbs .lg\:grid-cols-3 {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    #webcrumbs .lg\:grid-cols-4 {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }
  
</style>