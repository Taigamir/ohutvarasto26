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
        with urlopen(self.url) as response:
            return response.read().decode("utf-8")

    def submit(self, **fields):
        request = Request(
            self.url,
            data=urlencode(fields).encode("utf-8"),
            method="POST",
        )
        with urlopen(request) as response:
            return response.read().decode("utf-8")

    def test_create_warehouses_and_manage_stock(self):
        self.submit(action="create", name="Mehu", capacity="10")
        self.submit(action="create", name="Olut", capacity="20")
        page = self.get_page()
        self.assertIn("Mehu", page)
        self.assertIn("Olut", page)

        self.submit(
            action="add", warehouse_id="1", amount="8"
        )
        page = self.submit(
            action="take", warehouse_id="1", amount="3"
        )
        self.assertIn("Saldo: <strong>5</strong> /", page)
        self.assertIn("Varastosta Mehu otettiin 3.", page)
        self.assertIn("Saldo: <strong>0</strong> / 20 litraa", page)

    def test_reject_invalid_warehouse_and_stock_values(self):
        page = self.submit(action="create", name="Tyhjä", capacity="0")
        self.assertIn("Anna varastolle nimi ja positiivinen tilavuus.", page)
        self.assertNotIn("Tyhjä</h2>", page)

        self.submit(action="create", name="Varasto", capacity="10")
        page = self.submit(
            action="add", warehouse_id="1", amount="nan"
        )
        self.assertIn("Tarkista varasto ja määrä.", page)
        self.assertIn("Saldo: <strong>0</strong> / 10 litraa", page)

    def test_warehouse_names_are_escaped(self):
        self.submit(
            action="create", name="<script>alert(1)</script>", capacity="10"
        )
        page = self.get_page()
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertNotIn("<script>alert(1)</script>", page)


if __name__ == "__main__":
    unittest.main()
