#!/usr/bin/env python3
"""Simple regex engine (NFA-based). Zero dependencies."""

class State:
    def __init__(self, is_end=False):
        self.is_end = is_end; self.transitions = {}; self.epsilon = []

class NFA:
    def __init__(self, start, end):
        self.start = start; self.end = end

def char_nfa(c):
    s, e = State(), State(True)
    s.transitions[c] = [e]
    return NFA(s, e)

def concat(a, b):
    a.end.is_end = False; a.end.epsilon.append(b.start)
    return NFA(a.start, b.end)

def union(a, b):
    s, e = State(), State(True)
    s.epsilon = [a.start, b.start]
    a.end.is_end = False; a.end.epsilon.append(e)
    b.end.is_end = False; b.end.epsilon.append(e)
    return NFA(s, e)

def star(a):
    s, e = State(), State(True)
    s.epsilon = [a.start, e]
    a.end.is_end = False; a.end.epsilon = [a.start, e]
    return NFA(s, e)

def plus(a):
    s, e = State(), State(True)
    s.epsilon = [a.start]
    a.end.is_end = False; a.end.epsilon = [a.start, e]
    return NFA(s, e)

def question(a):
    s, e = State(), State(True)
    s.epsilon = [a.start, e]
    a.end.is_end = False; a.end.epsilon.append(e)
    return NFA(s, e)

def parse_regex(pattern):
    pos = [0]
    def expr():
        left = term()
        while pos[0] < len(pattern) and pattern[pos[0]] == '|':
            pos[0] += 1; right = term(); left = union(left, right)
        return left
    def term():
        result = None
        while pos[0] < len(pattern) and pattern[pos[0]] not in '|)':
            f = factor()
            result = concat(result, f) if result else f
        if result is None: s = State(True); result = NFA(s, s)
        return result
    def factor():
        base = atom()
        if pos[0] < len(pattern):
            if pattern[pos[0]] == '*': pos[0] += 1; return star(base)
            if pattern[pos[0]] == '+': pos[0] += 1; return plus(base)
            if pattern[pos[0]] == '?': pos[0] += 1; return question(base)
        return base
    def atom():
        if pattern[pos[0]] == '(':
            pos[0] += 1; r = expr(); pos[0] += 1; return r
        if pattern[pos[0]] == '.':
            pos[0] += 1; s, e = State(), State(True); s.transitions['.'] = [e]; return NFA(s, e)
        c = pattern[pos[0]]; pos[0] += 1; return char_nfa(c)
    return expr()

def epsilon_closure(states):
    stack = list(states); closure = set(states)
    while stack:
        s = stack.pop()
        for e in s.epsilon:
            if e not in closure: closure.add(e); stack.append(e)
    return closure

def match(pattern, text):
    nfa = parse_regex(pattern)
    current = epsilon_closure({nfa.start})
    for ch in text:
        next_states = set()
        for s in current:
            for key, targets in s.transitions.items():
                if key == ch or key == '.':
                    next_states.update(targets)
        current = epsilon_closure(next_states)
        if not current: return False
    return any(s.is_end for s in current)

def search(pattern, text):
    for i in range(len(text)):
        for j in range(i, len(text)+1):
            if match(pattern, text[i:j]):
                return (i, j, text[i:j])
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        print(match(sys.argv[1], sys.argv[2]))
