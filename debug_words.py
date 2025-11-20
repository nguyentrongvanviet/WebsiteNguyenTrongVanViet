import os
import sys

# Manual word analysis
query = "What's the distance from UIT to Hanoi?"
words = query.split()

print(f"Query: {query}")
print(f"Words: {words}")
print()

for i, word in enumerate(words):
    clean_word = word.strip('.,;:?!')
    print(f"{i}: '{word}' -> '{clean_word}'")
    print(f"   Length: {len(clean_word)}")
    print(f"   First char upper: {clean_word[0].isupper() if clean_word else False}")
    print(f"   Is 'UIT': {clean_word.lower() == 'uit'}")
    print(f"   Is 'Hanoi': {clean_word.lower() == 'hanoi'}")
    print(f"   In exclude list: {clean_word.lower() in ['what', 'how', 'can', 'the', 'distance', 'from', 'to', 'calculating']}")
    print()