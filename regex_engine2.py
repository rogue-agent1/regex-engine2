#!/usr/bin/env python3
"""Regex engine via NFA — supports . * + ? | () character classes."""
import sys

class State:
    _id = 0
    def __init__(self, label=None):
        State._id += 1
        self.id = State._id
        self.label = label  # None = epsilon, char, or special
        self.transitions = []  # (label_or_None, next_state)

def match_char(label, ch):
    if label == ".": return True
    if label.startswith("["):
        negate = label[1] == "^"
        chars = label[2:-1] if negate else label[1:-1]
        matched = ch in chars
        return not matched if negate else matched
    return label == ch

class NFA:
    def __init__(self, start, accept):
        self.start, self.accept = start, accept

def char_nfa(label):
    s, a = State(), State()
    s.transitions.append((label, a))
    return NFA(s, a)

def concat_nfa(a, b):
    a.accept.transitions.append((None, b.start))
    return NFA(a.start, b.accept)

def union_nfa(a, b):
    s, f = State(), State()
    s.transitions.extend([(None, a.start), (None, b.start)])
    a.accept.transitions.append((None, f))
    b.accept.transitions.append((None, f))
    return NFA(s, f)

def star_nfa(a):
    s, f = State(), State()
    s.transitions.extend([(None, a.start), (None, f)])
    a.accept.transitions.extend([(None, a.start), (None, f)])
    return NFA(s, f)

def plus_nfa(a):
    s, f = State(), State()
    s.transitions.append((None, a.start))
    a.accept.transitions.extend([(None, a.start), (None, f)])
    return NFA(s, f)

def question_nfa(a):
    s, f = State(), State()
    s.transitions.extend([(None, a.start), (None, f)])
    a.accept.transitions.append((None, f))
    return NFA(s, f)

def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for label, nxt in s.transitions:
            if label is None and nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure

def nfa_match(nfa, text):
    current = epsilon_closure({nfa.start})
    for ch in text:
        nxt = set()
        for s in current:
            for label, ns in s.transitions:
                if label is not None and match_char(label, ch):
                    nxt.add(ns)
        current = epsilon_closure(nxt)
        if not current: return False
    return nfa.accept in current

def parse_regex(pattern):
    pos = [0]
    def parse_expr():
        terms = [parse_concat()]
        while pos[0] < len(pattern) and pattern[pos[0]] == "|":
            pos[0] += 1
            terms.append(parse_concat())
        result = terms[0]
        for t in terms[1:]:
            result = union_nfa(result, t)
        return result
    def parse_concat():
        terms = []
        while pos[0] < len(pattern) and pattern[pos[0]] not in "|)":
            terms.append(parse_atom())
        if not terms: return char_nfa(None)  # epsilon
        result = terms[0]
        for t in terms[1:]:
            result = concat_nfa(result, t)
        return result
    def parse_atom():
        if pattern[pos[0]] == "(":
            pos[0] += 1
            nfa = parse_expr()
            pos[0] += 1  # skip )
        elif pattern[pos[0]] == ".":
            nfa = char_nfa("."); pos[0] += 1
        elif pattern[pos[0]] == "[":
            end = pattern.index("]", pos[0])
            cls = pattern[pos[0]:end+1]
            nfa = char_nfa(cls); pos[0] = end + 1
        else:
            nfa = char_nfa(pattern[pos[0]]); pos[0] += 1
        while pos[0] < len(pattern) and pattern[pos[0]] in "*+?":
            if pattern[pos[0]] == "*": nfa = star_nfa(nfa)
            elif pattern[pos[0]] == "+": nfa = plus_nfa(nfa)
            elif pattern[pos[0]] == "?": nfa = question_nfa(nfa)
            pos[0] += 1
        return nfa
    return parse_expr()

def regex_match(pattern, text):
    State._id = 0
    nfa = parse_regex(pattern)
    return nfa_match(nfa, text)

def test():
    assert regex_match("abc", "abc")
    assert not regex_match("abc", "abd")
    assert regex_match("a.c", "abc")
    assert regex_match("a*", "aaa")
    assert regex_match("a*", "")
    assert regex_match("a+", "aa")
    assert not regex_match("a+", "")
    assert regex_match("ab?c", "ac")
    assert regex_match("ab?c", "abc")
    assert regex_match("a|b", "a")
    assert regex_match("a|b", "b")
    assert regex_match("(ab)+", "abab")
    assert not regex_match("(ab)+", "aba")
    print("  regex_engine2: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("NFA-based regex engine")
