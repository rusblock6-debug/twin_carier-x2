def koef_vlazhnosti(percent: float) -> float:
    """
    Возвращает коэффициент по влажности грунта (%)
    0–5%   → 0.8 (сухой)
    5–15%  → 1.0 (оптимальная)
    15–30% → 1.2 (влажный)
    30–50% → 1.5–2.0 (глинистый)
    """
    if percent <= 5:
        return 0.8
    if percent <= 15:
        return 1.25
    if percent <= 30:
        return 1.35
    p = (percent - 30) / 20
    return 1.5 + 0.5 * min(max(p, 0), 1)


