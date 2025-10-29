from __future__ import annotations
from datetime import date, timedelta
from typing import List, Dict

from core.helpers import ensure_range
from core.services.revenue_service import revenue_series

def arima_forecast_series(resort:str|None, d1:date|None, d2:date|None, horizon:int=56) -> Dict[str, List[dict]]:
    """
    Returns:
      {
        "history": [{"date": "...", "value": ...}, ...],
        "forecast": [{"date": "...", "value": ...}, ...]
      }
    """
    try:
        import pandas as pd
        import numpy as np
        from statsmodels.tsa.arima.model import ARIMA
    except Exception as e:
        raise RuntimeError("statsmodels/pandas/numpy required. pip install statsmodels pandas numpy") from e

    d1, d2 = ensure_range(d1, d2, default_days=365)
    series = revenue_series(resort, d1, d2)  
    if not series:
        return {"history": [], "forecast": []}

    idx = sorted(series.keys())
    y = [series[dt] for dt in idx]
    s = pd.Series(y, index=pd.to_datetime(idx))

    model = ARIMA(s, order=(1,1,1))
    fit = model.fit(method_kwargs={"warn_convergence": False})

    future_idx = [idx[-1] + timedelta(days=i) for i in range(1, horizon+1)]
    fc = fit.forecast(steps=horizon)

    history = [{"date": d.isoformat(), "value": float(series[d])} for d in idx]
    forecast = [{"date": d.isoformat(), "value": float(v)} for d, v in zip(future_idx, fc)]

    return {"history": history, "forecast": forecast}
