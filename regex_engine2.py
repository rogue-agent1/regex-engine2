#!/usr/bin/env python3
"""regex_engine2 - NFA-based regex engine with Thompson's construction."""
import sys

class State:
    def __init__(self, label=None):
        self.label = label  # None = epsilon
        self.out = []

class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept

def char_nfa(c):
    s, a = State(c), State()
    s.out.append(a)
    return NFA(s, a)

def concat_nfa(a, b):
    a.accept.out.append(b.start)
    a.accept.label = b.start.label
    a.accept.out = b.start.out
    return NFA(a.start, b.accept)

def alt_nfa(a, b):
    s = State()
    s.out = [a.start, b.start]
    accept = State()
    a.accept.out.append(accept)
    b.accept.out.append(accept)
    return NFA(s, accept)

def star_nfa(a):
    s = State()
    accept = State()
    s.out = [a.start, accept]
    a.accept.out = [a.start, accept]
    return NFA(s, accept)

def plus_nfa(a):
    s = State()
    accept = State()
    s.out = [a.start]
    a.accept.out = [a.start, accept]
    return NFA(s, accept)

def parse_regex(pattern):
    pos = [0]
    def expr():
        left = seq()
        while pos[0] < len(pattern) and pattern[pos[0]] == '|':
            pos[0] += 1
            right = seq()
            left = alt_nfa(left, right)
        return left
    def seq():
        atoms = []
        while pos[0] < len(pattern) and pattern[pos[0]] not in '|)':
            atoms.append(atom())
        if not atoms:
            s, a = State(), State()
            s.out.append(a)
            return NFA(s, a)
        result = atoms[0]
        for a in atoms[1:]:
            result = concat_nfa(result, a)
        return result
    def atom():
        if pattern[pos[0]] == '(':
            pos[0] += 1
            r = expr()
            pos[0] += 1  # ')'
        elif pattern[pos[0]] == '.':
            pos[0] += 1
            r = char_nfa('.')
        else:
            r = char_nfa(pattern[pos[0]])
            pos[0] += 1
        if pos[0] < len(pattern):
            if pattern[pos[0]] == '*':
                pos[0] += 1
                r = star_nfa(r)
            elif pattern[pos[0]] == '+':
                pos[0] += 1
                r = plus_nfa(r)
            elif pattern[pos[0]] == '?':
                pos[0] += 1
                empty = NFA(State(), State())
                empty.start.out.append(empty.accept)
                r = alt_nfa(r, empty)
        return r
    return expr()

def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for out in s.out:
            if s.label is None and out not in closure:
                closure.add(out)
                stack.append(out)
    return closure

def match(nfa, text):
    current = epsilon_closure({nfa.start})
    for ch in text:
        next_states = set()
        for s in current:
            if s.label == ch or s.label == '.':
                for out in s.out:
                    next_states.add(out)
        current = epsilon_closure(next_states)
    return nfa.accept in current

def fullmatch(pattern, text):
    nfa = parse_regex(pattern)
    return match(nfa, text)

def test():
    assert fullmatch("abc", "abc")
    assert not fullmatch("abc", "abd")
    assert fullmatch("a|b", "a")
    assert fullmatch("a|b", "b")
    assert not fullmatch("a|b", "c")
    assert fullmatch("a*", "")
    assert fullmatch("a*", "aaa")
    assert fullmatch("a+", "a")
    assert not fullmatch("a+", "")
    assert fullmatch("ab?c", "ac")
    assert fullmatch("ab?c", "abc")
    assert fullmatch("(a|b)*c", "aababc")
    assert fullmatch(".+", "xyz")
    print("OK: regex_engine2")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    else:
        print("Usage: regex_engine2.py test")
