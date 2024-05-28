# examples with the abstract of the papers
examples = [
    {
    "Text": "The correct use of model evaluation, model selection, and algorithm selection techniques is vital in academic machine learning research as well as in many industrial settings. This article reviews different techniques that can be used for each of these three subtasks and discusses the main advantages and disadvantages of each technique with references to theoretical and empirical studies. Further, recommendations are given to encourage best yet feasible practices in research and applications of machine learning. Common methods such as the holdout method for model evaluation and selection are covered, which are not recommended when working with small datasets. Different flavors of the bootstrap technique are introduced for estimating the uncertainty of performance estimates, as an alternative to confidence intervals via normal approximation if bootstrapping is computationally feasible. Common cross-validation techniques such as leave-oneout cross-validation and k-fold cross-validation are reviewed, the bias-variance trade-off for choosing k is discussed, and practical tips for the optimal choice of k are given based on empirical evidence. Different statistical tests for algorithm comparisons are presented, and strategies for dealing with multiple comparisons such as omnibus tests and multiple-comparison corrections are discussed. Finally, alternative methods for algorithm selection, such as the combined F-test 5x2 crossvalidation and nested cross-validation, are recommended for comparing machine learning algorithms when datasets are small.",
    "Output": "General ML",
    },
    {
    "Text": "As one of the most successful approaches to building recommender systems,collaborative filtering(CF) uses the known preferences of a group of users to make recommendations or predictions of the unknown preferences for other users. In this paper, we first introduce CF tasks and their main challenges, such as data sparsity, scalability, synonymy, gray sheep, shilling attacks, privacy protection, etc., and their possible solutions. We then present three main categories of CF techniques: memory-based, modelbased, and hybrid CF algorithms (that combine CF with other recommendation techniques), with examples for representative algorithms of each category, and analysis of their predictive performance and their ability to address the challenges. From basic techniques to the state-of-the-art, we attempt to present a comprehensive survey for CF techniques, which can be served as a roadmap for research and practice in this area.",
    "Output": "Recommenders", 
    },
    { 
    "Text": "This paper is an attempt to explain all the matrix calculus you need in order to understand the training of deep neural networks. We assume no math knowledge beyond what you learned in calculus 1, and provide links to help you refresh the necessary math where needed. Note that you do not need to understand this material before you start learning to train and use deep learning in practice; rather, this material is for those who are already familiar with the basics of neural networks, and wish to deepen their understanding of the underlying math. Don’t worry if you get stuck at some point along the way—just go back and reread the previous section, and try writing down and working through some examples. And if you’re still stuck, we’re happy to answer your questions in the Theory category at forums.fast.ai. Note: There is a reference section at the end of the paper summarizing all the key matrix calculus rules and terminology discussed here.",
    "Output": "Neural Networks",
    },
    {
    "Text": "Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions. We provide comprehensive empirical evidence showing that these residual networks are easier to optimize, and can gain accuracy from considerably increased depth. On the ImageNet dataset we evaluate residual nets with a depth of up to 152 layers—8× deeper than VGG nets [41] but still having lower complexity. An ensemble of these residual nets achieves 3.57% error onthe ImageNet test set. This result won the 1st place on the ILSVRC 2015 classification task. We also present analysis on CIFAR-10 with 100 and 1000 layers. training error (%) 10 Jian Sun 20 56-layer 20-layer 0 test error (%) 10 0 56-layer 20-layer 0 6 5 4 3 2 1 0 iter. (1e4) 1 2 3 4 iter. (1e4) 5 6 Figure 1. Training error (left) and test error (right) on CIFAR-10 with 20-layer and 56-layer “plain” networks. The deeper network has higher training error, and thus test error. Similar phenomena on ImageNet is presented in Fig. 4. greatly benefited from very deep models. The depth of representations is of central importance for many visual recognition tasks. Solely due to our extremely deep representations, we obtain a 28% relative improvement on the COCO object detection dataset. Deep residual nets are foundations of our submissions to ILSVRC & COCO 2015 competitions1, where we also won the 1st places on the tasks of ImageNet detection, ImageNet localization, COCO detection, and COCO segmentation.",
    "Output": "Object Detection", 
    },
    {
    "Text": "Over the past few years, neural networks have re-emerged as powerful machine-learning models, yielding state-of-the-art results in fields such as image recognition and speech processing. More recently, neural network models started to be applied also to textual natural language signals, again with very promising results. This tutorial surveys neural network models from the perspective of natural language processing research, in an attempt to bring natural-language researchers up to speed with the neural techniques. The tutorial covers input encoding for natural language tasks, feed-forward networks, convolutional networks, recurrent networks and recursive networks, as well as the computation graph abstraction for automatic gradient computation",
    "Output": "NLP",
    },  
]
prompt_classification = """

<instructions>
You are a Scientific paper system. 
Please do the following:
1.  Given a list of classes, 
    classify the document into one of the classes into the <classes></classes> tags.
    Think your answer with the following reasoning: 
    First, check the examples showed into the <example></example> tags. 
    Second, list CLUES like: 
    What is the paper about?,
    What kind of issue the paper is addressing?, 
    What kind of machine learning field this paper is related? and why?.
    Before reply add your reasoning into the <thinking></thinking> tags.
    Skip any preamble text and provide your final answer 
    just replay with the class name within <label></label> tags.
</instructions>

<classes>General ML, Recommenders, Neural Networks, Object Detection, NLP</classes>

here are some examples of text documents with their expected output: <example>""" 

suffix_template="""
</example>
<document>{doc_text}</document>
<label></label>
"""

prompt_keypoints = """ 

<instructions>
You are a Scientific paper system. 
Please do the following:
1. Extract the authors from the paper and add them into <author></author> tags.
2. Extract the paper's publish date and add it into <date></date> tags.
3. Extract the paper's title and add it into <title></title> tags.
</instructions>

<document>{doc_text}</document>

<author></author>
<date></date>
<title></title>
"""