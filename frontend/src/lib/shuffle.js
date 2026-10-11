export function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// Shuffle a question's options, keeping correct_index pointing at the right answer
export function shuffleOptions(q) {
  const idx = shuffle(q.options.map((_, i) => i))
  return {
    ...q,
    options: idx.map(i => q.options[i]),
    correct_index: idx.indexOf(q.correct_index),
  }
}
