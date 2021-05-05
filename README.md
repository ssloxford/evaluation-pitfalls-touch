# Common Evaluation Pitfalls in Touch-Based Authentication Systems

Artifacts for "[Common Evaluation Pitfalls in Touch-Based Authentication Systems](https://arxiv.org/)".

<p align="center"><img src="https://github.com/ssloxford/evaluation-pitfalls-touch/blob/main/images/overview.png" width="70%"></p>

## Data
The data used in this paper is available on [http://example.com/](http://example.com/).

The `features.zip` contains the `features.csv` which is the only file needed to recreate the experiments presented in the paper.

If you would like to perform the feature extraction yourself, the `data_files.zip` folder contains all the necessary files with the following structure:
```
├── data_files                  
│   ├── UUID_X1                                    # User ID  
│   │   │── SESSION_Y1                             
│   │   │   │── scroll                             # Social media task 
│   │   │   │   │── REPETITON_W1       
│   │   │   │   │   │── accelerometer_data
│   │   │   │   │   │   └── ###-###-###.csv 
│   │   │   │   │   │── gyroscope_data
│   │   │   │   │   │   └── ###-###-###.csv 
│   │   │   │   │   └── touch_data
│   │   │   │   │       └── ###-###-###.csv 
|   |   |   |   └── REPETITON_W2    
|   |   |   |       └── ... 
│   │   │   └── swipe                               # Image gallery task
│   │   │       │── REPETITON_Z1
│   │   │       │   │── accelerometer_data
│   │   │       │   │   └── ###-###-###.csv
│   │   │       │   │── gyroscope_data
│   │   │       │   │   └── ###-###-###.csv
│   │   │       │   └── touch_data
│   │   │       │       └── ###-###-###.csv
│   │   |       └── REPETITON_Z2    
│   │   |           └── ... 
│   │   |
│   │   └── SESSION_Y2
│   │       └── ...
│   └── UUID_X2
│   │   └── ..
│   └── ... 
```


## Using this codebase

To use this repository, you will also need `docker`. Then complete the following steps:

1. `git clone https://github.com/ssloxford/evaluation-pitfalls-touch.git`
2. `cd evaluation-pitfalls-touch/data`
3. `wget https://github.com/ssloxford/short-lived-adversarial-perturbations/releases/download/usenix21/data.zip`
    - (Optional) If you would like to generate the feature.csv yourself run: <br/> `wget https://github.com/ssloxford/short-lived-adversarial-perturbations/releases/download/usenix21/data.zip` instead.
4. `unzip features.zip`
    - (Optional) `unzip data_files.zip`
4. `cd .. && docker build -t evaluation-pitfalls-touch .`
5. To start and connect to the docker container use: <br/> `docker run -it -v $(pwd)/data:/touch/data --name evaluation-pitfalls-touch  evaluation-pitfalls-touch`
    - (Optional) `cd data && python3 feature_extraction.py && cd ..`
6. You can now run the experiments - for instance `cd experiments && python3 p2_single_phone_model.py`


## iOS Application

We also share the source code of the iOS application in the that was developed for data collection purposes. This version can be found in the `ios-app` folder but is not immediately functional as a back-end server is needed to make it work. However, it can be used as a reference or made usable with minor modifications.


## Contributors

* [Martin Georgiev](http://www.cs.ox.ac.uk/people/martin.georgiev/)
* [Simon Eberz](https://www.cs.ox.ac.uk/people/simon.eberz/)
* [Henry Turner](http://www.cs.ox.ac.uk/people/henry.turner/)
* [Giulio Lovisotto](https://giuliolovisotto.github.io)
 

## Acknowledgements

This work was generously supported by a grant from Mastercard and by the Engineering and Physical Sciences Research Council \[grant numbers EP/N509711/1, EP/P00881X/1\].