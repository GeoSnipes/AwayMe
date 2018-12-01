import time

class CodeTimer:
    def __init__(self, name=None):
        self.name = " '"  + name + "'" if name else ''

    def __enter__(self):
        self.start = time.clock()

    def __exit__(self, exc_type, exc_value, traceback):
        timenow = time.clock()
        self.took = round((timenow - self.start) * 1000.0, 4)
        print('Code block' + self.name + ' took: ' + str(self.took) + ' ms')
        # print(exc_type, exc_value, traceback)

if __name__ =='__main__':
    with CodeTimer('loop 1'):
        for i in range(100000):
            pass

    with CodeTimer('loop 2'):
        for i in range(100000):
            pass
