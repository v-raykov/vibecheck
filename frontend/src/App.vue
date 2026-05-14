<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <header v-if="$route.name !== 'auth'">
      <nav>
        <h1>VibeCheck</h1>
      </nav>
    </header>

    <RouterView />
  </div>
</template>

<style>
#app {
  font-family: sans-serif;
  color: var(--text);
}
</style>