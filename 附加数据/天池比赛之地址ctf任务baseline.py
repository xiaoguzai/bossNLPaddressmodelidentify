import numpy as np
from tqdm import tqdm
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.backend as K
import numpy as np
import re
import os
maxlen = 256
#这里maxlen = 512会爆内存
epochs = 1
batch_size = 32
learning_rate = 2e-5  # bert_layers越小，学习率应该要越大
crf_lr_multiplier = 1000  # 必要时扩大CRF层的学习率
categories = set()
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"]="true"

import os
os.environ["CUDA_VISIBLE_DEVICES"] = '0'   #指定第一块GPU可用
config = tf.compat.v1.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.  # 程序最多只能占用指定gpu50%的显存
config.gpu_options.allow_growth = True      #程序按需申请内存
sess = tf.compat.v1.Session(config = config)

config_path = '/home/xiaoguzai/下载/uer/mixed_corpus_bert_large_model/bert_config.json'
checkpoint_path = '/home/xiaoguzai/下载/uer/mixed_corpus_bert_large_model/bert_model.ckpt'
dict_path = '/home/xiaoguzai/下载/uer/mixed_corpus_bert_large_model/vocab.txt'

categories_to_id = {'redundant':0,'prov':1,'city':2,'district':3,'devzone':4,'town':5,'community':6,'village_group':7,'road':8,'roadno':9,'poi':10,'subpoi':11,'houseno':12,'cellno':13,'floorno':14,'roomno':15,'detail':16,'assist':17,'distance':18,'intersection':19,'others':20}
id_to_categories = {categories_to_id[data]:data for data in categories_to_id}

def load_data(filename):
    """加载数据
    单条格式：[text, (start, end, label), (start, end, label), ...]，
              意味着text[start:end + 1]是类型为label的实体。
    """
    data_char = []
    data_id = []
    with open(filename, encoding='utf-8') as f:
        f = f.read()
        for l in f.split('\n\n'):
            if not l:
                continue
            current_char = []
            current_id = []
            for i, c in enumerate(l.split('\n')):
                try:
                    char, flag = c.split(' ')
                except:
                    print('l.split = ')
                    print(l.split('\n'))
                    print('error c = ')
                    print(c)
                    continue
                flag = flag.split('-')
                if len(flag) == 2:
                    flag1 = flag[0]
                    flag2 = flag[1]
                else:
                    flag1 = flag[0]
                current_char.append(char)
                if flag1 == 'O' or len(flag) == 1:
                    current_id.append(categories_to_id['redundant'])
                else:
                    if len(flag) == 2:
                        print('flag = ')
                        print(flag)
                        if flag1 == 'B' or flag1 == 'E':
                            current_id.append(categories_to_id[flag2]*2+1)
                        else:
                            current_id.append(categories_to_id[flag2]*2)
            data_char.append(current_char)
            data_id.append(current_id)
    return data_char,data_id

train_data,train_id = load_data('/home/xiaoguzai/数据/天池比赛地址实体识别数据集/train.conll')
evaluate_data,evaluate_id = load_data('/home/xiaoguzai/数据/天池比赛地址实体识别数据集/dev.conll')

from tokenization import FullTokenizer
tokenizer = FullTokenizer(dict_path)
train_token_ids = []
train_label_ids = []
for tokens in train_data:
    tokens = ["[CLS]"]+tokens+["[SEP]"]
    current_token = tokenizer.convert_tokens_to_ids(tokens)
    train_token_ids.append(current_token)
for ids in train_id:
    ids = [0]+ids+[0]
    train_label_ids.append(ids)
evaluate_token_ids = []
evaluate_label_ids = []
for tokens in evaluate_data:
    tokens = ["[CLS]"]+tokens+["[SEP]"]
    current_token = tokenizer.convert_tokens_to_ids(tokens)
    evaluate_token_ids.append(current_token)
for ids in evaluate_id:
    ids = [0]+ids+[0]
    evaluate_label_ids.append(ids)
train_data = []
train_id = []
evaluate_data = []
evaluate_id = []

import json
with open(config_path,'r') as load_f:
    config = json.load(load_f)
print('config = ')
print(config)
config['embedding_size'] = config['hidden_size']
config['num_layers'] = config['num_hidden_layers']

