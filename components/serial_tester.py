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
    Button {
        margin: 0 2;
    }
    ListView { border: solid purple; }
    Log { border: solid purple; }
    #button_container {
        align-horizontal: center;
        height: auto;
    }
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
        with Horizontal(id="button_container"):
            yield Button("Send Command", id="send_command")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        inp = self.query_one("#custom_input", Input)
        custom_cmd = inp.value.strip()

        if custom_cmd:
            self._send_and_log(custom_cmd, custom=True)
            inp.clear()
        else:
            lv = self.query_one("#command_list", ListView)
            if not lv.highlighted_child:
                return
            name = lv.highlighted_child.name
            assert name is not None
            self._send_and_log(name)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if cmd:
            self._send_and_log(cmd, custom=True)
            event.input.clear()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        name = event.item.name
        assert name is not None
        self._send_and_log(name)

    def on_mount(self) -> None:
        response = self.commander.read_response()
        if response:
            (self.query_one("#output", Log)
                .write_line(f"[startup] {response}"))
        else:
            (self.query_one("#output", Log)
                .write_line(f"[startup] No init message from device"))

    def _send_and_log(self, cmd: str, custom: bool = False) -> None:
        if custom:
            display = f"(custom) {cmd}"
            self.commander.send_command(cmd, custom=True)
        else:
            raw = self.commander.command_list[cmd]
            display = f"{cmd} → {raw!r}"
            self.commander.send_command(cmd)
        response = self.commander.read_response()
        (self.query_one("#output", Log)
            .write_line(f"> {display}\n  Response: {response or '(none)'}"))


if __name__ == "__main__":
    if sys.prefix == sys.base_prefix:
        print("Virtual env not active. Run:")
        print("Make sure it's activated and install")
        print("textual and pyserial inside.")
        sys.exit(1)
    SerialTesterApp().run()