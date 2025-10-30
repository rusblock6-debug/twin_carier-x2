import logging
import random

import numpy as np
from scipy import stats

__all__ = (
    "assess_stability",
    "calc_reliability",
    "find_closest_result",
)

logger = logging.getLogger(__name__)
# =========================
# Ввод/вывод
# =========================

def extract_metric(runs: list[dict], metric: str) -> np.ndarray:
    """
    Извлекает выбранную метрику из первых записей

    Параметры:
        runs   : исходные записи симуляций
        metric : название метрики: "trips" | "volume" | "weight"

    Возвращает:
        Массив значений выбранной метрики без пропусков.
    """
    xs: list[float] = []
    for rec in runs:
        s = (rec or {}).get("summary", {}) or {}
        if metric == "trips":
            v = s.get("trips")
        elif metric == "volume":
            v = s.get("volume")
        elif metric == "weight":
            v = s.get("weight")
        else:
            raise ValueError(f"Неизвестная метрика: {metric}")
        if v is not None:
            xs.append(float(v))
    x = np.asarray(xs, float)
    return x[~np.isnan(x)]


# =========================
# Базовые характеристики
# =========================

def descriptive_stats(x: np.ndarray) -> dict:
    """
    Краткая описательная статистика, полезная для понимания формы распределения

    Возвращает:
        n        : объём выборки
        mean     : среднее
        std      : выборочное стандартное отклонение
        median   : медиана
        q1, q3   : квартильный интервал
        iqr      : межквартильный размах
        skew     : асимметрия
        kurtosis : избыточный эксцесс
        xmin,xmax: минимальное и максимальное наблюдения
    """
    x = np.asarray(x, float)
    n = len(x)
    m = float(np.mean(x)) if n else np.nan
    s = float(np.std(x, ddof=1)) if n > 1 else np.nan
    med = float(np.median(x)) if n else np.nan
    q1, q3 = (np.quantile(x, 0.25), np.quantile(x, 0.75)) if n > 0 else (np.nan, np.nan)
    iqr = float(q3 - q1) if n > 0 else np.nan
    sk = stats.skew(x, bias=False) if n > 2 else np.nan
    kurt = stats.kurtosis(x, fisher=True, bias=False) if n > 3 else np.nan
    return dict(n=n, mean=m, std=s, median=med, q1=q1, q3=q3, iqr=iqr,
                skew=sk, kurtosis=kurt, xmin=float(np.min(x)), xmax=float(np.max(x)))


# =========================
# Интервалы (базовые)
# =========================

