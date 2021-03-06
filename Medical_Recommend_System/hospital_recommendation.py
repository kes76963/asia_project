import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QStringListModel
from PyQt5 import uic
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from gensim.models import Word2Vec
from scipy.io import mmwrite, mmread
import pickle
import webbrowser

form_window = uic.loadUiType('plz_Yes_button_edit_3.ui')[0]

class Exam(QWidget, form_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #데이터 불러오기
        self.df_review = pd.read_csv('./datasets/model_data_Hospital_and_info2.csv',index_col=0)
        self.df_review.info()
        self.Tfidf_matrix = mmread('./models/tfidf_hospital_review_l.mtx').tocsr()
        self.embedding_model = Word2Vec.load('./models/word2VecModel_hospital_l2.model')
        with open('./models/tfidf_l.pickle', 'rb') as f:
            self.Tfidf = pickle.load(f)

        # 카테고리 목록 리스트화
        self.cmb_title_2.addItem('과를 선택하세요')
        category = list(self.df_review.category.unique()) #카테고리 중복 없이
        category = sorted(category)

        for c in category :
            self.cmb_title_2.addItem(c)

        # 지역 목록 리스트화
        self.cmb_title.addItem('지역을 선택하세요')
        add_list = []
        for i in self.df_review.addresses:
            a = i.split(' ')[0] #지역이름만
            add_list.append(a)

        add_set = set(add_list) #중복 제거 위해 set
        address = list(add_set) #다시 list
        address = sorted(address)
        address.pop(0) #지역 아닌 다른 단어가 있어서 pop


        for add in address:
            self.cmb_title.addItem(add) #지역 목록

        # 병원 목록과 진료과목 리스트로 만들기
        total = ''
        for c in self.df_review.clinics:
            total += c

        totals = total.split(', ')
        total_set = set(totals)
        total = list(total_set)  #진료 과목
        total = sorted(total)

        titles = list(self.df_review.names) # 병원 이름
        titles = sorted(titles) # 따로 정렬하는 이유는 병원 이름이 먼저 나오게 하기 위해서

        key_title = titles + total      #병원 + 진료 과목

        #자동완성
        model = QStringListModel()
        model.setStringList(list(key_title))
        completer = QCompleter()
        completer.setModel(model)

        # 버튼 함수
        self.le_title.setCompleter(completer)
        self.le_title.returnPressed.connect(self.btn_recommend_slot)
        self.btn_recommend.clicked.connect(self.btn_recommend_slot) # 엔터 또는 버튼 클릭시
        self.cmb_title_2.currentIndexChanged.connect(self.cmb_title_slot_2)
        self.cmb_title.currentIndexChanged.connect(self.cmb_title_slot)
        self.listWidget.itemClicked.connect(self.hospital_info)
        self.btn_html.clicked.connect(self.open_web)
        self.btn_recommend_5.clicked.connect(self.btn_clicked)


    #리셋 기능
    def btn_clicked(self):
        print('리셋 버튼 클릭')
        self.cmb_title_2.clear()
        self.cmb_title.clear()
        self.le_title.clear()
        self.infotext.clear()

        #병원 정보 처음에 나오는 내용
        default_text = '[ 주요 진료 과목 ]\n\n[ 주소 ]\n\n[ 전화번호 ]'
        self.infotext.setText(default_text)

        category = list(self.df_review.category.unique())
        category = sorted(category)
        self.cmb_title_2.addItem('과를 선택하세요')
        self.cmb_title.addItem('지역을 선택하세요')

        add_list = []
        for i in self.df_review.addresses:
            a = i.split(' ')[0]
            add_list.append(a)

        add_set = set(add_list)
        address = list(add_set)
        address = sorted(address)
        address.pop(0)

        for add in address:
            self.cmb_title.addItem(add)  # 지역 목록

        for c in category:
            self.cmb_title_2.addItem(c)  # 카테고리 목록


    # 홈페이지 오픈
    def open_web(self):
        print('홈페이지 바로가기 클릭')
        title = self.listWidget.currentItem().text()
        html = self.df_review[self.df_review.names == title].iloc[0, 5]
        webbrowser.open(html) # 홈페이지 연동


    # 병원을 클릭 했을 때, 병원 정보 보여주기
    def hospital_info(self):
        print('병원 정보 클릭')
        title = self.listWidget.currentItem().text()

        try :
            a = self.df_review[self.df_review.names == title].iloc[0, 3].split(',')[:10] # 주요 진료 과목 10개만
            a = ','.join(a)
            b = self.df_review[self.df_review.names == title].iloc[0, 4] # 주소
            c = self.df_review[self.df_review.names == title].iloc[0, 6] # 전화번호
            #d = self.df_review[self.df_review.names == title].iloc[0, 5] # 홈페이지 url / 홈페이지 오픈 버튼으로 대체
            recommend = '[ 주요 진료 과목 ]\n{0}\n\n[ 주소 ]\n{1}\n\n[ 전화번호 ]\n{2}'.format(a, b, c)
            self.infotext.setText(recommend)
            recommend = '홈페이지 바로가기 클릭!'
            self.btn_html.setText(recommend)
        except :
            pass


    # 병원 지역별로 필터링
    def cmb_title_slot(self):
        print('지역 선택 클릭')
        self.le_title.clear() # 먼저 병원을 클릭 했을 때
        title = self.cmb_title_2.currentText()
        address = self.cmb_title.currentText()

        region = self.df_review[(self.df_review.category == title) &(self.df_review.region == address)].iloc[:10, 1] # 자체 추천 순위로 출력
        recommend = list(region)
        #print(recommend)

        self.listWidget.clear()
        self.listWidget.insertItems(0, recommend)


    # 카테고리 탑10 병원
    def cmb_title_slot_2(self):
        print('과 선택 클릭')
        title = self.cmb_title_2.currentText()

        top = self.df_review[self.df_review.category == title].iloc[:10,1]
        #recommend = '\n'.join(list(top)) # 이거는 lbl_result에
        recommend = list(top)

        self.listWidget.clear()
        self.listWidget.insertItems(0, recommend)

    # #과, 지역 기반 추천시스템
    # def getRecommendation(self, cosine_sim):
    #     print('추천 클릭')
    #     address = self.cmb_title.currentText()
    #     #print(type(address))
    #     print(address)
    #     simScores = list(enumerate(cosine_sim[-1]))
    #     simScores = sorted(simScores, key=lambda x: x[1],
    #                        reverse=True)
    #     #print(simScores)
    #     simlist = []
    #     for i in simScores :
    #         add = self.df_review.iloc[i[0],7]
    #         #print(add,end='')
    #         if add == address :
    #             #print(add)
    #             simlist.append(i)
    #
    #     #simScores = simScores[0:10]
    #     #h_idx = [i[0] for i in simScores]
    #     h_idx = [i[0] for i in simlist[0:10]]
    #     print(h_idx)
    #     RecHosptiallist = self.df_review.iloc[h_idx]
    #     #print(RecHosptiallist)
    #     return RecHosptiallist.names

    #키워드 기반 추천 시스템
    def getRecommendation2(self, cosine_sim):
        title = self.cmb_title_2.currentText()
        address = self.cmb_title.currentText()
        print(title, address)
        simScores = list(enumerate(cosine_sim[-1]))
        simScores = sorted(simScores, key=lambda x: x[1], reverse=True)

        if title == '과를 선택하세요' and address =='지역을 선택하세요':
            pass
        else :
            simlist = []
            for i in simScores :
                add = self.df_review.iloc[i[0],7] # 지역
                tit = self.df_review.iloc[i[0],0] # 카테고리

                if add == address and tit == title : # 지역, 카테고리 동시에 일치할 때만 추가
                    #print(add)
                    simlist.append(i)

            h_idx = [i[0] for i in simlist[0:10]]

            if len(h_idx) == 0:
                RecHosptiallist = [f'{address} 지역에는 관련된 키워드가 없습니다.']
                return RecHosptiallist.names
            else :
                RecHosptiallist = self.df_review.iloc[h_idx]
                print(RecHosptiallist, '출력')
                return RecHosptiallist.names

        simScores = simScores[0:11]
        h_idx = [i[0] for i in simScores]
        RecHosptiallist = self.df_review.iloc[h_idx]
        return RecHosptiallist.names


    def btn_recommend_slot(self):
        print('추천 시스템 클릭')
        title = self.le_title.text()

        try:
            if title in list(self.df_review['names']):
                h_idx = self.df_review[
                    self.df_review['names']==title].index[0]
                cosine_sim = linear_kernel(
                    self.Tfidf_matrix[h_idx],
                    self.Tfidf_matrix)
                # recommend = '\n'.join(
                #     list(self.getRecommendation(cosine_sim))[1:])
                recommend = list(self.getRecommendation2(cosine_sim))[:-1]

            #elif title in total :


            else:
                print(title, '예외 키워드')
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
                # recommend = '\n'.join(
                #     list(self.getRecommendation(cosine_sim))[:-1])

                recommend = list(self.getRecommendation2(cosine_sim))[:-1]
        except:
            if title :
                recommend =['검색어를 다시 확인해주세요']
                self.infotext.clear()

                default_text = '[ 주요 진료 과목 ]\n\n[ 주소 ]\n\n[ 전화번호 ]'
                self.infotext.setText(default_text)

            else:
                pass
        self.listWidget.clear()
        self.listWidget.insertItems(0, recommend)

        #self.LW.addItem(recommend[1])
        # self.addItemText = recommend
        # self.LW.addItem(self.addItemText)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Exam()
    w.show()
    sys.exit(app.exec_())
