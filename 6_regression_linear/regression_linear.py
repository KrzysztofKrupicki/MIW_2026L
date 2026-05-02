import matplotlib.pyplot as plt  # v=3.10.9
import numpy as np  # v=2.4.4

dane = np.loadtxt("./data/regresja_liniowa.txt", dtype=int, delimiter=" ")

X = dane[:, 0]
Y = dane[:, 1]

m_x = sum(X) / len(X)
m_y = sum(Y) / len(Y)

squares_ai_x = [(x - m_x) ** 2 for x in X]
squares_ai_y = [(y - m_y) ** 2 for y in Y]
s_x = (sum(squares_ai_x) / (len(X) - 1)) ** 0.5
s_y = (sum(squares_ai_y) / (len(Y) - 1)) ** 0.5

sum_xy = sum([x * y for x, y in zip(X, Y)])
sum_x2 = sum([x**2 for x in X])
sum_y2 = sum([y**2 for y in Y])
r_xy = ((len(X) * sum_xy) - (sum(X) * sum(Y))) / (
    ((len(X) * sum_x2 - (sum(X) ** 2))) * (len(Y) * sum_y2 - (sum(Y) ** 2))
) ** 0.5

b = round(r_xy * s_y / s_x, 2)
a = round(m_y - b * m_x, 2)
print(f"y = {b:.2f} * x + {a:.2f}")

x = np.linspace(min(X), max(X), 100)
y = b * x + a


plt.scatter(X, Y, label="Wartości niezależne")
plt.plot(x, y, color="red", label="Linia regresji")
plt.xlabel("Wartości X")
plt.ylabel("Wartości Y")
plt.legend()
plt.show()

new_x = int(input("Podaj wartość X: "))
print(f"X = {new_x}\nY = {b} * {new_x} + {a} = {round(b * new_x + a, 2)}")
