import difflib, os, glob
def best_match_against_corpus(text:str, corpus_dir:str="vault/corpus") -> dict:
    os.makedirs(corpus_dir, exist_ok=True)
    files = glob.glob(os.path.join(corpus_dir, "*.txt"))
    best = max(files, key=lambda f: difflib.SequenceMatcher(None, text, open(f).read()).ratio(), default="")
    return {"file": best, "score": difflib.SequenceMatcher(None, text, open(best).read()).ratio() if best else 0}
