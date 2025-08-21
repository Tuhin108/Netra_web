import threading
from functools import partial

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard

from ui.popup import BottomProgressPopup
from core.scanner import scan_url

class MainApp(App):
    def __init__(self, url_to_scan=None, platform_handler=None, **kwargs):
        super().__init__(**kwargs)
        self.url_to_scan = url_to_scan
        self.platform_handler = platform_handler
        self.popup = None

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=50)
        layout.add_widget(Label(
            text="Netra",
            font_size='24sp',
            halign='center'
        ))
        layout.add_widget(Label(
            text="Ready to intercept URLs.\n(This window can be hidden in a real app)",
            font_size='16sp',
            halign='center',
            color=(0.7, 0.7, 0.7, 1)
        ))
        return layout

    def on_start(self):
        if self.url_to_scan:
            self.trigger_scan(self.url_to_scan)

    def trigger_scan(self, url):
        if self.popup and self.popup.parent:
            self.popup.dismiss()

        self.popup = BottomProgressPopup()
        self.popup.show(0.05, "Starting scan...")

        # Run scanner in a separate thread
        scan_thread = threading.Thread(
            target=self._run_scan_thread,
            args=(url,)
        )
        scan_thread.daemon = True
        scan_thread.start()

    def _run_scan_thread(self, url):
        """Worker thread function."""
        trace_result, verdict = scan_url(url, self._update_progress_from_thread)
        
        # Schedule the final update on the main thread
        Clock.schedule_once(
            lambda dt: self._complete_scan(verdict, trace_result.final_url or url)
        )

    def _update_progress_from_thread(self, progress, message):
        """Called from the worker thread to update UI."""
        if self.popup:
            # partial() is used to pass arguments to the scheduled function
            update_func = partial(self.popup.update_state, progress, message)
            Clock.schedule_once(update_func)

    def _complete_scan(self, verdict, final_url):
        """Called on the main thread to finalize the UI."""
        if self.popup:
            self.popup.complete(
                verdict.label,
                final_url,
                self.open_url,
                self.copy_url
            )

    def open_url(self, url):
        if self.platform_handler:
            self.platform_handler.open_url(url)
        print(f"Requesting to open URL: {url}")

    def copy_url(self, url):
        Clipboard.copy(url)
        print(f"Copied to clipboard: {url}")
        if self.popup:
            # Optionally show a small confirmation
            self.popup.update_state(1.0, "URL Copied!")
