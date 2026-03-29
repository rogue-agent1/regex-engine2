#!/usr/bin/env python3
"""Simple regex engine supporting . * + ? | () character classes."""
import sys

class State:
    _id = 0
    def __init__(self, accept=False):
        State._id += 1; self.id = State._id
        self.accept, self.transitions, self.epsilon = accept, {}, []

def char_match(c, pattern_char):
    if pattern_char == ".": return True
    return c == pattern_char

def compile_regex(pattern):
    pos = [0]
    def parse_alt():
        left = parse_seq()
        while pos[0] < len(pattern) and pattern[pos[0]] == "|":
            pos[0] += 1; right = parse_seq()
            start, end = State(), State(True)
            start.epsilon = [left[0], right[0]]
            left[1].accept = False; left[1].epsilon.append(end)
            right[1].accept = False; right[1].epsilon.append(end)
            left = (start, end)
        return left
    def parse_seq():
        nodes = []
        while pos[0] < len(pattern) and pattern[pos[0]] not in ")|":
            nodes.append(parse_atom())
        if not nodes:
            s = State(True); return (s, s)
        result = nodes[0]
        for n in nodes[1:]:
            result[1].accept = False; result[1].epsilon.append(n[0])
            result = (result[0], n[1])
        return result
    def parse_atom():
        if pos[0] < len(pattern) and pattern[pos[0]] == "(":
            pos[0] += 1; node = parse_alt()
            if pos[0] < len(pattern) and pattern[pos[0]] == ")": pos[0] += 1
        else:
            c = pattern[pos[0]]; pos[0] += 1
            s, e = State(), State(True)
            s.transitions[c] = [e]; node = (s, e)
        if pos[0] < len(pattern) and pattern[pos[0]] in "*+?":
            q = pattern[pos[0]]; pos[0] += 1
            start, end = State(), State(True)
            node[1].accept = False
            if q in "*?": start.epsilon.append(end)
            if q in "*+": node[1].epsilon.append(node[0])
            start.epsilon.append(node[0]); node[1].epsilon.append(end)
            node = (start, end)
        return node
    return parse_alt()

def epsilon_closure(states):
    stack = list(states); closure = set(states)
    while stack:
        s = stack.pop()
        for e in s.epsilon:
            if e not in closure: closure.add(e); stack.append(e)
    return closure

def match(nfa_start, text):
    current = epsilon_closure({nfa_start})
    for c in text:
        next_states = set()
        for s in current:
            for pat, targets in s.transitions.items():
                if char_match(c, pat): next_states.update(targets)
        current = epsilon_closure(next_states)
        if not current: return False
    return any(s.accept for s in current)

def main():
    if len(sys.argv) < 2: print("Usage: regex_engine2.py <demo|test>"); return
    if sys.argv[1] == "test":
        State._id = 0
        nfa = compile_regex("ab")
        assert match(nfa[0], "ab"); assert not match(nfa[0], "ac")
        nfa2 = compile_regex("a*b")
        assert match(nfa2[0], "b"); assert match(nfa2[0], "ab"); assert match(nfa2[0], "aaab")
        nfa3 = compile_regex("a|b")
        assert match(nfa3[0], "a"); assert match(nfa3[0], "b"); assert not match(nfa3[0], "c")
        nfa4 = compile_regex("a+")
        assert match(nfa4[0], "a"); assert match(nfa4[0], "aaa"); assert not match(nfa4[0], "")
        nfa5 = compile_regex("ab?c")
        assert match(nfa5[0], "ac"); assert match(nfa5[0], "abc"); assert not match(nfa5[0], "abbc")
        nfa6 = compile_regex("(ab)*")
        assert match(nfa6[0], ""); assert match(nfa6[0], "ab"); assert match(nfa6[0], "abab")
        print("All tests passed!")
    else:
        pat = sys.argv[2] if len(sys.argv) > 2 else "a*b"
        text = sys.argv[3] if len(sys.argv) > 3 else "aaab"
        nfa = compile_regex(pat)
        print(f"/{pat}/ matches {text!r}: {match(nfa[0], text)}")

if __name__ == "__main__": main()
