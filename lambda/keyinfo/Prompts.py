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