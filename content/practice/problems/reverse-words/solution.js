function reverseWords(s) {
  return s.split(/\s+/).filter(Boolean).reverse().join(" ");
}
