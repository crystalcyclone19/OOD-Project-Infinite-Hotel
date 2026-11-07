import statistics as stat
import math
import csv
import os
from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple

def variance(numbers)-> float:
    total = 0
    mean = 0

    for n in numbers:
        mean += n / len(numbers)

    for n in numbers:
        total += (n - mean) ** 2

    return total / len(numbers)


def avg(numbers) -> float:
  total = 0
  for n in numbers:
   total += n/len(numbers)

  return total

def min(numbers) -> float:
    smallest = numbers[0]
    for n in numbers[1:]:
        if n < smallest:
            smallest = n
    return smallest
  

def max(numbers) -> float:
    largest = numbers[0]
    for n in numbers[1:]:
        if n > largest:
            largest = n
    return largest

def get_medians(y):
    return [stat.median(lst) for lst in y]





"""
Curve-fitting helpers (pure Python, no numpy needed).

    import util.math as m   # then m.fit_text / m.fit_metric / m.save_fits

    ks      = [1000, 10000, 20000, ...]       # K values
    medians = [69.8, 85.2, 109.6, ...]        # median time (us) for each K

    text, r2 = fit_text(ks, medians, "assign")           # simplest: ("y = ...", R2)
    best, all_fits = fit_metric(ks, medians, "assign")   # "assign" | "search" | "ordering" | "memory"
    print(best.formula, best.r2)                         # y = 13.58*ln K + -27.86   0.916
    y_hat = best.predict(50000)                          # the returned function

    save_fits("test_A/consistant_hashing/fit_assign.csv", all_fits, best,
              metric="assign", min_k=1000)
"""

_BASIS = {
    "K ln K":  lambda k: k * math.log(k),
    "K":       lambda k: float(k),
    "sqrt(K)": lambda k: math.sqrt(k),
    "ln K":    lambda k: math.log(k),
    "const":   lambda k: 0.0,
}
CANDIDATES = {
    "ordering": ["K ln K", "K", "sqrt(K)"],
    "assign":   ["ln K", "const", "sqrt(K)", "K"],
    "search":   ["ln K", "const", "sqrt(K)", "K"],
    "memory":   ["K", "K ln K", "sqrt(K)"],
}


@dataclass
class Fit:
    model: str            # e.g. "ln K"
    a: float              # coefficient on f(K)
    b: float              # intercept
    r2: float
    rmse: float
    formula: str          # readable text
    predict: Callable[[float], float]   # the fitted function y = a*f(K) + b


def _fit_one(ks: Sequence[float], ys: Sequence[float], model: str) -> Fit:
    f = [_BASIS[model](k) for k in ks]
    n = len(ys)
    my = sum(ys) / n
    if model == "const":
        a, b = 0.0, my
    else:
        mf = sum(f) / n
        sff = sum((x - mf) ** 2 for x in f)
        a = sum((x - mf) * (y - my) for x, y in zip(f, ys)) / sff if sff > 0 else 0.0
        b = my - a * mf
    pred = [a * x + b for x in f]
    ss_res = sum((y - p) ** 2 for y, p in zip(ys, pred))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    rmse = math.sqrt(ss_res / n)
    sign = "+" if b >= 0 else "-"
    formula = f"y = {b:.6g}" if model == "const" else f"y = {a:.6g}*{model} {sign} {abs(b):.6g}"
    basis = _BASIS[model]
    return Fit(model, a, b, r2, rmse, formula, lambda k, a=a, b=b, basis=basis: a * basis(k) + b)


def fit_metric(ks: Sequence[float], ys: Sequence[float], metric: str,
               min_k: float = 1000) -> Tuple[Fit, List[Fit]]:
    """Fit every candidate model for `metric`; return (best by R2, all fits).
    Points with K < min_k are ignored."""
    if metric not in CANDIDATES:
        raise ValueError(f"metric must be one of {list(CANDIDATES)}")
    pts = [(k, y) for k, y in zip(ks, ys) if k >= min_k]
    if len(pts) < 4:
        raise ValueError(f"need >= 4 points with K >= {min_k}, got {len(pts)}")
    k_use, y_use = zip(*pts)
    fits = [_fit_one(k_use, y_use, m) for m in CANDIDATES[metric]]
    best = fits[0]
    for ft in fits[1:]:                      # NOT max(): this file defines its own max(numbers)
        if not math.isnan(ft.r2) and (math.isnan(best.r2) or ft.r2 > best.r2):
            best = ft
    return best, fits


def fit_text(ks: Sequence[float], ys: Sequence[float], metric: str,
             min_k: float = 1000) -> Tuple[str, float]:
    """Simplest call: returns (formula text, R2) of the best model.
        text, r2 = fit_text(ks, medians, "assign")
        -> ("y = 12.9858*ln K - 22.0778", 0.8829)
    """
    best, _ = fit_metric(ks, ys, metric, min_k)
    return best.formula, best.r2


