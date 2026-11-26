"""Web interface for managing warehouse stock."""

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from math import isfinite
from urllib.parse import parse_qs, urlencode, urlsplit

from varasto import Varasto


class WarehouseServer(ThreadingHTTPServer):
    """HTTP server containing the warehouses managed by this process."""

    def __init__(self, server_address, request_handler):
        super().__init__(server_address, request_handler)
        self.warehouses = {}
        self.next_warehouse_id = 1


class WarehouseHandler(BaseHTTPRequestHandler):
    """Serve the warehouse list and handle warehouse and stock forms."""

    def do_GET(self):
        """Render the warehouse page."""
        message = parse_qs(urlsplit(self.path).query).get("message", [""])[0]
        self._send_page(message)

    def do_POST(self):
        """Create a warehouse or change its stock."""
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > 65536:
            self.send_error(413, "Request body too large")
            return

        form = parse_qs(self.rfile.read(content_length).decode("utf-8"))
        action = form.get("action", [""])[0]
        if action == "create":
            message = self._create_warehouse(form)
        elif action in ("add", "take"):
            message = self._update_stock(action, form)
        else:
            message = "Tuntematon toiminto."

        self.send_response(303)
        self.send_header("Location", f"/?{urlencode({'message': message})}")
        self.end_headers()

    def _create_warehouse(self, form):
        name = form.get("name", [""])[0].strip()
        capacity = self._number(form.get("capacity", [""])[0])
        if not name or capacity is None or capacity <= 0:
            return "Anna varastolle nimi ja positiivinen tilavuus."

        warehouse_id = str(self.server.next_warehouse_id)
        self.server.next_warehouse_id += 1
        self.server.warehouses[warehouse_id] = (name, Varasto(capacity))
        return f"Varasto {name} luotu."

    def _update_stock(self, action, form):
        warehouse = self.server.warehouses.get(
            form.get("warehouse_id", [""])[0]
        )
        amount = self._number(form.get("amount", [""])[0])
        if warehouse is None or amount is None or amount < 0:
            return "Tarkista varasto ja määrä."

        name, inventory = warehouse
        if action == "add":
            inventory.lisaa_varastoon(amount)
            return f"Varastoon {name} lisättiin tavaraa."

        taken = inventory.ota_varastosta(amount)
        return f"Varastosta {name} otettiin {taken:g}."

    @staticmethod
    def _number(value):
        try:
            number = float(value)
        except ValueError:
            return None
        return number if isfinite(number) else None

    def _send_page(self, message=""):
        warehouse_cards = []
        for warehouse_id, (name, inventory) in self.server.warehouses.items():
            safe_name = escape(name)
            warehouse_cards.append(
                f"""
                <article class="warehouse">
                  <h2>{safe_name}</h2>
                  <p>Saldo: <strong>{inventory.saldo:g}</strong> /
                     {inventory.tilavuus:g} litraa</p>
                  <p>Vapaata tilaa: {inventory.paljonko_mahtuu():g} litraa</p>
                  <div class="actions">
                    <form method="post">
                      <input type="hidden" name="action" value="add">
                      <input type="hidden" name="warehouse_id"
                             value="{warehouse_id}">
                      <label>Lisää (l)
                        <input type="number" name="amount" min="0"
                               step="any" required>
                      </label>
                      <button type="submit">Lisää tavaraa</button>
                    </form>
                    <form method="post">
                      <input type="hidden" name="action" value="take">
                      <input type="hidden" name="warehouse_id"
                             value="{warehouse_id}">
                      <label>Ota (l)
                        <input type="number" name="amount" min="0"
                               step="any" required>
                      </label>
                      <button type="submit">Ota tavaraa</button>
                    </form>
                  </div>
                </article>
                """
            )
        cards = "".join(warehouse_cards) or "<p>Varastoja ei ole vielä.</p>"
        safe_message = escape(message)
        page = f"""<!doctype html>
<html lang="fi">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Varastot</title>
    <style>
      body {{ font: 1rem system-ui, sans-serif; margin: 2rem auto;
             max-width: 800px; padding: 0 1rem; color: #17212b; }}
      input, button {{ font: inherit; padding: .45rem; }}
      label {{ display: grid; gap: .25rem; }}
      .warehouse {{ border: 1px solid #ccd5dc; border-radius: .5rem;
                    margin: 1rem 0; padding: 1rem; }}
      .actions {{ display: flex; flex-wrap: wrap; gap: 1rem; }}
      .actions form {{ display: flex; align-items: end; gap: .5rem; }}
      .message {{ background: #e8f3ec; padding: .75rem; }}
    </style>
  </head>
  <body>
    <h1>Varastonhallinta</h1>
    <p>Varastot ja niiden saldot. Määrät ilmoitetaan litroina.</p>
    <section>
      <h2>Luo varasto</h2>
      <form method="post">
        <input type="hidden" name="action" value="create">
        <label>Varaston nimi
          <input type="text" name="name" required maxlength="100">
        </label>
        <label>Tilavuus (l)
          <input type="number" name="capacity" min="0"
                 step="any" required>
        </label>
        <button type="submit">Luo varasto</button>
      </form>
    </section>
    <section>
      <h2>Varastot</h2>
      {f'<p class="message">{safe_message}</p>' if safe_message else ''}
      {cards}
    </section>
  </body>
</html>"""
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    """Start the warehouse web application on localhost."""
    server = WarehouseServer(("127.0.0.1", 8000), WarehouseHandler)
    print("Varastonhallinta: http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nPalvelin suljetaan.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
