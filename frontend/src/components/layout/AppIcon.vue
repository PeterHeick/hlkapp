<script setup lang="ts">
defineProps<{ name: string; size?: number; stroke?: number }>()
</script>

<template>
  <!-- Inline SVG ikoner — lucide-stil hairline -->
  <svg
    :width="size ?? 18"
    :height="size ?? 18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="stroke ?? 1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <!-- Spark / brand -->
    <template v-if="name === 'Spark'">
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
    </template>
    <!-- Globe / SEO -->
    <template v-else-if="name === 'Globe'">
      <circle cx="12" cy="12" r="10"/>
      <path d="M2 12h20"/>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
    </template>
    <!-- Settings / gear -->
    <template v-else-if="name === 'Settings'">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v0a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
    </template>
    <!-- Dashboard -->
    <template v-else-if="name === 'Dashboard'">
      <rect x="3" y="3" width="7" height="9"/>
      <rect x="14" y="3" width="7" height="5"/>
      <rect x="14" y="12" width="7" height="9"/>
      <rect x="3" y="16" width="7" height="5"/>
    </template>
    <!-- Calendar -->
    <template v-else-if="name === 'Calendar'">
      <rect x="3" y="4" width="18" height="18" rx="2"/>
      <path d="M16 2v4M8 2v4M3 10h18"/>
    </template>
    <!-- Chart -->
    <template v-else-if="name === 'Chart'">
      <path d="M3 3v18h18"/>
      <path d="M7 14l3-3 3 3 5-6"/>
    </template>
    <!-- Scissors -->
    <template v-else-if="name === 'Scissors'">
      <circle cx="6" cy="6" r="3"/>
      <circle cx="6" cy="18" r="3"/>
      <path d="M20 4L8.12 15.88M14.47 14.48L20 20M8.12 8.12L12 12"/>
    </template>
    <!-- Network / graf -->
    <template v-else-if="name === 'Network'">
      <circle cx="12" cy="5" r="2"/>
      <circle cx="5" cy="19" r="2"/>
      <circle cx="19" cy="19" r="2"/>
      <path d="M12 7v4M12 11l-5.5 6M12 11l5.5 6"/>
    </template>
    <!-- Sitemap / hierarki -->
    <template v-else-if="name === 'Sitemap'">
      <rect x="9" y="2" width="6" height="5" rx="1"/>
      <rect x="2" y="17" width="6" height="5" rx="1"/>
      <rect x="16" y="17" width="6" height="5" rx="1"/>
      <path d="M12 7v4M5 17v-2a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v2M12 11v3"/>
    </template>
    <!-- Save -->
    <template v-else-if="name === 'Save'">
      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
      <polyline points="17 21 17 13 7 13 7 21"/>
      <polyline points="7 3 7 8 15 8"/>
    </template>
    <!-- Lock -->
    <template v-else-if="name === 'Lock'">
      <rect x="3" y="11" width="18" height="11" rx="2"/>
      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
    </template>
    <!-- Play -->
    <template v-else-if="name === 'Play'">
      <polygon points="6 4 20 12 6 20 6 4"/>
    </template>
    <!-- Stop -->
    <template v-else-if="name === 'StopSquare'">
      <rect x="5" y="5" width="14" height="14" rx="1"/>
    </template>
    <!-- Check circle -->
    <template v-else-if="name === 'Check'">
      <circle cx="12" cy="12" r="10"/>
      <path d="M9 12l2 2 4-4"/>
    </template>
    <!-- Alert triangle -->
    <template v-else-if="name === 'AlertTri'">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <path d="M12 9v4M12 17h.01"/>
    </template>
    <!-- X Circle -->
    <template v-else-if="name === 'XCircle'">
      <circle cx="12" cy="12" r="10"/>
      <path d="M15 9l-6 6M9 9l6 6"/>
    </template>
    <!-- Arrow up (redirect) -->
    <template v-else-if="name === 'ArrowUp'">
      <path d="M12 19V5M5 12l7-7 7 7"/>
    </template>
    <!-- Arrow down (deep) -->
    <template v-else-if="name === 'ArrowDown'">
      <path d="M12 5v14M19 12l-7 7-7-7"/>
    </template>
    <!-- ChevronDown -->
    <template v-else-if="name === 'ChevronDown'">
      <polyline points="6 9 12 15 18 9"/>
    </template>
    <!-- Search -->
    <template v-else-if="name === 'Search'">
      <circle cx="11" cy="11" r="7"/>
      <path d="M21 21l-4.3-4.3"/>
    </template>
    <!-- List / prisliste -->
    <template v-else-if="name === 'List'">
      <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>
    </template>
  </svg>
</template>
