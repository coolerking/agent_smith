# サンプルコード

`imuDataVisualizer_madgwick` の `def updateImuMadgwickFilteredData()`

* 2連続データの差分で変化有無を判断するようになっているが本来は一発でＯＫのはず。よって `dead_zone` 変数なども不要のはず。
* `MadgwickAHRS` のコンストラクタ引数 `beta` は `sampleperiod` との兼ね合いで値設定が違うような気がする。とりあえずディフォルト１から始める。

以上
