### Introduction

#### What is Samantha

* A generic recommender and predictor server for both offline machine learning and recommendation modeling and fast online production serving.
* MIT licence, oriented to production use (online field experiments in research and typical industrial use)

#### What Samantha can do in simple words: full-fledged, self-contained server that can be used in production right away with one configuration file, including the following components

* Data management, including offline and online, in (indexing) and out (post-processing), through configurable backends of most relational databases (e.g. MySQL, PostresSQL, SQLServer etc.), ElasticSearch or Redis.
* Model management, including online updating, building, loading, dumping and serving.
* Data processing pipeline based on a data expanding and feature extraction framework
* State-of-the-art models: collaborative filtering, matrix factorization, knn, trees, boosting and bandits/reinforcement learning
* Experimental framework for randomized A/B and bucket testing
* Feedback (for online learning/optimization) and evaluation (for experimenting) loops among application front-end, application back-end server and Samantha
* Abstracted model parameter server (through extensible variable and index spaces)
* Generic oracle-based optimization framework/solver with classic solvers
* Flexible model dependency, e.g. model ensemble, stacking, boosting
* Schedulers for regular model rebuilding or backup
* Integration with other state-of-the-art systems including XGBoost and TensorFlow.
* Control and customize all these components through one centralized configuration file

#### The targeted users of Samantha (users here refer to those who use Samantha; instead, end users is used to refer to the ultimate users of applications built using Samantha)

* Individuals or organizations who want to deploy a data-driven predictive system with minimum effort. They might need it to support answering relevant research questions involving an intelligent predictive part in their system or just to have an initial try to see the effects of such a predictive component. 
* Individuals or organizations who are working on comparing and developing new machine learning or recommendation models/algorithms, especially those who care about deploying their models/algorithms into production and evaluate them in front of end users

#### What to support in the near future

* Text modeling
* Web interface based creation and deployment of recommender/predictor engines
* Scale up to clusters including data storage and model learning

[Detailed Documentation](docs/SamanthaDoc.pdf)

### Citation

* Qian Zhao. 2018. User-Centric Design and Evaluation of Online Interactive Recommender Systems. Ph.D. Thesis. University of Minnesota.

### Note

* Samantha is a project developed by <a href="http://www-users.cs.umn.edu/~qian/">Qian Zhao</a>, a Ph.D. candiate at GroupLens lab and originated from his research projects. Currently, Samantha is in the process of integrating with <a href="http://lenskit.org/" target="_blank">Lenskit</a>. Feel free to give a try if you're intersted though. 

### For the paper GB-CENT

* The experiments were run with Samantha in: Qian Zhao, Yue Shi, Liangjie Hong. GB-CENT: Gradient Boosted Categorical Embedding and Numerical Trees. In Proceedings of the 26th International World Wide Web conference (WWW 2017), ACM, 2017.
* Go to branch <a href="https://github.com/grouplens/samantha/blob/qian/gbcent/docs/README.md">qian/gbcent, docs/README.md</a> for details
