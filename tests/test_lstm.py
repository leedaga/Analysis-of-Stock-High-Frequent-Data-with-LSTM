from model.config import *
from model.network import *
from model.utils import *
from model.evaluator import Evaluator
from keras import backend as K
import matplotlib.pyplot as plt
import warnings
import os
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings("ignore")
K.clear_session()

lstm_conf = LSTM_Config()
lstm_conf.update(use_previous_model=0,
                 load_file_name='lstm.h5')

# step 1: Get dataset (csv)
data = pd.read_csv(lstm_conf['data_file_path'], encoding='gbk')

# step 2: Select Feature
mid_price = data['mid_price']
feature_and_label_name = lstm_conf['feature_name']
feature_and_label_name.extend(lstm_conf['label_name'])
data = data[feature_and_label_name].values

# step 3: Preprocess
data = feature_normalize(data)
train_size = int(len(data) * lstm_conf['training_set_proportion'])
train, test = data[0:train_size, :], data[train_size:len(data), :]
train_x, train_y = data_transform_lstm(train, lstm_conf['time_step'])
test_x, test_y = data_transform_lstm(test, lstm_conf['time_step'])

# step 4: Create and train model_weight
network = LSTMs(lstm_conf)
if lstm_conf['use_previous_model']:
    network.load(lstm_conf['load_file_name'])
else:
    network.train(train_x, train_y)
    network.save(lstm_conf['save_file_name'])

# step 5: Predict
train_pred = network.predict(train_x)
test_pred = network.predict(test_x)

# step 6: Evaluate
evaluator = Evaluator()
print('simple evaluation')

# method1
acc = evaluator.evaluate_trend(y_true=train_y, y_pred=train_pred)
print(acc)
acc = evaluator.evaluate_trend(y_true=test_y, y_pred=test_pred)
print(acc)

# method 2
acc_train_list = evaluator.evaluate_divided_trend(train_y, train_pred)
acc_test_list = evaluator.evaluate_divided_trend(test_y, test_pred)
print('acc_train_list = ' + str(acc_train_list))
print('acc_test_list = ' + str(acc_test_list))

# method 3
acc = evaluator.evaluate_trend_simple(train_y, train_pred)
print(acc)
acc = evaluator.evaluate_trend_simple(test_y, test_pred)
print(acc)

# step 7: Plot
train_mid_price = mid_price[0:train_size]
test_mid_price = mid_price[train_size:len(mid_price)]

# plt.figure(figsize=(200, 15))
# plt.plot(train_y)
# plt.plot(train_pred)
# plt.plot(train_mid_price-8.3)
# plt.legend(['train_label', 'train_predict', 'train_mid_price - 8.3'], loc='upper right')
# plt.title('train_set plot')
# plt.xlabel('time')
# plt.ylabel('price')
# plt.show()
#
# plt.figure(figsize=(200, 15))
# plt.plot(test_y)
# plt.plot(test_pred)
# plt.plot(np.arange(len(test_mid_price)), test_mid_price-8.3)
# plt.legend(['test_label', 'test_predict', 'test_mid_price - 8.3'], loc='upper right')
# plt.title('test_set plot')
# plt.xlabel('time')
# plt.ylabel('price')
# plt.show()

feature_list = lstm_conf['feature_name']
save_feature_selection(feature_list, acc)
