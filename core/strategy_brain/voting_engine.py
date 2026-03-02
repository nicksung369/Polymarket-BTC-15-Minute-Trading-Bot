# core/strategy_brain/voting_engine.py
from typing import List, Dict
from dataclasses import dataclass
from loguru import logger
from core.strategy_brain.fusion_engine.signal_fusion import get_fusion_engine  # 原仓库已有

@dataclass
class VotedSignal:
    direction: str
    confidence: float
    score: float
    historical_bias: float

class VotingEngine:
    def __init__(self):
        self.fusion = get_fusion_engine()
        logger.info("✅ VotingEngine 已加载（融合原fusion_engine + 作者10条规则）")

    def vote(self, signals: List, session_bias: float = 0.5) -> VotedSignal:
        fused = self.fusion.fuse_signals(signals)
        if not fused:
            return VotedSignal("NO", 0.0, 0.0, session_bias)

        # 历史bias加强信心
        final_conf = fused.confidence * (1 + (session_bias - 0.5) * 0.6)
        direction = "YES" if fused.direction == "BULLISH" else "NO"
        return VotedSignal(direction, min(1.0, final_conf), fused.score, session_bias)
