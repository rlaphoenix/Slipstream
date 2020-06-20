class Progress:
    def __init__(self):
        self.progress = 0
        self.c = None

    def set_c(self, js):
        # todo ; rename function to set_js_callback to be more descriptive
        self.c = js
