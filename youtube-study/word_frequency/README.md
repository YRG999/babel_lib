# README

To use `word_freq.py`:

1. Run `python word_freq.py <path/to/file.txt>`.
2. Optionally pass `--min-count N` to change the threshold (default: 10).
3. The program prints results to the console and saves a `<filename>_freq.txt` file in the same directory as the input.

## Example

```zsh
python word_freq.py transcript.txt
python word_freq.py transcript.txt --min-count 5
```

## Output columns

Each result line shows the count followed by the word, sorted by frequency descending:

```text
Words mentioned 10+ times (excluding common words):

   93  jill
   75  jack
   ...

Total unique qualifying words: 140
```

## Stopwords

Common English words are excluded: articles, conjunctions, prepositions, pronouns, auxiliary verbs, filler words, and contractions. The goal is to surface names, places, and meaningful topic words.

## Notes

- Input file must be UTF-8 encoded.
- Purely numeric tokens and single-character tokens are skipped.
- Contractions (e.g. `it's`, `don't`) are included in the stopword list and filtered out.
