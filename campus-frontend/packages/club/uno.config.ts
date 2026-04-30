import { defineConfig, presetUno } from 'unocss'

export default defineConfig({
  presets: [presetUno()],
  shortcuts: {
    'btn': 'px-4 py-2 rounded-lg transition-colors duration-200',
    'btn-primary': 'btn bg-blue-500 text-white hover:bg-blue-600',
    'card': 'bg-white rounded-xl shadow-md p-6',
  },
})
