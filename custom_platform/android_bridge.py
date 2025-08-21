try:
    from jnius import autoclass
    from android import activity, mActivity
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    ANDROID = True
except ImportError:
    ANDROID = False

class AndroidHandler:
    def __init__(self):
        self._intent_url = None
        if ANDROID:
            self._process_intent()

    def _process_intent(self):
        """Check the intent that started the app."""
        intent = mActivity.getIntent()
        if intent.getAction() == Intent.ACTION_VIEW:
            uri = intent.getData()
            if uri:
                self._intent_url = uri.toString()

    def get_url_from_intent(self):
        """Returns the URL from the intent, if available."""
        return self._intent_url

    def open_url(self, url: str):
        """Opens the given URL in an external browser on Android."""
        if not ANDROID:
            print("Not on Android, cannot open URL via intent.")
            return

        try:
            uri = Uri.parse(url)
            intent = Intent(Intent.ACTION_VIEW, uri)
            # Create a chooser to ensure the user can select a browser
            chooser = Intent.createChooser(intent, "Open with...")
            chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            mActivity.startActivity(chooser)
        except Exception as e:
            print(f"Error opening URL on Android: {e}")
