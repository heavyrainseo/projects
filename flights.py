import seaborn as sns
import matplotlib.pyplot as plt

flt = sns.load_dataset("flights")

flt_year = flt.groupby("year", as_index=False)["passengers"].sum()
print(flt_year)

sy = flt_year["year"].std()
sp = flt_year["passengers"].std()
# cov = flt_year["year"].cov(flt_year["passengers"]) # 기존 라인 주석 처리
# print(f'r : {cov/(sy*sp)}') # 기존 라인 주석 처리

# 개선된 상관 계수 계산
correlation = flt_year["year"].corr(flt_year["passengers"])
# 선형회귀 기울기
a = correlation * flt_year["passengers"].std()/flt_year["year"].std()
# 선형회귀 절편
b = flt_year['passengers'].mean() - a * flt_year['year'].mean()

print(f'r : {correlation:.3f}, {a}, {b}')
sns.barplot(data=flt_year, x="year", y="passengers")
plt.savefig("flights_barplot.png")
#plt.show()
plt.close()

flt_pivot = flt.pivot(index="month", columns="year", values="passengers")
sns.heatmap(flt_pivot, annot=True, fmt="d", cmap="YlGnBu")
plt.savefig("flights_heatmap.png")
#plt.show()
plt.close()

plt.plot(flt_year['year'], flt_year['passengers'])
plt.plot(flt_year['year'], flt_year['year']*a+b)
plt.savefig('flights_linearregression.png')
plt.show()