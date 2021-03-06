import numpy as np
from matplotlib import pyplot as plt
from pandas import read_csv
import math
from keras.models import Sequential
from keras import layers
from keras.layers import Dense
from keras.optimizers import RMSprop
from matplotlib import pyplot
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import explained_variance_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

seed = 7
batch_size = 1
epochs = 200
filename = '369.csv'
look_back=5

def create_dataset(dataset):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        x = dataset[i: i + look_back, 0]
        dataX.append(x)
        y = dataset[i + look_back, 0]
        dataY.append(y)
    return np.array(dataX), np.array(dataY)

def build_model():
    model = Sequential()
    model.add(layers.GRU(units=50, input_shape=(1, look_back)))
    model.add(Dense(units=1))
    model.compile(optimizer=RMSprop(), loss='mae')
    return model

if __name__ == '__main__':

    # 设置随机种子
    np.random.seed(seed)

    # 导入数据
    data = read_csv(filename, usecols=[1], engine='python')  # footer drop
    dataset = data.values.astype('float32')
    # 标准化数据
    scaler = MinMaxScaler()
    dataset = scaler.fit_transform(dataset)
    train_size = int(len(dataset) * 0.677777)
    validation_size = len(dataset) - train_size
    train, validation = dataset[0: train_size, :], dataset[train_size: len(dataset), :]

    # 创建dataset，让数据产生相关性
    X_train, y_train = create_dataset(train)
    X_validation, y_validation = create_dataset(validation)

    # 将输入转化成为【sample， time steps, feature]
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_validation = np.reshape(X_validation, (X_validation.shape[0], 1, X_validation.shape[1]))

    # 训练模型
    model = build_model()
    model.summary()
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=2)

    # 模型预测数据
    predict_train = model.predict(X_train)
    predict_validation = model.predict(X_validation)

    # 反标准化数据 --- 目的是保证MSE的准确性
    predict_train = scaler.inverse_transform(predict_train)
    y_train = scaler.inverse_transform([y_train])
    predict_validation = scaler.inverse_transform(predict_validation)
    y_validation = scaler.inverse_transform([y_validation])

    def mape(y_validation, predict_validation):
        return np.mean(np.abs((predict_validation - y_validation) / y_validation)) * 100

    # 评估模型
    train_rmse = math.sqrt(mean_squared_error(y_train[0], predict_train[:, 0]))
    print('Train Score: %.3f RMSE' % train_rmse)
    validation_rmse = math.sqrt(mean_squared_error(y_validation[0], predict_validation[:, 0]))
    print('Validation Score: %.3f RMSE' % validation_rmse)
    train_mse = mean_squared_error(y_train[0], predict_train[:, 0])
    print('Train Score: %.3f MSE' % train_mse)
    validation_mse = mean_squared_error(y_validation[0], predict_validation[:, 0])
    print('validation Score: %.3f MSE' % validation_mse)
    train_mae = mean_absolute_error(y_train[0], predict_train[:, 0])
    print('Train Score: %.3f MAE' % train_mae)
    validation_mae = mean_absolute_error(y_validation[0], predict_validation[:, 0])
    print('Validation Score: %.3f MAE' % validation_mae)
    train_evs = explained_variance_score(y_train[0], predict_train[:, 0])
    print('Train Score: %.3f EVS' % train_evs)
    validation_evs = explained_variance_score(y_validation[0], predict_validation[:, 0])
    print('validation Score: %.3f EVS' % validation_evs)
    train_mape = mape(y_train[0], predict_train[:, 0])
    print('Train Score: %.3f MAPE' % train_mape)
    validation_mape = mape(y_validation[0], predict_validation[:, 0])
    print('validation Score: %.3f MAPE' % validation_mape)

    #评价指标输出
    Train_evaluate_name=['Train RMSE','Train MSE','Train MAE','Train EVS','Train MAPE']
    Train_evaluate_data_result=[train_rmse,train_mse,train_mae,train_evs,train_mape]

    Validation_evaluate_name=['Validation RMSE','Validation MSE','Validation MAE','Validation EVS','Validation MAPE']
    Validation_evaluate_data_result=[validation_rmse,validation_mse,validation_mae,validation_evs,validation_mape]
    c = np.vstack([Train_evaluate_data_result,Validation_evaluate_data_result])
    np.savetxt("evaluate_data.csv" , c ,fmt="%3f", delimiter=',')

    #预测数据y存储
    np.savetxt('predict_validation.csv', predict_validation, delimiter=',')
    np.savetxt('predict_train.csv', predict_train, delimiter=',')
    # 构建通过训练集进行预测的图表数据
    predict_train_plot = np.empty_like(dataset)
    predict_train_plot[:, :] = np.nan
    predict_train_plot[look_back:len(predict_train) + look_back, :] = predict_train

    # 构建通过评估数据集进行预测的图表数据
    predict_validation_plot = np.empty_like(dataset)
    predict_validation_plot[:, :] = np.nan
    predict_validation_plot[len(predict_train) + look_back * 2 + 1:len(dataset) - 1, :] = predict_validation

    # 图表显示
    dataset = scaler.inverse_transform(dataset)
    plt.plot(dataset, color='blue')
    plt.plot(predict_train_plot, color='green')
    plt.plot(predict_validation_plot, color='red')
    plt.show()