import json
import os
import tempfile
import unittest
from unittest.mock import patch

import taximeter


def make_trip(state, last_change=1000.0):
    """Build a trip dictionary the same way start_trip() does."""
    return {
        "state": state,
        "last_change": last_change,
        "total": 0.0,
        "start_time": "2026-11-06T10:00:00",
    }


class TestFareCalculation(unittest.TestCase):
    @patch("taximeter.time.time")
    def test_stopped_fare(self, mock_time):
        mock_time.return_value = 1010.0  # 10 seconds later
        trip = make_trip("stopped")
        taximeter.update_fare(trip)
        self.assertAlmostEqual(trip["total"], 10 * taximeter.RATE_STOPPED)

    @patch("taximeter.time.time")
    def test_moving_fare(self, mock_time):
        mock_time.return_value = 1010.0
        trip = make_trip("moving")
        taximeter.update_fare(trip)
        self.assertAlmostEqual(trip["total"], 10 * taximeter.RATE_MOVING)

    @patch("taximeter.time.time")
    def test_fare_across_state_change(self, mock_time):
        trip = make_trip("stopped")
        mock_time.return_value = 1010.0  # 10 s stopped
        taximeter.change_state(trip, "moving")
        mock_time.return_value = 1020.0  # then 10 s moving
        taximeter.update_fare(trip)
        expected = 10 * taximeter.RATE_STOPPED + 10 * taximeter.RATE_MOVING
        self.assertAlmostEqual(trip["total"], expected)

    @patch("taximeter.time.time")
    def test_same_state_changes_nothing(self, mock_time):
        mock_time.return_value = 1010.0
        trip = make_trip("stopped")
        taximeter.change_state(trip, "stopped")
        self.assertEqual(trip["total"], 0.0)
        self.assertEqual(trip["last_change"], 1000.0)

    @patch("taximeter.time.time")
    def test_zero_seconds_costs_nothing(self, mock_time):
        mock_time.return_value = 1000.0
        trip = make_trip("moving")
        taximeter.update_fare(trip)
        self.assertEqual(trip["total"], 0.0)


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "config.json")

    def write_config(self, text):
        with open(self.path, "w") as file:
            file.write(text)

    def test_valid_config(self):
        self.write_config(json.dumps({"rate_stopped": 0.1, "rate_moving": 0.2}))
        with patch.object(taximeter, "CONFIG_FILE", self.path):
            self.assertEqual(taximeter.load_rates(), (0.1, 0.2))

    def test_missing_file_uses_defaults(self):
        with patch.object(taximeter, "CONFIG_FILE", self.path):  # file not created
            self.assertEqual(
                taximeter.load_rates(),
                (taximeter.DEFAULT_RATE_STOPPED, taximeter.DEFAULT_RATE_MOVING),
            )

    def test_broken_json_uses_defaults(self):
        self.write_config("this is not json")
        with patch.object(taximeter, "CONFIG_FILE", self.path):
            self.assertEqual(
                taximeter.load_rates(),
                (taximeter.DEFAULT_RATE_STOPPED, taximeter.DEFAULT_RATE_MOVING),
            )

    def test_negative_rate_uses_defaults(self):
        self.write_config(json.dumps({"rate_stopped": -1, "rate_moving": 0.05}))
        with patch.object(taximeter, "CONFIG_FILE", self.path):
            self.assertEqual(
                taximeter.load_rates(),
                (taximeter.DEFAULT_RATE_STOPPED, taximeter.DEFAULT_RATE_MOVING),
            )


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "trips.json")

    def test_no_file_gives_empty_history(self):
        with patch.object(taximeter, "HISTORY_FILE", self.path):
            self.assertEqual(taximeter.load_history(), [])

    def test_save_and_load_trip(self):
        trip = make_trip("stopped")
        trip["total"] = 0.456
        with patch.object(taximeter, "HISTORY_FILE", self.path):
            taximeter.save_trip(trip)
            history = taximeter.load_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["start"], "2026-11-06T10:00:00")
        self.assertEqual(history[0]["total_eur"], 0.46)  # rounded to cents

    def test_two_trips_are_both_kept(self):
        with patch.object(taximeter, "HISTORY_FILE", self.path):
            taximeter.save_trip(make_trip("stopped"))
            taximeter.save_trip(make_trip("moving"))
            self.assertEqual(len(taximeter.load_history()), 2)

    def test_corrupted_file_gives_empty_history(self):
        with open(self.path, "w") as file:
            file.write("{ broken")
        with patch.object(taximeter, "HISTORY_FILE", self.path):
            self.assertEqual(taximeter.load_history(), [])


if __name__ == "__main__":
    unittest.main()