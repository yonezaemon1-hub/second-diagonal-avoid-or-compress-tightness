#!/usr/bin/env python3
"""
Independent verifier for the second-diagonal avoid-or-compress construction.

Parameters:
    r = |A| >= 1
    L = n - |A| >= 3
    n = r + L
    S = A union {B0, B1}
Hence |S|-|A| = 2 and the Lemma-2 upper bound is n-|A| = L.

The verifier independently checks:
  1. shortest avoid-or-compress distance from S relative to A is exactly L,
  2. strong connectivity,
  3. an explicit reset word maps all Q to a singleton.

No external packages required.
"""

from collections import deque
import argparse
import json


def construct(r: int, L: int):
    if r < 1 or L < 3:
        raise ValueError("Require r>=1 and L>=3.")
    if L % 2 == 0 and L < 4:
        raise ValueError("Even construction requires L>=4.")

    # State encoding:
    # A_i = i, i=0,...,r-1
    # B_j = r+j, j=0,...,L-1
    n = r + L
    a = [None] * n
    b = [None] * n

    # b fixes A and cycles B.
    for i in range(r):
        b[i] = i
    for j in range(L):
        b[r + j] = r + ((j + 1) % L)

    # a moves through A and then enters B0.
    for i in range(r):
        a[i] = i + 1 if i < r - 1 else r

    if L % 2 == 1:
        # Odd L:
        # even B_j -> A0
        # odd  B_j -> B1
        for j in range(L):
            a[r + j] = 0 if j % 2 == 0 else r + 1
    else:
        # Even L:
        # even B_j -> A0
        # ordinary odd B_j -> B1
        # special B_{L-1} -> B2
        for j in range(L):
            if j % 2 == 0:
                a[r + j] = 0
            elif j == L - 1:
                a[r + j] = r + 2
            else:
                a[r + j] = r + 1

    return a, b


def apply_subset(X, trans):
    return frozenset(trans[x] for x in X)


def apply_word(X, a, b, word):
    for ch in word:
        X = apply_subset(X, a if ch == "a" else b)
    return X


def shortest_avoid_or_compress(r: int, L: int):
    a, b = construct(r, L)
    A = frozenset(range(r))
    S = frozenset(list(range(r)) + [r, r + 1])

    q = deque([(S, "")])
    seen = {S}

    while q:
        X, w = q.popleft()

        if w and ((not A.issubset(X)) or len(X) < len(S)):
            return len(w), w, X

        for ch, trans in (("a", a), ("b", b)):
            Y = apply_subset(X, trans)
            if Y not in seen:
                seen.add(Y)
                q.append((Y, w + ch))

    raise RuntimeError("No avoid-or-compress word found.")


def strongly_connected(a, b):
    n = len(a)
    for s in range(n):
        seen = {s}
        q = deque([s])
        while q:
            x = q.popleft()
            for trans in (a, b):
                y = trans[x]
                if y not in seen:
                    seen.add(y)
                    q.append(y)
        if len(seen) != n:
            return False
    return True


def core_entry_word(r: int, L: int):
    if L % 2 == 1:
        return "a" + "b" * (L - 1) + "a"
    return "aa" + "b" * (L - 2) + "aa"


def explicit_reset_word(r: int, L: int):
    """
    Map Q into C=A union {B0}, then synchronize C.

    On C, alpha=a is an (r+1)-cycle.

    Define u:
      odd L:  u = b a b^(L-1) a
      even L: u = b^(L-1) a^2

    gamma = u alpha^(m-2), m=r+1.
    On C, gamma fixes every core state except the last one, which is
    mapped to its predecessor.

    Conjugating gamma by powers of alpha gives all adjacent merges.
    """
    m = r + 1

    if L % 2 == 1:
        w0 = "a" + "b" * (L - 1) + "a"
        u = "b" + "a" + "b" * (L - 1) + "a"
    else:
        w0 = "aa" + "b" * (L - 2) + "aa"
        u = "b" * (L - 1) + "aa"

    gamma = u + "a" * (m - 2)

    merges = []
    for j in range(m - 1):
        # alpha^j gamma alpha^{-j}; alpha^{-j}=alpha^(m-j) on C.
        left = "a" * j
        right = "" if j == 0 else "a" * (m - j)
        merges.append(left + gamma + right)

    return w0 + "".join(merges)


def verify_one(r: int, L: int):
    a, b = construct(r, L)
    n = r + L
    A = frozenset(range(r))
    S = frozenset(list(range(r)) + [r, r + 1])
    Q = frozenset(range(n))
    C = frozenset(list(range(r)) + [r])

    d, shortest_word, terminal = shortest_avoid_or_compress(r, L)

    if L % 2 == 1:
        claimed = "b" * (L - 1) + "a"
    else:
        claimed = "b" * (L - 2) + "aa"

    claimed_terminal = apply_word(S, a, b, claimed)
    claimed_success = ((not A.issubset(claimed_terminal))
                       or len(claimed_terminal) < len(S))

    w0 = core_entry_word(r, L)
    core_image = apply_word(Q, a, b, w0)

    reset = explicit_reset_word(r, L)
    reset_image = apply_word(Q, a, b, reset)

    return {
        "r": r,
        "L": L,
        "n": n,
        "S_size": len(S),
        "A_size": len(A),
        "shortest_distance": d,
        "shortest_word": shortest_word,
        "claimed_word": claimed,
        "claimed_word_length": len(claimed),
        "claimed_word_succeeds": claimed_success,
        "strongly_connected": strongly_connected(a, b),
        "core_entry_word_length": len(w0),
        "core_entry_image_is_subset_of_core": core_image.issubset(C),
        "reset_word_length": len(reset),
        "reset_image_size": len(reset_image),
        "PASS": (
            d == L
            and len(claimed) == L
            and claimed_success
            and strongly_connected(a, b)
            and core_image.issubset(C)
            and len(reset_image) == 1
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r-max", type=int, default=30)
    ap.add_argument("--L-max", type=int, default=40)
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args()

    rows = []
    for r in range(1, args.r_max + 1):
        for L in range(3, args.L_max + 1):
            rows.append(verify_one(r, L))

    failures = [x for x in rows if not x["PASS"]]
    summary = {
        "r_range": [1, args.r_max],
        "L_range": [3, args.L_max],
        "cases": len(rows),
        "failures": len(failures),
        "all_pass": not failures,
        "max_n": args.r_max + args.L_max,
    }

    print(json.dumps(summary, indent=2))
    if failures:
        print(json.dumps(failures[:10], indent=2))
        raise SystemExit(1)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"summary": summary, "cases": rows}, f, indent=2)


if __name__ == "__main__":
    main()
