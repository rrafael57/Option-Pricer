# Option Pricer: Black-Scholes vs. Monte Carlo

This is a Python program in which I implemented functions that price European call and put options with two different methods: the analytical Black-Scholes formula and a Monte Carlo simulation. Both results are compared and it also calculates two of the most important option sensitivities, Delta and Gamma.

The project started as my final project for CS50's Introduction to Programming with Python (CS50P) as a command line program. Afterwards I extended it with a graphical user interface and visualisations.

**Credits:** I implemented all of the pricing logic myself, including the Black-Scholes formula, the Monte Carlo simulation, Delta, Gamma, the normal distribution functions, input validation and the tests (project.py and test_project.py). The graphical user interface and the visualisations (gui.py) were built with the help of Claude Opus 5.5.

Definition: An option is a contract that gives the holder the right, but not the obligation, to buy (call) or sell (put) a stock at a fixed price (the strike price) at a certain date (the maturity). This program answers the question of what price would be fair today for this right.

The user enters values: the current stock price (S), the strike price (K), the time to maturity in years (T), the risk-free interest rate (r), the volatility (sigma) and the option type (call or put). The program then outputs:

- the Black-Scholes price
- the Monte Carlo price
- the absolute difference between the two
- Delta
- Gamma

Since both methods are based on geometric Brownian motion (a model for stock pricing), the Monte Carlo price converges to the Black-Scholes price as the number of simulations increases. Seeing both numbers next to each other is a good check that the implementation is correct.

### Files

**project.py** contains the command line program and all calculation functions:

- `main()` asks the user for the inputs, calculates all values by using the other functions and prints the results. If an input is invalid, the program exits with an error message.
- `get_float(prompt)` keeps asking for input until the user enters a valid number (float).
- `get_option_type()` keeps asking until the user enters "call" or "put" (case insensitive).
- `validate(S, K, T, sigma, option)` raises a ValueError if S, K, T or sigma are not positive or if the option type is neither call nor put.
- `norm_cdf(x)` returns the cumulative distribution function (CDF) of the standard normal distribution, implemented with `math.erf`.
- `norm_pdf(x)` returns the probability density function (PDF) of the standard normal distribution.
- `d1_d2(S, K, T, r, sigma)` calculates the two helper values d1 and d2 used in the Black-Scholes formula.
- `black_scholes(S, K, T, r, sigma, option)` returns the exact option price using the Black-Scholes formula.
- `monte_carlo(S, K, T, r, sigma, option, n, seed)` simulates n possible stock prices at maturity, calculates the payoff of the option for each one, takes the average and discounts it back to today.
- `delta(S, K, T, r, sigma, option)` returns how much the option price changes when the stock price rises by 1.
- `gamma(S, K, T, r, sigma)` returns how much Delta changes when the stock price rises by 1. Gamma is the same for calls and puts (that's why it doesn't need the option type when called).

**gui.py** contains the graphical user interface, built with `tkinter` and `matplotlib`. It reuses all calculation functions from project.py. The window has input fields for all values (including the number of simulations), a call/put selection and a results panel. It also shows two charts:

- **Option value vs. stock price:** the Black-Scholes value of the option today across a range of stock prices, compared to the payoff at maturity. The current price is marked in red. The gap between the two lines is the time value of the option.
- **Monte Carlo convergence:** Monte Carlo estimates for an increasing number of simulations, compared to the Black-Scholes price. It shows how the random estimate gets closer to the exact value the more simulations are used.

**test_project.py** contains the tests for all calculation functions, written with pytest. The functions are tested against known textbook values (for S=100, K=100, T=1, r=0.05, sigma=0.2 the call is worth about 10.4506 and the put about 5.5735). The tests also check put-call parity, the symmetry of the normal distribution, that Monte Carlo with a fixed seed lands close to the Black-Scholes price, and that invalid inputs raise a ValueError.

**requirements.txt** lists the libraries that need to be installed: pytest (for the tests) and matplotlib (for the charts in the GUI).

### Design choices

**No external math libraries.** There are other libraries that may be more tailored to financial mathematics (like numpy or scipy), but I decided to use only Python's built-in `math` and `random` modules for the calculations. The normal CDF is calculated with the error function `math.erf`, using the relation N(x) = 0.5 * (1 + erf(x / sqrt(2))). This deepened my understanding of every formula instead of calling a premade function, and it avoids having to install many libraries.

**Separate validation function.** All calculation functions call `validate` first, so invalid inputs are caught in one place and the error messages are consistent. This also makes the input checks easy to test.

**Seed parameter in Monte Carlo.** Monte Carlo results are random, which makes them hard to test. By passing a seed to `random.Random`, the same random numbers are generated every time, so the tests are reproducible. In the actual program the seed is None, so every run gives a slightly different result. I chose this to make it more realistic while still being able to change the seed.

**Number of simulations.** I chose n = 100,000 simulations as default. This keeps the difference to the Black-Scholes price usually below 0.1 while the program still runs in a few seconds. It is a good balance between speed and accuracy. In the GUI the number can be changed.

**Calculations separated from input.** The input functions (`get_float`, `get_option_type`) and the calculation functions are strictly separated. Only `main` deals with the user, so all calculation functions can be tested without needing any input. This helped a lot during development, and it made it possible to add the GUI later without changing any of the calculation functions.

**GUI in a separate file.** The GUI lives in its own file and only imports the calculation functions from project.py. That way the command line version still works exactly as before, and the same tested functions are used in both versions.

### How to run

Install the requirements:

pip install -r requirements.txt

Start the GUI:

python gui.py

Start the command line version:

python project.py

Run the tests:

pytest test_project.py
