<template>
  <section class="mini-section">
    <h2>{{ title }}</h2>
    <ul v-if="items && items.length">
      <li v-for="item in items" :key="item.skill">
        <span>{{ item.skill }}</span>
      </li>
    </ul>
    <p v-else class="muted">None yet</p>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  items: {
    type: Array,
    default: () => []
  }
})
</script>

