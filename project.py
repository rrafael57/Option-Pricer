import math
import sys
import random

def main(): #fragt nach eingaben, macht rechnungen und gibt das resultat aus
    #nach allen eingaben schritt für schritt abfragen
    S = get_float('Aktienkurs: ')
    K = get_float('Strike Preis: ')
    T = get_float('Laufzeit (in Jahren): ')
    r = get_float('Risikoloser Zinssatz: ')
    sigma = get_float('Volatilität: ')
    option= get_option_type()
    try:
        scholes=black_scholes(S, K, T, r, sigma, option) #für die werte black scholes berechnen
        monte=monte_carlo(S, K, T, r, sigma, option, n=100000, seed=None) #monte carlo für die werte berechnen, n und seed sind gewählt aber anpassbar
        D=delta(S, K, T, r, sigma, option) #delta berechnen
        G=gamma(S, K, T, r, sigma) #gamma berechnen
    except ValueError as e:
        sys.exit(e)
    #Alle zahlen auf 4 Kommastellen gerundet zurückgeben
    print(f"Black-Scholes-Preis: {scholes:.4f}")
    print(f"Monte-Carlo-Preis: {monte:.4f}")
    print(f"Abweichung: {abs(scholes-monte):.4f}")
    print(f"Delta: {D:.4f}")
    print(f"Gamma: {G:.4f}")

def get_float(prompt): #fragt nach, bis eine gültige Zahl gegeben wird und macht daraus einen float
    while True:
        try:
            value=float(input(prompt))
            return value
        except ValueError:
            print('input must be a float')

def get_option_type(): #erwartet call oder put
    while True:
        eingabe=input('call oder put: ').strip().lower()
        if eingabe == 'call' or eingabe == 'put': #nur wert zurückgeben wenn der typ der Option stimmt
            return eingabe
        else:
            print('option must be of the type call or put')

def validate(S,K,T,sigma,option): #soll error gebe, wenn zahlen nicht positiv sind oder die option nicht call oder put ist
    if S<=0 or T<=0 or K<=0 or sigma<=0:
        raise ValueError('at least one of the values is not positive')
    if option.lower() != 'call' and option.lower() != 'put':
        raise ValueError('option is neither call nor put')

def norm_cdf(x): #wahrscheinlichkeit, dass zufallsvariabel kleiner ist wie x
    y=x/math.sqrt(2) #skala anpassen, weil die erf funktion mit e^(-t^2) rechnet
    return (math.erf(y)+1)*0.5 #erf ist von -1 bis 1, umformatiere dass die wahrscheinlichkeit zwischen 0 und 1 liegt

def norm_pdf(x): #höhe der Kurve an der Stelle X
    p=math.exp(-x**2 / 2) # bestimmt die Glockenform
    q=math.sqrt(2 * math.pi) # normiert die kurve, damit die gesamtfläche 1 ist
    return p/q #gibt dichte an stelle X zurück

def d1_d2(S, K, T, r, sigma): #berechnet Hilfsgrössen d1 und d2 mithilfe Black-Scholes-Formel und gibt diese zurück
    d1=(math.log(S/K)+(r+sigma**2/2)*T)/(sigma * math.sqrt(T)) # misst, wie weit die Option im Geld ist, in Standardabweichungen
    d2=d1 - sigma * math.sqrt(T) # d1 minus die Schwankung über die gesamte Laufzeit
    return d1, d2 #gibt beides als Tupel zurück

def black_scholes(S, K, T, r, sigma, option): #berechnet den Optionspreis für call oder put mit der Black-Scholes-Formel
    validate(S,K,T,sigma,option) #schauen ob inputs dem format entsprechen
    d1, d2= d1_d2(S, K, T, r, sigma) #d1 und d2 berechnen
    if option.lower() == 'call':
        return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2) #black-scholes-formel für call option
    if option.lower() == 'put':
        return K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1) #black-scholes-formel für put option

def monte_carlo(S, K, T, r, sigma, option, n, seed): #macht n simulationen für den Endkurs der Aktie, nimmt von allen Payoffs den Durchschnitt und diskonitert ihn auf heute
    validate(S,K,T,sigma,option) #inputs testen
    rng=random.Random(seed)
    summe = 0 #summe aller payoffs
    for _ in range(n):
        Z = rng.gauss(0,1) #zufallszahl, normalverteilt mit mittelwert 0 und abweichung 1
        ST = S * math.exp((r - sigma**2 / 2) * T + sigma * math.sqrt(T) * Z) #Formel für den Endkurs
        if option.lower() == 'call':
            payoff=max(ST-K,0) #payoff formel für call option
        else:
            payoff=max(K-ST,0) #payoff formel für put option
        summe+=payoff
    average= summe/n #durchschnittlicher payoff
    return average*math.exp(-r * T) #abgezinster durchschnitt -> fairer options preis

def delta(S, K, T, r, sigma, option): #wie stark ändert sich der Optionspreis, wenn Aktienkurs um 1 steigt
    validate(S,K,T,sigma,option) #inputs testen
    d1, _ = d1_d2(S, K, T, r, sigma) #d1 berechnen, d2 wird nicht gebraucht
    if option.lower() == 'call':
        return norm_cdf(d1) #Ableitung der black-scholes-formel nach S ergibt N(d1)
    else:
        return norm_cdf(d1) - 1 # wegen der put-call-parität folgt delta put = delta call - 1

def gamma(S, K, T, r, sigma): # wie stark sich Delta ändert, wenn Aktienkurs um 1 steigt
    validate(S,K,T,sigma,"call") #inputs testen, call weil es für beide gleich ist und in gamma nicht nach der art der Option gefragt wird
    d1, _= d1_d2(S, K, T, r, sigma) #d1 berechnen
    return norm_pdf(d1) / (S * sigma * math.sqrt(T))

if __name__ == "__main__":
    main()
