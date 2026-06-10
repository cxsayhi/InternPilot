<template>
  <div class="analysis-layout">
    <form class="panel input-panel" @submit.prevent="submitAnalysis">
      <div class="field-row">
        <label>
          Company
          <input v-model="form.company" type="text" placeholder="Optional" />
        </label>
        <label>
          Role
          <input v-model="form.role" type="text" placeholder="Java Backend Intern" />
        </label>
      </div>

      <label>
        Resume
        <textarea
          v-model="form.resumeText"
          rows="11"
          placeholder="Paste your resume or project bullets here"
        />
      </label>

      <label>
        Job Description
        <textarea
          v-model="form.jobText"
          rows="11"
          placeholder="Paste internship JD here"
        />
      </label>

      <button class="primary-button" type="submit" :disabled="loading">
        {{ loading ? 'Analyzing...' : 'Analyze application' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
    </form>

    <section class="panel result-panel" aria-live="polite">
      <div v-if="!result" class="empty-state">
        Paste a resume and job description to generate the first application analysis.
      </div>

      <template v-else>
        <div class="score-block">
          <span class="score">{{ result.matchScore }}</span>
          <span class="score-label">match score</span>
        </div>

        <div class="result-grid">
          <ResultList title="Strong matches" :items="result.strongMatches" />
          <ResultList title="Weak matches" :items="result.weakMatches" />
          <ResultList title="Missing skills" :items="result.missingSkills" />
        </div>

        <section class="section-block">
          <h2>Resume bullet suggestions</h2>
          <article
            v-for="suggestion in result.rewriteSuggestions"
            :key="suggestion.id"
            class="suggestion"
          >
            <p class="muted">Original</p>
            <p>{{ suggestion.originalBullet }}</p>
            <p class="muted">Suggested</p>
            <p>{{ suggestion.suggestedBullet }}</p>
            <span class="status">{{ suggestion.status }}</span>
          </article>
        </section>

        <section class="section-block">
          <h2>7-day improvement plan</h2>
          <ol class="plan-list">
            <li v-for="item in result.learningPlan" :key="item.day">
              <strong>Day {{ item.day }}: {{ item.title }}</strong>
              <span>{{ item.deliverable }}</span>
            </li>
          </ol>
        </section>
      </template>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { analyzeApplication } from '../services/api'
import ResultList from './ResultList.vue'

const form = reactive({
  company: '',
  role: '',
  resumeText: '',
  jobText: ''
})

const loading = ref(false)
const error = ref('')
const result = ref(null)

async function submitAnalysis() {
  error.value = ''
  result.value = null
  loading.value = true

  try {
    result.value = await analyzeApplication({
      company: form.company || null,
      role: form.role || null,
      resumeText: form.resumeText,
      jobText: form.jobText
    })
  } catch (err) {
    error.value = err.message || 'Analysis failed.'
  } finally {
    loading.value = false
  }
}
</script>