from models import Bert
from models import ConditionalRandomField
input_ids = keras.layers.Input(shape=(None,),dtype='int32',name='input_ids')
bertmodel = Bert(**config)
output = bertmodel(input_ids)
#output = keras.layers.Bidirectional(keras.layers.LSTM(128, return_sequences=True))(output)
#上面的得分为0.7几
output = keras.layers.Bidirectional(keras.layers.LSTM(128,return_sequences=True))(output)
#上面的得分一次为0.81，一次为0.7几
r"""
output = keras.layers.RNN(keras.layers.LSTMCell(
        units = 3, # 输出
        return_sequences = True,
        input_shape= (None,None,768), # 输入
   ))(output)
"""
result_dense = keras.layers.Dense(units = len(categories_to_id)*2,
                           kernel_initializer = tf.keras.initializers.TruncatedNormal(stddev=0.02),
                           name = "final_dense")
output = result_dense(output)
CRF = ConditionalRandomField(lr_multiplier=crf_lr_multiplier)
output = CRF(output)
print('output = ')
print(output)
model = keras.Model(inputs=input_ids,outputs=output)

from loader import load_stock_weights
load_stock_weights(bert=bertmodel,ckpt_path=checkpoint_path)

learning_rate = 2e-5
model.compile(
    loss = CRF.sparse_loss,
    optimizer = keras.optimizers.Adam(learning_rate),
    metrics = [CRF.sparse_accuracy]
)
model.summary()

batch_size = 48
epochs = 1
#from tokenization import sequence_padding
def sequence_padding(inputs):
    max_seq_len = max([len(x) for x in inputs])
    token_type_ids = [0]*max_seq_len
    x = []
    for input_ids in inputs:
        input_ids = input_ids+[0]*(max_seq_len-len(input_ids))
        x.append(np.array(input_ids))
    return np.array(x)
    
class DataGenerator(object):
    def __init__(self,token_ids,label_ids,batch_size=48):
        self.token_ids = token_ids
        self.label_ids = label_ids
        self.batch_size = batch_size
        self.steps = int(np.floor(len(self.token_ids)/self.batch_size))
        self.totals = len(self.token_ids)
        self.maxlen = maxlen
    
    def __len__(self):
        return int(np.floor(len(self.token_ids)/self.batch_size))
    
    def sample(self, random=False):
        """采样函数，每个样本同时返回一个is_end标记
        """
        indices = list(range(len(self.token_ids)))
        np.random.shuffle(indices)
        for i in indices:
            yield self.token_ids[i],self.label_ids[i]
        
    def __iter__(self,random=False):
        random = False
        batch_data = []
        batch_token_ids = []
        batch_label_ids = []
        currents = 0
        for current_token_ids,current_label_ids in self.sample(random):
        #传入的数据在下面定义train_generator = data_generator(train_data, batch_size)
        #这里如果使用tqdm(self.sample(random))，它就会连续地不断产生红色区域
        #如果不使用tqdm(self.sample(random))，它就会连续以...的形式输出进度
        #因为model.fit()函数之中自带相应的进度条
            batch_token_ids.append(current_token_ids)
            batch_label_ids.append(current_label_ids)
            currents = currents+1
            if len(batch_token_ids) == self.batch_size or currents == self.totals:
                #len(batch_token_ids) == self.batch_size:当前批次结束
                #is_end:所有数据结束(可能不够一个批次)
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_label_ids = sequence_padding(batch_label_ids)
                yield batch_token_ids,batch_label_ids
                r"""
                这里的batch_token_ids和batch_segment_ids外面必须加上np.array
                """
                batch_token_ids,batch_label_ids = [],[]
                #每一个批次结束的时候

    def cycle(self,random=True):
        while True:
            for d in self.__iter__(random):
                yield d

