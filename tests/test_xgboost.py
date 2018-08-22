from model.config import *
from model.utils import *
from model.evaluator import Evaluator
from model.config import *
from model.network import *
from model.utils import *
from model.evaluator import Evaluator
from keras import backend as K
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import xgboost as xgb
from model.classifier import *
from sklearn import preprocessing
from model.classifier import *

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings("ignore")
K.clear_session()

conf = LM_Config()

# step 1: Get dataset (csv)
data = pd.read_csv(conf['data_file_path'], encoding='gbk')

# step 2: Select Feature
feature_and_label_name = conf['feature_name']
feature_and_label_name.extend(conf['label_name'])
data = data[feature_and_label_name].values

# step 3: Preprocess
data = feature_normalize(data)
train_size = int(len(data) * conf['training_set_proportion'])
train, test = data[0:train_size, :], data[train_size:len(data), :]
train_x, train_y = data_transform_for_xgboost(train)
test_x, test_y = data_transform_for_xgboost(test)
train_y = sign(train_y)
test_y = sign(test_y)

train_x, train_y = over_sampling_naive(train_x, train_y)

dtrain = xgb.DMatrix(train_x, train_y)
dtest = xgb.DMatrix(test_x, test_y)

param = {
    'booster': 'gbtree',
    'silent': True,
    'eta': 0.01,
    'max_depth': 4,
    'gamma': 0.1,
    'objective': 'multi:softmax',
    'num_class': 3,
    'seed': 1000,
    'scale_pos_weight': 1
}

model = xgb.XGBClassifier(**param, dtrain=dtrain)
model.fit(train_x, train_y)
train_pred = model.predict(train_x)
test_pred = model.predict(test_x)

evaluator = Evaluator()

print('evaluate trend')
acc = evaluator.evaluate_trend(train_y, train_pred)
print(acc)
acc = evaluator.evaluate_trend(test_y, test_pred)
print(acc)

print('evaluate trend without stay')
acc = evaluator.evaluate_trend_2(train_y, train_pred)
print(acc)
acc = evaluator.evaluate_trend_2(test_y, test_pred)
print(acc)

print('simple evaluate')
acc = evaluator.evaluate_trend_simple(train_y, train_pred)
print(acc)
acc = evaluator.evaluate_trend_simple(test_y, test_pred)
print(acc)


# step 7: Plot
sample_size = 50
x_list = []
pred_list = []
true_list = []
for i in range(sample_size):
    if test_y[i] != 0:
        x_list.append(i)
        pred_list.append(test_pred[i])
        true_list.append(test_y[i])
plt.scatter(x_list, true_list)
plt.scatter(x_list, pred_list, marker='x')
plt.show()