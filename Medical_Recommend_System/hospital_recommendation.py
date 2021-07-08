import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QStringListModel
from PyQt5 import uic
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from gensim.models import Word2Vec
from scipy.io import mmwrite, mmread
import pickle
form_window = uic.loadUiType('recommender_2.ui')[0]

class Exam(QWidget, form_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #데이터 불러오기
        self.df_review = pd.read_csv('./datasets/model_data_Hospital_and_info2.csv',index_col=0)
        self.Tfidf_matrix = mmread('./models/tfidf_hospital_review_l.mtx').tocsr()
        self.embedding_model = Word2Vec.load('./models/word2VecModel_hospital_l2.model')
        with open('./models/tfidf_l.pickle', 'rb') as f:
            self.Tfidf = pickle.load(f)

        category = list(self.df_review.category.unique())
        print(category)
        category = sorted(category)
        self.cmb_title_2.addItem('과를 선택하세요')
        for c in category :
            self.cmb_title_2.addItem(c) #카테고리 목록


        total = ''
        for c in self.df_review.clinics:
            total += c

        #과를 추가하기
        totals = total.split(', ')
        total_set = set(totals)
        total = list(total_set)  #진료 과목

        titles = list(self.df_review.names) # 병원 이름
        titles = sorted(titles)

        key_title = titles + total
        key_title = sorted(key_title) #병원 + 진료 과목

        #자동완성
        model = QStringListModel()
        model.setStringList(list(key_title))
        completer = QCompleter()
        completer.setModel(model)
        self.le_title.setCompleter(completer)
        self.le_title.returnPressed.connect(self.btn_recommend_slot)

        self.btn_recommend.clicked.connect(self.btn_recommend_slot)
        self.cmb_title_2.currentIndexChanged.connect(self.cmb_title_slot_2)
        self.cmb_title.currentIndexChanged.connect(self.cmb_title_slot)


    #지역 한정 병원
    def cmb_title_slot(self):
        title = self.cmb_title_2.currentText()
        address = self.cmb_title.currentText()
        print(address)

        region = self.df_review[(self.df_review.category == title) &(self.df_review.region == address)].iloc[:9, 1]
        recommend = '\n'.join(list(region))
        self.lbl_result.setText(recommend)


    #카테고리 탑10 병원
    def cmb_title_slot_2(self):
        title = self.cmb_title_2.currentText()

        #지역을 추가하기
        add_list = []
        for i in self.df_review.addresses:
            a = i.split(' ')[0]
            add_list.append(a)

        add_set = set(add_list)
        address = list(add_set)
        address = sorted(address)
        address.pop(0)

        self.cmb_title.addItem('지역을 선택하세요')
        for add in address:
            self.cmb_title.addItem(add) #지역 목록


        print(title)
        #print(self.df_review.category.unique())
        top = self.df_review[self.df_review.category == title].iloc[:9,1]
        recommend = '\n'.join(list(top))
        print(recommend)
        #c = c[c.category == title].loc[:9, 'names']
        #print(a)
        self.lbl_result.setText(recommend)
        #self.cmb_title.currentIndexChanged.connect(self.cmb_title_slot, title)

    def getRecommendation(self, cosine_sim):
        simScores = list(enumerate(cosine_sim[-1]))
        simScores = sorted(simScores, key=lambda x: x[1],
                           reverse=True)
        simScores = simScores[0:10]
        movieidx = [i[0] for i in simScores]
        RecMovielist = self.df_review.iloc[movieidx]
        #print(RecMovielist)
        return RecMovielist.names



    def btn_recommend_slot(self):
        title = self.le_title.text()
        try:
            if title in list(self.df_review['names']):
                movie_idx = self.df_review[
                    self.df_review['names']==title].index[0]
                cosine_sim = linear_kernel(
                    self.Tfidf_matrix[movie_idx],
                    self.Tfidf_matrix)
                recommend = '\n'.join(
                    list(self.getRecommendation(cosine_sim))[1:])

            #elif title in total :


            else:
                print(title)
                sentence = [title] * 10

                sim_word = self.embedding_model.wv.most_similar(title, topn=10)
                labels = []
                for label, _ in sim_word:
                    labels.append(label)
                print(labels)

                for i, word in enumerate(labels):
                    sentence += [word] * (9 - i)

                sentence = ' '.join(sentence)
                sentence_vec = self.Tfidf.transform([sentence])
                cosine_sim = linear_kernel(sentence_vec,
                                           self.Tfidf_matrix)
                recommend = '\n'.join(
                    list(self.getRecommendation(cosine_sim))[:-1])
        except:
            recommend ='검색 결과를 다시 확인해주세요'
        self.lbl_result.setText(recommend)

        #self.LW.addItem(recommend[1])
        # self.addItemText = recommend
        # self.LW.addItem(self.addItemText)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Exam()
    w.show()
    sys.exit(app.exec_())