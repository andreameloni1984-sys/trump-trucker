import unittest
from sputnik_focused_trader import analyze_focused_market


def candles(direction="up", count=240):
    rows=[]
    price=100.0
    for i in range(count):
        step = 0.25 if direction == "up" else -0.25 if direction == "down" else (0.25 if i%2 else -0.25)
        nxt=price+step
        rows.append({"open":price,"high":max(price,nxt)+0.1,"low":min(price,nxt)-0.1,"close":nxt,"volume":1000+i})
        price=nxt
    return rows


class FocusedTraderTests(unittest.TestCase):
    def test_requires_200_complete_candles(self):
        result=analyze_focused_market("GOLD", candles(count=100))
        self.assertEqual(result["status"], "INSUFFICIENT_DATA")
        self.assertEqual(result["direction"], "NEUTRAL")

    def test_uptrend_selects_long(self):
        result=analyze_focused_market("WTI", candles("up"))
        self.assertEqual(result["direction"], "LONG")
        self.assertEqual(result["status"], "DIRECTIONAL")
        self.assertIsNotNone(result["atr14"])

    def test_downtrend_selects_short(self):
        result=analyze_focused_market("GOLD", candles("down"))
        self.assertEqual(result["direction"], "SHORT")

    def test_mixed_structure_does_not_force_direction(self):
        result=analyze_focused_market("BRENT", candles("mixed"))
        self.assertEqual(result["direction"], "NEUTRAL")

    def test_invalid_candles_are_ignored(self):
        rows=candles()
        rows.extend([{"close":float("nan")}, {"open":2,"high":1,"low":3,"close":2}])
        result=analyze_focused_market("GOLD", rows)
        self.assertEqual(result["candles_used"], 240)


if __name__ == "__main__":
    unittest.main()
