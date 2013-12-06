class Media(object):
    _instance = None

    def __init__(self):
        self.folders = []
    def add(self, folder):
        self.folders.append(folder)

def get():
    if Media._instance is None:
        Media._instance = Media()
    return Media._instance

def add(folder):
    get().add(folder)

def folders():
    return get().folders
