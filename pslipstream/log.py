class Log:
    def __init__(self):
        self.entries = []
        self.js = None
        self.max_entries = 100

    def set_js(self, js):
        """
        Set a callback to JavaScript code for communication.
        :param js: Callback function set by JavaScript
        :return: Initial log contents
        """
        # todo ; rename function to set_js_callback to be more descriptive
        self.js = js
        self.read_all()

    def write(self, entry, echo=True):
        self.entries.append(entry)
        while len(self.entries) > self.max_entries:
            self.entries.pop(0)
        if echo:
            print(entry.strip())
        if self.js:
            # update js log
            self.read_all()

    def read_all(self):
        entries = "\n".join(self.entries).strip()
        if self.js:
            self.js.Call(entries)
        return entries