class Evaluator(keras.callbacks.Callback):
    def __init__(self,evalute_token_ids,evaluate_label_ids):
        self.best_score = 0.0
        self.evaluate_token_ids = evaluate_token_ids
        self.evaluate_label_ids = evaluate_label_ids
    
    def on_epoch_end(self,epoch,logs=None):
        wrong_data = []
        label_id = []
        predict_data = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0}
        true_data = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0}
        predict_true_data = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0}
        fp = open('./wrong_data.txt','w')
        for i in tqdm(range(len(self.evaluate_token_ids))):
            current_result = model(np.array([np.array(self.evaluate_token_ids[i])]))
            current_result = current_result.numpy()
            current_result = current_result.argmax(axis=-1)
            current_id = current_result//2
            current_data = current_id[0]
            #进行预测
            for j in range(len(current_data)):
                #打上标签
                current_label = self.evaluate_label_ids[i][j]//2
                predict_data[current_data[j]] = predict_data[current_data[j]]+1
                true_data[current_label] = true_data[current_label]+1
                if current_data[j] == current_label:
                    predict_true_data[current_data[j]] = predict_true_data[current_data[j]]+1
                else:
                    current_dict = {"wrong_id":i,"wrong_word":tokenizer.inv_vocab[self.evaluate_token_ids[i][j]],"predict_data":id_to_categories[current_data[j]],"true_data":id_to_categories[current_label]}
                    fp.write(str(current_dict)+'\n')
        fp.write('\n\n\n\n\n\n')
        fp.close()
        score1,score2,score3 = 0,0,0
        total_score1 = {}
        total_score2 = {}
        total_score3 = {}
        total_score = 0
        for data in predict_true_data:
            if data == 0:
                continue
            
            if predict_data[data] == 0:
                score1 = 0
            else:
                score1 = predict_true_data[data]/predict_data[data]
            
            if true_data[data] == 0:
                score2 = 0
            else:
                score2 = predict_true_data[data]/true_data[data]
            
            if score1+score2 == 0:
                score3 = 0
            else:
                score3 = 2*score1*score2/(score1+score2)
            
            total_score1[data] = score1
            total_score2[data] = score2
            total_score3[data] = score3
            total_score = total_score+score1+score2+score3
        print('准确率 = ')
        print(total_score1)
        print('召回率 = ')
        print(total_score2)
        print('f1_score = ')
        print(total_score3)
        print('总分数为')
        print(total_score)
        if total_score > self.best_score:
            model.save_weights('./词性标注best_model.h5')

data_generator = DataGenerator(train_token_ids,train_label_ids,batch_size)
evaluator = Evaluator(evaluate_token_ids,evaluate_label_ids)

input_ids = keras.layers.Input(shape=(None,),dtype='int32',name='input_ids')
output_ids = model(input_ids)
print(output_ids)

import os
os.environ["TF_FORCE_GPU_ALLOW_GROWTH"]="true"
model.fit(
    data_generator.cycle(),
    steps_per_epoch = len(data_generator),
    epochs = 10,
    callbacks = [evaluator]
)

model.load_weights('./词性标注best_model.h5')

f = open("/home/xiaoguzai/数据/天池比赛地址实体识别数据集/final_test.txt")               # 返回一个文件对象   
line = f.readline()               # 调用文件的 readline()方法   
test_data = []
import re
while line:
    line = re.sub(r'^([0-9]+)','',line)
    line = re.sub(r'\n','',line)
    test_data.append(line[1:])
    line = f.readline()   
f.close()

test_str_ids = []
test_label_ids = []
from tokenization import FullTokenizer
tokenizer = FullTokenizer(dict_path)
for data in tqdm(test_data):
    test_str_ids.append(list(data))
    tokens = ["[CLS]"]+list(data)+["[SEP]"]
    current_token = tokenizer.convert_tokens_to_ids(tokens)
    result_label = model(np.array([np.array(current_token)]))
    result_label = np.array(result_label).argmax(axis=-1)
    result_label = result_label[0][1:-1]
    test_label_ids.append(list(result_label))

f = open('/home/xiaoguzai/数据/天池比赛地址实体识别数据集/results.txt','w')
prelabel = None
for i in range(len(test_data)):
    f.write(str(i+1)+'\u0001')
    f.write(test_data[i]+'\u0001')
    for j in range(len(test_label_ids[i])):
        if test_label_ids[i][j] == 20:
            f.write('O')
            prelabel = 'O'
        else:
            if test_label_ids[i][j]%2 == 0:
                f.write('I-')
                prelabel = 'I'
            else:
                if id_to_categories[test_label_ids[i][j]//2] == 'assist':
                    f.write('S-')
                else:
                    if j == 0:
                        f.write('B-')
                        prelabel = 'B'
                    else:
                        if prelabel == 'B':
                            f.write('E-')
                            prelabel = 'E'
                        elif prelabel == 'E':
                            f.write('B-')
                            prelabel = 'B'
                        elif prelabel == 'I':
                            f.write('E-')
                            prelabel = 'E'
            f.write(id_to_categories[test_label_ids[i][j]//2])
        if j != len(test_label_ids[i])-1:
            f.write(' ')
        else:
            f.write('\n')

f = open('/home/xiaoguzai/数据/天池比赛地址实体识别数据集/验证集数据.txt','w')
for data in evaluate_data:
    f.write(''.join(data))
    f.write('\n')
f.close()
