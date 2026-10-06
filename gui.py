import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from project import black_scholes, monte_carlo, delta, gamma


# (schlüssel, beschriftung, standardwert)
FIELDS = [
    ("S", "Stock price (S)", "100"),
    ("K", "Strike price (K)", "100"),
    ("T", "Time to maturity in years (T)", "1"),
    ("r", "Risk-free rate (r)", "0.05"),
    ("sigma", "Volatility (sigma)", "0.2"),
]

RESULTS = ["Black-Scholes price", "Monte Carlo price", "Difference", "Delta", "Gamma"]


class OptionPricerApp:
    def __init__(self, root):  # baut das fenster mit eingaben, resultaten und grafiken auf
        self.root = root
        root.title("Option Pricer: Black-Scholes vs. Monte Carlo")

        panel = ttk.Frame(root, padding=10)
        panel.grid(row=0, column=0, sticky="n")

        # eingabefelder
        self.entries = {}
        for i, (key, label, default) in enumerate(FIELDS):
            ttk.Label(panel, text=label).grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(panel, width=12)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=(8, 0), pady=2)
            self.entries[key] = entry

        row = len(FIELDS)
        ttk.Label(panel, text="Simulations (n)").grid(row=row, column=0, sticky="w", pady=2)
        self.n_entry = ttk.Entry(panel, width=12)
        self.n_entry.insert(0, "100000")
        self.n_entry.grid(row=row, column=1, padx=(8, 0), pady=2)

        # auswahl call oder put
        ttk.Label(panel, text="Option type").grid(row=row + 1, column=0, sticky="w", pady=2)
        self.option = tk.StringVar(value="call")
        types = ttk.Frame(panel)
        types.grid(row=row + 1, column=1, padx=(8, 0), sticky="w")
        ttk.Radiobutton(types, text="Call", variable=self.option, value="call").pack(side="left")
        ttk.Radiobutton(types, text="Put", variable=self.option, value="put").pack(side="left")

        ttk.Button(panel, text="Calculate", command=self.calculate).grid(
            row=row + 2, column=0, columnspan=2, sticky="ew", pady=10
        )
        root.bind("<Return>", lambda event: self.calculate())  # enter-taste rechnet auch

        # resultate
        box = ttk.LabelFrame(panel, text="Results", padding=10)
        box.grid(row=row + 3, column=0, columnspan=2, sticky="ew")
        self.result_labels = {}
        for i, name in enumerate(RESULTS):
            ttk.Label(box, text=name + ":").grid(row=i, column=0, sticky="w")
            value = ttk.Label(box, text="-", width=10, anchor="e")
            value.grid(row=i, column=1, sticky="e")
            self.result_labels[name] = value

        # grafiken
        self.figure = Figure(figsize=(10, 4.5), dpi=100)
        self.ax_price = self.figure.add_subplot(1, 2, 1)
        self.ax_conv = self.figure.add_subplot(1, 2, 2)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10)

        self.calculate()  # direkt mit den standardwerten starten

    def read_inputs(self):  # liest alle eingaben und gibt sie als zahlen zurück
        values = {}
        for key, label, _ in FIELDS:
            try:
                values[key] = float(self.entries[key].get())
            except ValueError:
                raise ValueError(f"{label} must be a number")
        try:
            n = int(self.n_entry.get())
        except ValueError:
            raise ValueError("Simulations (n) must be a whole number")
        if n <= 0:
            raise ValueError("Simulations (n) must be positive")
        return values, n

    def calculate(self):  # rechnet alles mit den funktionen aus project.py und aktualisiert die anzeige
        try:
            v, n = self.read_inputs()
            S, K, T, r, sigma = v["S"], v["K"], v["T"], v["r"], v["sigma"]
            option = self.option.get()
            bs = black_scholes(S, K, T, r, sigma, option)
            mc = monte_carlo(S, K, T, r, sigma, option, n=n, seed=None)
            d = delta(S, K, T, r, sigma, option)
            g = gamma(S, K, T, r, sigma)
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        results = [bs, mc, abs(bs - mc), d, g]
        for name, value in zip(RESULTS, results):
            self.result_labels[name].config(text=f"{value:.4f}")

        self.plot_price_curve(S, K, T, r, sigma, option, bs)
        self.plot_convergence(S, K, T, r, sigma, option, n, bs, mc)
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_price_curve(self, S, K, T, r, sigma, option, price):  # optionswert heute vs. payoff am verfall
        ax = self.ax_price
        ax.clear()
        low, high = 0.5 * min(S, K), 1.5 * max(S, K)
        steps = 200
        stock_prices = [low + (high - low) * i / steps for i in range(steps + 1)]
        values = [black_scholes(s, K, T, r, sigma, option) for s in stock_prices]
        if option == "call":
            payoffs = [max(s - K, 0) for s in stock_prices]
        else:
            payoffs = [max(K - s, 0) for s in stock_prices]

        ax.plot(stock_prices, values, label="Value today (Black-Scholes)")
        ax.plot(stock_prices, payoffs, "--", label="Payoff at maturity")
        ax.axvline(K, color="gray", linestyle=":", linewidth=1, label="Strike")
        ax.scatter([S], [price], color="red", zorder=3, label=f"Current price: {price:.2f}")
        ax.set_title(f"{option.capitalize()} value vs. stock price")
        ax.set_xlabel("Stock price")
        ax.set_ylabel("Option value")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)

    def plot_convergence(self, S, K, T, r, sigma, option, n, bs_price, mc_price):  # monte carlo nähert sich black-scholes an
        ax = self.ax_conv
        ax.clear()
        sizes = [s for s in (100, 300, 1000, 3000, 10000, 30000) if s < n]
        estimates = [monte_carlo(S, K, T, r, sigma, option, n=s, seed=None) for s in sizes]
        sizes.append(n)
        estimates.append(mc_price)  # letzter punkt ist das resultat von oben

        ax.plot(sizes, estimates, "o-", label="Monte Carlo estimate")
        ax.axhline(bs_price, color="red", linestyle="--", label="Black-Scholes price")
        ax.set_xscale("log")
        ax.set_title("Monte Carlo convergence")
        ax.set_xlabel("Number of simulations (log scale)")
        ax.set_ylabel("Option price")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)


def main():
    root = tk.Tk()
    OptionPricerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
