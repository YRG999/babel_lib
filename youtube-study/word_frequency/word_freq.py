import argparse
import re
import sys
from collections import Counter
from pathlib import Path

STOPWORDS = {
    # articles
    "a", "an", "the",
    # conjunctions
    "and", "but", "or", "nor", "for", "yet", "so", "either", "neither",
    # prepositions
    "in", "on", "at", "to", "of", "with", "by", "from", "into", "through",
    "during", "before", "after", "above", "below", "between", "about",
    "against", "along", "around", "without", "within", "upon", "over",
    "under", "per", "via", "re", "off", "out", "up", "down", "as",
    # pronouns
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
    "us", "them", "my", "your", "his", "its", "our", "their", "this",
    "that", "these", "those", "who", "whom", "whose", "which", "what",
    "myself", "yourself", "himself", "herself", "itself", "ourselves",
    "themselves", "anything", "something", "nothing", "everything",
    "anyone", "someone", "everyone", "nobody", "somebody", "everybody",
    # auxiliary verbs
    "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "shall", "can", "must", "need", "dare", "used",
    "ought", "going", "gonna", "wanna", "gotta",
    # common verbs
    "get", "gets", "got", "gotten", "go", "goes", "went", "gone",
    "come", "comes", "came", "know", "knows", "knew", "known",
    "think", "thinks", "thought", "say", "says", "said", "like",
    "likes", "liked", "just", "make", "makes", "made", "take", "takes",
    "took", "taken", "see", "sees", "saw", "seen", "want", "wants",
    "wanted", "tell", "tells", "told", "feel", "feels", "felt",
    "let", "lets", "put", "puts", "mean", "means", "meant",
    "keep", "keeps", "kept", "start", "starts", "started",
    "seem", "seems", "seemed", "show", "shows", "showed", "shown",
    "hear", "hears", "heard", "play", "plays", "played",
    "run", "runs", "ran", "move", "moves", "moved", "live", "lives",
    "lived", "believe", "believes", "believed", "hold", "holds", "held",
    "bring", "brings", "brought", "happen", "happens", "happened",
    "write", "writes", "wrote", "written", "provide", "provides",
    "sit", "sits", "sat", "stand", "stands", "stood", "lose", "loses",
    "lost", "pay", "pays", "paid", "meet", "meets", "met",
    "include", "includes", "included", "continue", "continues", "continued",
    "set", "sets", "learn", "learns", "learned", "change", "changes",
    "changed", "lead", "leads", "led", "understand", "understands",
    "understood", "watch", "watches", "watched", "follow", "follows",
    "followed", "stop", "stops", "stopped", "create", "creates",
    "created", "speak", "speaks", "spoke", "spoken", "read", "reads",
    "spend", "spends", "spent", "grow", "grows", "grew", "grown",
    "open", "opens", "opened", "walk", "walks", "walked", "win",
    "wins", "won", "offer", "offers", "offered", "remember", "remembers",
    "remembered", "love", "loves", "loved", "consider", "considers",
    "considered", "appear", "appears", "appeared", "buy", "buys",
    "bought", "wait", "waits", "waited", "serve", "serves", "served",
    "die", "dies", "died", "send", "sends", "sent", "expect", "expects",
    "expected", "build", "builds", "built", "stay", "stays", "stayed",
    "fall", "falls", "fell", "fallen", "cut", "cuts", "reach", "reaches",
    "reached", "kill", "kills", "killed", "remain", "remains", "remained",
    "suggest", "suggests", "suggested", "raise", "raises", "raised",
    "pass", "passes", "passed", "sell", "sells", "sold", "require",
    "requires", "required", "report", "reports", "reported", "decide",
    "decides", "decided", "pull", "pulls", "pulled", "break", "breaks",
    "broke", "broken", "wish", "wishes", "wished", "manage", "manages",
    "managed", "turn", "turns", "turned", "help", "helps", "helped",
    "give", "gives", "gave", "given", "look", "looks", "looked",
    "use", "uses", "used", "work", "works", "worked", "try", "tries",
    "tried", "ask", "asks", "asked", "call", "calls", "called",
    "talk", "talks", "talked", "end", "ends", "ended",
    # common nouns/fillers that aren't meaningful signal
    "thing", "things", "stuff", "way", "ways", "time", "times",
    "year", "years", "day", "days", "week", "weeks", "month", "months",
    "number", "numbers", "part", "parts", "place", "places",
    "hand", "hands", "word", "words", "point", "points",
    "fact", "facts", "case", "cases", "side", "sides", "kind", "kinds",
    "lot", "lots", "bit", "bits", "sort", "sorts", "type", "types",
    "man", "men", "woman", "women", "person", "people", "guy", "guys",
    "kid", "kids", "boy", "boys", "girl", "girls",
    # adverbs / discourse markers
    "not", "no", "yes", "back", "then", "now", "here", "there",
    "when", "where", "how", "why", "well", "still", "even", "also",
    "too", "very", "much", "more", "most", "less", "least", "some",
    "any", "all", "each", "both", "few", "only", "same", "than", "such",
    "next", "last", "never", "always", "often", "again", "since",
    "while", "though", "although", "if", "unless", "because",
    "however", "therefore", "thus", "hence", "moreover", "furthermore",
    "otherwise", "instead", "already", "really", "quite", "rather",
    "almost", "enough", "else", "ever", "maybe", "perhaps", "whether",
    "once", "twice", "another", "other", "many", "several", "different",
    "every", "second", "first", "third", "fourth", "fifth", "half", "whole",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "full", "sure", "able", "own", "right", "left", "little", "big", "early",
    "late", "true", "false", "long", "short", "hard", "easy", "free",
    "clear", "close", "deep", "real", "likely", "possible", "available",
    "local", "recent", "best", "better", "worse", "worst", "great",
    "good", "bad", "okay", "fine", "various", "certain",
    "whatever", "whenever", "wherever", "whichever", "whoever",
    "actually", "basically", "literally", "totally", "honestly",
    "definitely", "probably", "obviously", "exactly", "especially",
    "pretty", "simply", "quickly", "easily", "already", "finally",
    "recently", "usually", "actually", "certainly", "generally",
    "seriously", "clearly", "nearly", "directly", "specifically",
    "mainly", "mostly", "partly", "slightly", "completely", "entirely",
    "absolutely", "relatively", "fairly", "rather", "quite", "extremely",
    "highly", "super", "yeah", "yep", "nope", "okay", "ok", "like",
    "uh", "um", "ah", "oh", "hmm", "hey", "hi", "hello", "bye",
    "thank", "thanks", "please", "welcome", "sorry", "excuse",
    # contractions (split into components above, but whole forms appear in transcripts)
    "i'm", "i'll", "i've", "i'd",
    "you're", "you'll", "you've", "you'd",
    "he's", "he'll", "he'd",
    "she's", "she'll", "she'd",
    "it's", "it'll", "it'd",
    "we're", "we'll", "we've", "we'd",
    "they're", "they'll", "they've", "they'd",
    "that's", "that'll", "that'd",
    "there's", "there'll", "there'd",
    "here's", "what's", "who's", "how's", "where's", "when's", "why's",
    "let's", "ain't",
    "don't", "doesn't", "didn't", "won't", "wouldn't", "can't",
    "couldn't", "shouldn't", "isn't", "aren't", "wasn't", "weren't",
    "haven't", "hasn't", "hadn't", "mustn't", "needn't",
}