def predictive_interval_t(x: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """
    Двусторонний t-предиктивный интервал уровня 1-α для будущего наблюдения

    Идея:
        Если данные близки к симметрии и нормальности, то
        (X_new - среднее)/[S*sqrt(1+1/n)] ~ t_{n-1}.
        Отсюда границы: среднее ± t_{1-α/2, n-1} * S * sqrt(1+1/n).

    Возвращает:
        (нижняя, верхняя) границы вероятностного коридора
    """
    x = np.asarray(x, float)
    n = len(x)
    if n == 0:
        return (np.nan, np.nan)
    m = float(np.mean(x))
    if n == 1:
        # При одном наблюдении разумной ширины нет - обе границы равны ему
        return (m, m)
    s = float(np.std(x, ddof=1))
    tval = float(stats.t.ppf(1 - alpha / 2, df=n - 1))
    half = tval * s * np.sqrt(1 + 1 / n)
    return (m - half, m + half)

def robust_pi_quantiles(x: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """
    Робастный предиктивный интервал по эмпирическим квантилям.

    Идея:
        Никаких предположений о форме: берём квантиль α/2 и 1-α/2.
        Интервал естественно подстраивается под асимметрию распределения
    """
    x = np.asarray(x, float)
    if len(x) == 0:
        return (np.nan, np.nan)
    lo, hi = np.quantile(x, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)

def split_conformal_pi(x: np.ndarray, alpha: float = 0.05, seed: int = 123) -> tuple[float, float]:
    """
    Симметричный split-conformal интервал с гарантией покрытия ≈ 1-α

    Идея:
        Делим данные на обучение и калибровку.
        На обучении считаем центр (среднее), на калибровке - остатки |X-центр|
        Берём дискретный квантиль остатка уровня 1-α
        симметрично откладываем от центра.

    """
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float).copy()
    n = len(x)
    if n == 0:
        return (np.nan, np.nan)
    if n == 1:
        return float(x[0]), float(x[0])
    rng.shuffle(x)
    n_cal = n // 2
    train, cal = x[: n - n_cal], x[n - n_cal :]
    mu = float(np.mean(train))
    scores = np.abs(cal - mu)

    k = int(np.ceil((1 - alpha) * (n_cal + 1)))
    k = np.clip(k, 1, n_cal)
    q = float(np.partition(np.sort(scores), k - 1)[k - 1])
    return (mu - q, mu + q)

def lognormal_pi(x: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """
    Интервал при лог-нормальной аппроксимации
    """
    x = np.asarray(x, float)
    if np.any(x <= 0) or len(x) < 2:
        return predictive_interval_t(x, alpha=alpha)
    lx = np.log(x)
    m = float(np.mean(lx))
    s = float(np.std(lx, ddof=1))
    tval = float(stats.t.ppf(1 - alpha / 2, df=len(x) - 1))
    half = tval * s * np.sqrt(1 + 1 / len(x))
    return float(np.exp(m - half)), float(np.exp(m + half))


# =========================
# Новые интервалы/центры
# =========================

def kde_hdi(x: np.ndarray, alpha: float = 0.05, grids: int = 2048) -> tuple[float, float]:
    """
    Интервал наибольшей плотности (HDI) по сглаженной оценке плотности (KDE).

    """
    x = np.asarray(x, float)
    kde = stats.gaussian_kde(x)
    g = np.linspace(np.min(x), np.max(x), grids)
    f = kde(g)
    idx = np.argsort(f)[::-1]            # точки сетки в порядке убывания плотности
    cs = np.cumsum(f[idx])
    cs /= cs[-1]                          # нормировка до 1
    mask = cs <= (1 - alpha)
    sel = np.sort(g[idx][mask])
    if len(sel) == 0:
        return float(np.min(x)), float(np.max(x))
    return float(sel[0]), float(sel[-1])

def bootstrap_pi(x: np.ndarray, alpha: float = 0.05, B: int = 5000, seed: int = 123) -> tuple[float, float]:
    """
    Бутстрэп-интервал (перцентильный): эмпирическое предиктивное распределение.
    """
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    draws = rng.choice(x, size=B, replace=True)
    lo, hi = np.quantile(draws, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)

def jackknife_plus_pi(x: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """
    Интервал Jackknife+
    """
    x = np.asarray(x, float)
    n = len(x)
    if n <= 1:
        return predictive_interval_t(x, alpha=alpha)
    mu_full = float(np.mean(x))
    mu_loo = np.array([(np.sum(x) - xi) / (n - 1) for xi in x])
    resid = np.abs(x - mu_loo)
    q = np.quantile(resid, 1 - alpha, method="higher")
    return float(mu_full - q), float(mu_full + q)

def split_conformal_asymmetric(x: np.ndarray, alpha: float = 0.05, seed: int = 123) -> tuple[float, float]:
    """
    Асимметричный split-conformal
    """
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float).copy()
    n = len(x)
    if n == 0:
        return (np.nan, np.nan)
    if n == 1:
        return float(x[0]), float(x[0])
    rng.shuffle(x)
    n_cal = n // 2
    tr, cal = x[:-n_cal], x[-n_cal:]
    mu = float(np.mean(tr))
    e = cal - mu
    q_lo = np.quantile(e, alpha / 2, method="lower")
    q_hi = np.quantile(e, 1 - alpha / 2, method="higher")
    return float(mu + q_lo), float(mu + q_hi)

def yeojohnson_pi(x: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """
    Интервал на основе преобразования Йео–Джонсона
    """
    x = np.asarray(x, float)
    if len(x) < 2:
        return predictive_interval_t(x, alpha=alpha)

    lam = stats.yeojohnson_normmax(x)     # оценка параметра преобразования
    y = stats.yeojohnson(x, lmbda=lam)
    n = len(y)
    m, s = float(np.mean(y)), float(np.std(y, ddof=1))
    tval = float(stats.t.ppf(1 - alpha / 2, df=n - 1))
    half = tval * s * np.sqrt(1 + 1 / n)
    lo_y, hi_y = m - half, m + half

    # Обратное преобразование Йео–Джонсона (устойчивая реализация):
    #   для y >= 0: x = ((y*λ + 1)^(1/λ) - 1)   (λ ≠ 0), иначе предел exp(y) - 1
    #   для y <  0: x = 1 - (1 - y*(2-λ))^(1/(2-λ))   (λ ≠ 2), иначе предел 1 - exp(-y)
    def inv_yj(yv: np.ndarray, lmbda: float) -> np.ndarray:
        yv = np.asarray(yv, float)
        out = np.empty_like(yv)

        pos = yv >= 0
        l2 = 2.0 - lmbda
        tiny = np.finfo(float).tiny  # защита от нулевого основания степени

        with np.errstate(invalid="ignore", over="raise", under="ignore", divide="ignore"):
            # Ветвь y >= 0
            if pos.any():
                if abs(lmbda) > 1e-12:
                    base_pos = yv[pos] * lmbda + 1.0
                    base_pos = np.maximum(base_pos, tiny)
                    out[pos] = np.power(base_pos, 1.0 / lmbda) - 1.0
                else:
                    out[pos] = np.expm1(yv[pos])  # предел при λ → 0

            # Ветвь y < 0
            neg = ~pos
            if neg.any():
                if abs(l2) > 1e-12:
                    base_neg = 1.0 - yv[neg] * l2
                    base_neg = np.maximum(base_neg, tiny)
                    out[neg] = 1.0 - np.power(base_neg, 1.0 / l2)
                else:
                    out[neg] = 1.0 - np.exp(-yv[neg])  # предел при λ → 2

        return out

    # Из-за монотонности преобразования достаточно обратить границы и отсортировать
    lo = float(np.min(inv_yj(np.array([lo_y, hi_y]), lam)))
    hi = float(np.max(inv_yj(np.array([lo_y, hi_y]), lam)))
    return lo, hi

def half_sample_mode(x: np.ndarray) -> float:
    """
    Робастная мода (Half-Sample Mode, HSM).
    """
    y = np.sort(np.asarray(x, float))
    n = len(y)
    if n <= 2:
        return float(np.mean(y))
    k = n // 2
    widths = y[k:] - y[:n - k]
    j = int(np.argmin(widths))
    return half_sample_mode(y[j:j + k + (n % 2)])

def kde_mode(x: np.ndarray, grids: int = 512) -> float:
    """
    Мода по сглаженной плотности (KDE)
    """
    kde = stats.gaussian_kde(x)
    grid = np.linspace(np.min(x), np.max(x), grids)
    dens = kde(grid)
    return float(grid[np.argmax(dens)])


# =========================
# Калибровка: покрытие и PIT
# =========================

def loo_coverage(x: np.ndarray, get_interval, alpha: float = 0.05, **kwargs) -> float:
    """
    Эмпирическое покрытие leave-one-out кросс-валидайция

    """
    x = np.asarray(x, float)
    n = len(x)
    if n < 3:
        return np.nan
    inside = 0
    for i in range(n):
        x_ = np.delete(x, i)
        lo, hi = get_interval(x_, alpha=alpha, **kwargs)
        inside += int(lo <= x[i] <= hi)
    return inside / n

def pit_values_t_predictive(x: np.ndarray) -> np.ndarray:
    """
    PIT (вероятностное преобразование) для t-предиктивной модели
    """
    x = np.asarray(x, float)
    n = len(x)
    m = float(np.mean(x))
    s = float(np.std(x, ddof=1)) if n > 1 else 1.0
    scale = s * np.sqrt(1 + 1 / n) if n > 0 else 1.0
    z = (x - m) / (scale if scale > 0 else 1.0)
    return stats.t.cdf(z, df=max(n - 1, 1))


# =========================
# Выбор лучшего интервала + обоснование
# =========================

def interval_width(iv: tuple[float, float]) -> float:
    """
    Ширина интервала. Если границы нечисловые - вернуть бесконечность,
    чтобы такой метод оказался в конце при сравнении
    """
    lo, hi = iv
    return float(hi - lo) if (np.isfinite(hi) and np.isfinite(lo)) else np.inf

def select_best_interval(
    alpha: float,
    intervals: dict[str, tuple[float, float]],
    coverages: dict[str, float],
    skew: float,
    tol: float = 0.03,
) -> tuple[str, tuple[float, float], str]:
    """
    Выбирает лучший интервал по простому и понятному правилу.

    Правило:
        1) Сначала фильтруем методы с покрытием LOO не хуже цели (1-α-допуск)
        2) Среди них берём наименьшую ширину
        3) При сильной асимметрии (|skew|>1) отдаём предпочтение робастным методам

    Возвращает:
        (название метода, его интервал, строка-обоснование выбора)
    """
    target = 1 - alpha
    robust_names = {
        "quantile-PI", "conformal-PI", "asym-conformal-PI",
        "jackknife+-PI", "bootstrap-PI", "kde-HDI"
    }

    def score(name: str):
        iv = intervals[name]
        cov = coverages.get(name, np.nan)
        width = interval_width(iv)

        # Методы без оценённого покрытия (или с NaN) не ставим в приоритет первыми
        if np.isnan(cov):
            return (0, 1.0, 0, -width)

        ok = 1 if cov >= target - tol else 0
        shortfall = max(0.0, target - cov)
        robust_bonus = 1 if (abs(skew) > 1.0 and name in robust_names) else 0

        return (ok, -shortfall, robust_bonus, -width)

    ranked = sorted(intervals.keys(), key=lambda nm: score(nm), reverse=True)
    best = ranked[0]
    iv = intervals[best]
    cov = coverages.get(best, np.nan)
    w = interval_width(iv)

    reasons = []
    if not np.isnan(cov):
        if cov >= target - tol:
            reasons.append(f"покрытие LOO {cov:.3f} близко к целевому {target:.3f}")
        else:
            reasons.append(f"лучшая калибровка среди методов (LOO {cov:.3f} при цели {target:.3f})")
    reasons.append(f"минимальная ширина среди сопоставимых: {w:.2f}")
    if abs(skew) > 1.0 and best in robust_names:
        reasons.append(f"учёт асимметрии (|асимметрия|={abs(skew):.2f}) - робастный метод предпочтительнее")

    return best, iv, "; ".join(reasons)


# =========================
# Основные функции
# =========================

def assess_stability(
        results: list[dict],
        metric: str = "weight",
        prev_metric_median: float | None = None,
        cur_stable_streak: int = 0,
        alpha: float = 0.05,  # Уровень α (по умолчанию 0.05 → 95% предиктивный интервал)
        r_target: float = 0.05,  # Порог относительной половины ширины t-интервала
        delta_target: float = 0.01,  # Порог относительного сдвига медианы между шагами
        consecutive: int = 2,  # Сколько раз подряд должны выполниться оба порога
) -> tuple[bool, np.ndarray, float, int]:
    """
    Оценка стабильности переданного набора данных с учётом предыдущих оценок на более
    узкой выборке (от предыдущего запуска требуются `prev_metric_median` и `cur_stable_streak`).

    Критерии оценки:
        1) Относительная половина ширины t-интервала мала:
           ((верх - низ)/2) / |медиана| ≤ r_target.
           Это означает, что коридор неопределённости относительно уровня
           метрики уже достаточно узок
        2) Медиана почти не меняется относительно предыдущего шага:
           |сдвиг медианы| / |медиана| ≤ delta_target

    Параметр `consecutive` требует, чтобы оба условия выполнялись указанное
    число шагов подряд - так мы избегаем преждевременной остановки
    из-за случайных колебаний
    """

    metric_array = extract_metric(results, metric)

    eps = 1e-12
    n_total = len(metric_array)

    sub = metric_array[:]
    lo, hi = predictive_interval_t(sub, alpha=alpha)
    half = 0.5 * (hi - lo)
    metric_median = float(np.median(sub))
    rel_half = half / max(abs(metric_median), eps)
    rel_delta = (
        np.inf
        if prev_metric_median is None
        else abs(metric_median - prev_metric_median) / max(abs(metric_median), eps)
    )

    ok = (rel_half <= r_target) and (prev_metric_median is not None and rel_delta <= delta_target)
    stable_streak = (cur_stable_streak + 1) if ok else 0
    stability_achieved = stable_streak >= consecutive

    logger.info("ШАГ ОЦЕНКИ ДАННЫХ")
    rd_txt = "-" if prev_metric_median is None else f"{rel_delta:.4f}"
    logger.info(
        f"metric={metric} | n={n_total} | median={metric_median:.3f} | tPI=[{lo:.3f},{hi:.3f}] "
        f"| rel_half={rel_half:.4f} | rel_delta={rd_txt} | ok={ok} | streak={stable_streak}"
    )
    if stability_achieved:
        logger.info("СТАБИЛЬНОСТЬ ДОСТИГНУТА")
    else:
        logger.info("СТАБИЛЬНОСТЬ НЕ ДОСТИГНУТА")
    return stability_achieved, metric_array, metric_median, stable_streak


def calc_reliability(
        metric_array: np.ndarray,
        alpha: float = 0.05,  # Уровень α (по умолчанию 0.05 → 95% предиктивный интервал)
        boot_b: int = 5000,  # Число пересэмплирований для бутстрэпа
        seed: int | None = None,  # Зерно случайности для методов со сплитом
) -> tuple[float, float, float]:
    """Расчёт наиболее правдоподобного значения на основании стабильной выборки данных"""

    if seed is None:
        seed = random.getrandbits(128)

    # Базовые характеристики и тесты формы (для понимания, когда t-модель уместна)
    desc = descriptive_stats(metric_array)
    # Шапиро–Уилк нормальность
    sh_stat, sh_p = stats.shapiro(metric_array) if len(metric_array) <= 5000 else (np.nan, np.nan)
    # Андерсон–Дарлинг - чувствителен к хвостам
    ad_stat, _, _ = stats.anderson(metric_array, dist="norm")

    logger.info(f"Базовые статистики метрики (n={len(metric_array)}, α={alpha})")
    for k, v in desc.items():
        logger.info(f"{k}: {v}")
    logger.info(f"Shapiro p={sh_p:.3g} ; Anderson stat={ad_stat:.3f}")

    # Интервалы (разные подходы)
    tpi   = predictive_interval_t(metric_array, alpha=alpha)
    qpi   = robust_pi_quantiles(metric_array, alpha=alpha)
    cpi   = split_conformal_pi(metric_array, alpha=alpha, seed=seed)
    lnpi  = lognormal_pi(metric_array, alpha=alpha)
    hdi   = kde_hdi(metric_array, alpha=alpha)
    boot  = bootstrap_pi(metric_array, alpha=alpha, B=boot_b, seed=seed)
    jack  = jackknife_plus_pi(metric_array, alpha=alpha)
    asymc = split_conformal_asymmetric(metric_array, alpha=alpha, seed=seed)
    yjpi  = yeojohnson_pi(metric_array, alpha=alpha)

    intervals: dict[str, tuple[float, float]] = {
        "t-PI": tpi,
        "quantile-PI": qpi,
        "conformal-PI": cpi,
        "lognormal-PI": lnpi,
        "kde-HDI": hdi,
        "bootstrap-PI": boot,
        "jackknife+-PI": jack,
        "asym-conformal-PI": asymc,
        "yeojohnson-PI": yjpi,
    }

    # Эмпирическое покрытие LOO по каждому методы
    coverages: dict[str, float] = {}
    coverages["t-PI"]              = loo_coverage(metric_array, predictive_interval_t, alpha=alpha)
    coverages["quantile-PI"]       = loo_coverage(metric_array, robust_pi_quantiles, alpha=alpha)
    coverages["conformal-PI"]      = loo_coverage(metric_array, split_conformal_pi, alpha=alpha, seed=seed)
    coverages["jackknife+-PI"]     = loo_coverage(metric_array, jackknife_plus_pi, alpha=alpha)
    coverages["asym-conformal-PI"] = loo_coverage(metric_array, split_conformal_asymmetric, alpha=alpha, seed=seed)
    coverages["bootstrap-PI"]      = loo_coverage(metric_array, bootstrap_pi, alpha=alpha, B=boot_b, seed=seed)

    logger.info("ПРЕДИКТИВНЫЕ ИНТЕРВАЛЫ (ширина и покрытие LOO, если применимо)")
    for name, (lo, hi) in intervals.items():
        w = interval_width((lo, hi))
        cov = coverages.get(name, np.nan)
        cov_txt = f"  LOO cover={cov:.3f}" if not np.isnan(cov) else ""
        logger.info(f"{name:17s} [{lo:.6g}, {hi:.6g}]  width={w:.6g}{cov_txt}")

    # Диагностика t-модели через PIT
    u = pit_values_t_predictive(metric_array)
    ks_stat, ks_p = stats.kstest(u, "uniform")  # сравнение распределения PIT с равномерным
    pit_cov = float(np.mean((u >= alpha/2) & (u <= 1 - alpha/2)))

    logger.info("=== PIT (t-модель) ===")
    logger.info(f"KS vs U(0,1): stat={ks_stat:.3f}, p={ks_p:.3g}; доля u∈({alpha/2:.3f},{1-alpha/2:.3f})={pit_cov:.3f}")

    #Автоматический выбор лучшего интервала и точек
    best_name, best_iv, why = select_best_interval(
        alpha=alpha, intervals=intervals, coverages=coverages, skew=desc["skew"], tol=0.03
    )
    best_lo, best_hi = best_iv

    # Наиболее правдоподобные точки: HSM (робастная мода), мода по KDE, медиана
    mode_kde = kde_mode(metric_array)
    mode_hsm = half_sample_mode(metric_array)
    median   = float(np.median(metric_array))

    logger.info("АВТО-ВЫБОР ЛУЧШЕГО ИНТЕРВАЛА")
    logger.info(f"Лучший метод: {best_name}")
    logger.info(f"MIN={best_lo:.6g}, MAX={best_hi:.6g}")
    logger.info(f"Наиболее правдоподобное (HSM)={mode_hsm:.6g}; (мода KDE)={mode_kde:.6g}; (медиана)={median:.6g}")
    logger.info(f"Обоснование: {why}")
    return mode_hsm, best_lo, best_hi


def find_closest_result(
        results: list[dict],
        metric_reliable: float,
        metric_best_max: float,
        metric: str = "weight",
) -> dict:
    """Поиск ближайшего к правдоподобному значению результата, не превышающего лучшее максимальное"""

    closest_idx = 0
    closest_diff = metric_best_max
    for i, result in enumerate(results):
        metric_value = result["summary"][metric]
        weight_diff = abs(metric_value - metric_reliable)
        if weight_diff < closest_diff and metric_value < metric_best_max:
            closest_idx = i
            closest_diff = weight_diff
    closest_result = results[closest_idx]

    return closest_result
