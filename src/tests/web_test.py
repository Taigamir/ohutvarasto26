"""Tests for the warehouse web interface."""

import threading
import unittest
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from index import WarehouseHandler, WarehouseServer


class TestWarehouseWeb(unittest.TestCase):
    """Exercise warehouse management through HTTP."""

    def setUp(self):
        self.server = WarehouseServer(
            ("127.0.0.1", 0), WarehouseHandler
        )
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def get_page(self):
        """Return the rendered warehouse page."""
        with urlopen(self.url) as response:
            return response.read().decode("utf-8")

    def submit(self, **fields):
        """Submit a form and return the page after its redirect."""
        request = Request(
            self.url,
            data=urlencode(fields).encode("utf-8"),
            method="POST",
        )
        with urlopen(request) as response:
            return response.read().decode("utf-8")

    def create_warehouse(self, name, capacity):
        """Create a warehouse with the provided details."""
        return self.submit(action="create", name=name, capacity=capacity)

    def update_stock(self, action, warehouse_id, amount):
        """Submit a stock change for one warehouse."""
        return self.submit(
            action=action, warehouse_id=warehouse_id, amount=amount
        )

    def assert_balance(self, page, balance, capacity):
        """Check that the page shows a warehouse's balance and capacity."""
        normalized_page = " ".join(page.split())
        self.assertIn(
            f"Saldo: <strong>{balance}</strong> / {capacity} litraa",
            normalized_page,
        )

    def assert_balances(self, page, *balances):
        """Check multiple warehouse balances on a single page."""
        for balance, capacity in balances:
            self.assert_balance(page, balance, capacity)

    def assert_message(self, page, message):
        """Check that the page displays the expected feedback."""
        self.assertIn(message, page)

    def test_create_warehouses_and_manage_stock(self):
        """Create multiple warehouses, then add and withdraw goods."""
        self.create_warehouse("Mehu", "10")
        self.create_warehouse("Olut", "20")
        page = self.get_page()
        self.assert_balances(page, ("0", "10"), ("0", "20"))

        self.update_stock("add", "1", "8")
        page = self.update_stock("take", "1", "3")
        self.assert_balance(page, "5", "10")
        self.assert_message(page, "Varastosta Mehu otettiin 3.")
        self.assert_balance(page, "0", "20")

    def test_reject_invalid_warehouse_and_stock_values(self):
        """Reject invalid capacity and non-finite stock values."""
        page = self.create_warehouse("Tyhjä", "0")
        self.assert_message(
            page, "Anna varastolle nimi ja positiivinen tilavuus."
        )
        self.assertNotIn("Tyhjä</h2>", page)

        self.create_warehouse("Varasto", "10")
        page = self.update_stock("add", "1", "nan")
        self.assert_message(page, "Tarkista varasto ja määrä.")
        self.assert_balance(page, "0", "10")

    def test_warehouse_names_are_escaped(self):
        """Escape warehouse names before inserting them into HTML."""
        self.create_warehouse("<script>alert(1)</script>", "10")
        page = self.get_page()
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertNotIn("<script>alert(1)</script>", page)


if __name__ == "__main__":
    unittest.main()
