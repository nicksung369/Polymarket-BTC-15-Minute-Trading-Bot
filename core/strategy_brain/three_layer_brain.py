# core/strategy_brain/three_layer_brain.py
from .voting_engine import VotingEngine
from feedback.session_memory import SessionMemory
from execution.defense_sentinel import DefenseSentinel
from loguru import logger

class ThreeLayerBrain:
    def __init__(self):
        self.memory = SessionMemory()
        self.voter = VotingEngine()
        self.sentinel = DefenseSentinel()
        logger.info("🚀 ThreeLayerBrain 三层系统已就绪！")

    def decide(self, signals, features: dict, price, time_left, spread, cvd_agree, volatile, margin_ok):
        bias = self.memory.get_historical_bias(features)
        voted = self.voter.vote(signals, bias)
        size, go = self.sentinel.decide_position(voted, price, time_left, spread, cvd_agree, volatile, margin_ok)
        return voted, size, go