def save_fits(path: str, fits: List[Fit], best: Fit, metric: str, min_k: float = 1000,
              meta: dict = None) -> None:
    """Write one row per model (a, b, R2, RMSE, formula, best flag) to a CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for k, v in (meta or {}).items():
            w.writerow([f"# {k}: {v}"])
        w.writerow([f"# metric: {metric}"])
        w.writerow([f"# fitted rows: K >= {min_k:g}"])
        w.writerow(["model", "a", "b", "R2", "RMSE_us", "formula", "best"])
        for ft in fits:
            w.writerow([ft.model, f"{ft.a:.8g}", f"{ft.b:.8g}", f"{ft.r2:.6f}",
                        f"{ft.rmse:.4f}", ft.formula, "yes" if ft is best else ""])



def _solve(A, b):
    """Gaussian elimination for a small square system. Returns None if singular."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = c
        for r in range(c + 1, n):
            if abs(M[r][c]) > abs(M[p][c]):
                p = r
        if abs(M[p][c]) < 1e-9:
            return None
        M[c], M[p] = M[p], M[c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


def fit_log_k_log_m_multi(ks, ys, ms=None, min_k=1000):
    """Fit the analysed cost  O(log K + log M)  to measured times.

        y = a*ln K + c*ln M + d

    ks : K values        ys : measured times        ms : M = N*V for each point
    (a single number is also accepted when M is the same for every point).

    * M varies (e.g. you repeat the test with different V or N):  a, c, d are all fitted.
    * M is constant (Test A: N=10, V=32 -> M=320): ln M is just a constant, so it can
      not be separated from the intercept. Then it fits y = a*ln K + d and says so.

    Returns (text, r2). Text is always in the form  y = a*ln K + c*ln M + d.
    """
    if ms is None or isinstance(ms, (int, float)):
        ms = [ms if ms is not None else 1] * len(ks)
    pts = [(k, m_, y) for k, m_, y in zip(ks, ms, ys) if k >= min_k]
    if len(pts) < 4:
        raise ValueError("need at least 4 points with K >= min_k")
    n = len(pts)
    lk = [math.log(k) for k, _, _ in pts]
    lm = [math.log(m_) for _, m_, _ in pts]
    y = [p[2] for p in pts]
    my = sum(y) / n
    ss_tot = sum((v - my) ** 2 for v in y)

    def r2_of(pred):
        ss_res = sum((v - p) ** 2 for v, p in zip(y, pred))
        return 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    # try the full model  a*lnK + c*lnM + d
    X = [[lk[i], lm[i], 1.0] for i in range(n)]
    A = [[sum(X[i][r] * X[i][c] for i in range(n)) for c in range(3)] for r in range(3)]
    bb = [sum(X[i][r] * y[i] for i in range(n)) for r in range(3)]
    sol = _solve(A, bb)
    if sol is not None:
        a, c, d = sol
        pred = [a * lk[i] + c * lm[i] + d for i in range(n)]
        sign = "+" if d >= 0 else "-"
        return f"y = {a:.6g}*ln K + {c:.6g}*ln M {sign} {abs(d):.6g}", r2_of(pred)

    # M constant -> ln M merges into the intercept: only a and (c*ln M + d) can be found
    mk = sum(lk) / n
    sxx = sum((v - mk) ** 2 for v in lk)
    a = sum((lk[i] - mk) * (y[i] - my) for i in range(n)) / sxx
    const = my - a * mk                      # = c*ln M + d
    pred = [a * v + const for v in lk]
    return (f"y = {a:.6g}*ln K + c*ln M + d   [M = {ms[0]:g} constant, so c*ln M + d = {const:.6g}]",
            r2_of(pred))


def fit_log_k_log_m(ks, ys, M, min_k=1000):
    """Fit the analysed cost O(log K + log M) when M (= N*V) is a known constant.

        text, r2 = fit_log_k_log_m(K, medians, N * V)
        -> ("y = 1.7982*ln K + 5.53065", 0.8829)

    Because M is fixed, c*ln M + d is one constant, so the result is ready to use:
        y = a*ln K + b      (b already includes the log M part)
    For runs with several different M values use fit_log_k_log_m_multi().
    """
    pts = [(k, y) for k, y in zip(ks, ys) if k >= min_k]
    if len(pts) < 4:
        raise ValueError("need at least 4 points with K >= min_k")
    lk = [math.log(k) for k, _ in pts]
    y = [v for _, v in pts]
    n = len(y)
    mk, my = sum(lk) / n, sum(y) / n
    sxx = sum((v - mk) ** 2 for v in lk)
    a = sum((lk[i] - mk) * (y[i] - my) for i in range(n)) / sxx
    b = my - a * mk
    ss_res = sum((y[i] - (a * lk[i] + b)) ** 2 for i in range(n))
    ss_tot = sum((v - my) ** 2 for v in y)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    sign = "+" if b >= 0 else "-"
    return f"y = {a:.6g}*ln K {sign} {abs(b):.6g}", r2