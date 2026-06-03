# Christopher Lee Crader - ccrader@uw.edu
# Most of this was generated with Claude - I just corrected
# a couple errors and made some modifications.
import sys

from commander import Commander
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Log, Static
from textual.containers import Horizontal, Vertical



class SerialTesterApp(App):
    CSS = """
    ListView { border: solid purple; }
    Log { border: solid purple; }
    #status { border: solid gold; padding: 0 1; }
    """

    def compose(self) -> ComposeResult:
        self.commander = Commander()
        yield Header()
        with Horizontal():
            with Vertical():
                yield ListView(
                    *[ListItem(Label(cmd), name=cmd) for cmd in self.commander.command_list],
                    id="command_list"
                )
            yield Log(id="output")
        yield Static(self.commander.connection_status, id="status")
        yield Input(placeholder="Custom command...", id="custom_input")
        yield Button("Send Selected", id="send_named")
        yield Button("Send Custom", id="send_custom")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        log = self.query_one("#output", Log)
        inp = self.query_one("#custom_input", Input)

        if event.button.id == "send_named":
            lv = self.query_one("#command_list", ListView)
            if lv.highlighted_child:
                cmd = lv.highlighted_child.name
                self.commander.send_command(cmd)
                response = self.commander.read_response()
                log.write_line(f"> {cmd}\n  Response: {response or '(none)'}")
        elif event.button.id == "send_custom":
            cmd = inp.value.strip()
            if cmd:
                self.commander.send_command(cmd, custom=True)
                response = self.commander.read_response()
                log.write_line(f"> (custom) {cmd!r}\n  Response: {response or '(none)'}")
                inp.clear()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if cmd:
            self.commander.send_command(cmd, custom=True)
            response = self.commander.read_response()
            (self.query_one("#output", Log)
                .write_line(f"> (custom) {cmd!r}\n  Response: {response or '(none)'}"))
            event.input.clear()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        cmd = event.item.name
        self.commander.send_command(cmd)
        response = self.commander.read_response()
        (self.query_one("#output", Log)
            .write_line(f"> {cmd}\n  Response: {response or '(none)'}"))


if __name__ == "__main__":
    if sys.prefix == sys.base_prefix:
        print("Virtual env not active. Run:")
        print("Make sure it's activated and install")
        print("textual and pyserial inside.")
        sys.exit(1)
    SerialTesterApp().run()