# Concept: Safe Formula Evaluation in `senaite.core.content.calculation`

## 1. Current state and risk

`calculate_formula()` (`src/senaite/core/content/calculation.py:152`) runs
user-supplied formulas through Python's `eval` builtin with a curated
`globals` dict (`__builtins__: None`, stdlib helpers, optional user
imports).

The sandbox is **insufficient**:

- `eval` accepts the full Python expression grammar -- attribute
  access, subscripts, comprehensions, generator expressions, lambdas,
  `.__class__.__bases__[0].__subclasses__()` escape chains, etc. The
  "no `__builtins__`" trick has well-known bypasses through any
  reachable object (e.g. `[].__class__.__mro__[1].__subclasses__()`).
- The `imports` field (`IImportRecord`) lets a Manager configure
  arbitrary `importlib.import_module(...)` calls and pull any callable
  out by name. That is RCE-by-design for anyone who can edit a
  Calculation.
- Every Site Administrator / LabManager can edit a Calculation -- so a
  single compromised LabManager account becomes full Zope process
  compromise.

Threat model going forward: **a Calculation editor must not be able to
execute arbitrary Python or read/write arbitrary objects, files, or
sockets.** Only deterministic numerical/string evaluation over declared
parameters.

## 2. Goals and non-goals

**Goals**

- Replace the `eval` call with a parser/evaluator that only accepts a
  declared subset of expressions.
- Preserve every formula currently used in production lab installs
  (arithmetic, comparisons, `math.*`, `floor`, `ceil`, conditional
  expressions, simple branching).
- Keep the existing `[Keyword]` substitution UX unchanged.
- Provide a deprecation path for the `imports` field rather than
  removing it abruptly.

**Non-goals**

- Turing-complete scripting. If a lab needs that, they should write a
  Python adapter and register it via ZCML, not type Python into a
  TextField.
- Exact bit-for-bit numerical compatibility with the `eval` builtin
  for pathological cases (NaN propagation order etc.).

## 3. Approach: AST whitelist

Use Python's built-in `ast` module to parse the formula once and walk
the tree, rejecting any node not on the whitelist. This is the
canonical safe-evaluation technique (also used by `asteval`,
`simpleeval`); we already control the input grammar via `[brackets]`,
so the whitelist can be tight.

### Allowed AST nodes

- `Expression`, `Module` (top level)
- `Num`, `Constant` (numeric / string / bool / None literals only)
- `Name`, `Load` (resolved against an explicit symbol table -- see §4)
- `BinOp` with `Add, Sub, Mult, Div, FloorDiv, Mod, Pow`
- `UnaryOp` with `UAdd, USub, Not`
- `BoolOp` with `And, Or`
- `Compare` with `Eq, NotEq, Lt, LtE, Gt, GtE`
- `IfExp` (ternary `a if cond else b` -- already used in lab formulas)
- `Call` -- only when `func` is a `Name` resolving to a whitelisted
  callable (§4); reject `Attribute` calls
- `Tuple`, `List` -- only as call arguments, with a node-count cap

### Rejected

- `Attribute`, `Subscript`, `Lambda`, `ListComp`, `DictComp`, `SetComp`,
  `GeneratorExp`, `Yield`, `Await`, `Starred`, `Assign`, `AugAssign`,
  `Import`, `ImportFrom`, `FunctionDef`, `ClassDef`, `Try`, f-strings
  (`JoinedStr`, `FormattedValue`), `NamedExpr` (walrus).

A single `NodeVisitor` raises `FormulaError` on any non-whitelisted
node, with the offending source position so the validator can surface
it inline.

### Resource limits

- Cap source length (e.g. 4 KB).
- Cap AST node count after parse (e.g. 500 nodes) -- kills accidental
  or hostile expression bombs before evaluation.
- Cap `**` exponent (e.g. |exp| <= 1000) to prevent `9**9**9` CPU/memory
  DoS.
- Wrap evaluation in a numeric-only contract: numeric ops on
  `int`/`float`/`Decimal` only; strings stay strings; booleans coerce
  to int as today.

## 4. Symbol table (replaces `getGlobals`)

Two layers, both explicit:

**4.1 Built-in functions** -- a hard-coded module-level dict, frozen at
import time:

```python
SAFE_FUNCS = {
    "abs": abs, "min": min, "max": max, "sum": sum,
    "round": round, "pow": pow, "len": len,
    "int": int, "float": float, "bool": bool, "str": str,
    "floor": math.floor, "ceil": math.ceil, "sqrt": math.sqrt,
    "log": math.log, "log10": math.log10, "exp": math.exp,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "pi": math.pi, "e": math.e,
    ...
}
```

