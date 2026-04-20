<template>
  <label class="field" :class="{ 'field--error': !!error }">
    <span v-if="label" class="field__label">{{ label }}</span>
    <input
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      class="field__input co-focus"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <span v-if="error" class="field__error">{{ error }}</span>
    <span v-else-if="hint" class="field__hint">{{ hint }}</span>
  </label>
</template>

<script setup>
defineProps({
  modelValue: [String, Number],
  label: String,
  placeholder: String,
  hint: String,
  error: String,
  type: { type: String, default: 'text' },
  disabled: Boolean,
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.field { display: flex; flex-direction: column; gap: 6px; }
.field__label { font-size: 11px; letter-spacing: 0.06em; color: var(--co-text-dim); text-transform: uppercase; }
.field__input {
  padding: 10px 12px;
  font-family: var(--co-font-mono);
  font-size: 13px;
  color: var(--co-text);
  background: var(--co-surface);
  border: 1px solid var(--co-border-2);
  border-radius: var(--co-radius);
  outline: none;
}
.field__input:focus { border-color: var(--co-accent); }
.field__input::placeholder { color: var(--co-text-mute); }
.field__hint { font-size: 11px; color: var(--co-text-mute); }
.field__error { font-size: 11px; color: var(--co-error); }
.field--error .field__input { border-color: var(--co-error); }
</style>
