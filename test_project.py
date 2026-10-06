import math
import pytest
from project import norm_cdf, norm_pdf, validate, d1_d2, black_scholes, monte_carlo, delta, gamma #zu prüfende funktionen


def test_norm_cdf():
    assert norm_cdf(0) == pytest.approx(0.5) #mittelwert testen
    assert norm_cdf(1.96) == pytest.approx(0.975, abs=1e-3) #grenzwert 1
    assert norm_cdf(-1.96) == pytest.approx(0.025, abs=1e-3) #grenzwert 2


def test_validate():
    with pytest.raises(ValueError):
        validate(S=-100, K=100, T=1, sigma=0.2, option="call") #negative zahl -> error
    with pytest.raises(ValueError):
        validate(S=100, K=0, T=1, sigma=0.2, option="call") #0 -> error
    with pytest.raises(ValueError):
        validate(S=100, K=100, T=-1, sigma=0.2, option="call") #andere neg. zahl -> error
    with pytest.raises(ValueError):
        validate(S=100, K=100, T=1, sigma=0, option="call") #anders 0 -> error
    with pytest.raises(ValueError):
        validate(S=100, K=100, T=1, sigma=0.2, option="swap") #falscher option typ -> error
    assert validate(S=100, K=100, T=1, sigma=0.2, option="put") is None #wenn alles berücksichtigt wird -> kein error


def test_d1_d2():
    d1, d2 = d1_d2(100, 100, 1, 0.05, 0.2) #ein beispiel machen und schauen ob die values ungefähr stimmen
    assert d1 == pytest.approx(0.35)
    assert d2 == pytest.approx(0.15)


def test_black_scholes():
    assert black_scholes(100, 100, 1, 0.05, 0.2, "call") == pytest.approx(10.4506, abs=1e-3) #black scholes für call option
    assert black_scholes(100, 100, 1, 0.05, 0.2, "put") == pytest.approx(5.5735, abs=1e-3) #black scholes für put option
    assert black_scholes(100, 100, 1, 0.05, 0.2, "CALL") == pytest.approx(10.4506, abs=1e-3) #schauen ob es auch mit caps geht
    with pytest.raises(ValueError):
        black_scholes(100, 100, 1, 0.05, 0.2, "swap") #testet, ob nur call und put akzeptiert werden


def test_put_call_parity():
    S, K, T, r, sigma = 100, 90, 0.5, 0.03, 0.25 # beispielswerte
    call = black_scholes(S, K, T, r, sigma, "call") #preis der call option
    put = black_scholes(S, K, T, r, sigma, "put") # preis der put option
    assert call - put == pytest.approx(S - K * math.exp(-r * T)) # call preis minus put preis muss immer den abgezinsten strike preis ergeben

def test_norm_pdf():
    assert norm_pdf(0) == pytest.approx(0.3989, abs=1e-4) #wert für 0 testen
    assert norm_pdf(1) == pytest.approx(norm_pdf(-1)) #schauen ob wert für positive und negative zahl gleich ist


def test_monte_carlo():
    call = monte_carlo(100, 100, 1, 0.05, 0.2, "call", n=100000, seed=42)
    put = monte_carlo(100, 100, 1, 0.05, 0.2, "put", n=100000, seed=42)
    assert call == pytest.approx(10.4506, rel=0.02) #beispiel mit call option
    assert put == pytest.approx(5.5735, rel=0.02) #beispiel mit put option
    with pytest.raises(ValueError):
        monte_carlo(100, -100, 1, 0.05, 0.2, "call", n=1000, seed=42) #mit negativen zahlen


def test_delta():
    call = delta(100, 100, 1, 0.05, 0.2, "call")
    put = delta(100, 100, 1, 0.05, 0.2, "put")
    assert call == pytest.approx(0.6368, abs=1e-4) #für call testen
    assert put == pytest.approx(-0.3632, abs=1e-4) #für put testen
    assert call - put == pytest.approx(1) # Put-Call-Parität testen


def test_gamma():
    g = gamma(100, 100, 1, 0.05, 0.2)
    assert g == pytest.approx(0.0188, abs=1e-4) #gamma testen
    assert g > 0 #testen, dass gamma positiv sein muss
