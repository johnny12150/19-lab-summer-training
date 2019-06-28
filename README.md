# 2019 Lab的暑期訓練
## 時間表
> https://docs.google.com/spreadsheets/d/1VIjkSkHaKyyWUgojbz2mj1N6KN3iev-BVKLWan3W66E/edit#gid=0

## 使用到的套件
可以參考以上的Pipfile

**cuda與cuDNN需要另外安裝**，v10不需要手動設定環境變數
> https://medium.com/@WhoYoung99/2018%E6%9C%80%E6%96%B0win10%E5%AE%89%E8%A3%9Dtensorflow-gpu-keras-8b3f8652509a

cuda, cuDNN跟Node.js一樣直接裝在全域(global)

若嫌麻煩可以改用conda的虛擬環境
> https://medium.com/%E9%9B%9E%E9%9B%9E%E8%88%87%E5%85%94%E5%85%94%E7%9A%84%E5%B7%A5%E7%A8%8B%E4%B8%96%E7%95%8C/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92-ml-note-windows-%E6%90%AD%E5%BB%BAtensorflow-gpu-%E7%92%B0%E5%A2%83-anaconda-tensorflow-gpu-cuda-cudnn-a047c0f275f4

### IDE
主要使用jupyer lab, 並搭配以下extensions:
* Jupyterlab-toc: 可以顯示jupyter內markdown的大綱
* jupyterlab-go-to-definition
* nbdime: 比較不同commit的ipynb的差異
* jupyterlab-variableInspector: 在jupyter lab內觀察變數的內容