"""
System Tray Manager for DataCollector.
Provides background system tray hosting via pystray, allowing the application
to continue recording even when the main GUI window is closed.
"""

import threading
from typing import Callable, Optional
from PIL import Image, ImageDraw

class TrayManager:
    def __init__(
        self,
        on_show_window: Optional[Callable[[], None]] = None,
        on_toggle_recording: Optional[Callable[[], None]] = None,
        on_export: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None,
        app_name: str = "DataCollector"
    ):
        self.on_show_window = on_show_window
        self.on_toggle_recording = on_toggle_recording
        self.on_export = on_export
        self.on_exit = on_exit
        self.app_name = app_name

        self._icon = None
        self._is_recording = True
        self._thread: Optional[threading.Thread] = None

    def _create_icon_image(self, is_active: bool = True) -> Image.Image:
        """Create a dynamic colored circle icon (Green for active, Amber for paused)."""
        width = 64
        height = 64
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        # Background disk
        bg_color = "#10B981" if is_active else "#F59E0B"
        dc.ellipse([8, 8, width - 8, height - 8], fill=bg_color, outline="#1E293B", width=4)
        # Inner dot
        dc.ellipse([24, 24, width - 24, height - 24], fill="#FFFFFF")
        return image

    def set_recording_state(self, is_recording: bool):
        self._is_recording = is_recording
        if self._icon:
            self._icon.icon = self._create_icon_image(is_recording)

    def _menu_show(self, icon, item):
        if self.on_show_window:
            self.on_show_window()

    def _menu_toggle(self, icon, item):
        if self.on_toggle_recording:
            self.on_toggle_recording()

    def _menu_export(self, icon, item):
        if self.on_export:
            self.on_export()

    def _menu_exit(self, icon, item):
        if self.on_exit:
            self.on_exit()
        self.stop()

    def start(self):
        try:
            import pystray
            menu = pystray.Menu(
                pystray.MenuItem("Open Dashboard", self._menu_show, default=True),
                pystray.MenuItem("Pause/Resume Recording", self._menu_toggle),
                pystray.MenuItem("Export Dataset", self._menu_export),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit DataCollector", self._menu_exit)
            )
            self._icon = pystray.Icon(
                self.app_name,
                self._create_icon_image(self._is_recording),
                f"{self.app_name} (Background Telemetry Active)",
                menu
            )
            self._thread = threading.Thread(target=self._icon.run, daemon=True)
            self._thread.start()
        except Exception as e:
            # Fallback for environments without tray support
            print(f"System Tray notification: {e}")

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None
