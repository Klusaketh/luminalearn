function isPalindrome(s) {
  const alnum = (ch) => /[\p{L}\p{N}]/u.test(ch);
  let i = 0, j = s.length - 1;
  while (i < j) {
    if (!alnum(s[i])) i++;
    else if (!alnum(s[j])) j--;
    else if (s[i].toLowerCase() !== s[j].toLowerCase()) return false;
    else { i++; j--; }
  }
  return true;
}
