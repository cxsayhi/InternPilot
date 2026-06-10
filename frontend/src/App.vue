<template>
  <main class="app-shell">
    <section class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">InternPilot</p>
          <h1>Internship Application Analyzer</h1>
        </div>
        <span class="chain">Frontend -> Spring Boot -> Agent Service</span>
      </header>

      <ApplicationAnalyzer />
    </section>
  </main>
</template>

<script setup>
import ApplicationAnalyzer from './components/ApplicationAnalyzer.vue'
</script>