This is a curated allowlist of the `math` members and builtins actually
useful in lab calculations. No `__builtins__`, no `cmp`, no `xrange`,
no `enumerate`, no `format` (the current globals leak more than is
needed).

**4.2 Parameter values** -- the substitution mapping passed in by the
caller (interim fields + dependent service results). These are looked
up by `Name` nodes whose id matches a key. They are pre-coerced to
numeric/string before evaluation; if a value cannot be coerced, raise
`FormulaError` with the keyword.

Crucially: `Name` resolution checks `SAFE_FUNCS` *and* the parameter
map only. Any other identifier raises `NameError`. This eliminates the
"reach a class, walk MRO, escape" family of exploits because no `Name`
ever resolves to an object with attributes that matter.

### `Call` handling

- `func` must be a bare `Name` (not `Attribute`) -- so `math.floor(x)`
  is not allowed; users write `floor(x)` instead.
- The resolved object must be in `SAFE_FUNCS`. Parameter-dict values
  are never callable.
- Keyword arguments allowed; `*args` / `**kwargs` rejected at AST
  level.

## 5. Migrating away from the `imports` field

The `imports` field today lets users execute
`importlib.import_module(...)` for any module -- `os`, `subprocess`,
`pickle`. This must die.

**Step 1 (this PR):** mark the field deprecated in the UI; on save,
emit a warning if the configured import isn't in a hard allowlist
(`math`, `statistics`). Existing values keep working through a
compatibility shim that maps known-good `(module, function)` pairs into
`SAFE_FUNCS`.

**Step 2 (next minor release):** make non-allowlisted imports a
validation error; migrate stored Calculations via an upgrade step that
drops disallowed entries and logs them. Provide a ZCML extension point
(`senaite.core.calculation.functions` named utility) so add-ons can
register additional safe callables in code, where they are subject to
code review -- not in the ZMI.

**Step 3 (later):** remove the field and the `imports` parameter from
`calculate_formula`. The compatibility shim handles old DBs.

## 6. Code shape

Suggested module layout in `senaite/core/calculation/`:

```
senaite/core/calculation/
    __init__.py
    evaluator.py     # parse() + evaluate() + FormulaError
    functions.py     # SAFE_FUNCS registry + register(name, callable)
    legacy.py        # deprecation shim for the imports field
```

`calculate_formula()` becomes a thin wrapper that calls
`evaluator.evaluate(formula, parameters)`. The square-bracket -> `{name}`
translation stays in `FormulaFormatter` but the result goes to
`evaluate`, not the `eval` builtin.

The `try/except` cascade currently in `calculate_formula` collapses to:
`FormulaError`, `ZeroDivisionError`, `ArithmeticError`. No more
catching `Exception` to mask sandbox escapes.

## 7. Validation hook

`senaite.core.validators.formula.FormulaValidator` already runs on
save. Extend it to:

1. Run `evaluator.parse(formula)` -- surfaces grammar/whitelist
   violations as a field error before the value is persisted.
2. Run `evaluator.evaluate(formula, dummy_params)` with `0.0`/`""`
   placeholders for every declared keyword -- catches `NameError` for
   unresolved keywords *and* trivially-undefined-at-runtime expressions
   at edit time.

This means the formula stored in the DB is *guaranteed* parseable;
runtime evaluation can never blow up on syntax.

## 8. Test plan

- Unit tests for `evaluator`: happy paths (existing production formulas
  pulled from sample DBs), each rejected node type, depth/length/
  exponent limits, NaN/Inf handling, division by zero, unknown
  identifier, unicode formula text.
- Targeted exploit tests:
  `().__class__.__bases__[0].__subclasses__()`,
  `[c for c in ().__class__.__mro__]`, attribute access on parameter
  strings, recursive `**`, oversized literal, encoded payloads via
  `chr()`.
- Migration tests: DB with `imports=[("os","system")]` round-trips
  through upgrade step and ends up sanitised + logged.
- Backwards-compat: the existing `bika.lims` calculation tests should
  pass unchanged; if any fails, the formula it uses is the source of
  truth for what the whitelist must accept.

## 9. Performance

Parsing every call adds work, but `ast.parse` on a <1 KB string is
microseconds and dwarfed by the existing ZODB lookups for dependent
service results. Optionally cache the compiled-and-validated AST on
the Calculation object keyed by formula hash -- invalidated in
`setFormula`. Not required for correctness; defer until profiling
says so.

## 10. Rollout

1. Land evaluator + tests behind a feature flag
   (`SENAITE_SAFE_EVAL=1`) -- both paths coexist for one release so
   production sites can A/B against real formulas.
2. Flip default to safe evaluator; keep the legacy path reachable via
   env var for one more release as an emergency escape hatch, with a
   startup warning.
3. Remove the legacy path and the `imports` field per §5 step 3.
