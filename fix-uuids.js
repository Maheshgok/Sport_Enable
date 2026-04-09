import fs from 'fs';

const filePath = 'database/schema/05_sample_data.sql';
let content = fs.readFileSync(filePath, 'utf8');

// Find all UUIDs and replace invalid hex characters
// Valid hex: 0-9, a-f
// Replace: g-z with valid hex digits
const replacements = {
  'g': '1', 'h': '2', 'i': '3', 'j': '4', 'k': '5', 'l': '6', 'm': '7', 'n': '8', 
  'o': '9', 'p': 'a', 'q': 'b', 'r': 'c', 's': 'd', 't': 'e', 'u': 'f', 'v': '0',
  'w': '1', 'x': '2', 'y': '3', 'z': '4'
};

// Replace invalid characters in UUID patterns
content = content.replace(/['"]([0-9a-z]{8})-([0-9a-z]{4})-([0-9a-z]{4})-([0-9a-z]{4})-([0-9a-z]{12})['"]/gi, (match, p1, p2, p3, p4, p5) => {
  const quote = match[0];
  
  const fix = (str) => str.toLowerCase().split('').map(c => {
    if (c >= 'g' && c <= 'z') return replacements[c];
    return c;
  }).join('');
  
  return `${quote}${fix(p1)}-${fix(p2)}-${fix(p3)}-${fix(p4)}-${fix(p5)}${quote}`;
});

fs.writeFileSync(filePath, content);
console.log('✅ Fixed all invalid UUIDs');
