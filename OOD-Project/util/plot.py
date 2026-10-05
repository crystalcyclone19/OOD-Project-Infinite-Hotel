import matplotlib.pyplot as plt


class Plot:
    def __init__(self):
        self.fig, self.ax = plt.subplots()


    def plot(self, x, x_label, y, y_label, color):
        self.ax.plot(x, y, color=color)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)


    def show(self):
        plt.show()