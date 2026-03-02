# feedback/session_memory.py
import sqlite3
import json
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass
import numpy as np
from loguru import logger

@dataclass
class Session:
    timestamp: datetime
    features: Dict[str, float]
    direction: str
    outcome: str
    pnl: float

class SessionMemory:
    def __init__(self, db_path: str = "sessions.db", history_limit: int = 200):
        self.db_path = db_path
        self.history_limit = history_limit
        self._init_db()
        logger.info(f"✅ SessionMemory 初始化完成（保留最近{history_limit}轮）")

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                features TEXT,
                direction TEXT,
                outcome TEXT,
                pnl REAL
            )
        ''')
        conn.commit()
        conn.close()

    def add_session(self, features: Dict, direction: str, outcome: str, pnl: float):
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO sessions (timestamp, features, direction, outcome, pnl) VALUES (?, ?, ?, ?, ?)",
                     (datetime.now().isoformat(), json.dumps(features), direction, outcome, pnl))
        conn.commit()
        conn.close()

    def get_historical_bias(self, current_features: Dict) -> float:
        """返回历史相似胜率 bias (0.5 = 中性)"""
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT features, direction, outcome FROM sessions ORDER BY timestamp DESC LIMIT ?", 
                           (self.history_limit,)).fetchall()
        conn.close()

        if not rows:
            return 0.5

        sessions = []
        curr_vec = np.array(list(current_features.values()))
        for row in rows:
            feats = json.loads(row[0])
            vec = np.array(list(feats.values()))
            dist = np.linalg.norm(curr_vec - vec)
            sessions.append((dist, row[1], row[2]))  # dist, direction, outcome

        sessions.sort(key=lambda x: x[0])
        top_k = sessions[:30]
        yes_wins = sum(1 for _, dir, out in top_k if dir == "YES" and out == "WIN")
        total = len([x for _, _, out in top_k if out != "PENDING"])
        return yes_wins / total if total > 0 else 0.5
