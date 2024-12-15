/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    'content/**.md',
    'src/utahwaterpoloassociation/templates/**.jinja2',
    'output/*/**.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}

