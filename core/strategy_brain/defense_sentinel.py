# execution/defense_sentinel.py
from decimal import Decimal
from typing import Tuple
from loguru import logger
from .risk_engine import get_risk_engine  # 原仓库

class DefenseSentinel:
    def __init__(self):
        self.risk = get_risk_engine()

    def decide_position(self, voted, current_price: Decimal, time_left_sec: int,
                        spread: float, cvd_agree: bool, is_volatile: bool, margin_ok: bool) -> Tuple[Decimal, bool]:
        confidence = voted.confidence
        size = self.risk.calculate_position_size(float(confidence))  # 原risk方法

        # 作者精确5问题
        q1 = cvd_agree
        q2 = time_left_sec > 180
        q3 = spread < 0.008
        q4 = not is_volatile
        q5 = margin_ok
        passed = sum([q1, q2, q3, q4, q5])

        if passed < 4 or confidence < 0.65:
            logger.info(f"🛡️ Defense Sentinel 拒绝下单 ({passed}/5)")
            return Decimal("0"), False

        size = min(size * (1.0 if passed == 5 else 0.6), Decimal("3.0"))
        logger.info(f"🛡️ Defense Sentinel 通过 → {voted.direction} ${float(size):.2f}")
        return size, True
