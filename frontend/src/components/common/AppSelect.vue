<template>
  <label class="field">
    <span v-if="label" class="field__label">{{ label }}</span>
    <select
      :value="modelValue"
      :disabled="disabled"
      class="field__select co-focus"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option v-for="opt in normalizedOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
    </select>
  </label>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  modelValue: [String, Number],
  label: String,
  placeholder: String,
  options: { type: Array, default: () => [] },
  disabled: Boolean,
})
defineEmits(['update:modelValue'])
const normalizedOptions = computed(() =>
  props.options.map((o) => (typeof o === 'string' ? { value: o, label: o } : o))
)
</script>

<style scoped>
.field { display: flex; flex-direction: column; gap: 6px; }
.field__label { font-size: 11px; letter-spacing: 0.06em; color: var(--co-text-dim); text-transform: uppercase; }
.field__select {
  padding: 10px 12px;
  font-family: var(--co-font-mono);
  font-size: 13px;
  color: var(--co-text);
  background: var(--co-surface);
  border: 1px solid var(--co-border-2);
  border-radius: var(--co-radius);
}
.field__select:focus { border-color: var(--co-accent); outline: none; }
</style>