def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9'\-\s]", " ", text)
    tokens = []
    for tok in text.split():
        tok = tok.strip("'-")
        if len(tok) < 2:
            continue
        if tok.isdigit():
            continue
        tokens.append(tok)
    return tokens


def analyze(filepath, min_count):
    path = Path(filepath)
    if not path.exists():
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8", errors="replace")
    tokens = tokenize(text)
    counts = Counter(tok for tok in tokens if tok not in STOPWORDS)
    qualifying = [(word, count) for word, count in counts.most_common() if count >= min_count]

    lines = [f"Words mentioned {min_count}+ times (excluding common words):\n"]
    if qualifying:
        width = len(str(qualifying[0][1]))
        for word, count in qualifying:
            lines.append(f"  {count:>{width}}  {word}")
    else:
        lines.append("  (none found)")
    lines.append(f"\nTotal unique qualifying words: {len(qualifying)}")

    output = "\n".join(lines)
    print(output)

    out_path = path.parent / (path.stem + "_freq.txt")
    out_path.write_text(output + "\n", encoding="utf-8")
    print(f"\nSaved to: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Count significant word frequencies in a text file.")
    parser.add_argument("file", help="Path to the input text file")
    parser.add_argument("--min-count", type=int, default=10, metavar="N",
                        help="Minimum number of occurrences to include (default: 10)")
    args = parser.parse_args()
    analyze(args.file, args.min_count)


if __name__ == "__main__":
    main()
