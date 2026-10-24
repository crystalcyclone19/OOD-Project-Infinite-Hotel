import matplotlib.pyplot as plt
import util.math as m
import statistics as stat

class Graph:
    def __init__(self,
                title_size: int = 10,
                label_size: int = 10,
                tick_size: int = 9,
                legend_size: int = 9,
                report_size: int = 9,
        ):
        self.fig = None
        self.figures = {}

        self.title_size = title_size
        self.label_size = label_size
        self.tick_size = tick_size
        self.legend_size = legend_size
        self.report_size = report_size
        plt.rcParams["font.family"] = "Calibri"
        # Arial
        # Calibri 
        # DejaVu Sans

    def add_median_low_high_graph(self,figure_name:str,
                                  x :list, x_label :str,
                                  y:list, y_label:str,
                                  label: str,
                                  color: str,
                                  ): 
        if figure_name not in self.figures:
            self.figures[figure_name] = {
                "plots": [],
                "title": None,
                "report":None
            }
        self.figures[figure_name]["plots"].append({
            "x": x,
            "low":[min(lst) for lst in y],
            "high":[max(lst) for lst in y],
            "median":[stat.median(lst) for lst in y],
            "label": label,
            "color": color,
            "x_label": x_label,
            "y_label": y_label
        }) 

    def add_graph(
        self,
        figure_name: str,
        x: list,
        x_label: str,
        y: list,
        y_label: str,
        label: str,
        color: str,
    ):


        if figure_name not in self.figures:
            self.figures[figure_name] = {
                "plots": [],
                "title": None,
                "report":None
            }

        self.figures[figure_name]["plots"].append({
            "x": x,
            "y": y,
            "label": label,
            "color": color,
            "x_label": x_label,
            "y_label": y_label
        })

    def set_title(self, figure_name: str, title: str):
        if figure_name not in self.figures:
            self.figures[figure_name] = {
                "plots": [],
                "title": None,
                "report":None
            }
        self.figures[figure_name]["title"] = title

    def set_report(self, figure_name :str, report_text:str):
        if figure_name not in self.figures:
            self.figures[figure_name] = {
                "plots": [],
                "title": None,
                "report":None
            }
        self.figures[figure_name]["report"] = report_text
    
    def save(self, file_name:str):
         self.load()
         self.fig.savefig(f"graph/{file_name}.png", dpi=200, bbox_inches="tight")
         print(f"Export graph to graph/{file_name}.png...")
         plt.close(self.fig)

    def load(self):

        number_of_graphs = len(self.figures)
        self.fig = plt.figure(figsize=(16, 10))
        offsets = [(0, 10), (0, -16), (22, 0), (-22, 0)]

        # 2 rows:
        # row 0 = graph
        # row 1 = report
        #
        # number_of_graphs columns
        gs = self.fig.add_gridspec(
            2,
            number_of_graphs,
            height_ratios=[5, 3] # 1st occupied 5\8 space(Graph), 2nd occupied 3\8 space(Report)
        )
        # 2,numebr_of_graphs -->   ________________
                                # |  G1    |   G2  | 5 --
                                # |________|_______|    |--> 8
                                # |  R1    |   R2  | 3 --
                                # |________|_______|

        for i, (figure_name, figure) in enumerate(self.figures.items()):
            # =========================
            # Graph area(ax)
            # =========================
            ax = self.fig.add_subplot(gs[0, i])
            ax.set_xscale("log")

            for n, plot in enumerate(figure["plots"]):
                dx, dy = offsets[n % len(offsets)]
                box = dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8)

                # Error Graph
                if "low" in plot:
                    yerr = [[ me - lo for me,lo in zip(plot["median"],plot["low"])],
                            [ hi- me for me,hi in zip(plot["median"],plot["high"])]
                           ]

                    ax.errorbar(plot["x"],
                                plot["median"],
                                yerr=yerr,
                                marker="o",
                                color=plot["color"],
                                label=plot["label"]
                                )
                    

                    for xv, md, lo, hi in zip(plot["x"], plot["median"], plot["low"], plot["high"]):
                        # max: above the top of the bar
                        ax.annotate(f"max {hi:.2f}", (xv, hi), textcoords="offset points",
                                    xytext=(0, 6), ha="center", va="bottom",
                                    fontsize=self.tick_size - 1, color=plot["color"], bbox=box)
                        # min: below the bottom of the bar
                        ax.annotate(f"min {lo:.2f}", (xv, lo), textcoords="offset points",
                                    xytext=(0, -6), ha="center", va="top",
                                    fontsize=self.tick_size - 1, color=plot["color"], bbox=box)
                        # median: to the right of the dot
                        ax.annotate(f"med {md:.2f}", (xv, md), textcoords="offset points",
                                    xytext=(8, 0), ha="left", va="center",
                                    fontsize=self.tick_size - 1, color=plot["color"], bbox=box)
                    
                # Normal Graph
                else:
                    ax.plot(
                        plot["x"],
                        plot["y"],
                        color=plot["color"],
                          label=plot["label"]
                    )

                    for x,y in zip(plot["x"],plot["y"]):
                        ax.annotate(f"{y:.2f}",(x,y),textcoords="offset points",
                                    xytext=(dx,dy) ,ha="center",fontsize=self.tick_size,
                                    color=plot["color"],bbox=box    
                                    )

                ax.set_xlabel(plot["x_label"],fontsize=self.label_size)
                ax.set_ylabel(plot["y_label"],fontsize=self.label_size)


            # =========================
            # Title
            # =========================
            if figure["title"] is not None:
                ax.set_title(figure["title"],fontsize=self.title_size)   

            # =========================
            # X,Y
            # =========================
            ax.tick_params(axis="both", labelsize=self.tick_size)

            # =========================
            # Report area(ax)
            # =========================
            report_ax = self.fig.add_subplot(gs[1, i])

            # Hide the report area's axes
            report_ax.axis("off")

            if figure["report"] is not None:
                report_ax.text(
                    0,
                    -0.15,
                    figure["report"],
                    transform=report_ax.transAxes,
                    fontsize=self.report_size
                )

            # =========================
            # Grid
            # =========================
            # Legend
            ax.legend(fontsize=self.legend_size)

            # Grid
            ax.grid(
                True,
                which="major",
                linestyle=":",
                alpha=0.7
            )

            ax.grid(
                True,
                which="minor",
                linestyle="--",
                alpha=0.7
            )
    def show(self):
        self.load()
        plt.show()
    def clear(self):
        self.figures = {}

