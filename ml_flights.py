from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import seaborn as sns

def normalize_year(year, mean, std):
	return (year.astype("float32") - mean) / std


flights = sns.load_dataset("flights")
flt_year = flights.groupby("year", as_index=False)["passengers"].sum()
print(flt_year.head())

year = flt_year[["year"]].astype("float32")
year_mean = year.mean()
year_std = year.std()
year = normalize_year(year, year_mean, year_std)
passengers = flt_year["passengers"].astype("float32")

model = Sequential()
model.add(Input(shape=(1,)))
model.add(Dense(1, activation="linear"))
model.compile(optimizer="sgd", loss="mse")
history = model.fit(year, passengers, epochs=10000, verbose=0)
model.save("flights_model.keras")

import matplotlib.pyplot as plt

plt.plot(history.history["loss"])
plt.title("Model Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.show()

year_test = normalize_year(flt_year[["year"]], year_mean, year_std)
predictions = model.predict(year_test)
print(predictions[:5])