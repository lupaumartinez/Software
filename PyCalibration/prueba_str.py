
def transform_str(str_values):

	values = list(str(str_values).split(","))

	data = []

	for i in range(len(values)):
		data.append(float(values[i]))

	return data

str_values = '1,4,7,8'
datas = transform_str(str_values)

print(datas)