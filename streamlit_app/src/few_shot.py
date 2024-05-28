import streamlit as st

from langchain_community.embeddings import BedrockEmbeddings

from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import (
    MaxMarginalRelevanceExampleSelector,
    SemanticSimilarityExampleSelector,
)
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate


examples = [
    {
    "Text": "oracle problem problem error action please enable populate sheet thank design lead",
    "Output": "HR Support",
    },
    { "Text": "extended sick leave thursday pm extended sick leave hi had confirmation reports has had his sick leave extended by his doctor until please amend outstanding reflect submit cheers production editorial consultant",
    "Output": "HR Support", 
    },
    { 
    "Text": "for south tuesday october pm south hi please provide south requested thank senior tester",
    "Output": "HR Support",
    },
    {
    "Text": "access rights rights hello please provide these links thank browse",
    "Output": "HR Support", 
    },
    {
    "Text": "new stairter bucharest re hi please find filled form resume he has he requires stand he work standing due his conditions let other pending side thank best regards self december pm hello please fill date please advised currently contractor thank administration offcer",
    "Output": "HR Support",
    },
    {
    "Text": "project manager change pas december pm re change dear further please switch back role thank best regards programme",
    "Output": "Miscellaneous",
    },
    {
    "Text": "com friday october hello please add colleague thanks senior engineer",
    "Output": "Miscellaneous",
    },
    {
    "Text": "adding to network friday november pm hi please log two tickets tickets assigned directly best regards engineer friday november re ne si accounts thursday november pm hi add please recently joined thank",
    "Output": "Miscellaneous",
    },
    {
    "Text": "sn approval sn hello please update include thanks",
    "Output": "Miscellaneous",
    },
    {
    "Text": "changes changes hi please make changes title change old git tool please log best regards engineer",
    "Output": "Miscellaneous",
    },
    {
    "Text": "pre sales code set up oracle pre code has assigned hello please notify client codes after client holds least opportunity stage please notify opportunities stage proceed setting code requested thank kind regards friday october pm pre code has assigned hello please advised record number has assigned please review details take appropriate action reference number details requested location tower summary pre code additional comments requirements pre code dear please client code per attached form thank assign reference assignment summary location tower attachments pre code setup form please link kind regards ref msg",
    "Output": "Internal Project",
    },
    {
    "Text": "project codes to be opened spare oracle wednesday codes opened spare hello please thank regards analyst tuesday pm codes opened spare hi please help opening attached codes spare please let thanks accounts receivable lead",
    "Output": "Internal Project",
    },
    {
    "Text": "new project code oracle fusion pm code creation importance high hello per attached completed form please create code upcoming client please expedite code creation today possible ensure available possible forecast upcoming work possibly july please advise additional information forms required thanks nj",
    "Output": "Internal Project",
    },
    {
    "Text": "project to be closed pas july closed hi please close phase costs were recognized other activity planned pm approved closure thank officer",
    "Output": "Internal Project",
    },
    {
    "Text": "new project code pas hello please code starting opportunity identified by coming out past he has led effort door has him work client he has had initial call along next steps formal he working schedule follow call same folks meet client mid thanks",
    "Output": "Internal Project",
    },
    {
    "Text": "laptop refresh etc refresh etc hi since few years wondering due changed upgrade also procedure buy want thank senior analyst architecture",
    "Output": "Hardware",
    },
    {
    "Text": "fixing laptop screen sent thursday march fixing laptop screen dear laptop monitor little problem would appreciate if you could take look fix if possible regards software developer",
    "Output": "Hardware",
    },
    {
    "Text": "mobile phone replacement mobile phone replacement hello replace mobile phone call buttons started fell battery swelling phone details follows phone model blackberry best regards",
    "Output": "Hardware",
    },
    {
    "Text": "managed print services print good morning well called speak regarding print contracts advised experts print document established experience helping clients manage efficiently experience work efficiently where help working similar size businesses save across expenditure print beginning introductory meeting helps both parties fully understand each other then together review certain areas which range costs waste consolidation equipment agreements suitability hardware features compared location requirements hardware reliability consumable purchases especially toner printers levels invoicing strategies promote enforce efficient print duplex mono routing large jobs suitable output device auditing monitor understand distribute print costs document scanning processes meet reviewing october kind regards trainee class ermine st",
    "Output": "Hardware",
    },
    {
    "Text": "access request account hello everyone colleague had her working yesterday since she hand over requesting her please map file other solution thank kind regards infrastructure",
    "Output": "Hardware",
    },
    {
    "Text": "check if com is still available wednesday pm undeliverable expire days has failed these groups entered found please recipient problem continues please diagnostic information administrators generating remote returned resolver found id wed return path by id wed wed rf axe nj msg ref tower originating version banners checked tower id wed id wed id via transport wed mime version priority priority urgent importance high date wed expire days id unique impersonation protect similar false newly observed false user name false mismatch false targeted threat dictionary false authentication results pass designates permitted client envelope content type text content transfer encoding base",
    "Output": "Access",
    },
    {
    "Text": "request access to confluence space tuesday october pm confluence hi please confluence best regards senior analyst",
    "Output": "Access",
    },
    {
    "Text": "caps project please install credentials binding on master november caps please install credentials binding importance high hi context caps slave registered slave git push git tag git installed display credentials binding credentials push thanks help best regards software consultant design lead lead",
    "Output":"Access",
    },
    {
    "Text": "access to confluence pm re create conf mobile question add mobile listed search kind guys",
    "Output": "Access",
    },
    {
    "Text": "access to ms project thursday pm hi please added licence cost code thanks",
    "Output": "Access",
    },
    {
    "Text": "wants to access resources wants resources signature accept decline requests",
    "Output": "Storage",
    },
    {
    "Text": "remove out of com out hello colleague holiday by mistake she has mailbox out please help out thank great accounts payable",
    "Output": "Storage",
    },
    {
    "Text": "wants to access companies view wants companies view please sector information accept decline requests",
    "Output": "Storage",
    },
    {
    "Text": "mailbox full sent thursday undeliverable notification fusion purchase requests completed failed these or groups recipient mailbox full can accept please try message later or contact recipient directly following organization rejected your message diagnostic information for administrators generating server remote server returned mailbox full deliver exception failed process message due permanent exception with message cannot open mailbox configuration servers attendant stage original message headers with server id with id content type application name content transfer encoding binary notification fusion purchase requests completed thread topic notification fusion purchase requests completed thread index importance high priority date message id accept language en content language en attach yes mime version transport hosted originating return path response suppress",
    "Output": "Storage",
    },
    {
    "Text": "restrict access to tax project friday pm folder hi folder tax please restrict myself please thanks tax",
    "Output": "Storage",
    },
    {
    "Text": "low disc space problem pm low disc problem hi other colleagues facing low disc problem please merge two partitions partition best regards engineer",
    "Output": "Administrative rights",
    },
    {
    "Text": "issues with outlook sent monday can connect hi something appears have changed with credentials accepted but can use same credentials connect via web was working friday can you fix please thanks ext mob en glee",
    "Output": "Administrative rights",
    },
    {
    "Text": "windows update sent wednesday update hello have followed steps for update get updates thank you accounts payable",
    "Output": "Administrative rights",
    },
    {
    "Text": "outlook issues not received from a user sent thursday help with dear please help configure receive assign regards administrator",
    "Output": "Administrative rights",
    },
    {
    "Text": "windows update update hello running receive update please thanks",
    "Output": "Administrative rights",
    },
    {
    "Text": "new purchase po po replenishment friday pm re purchase po po hi highlighted red machine po has present please create replenishment also solve inquiry attached replace assign yesterday growth remember discussion looks prepared unassigned her maybe did please perform order supplier by attached image thank administrator phone thursday pm re purchase po po hi please create installation prepare po final owner po has raised by her she starts st going deliver her order next days replenish growth feasible fulfilled thank administrator phone thursday pm re purchase po sn ca inca cutie si si inca moment engineer ext thursday pm re purchase po va ne va sn growth etc el id thank administrator phone wednesday purchase po dear purchased please log installation please take consideration mandatory receipts section order receive item ordered kind regards administrator",
    "Output": "Purchase",
    },
    {
    "Text":   "thursday july good morning adaptor sd arrived accommodate her mobile device please log installation by thanks apologies delay fan courier failed deliveries about two weeks administrator phone",
    "Output": "Purchase",
    },
    {
    "Text": "new purchase po tuesday july pm purchase po ear purchased requested by pro please log allocation please take consideration mandatory receipts section order receive item ordered how video please explorer kind regards administrator",
    "Output": "Purchase",
    },
    {
    "Text": "new purchase po wednesday october pm purchase po dear purchased symmetry galaxy black please log installation please take consideration mandatory receipts section order receive item ordered kind regards administrator",
    "Output": "Purchase",
    },
    {
    "Text": "replenish purchase request for it final owner id has been approved july pm purchase final owner id has approved hi purchased received please log replenish stocks thank administrator ext",
    "Output": "Purchase",
    },

]

class build_prompt(object):
    def __init__(self, text, bedrock_client):
        self.input_text= text
        self.examples = examples
        self.bedrock= bedrock_client
        
    def generate_prompt(self):
        example_prompt = PromptTemplate(
            input_variables=["Text", "Output"],
            template="Text: {Text}\nOutput: {Output}",
        )
        # select the most similar example to the input
        example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
            # The list of examples available to select from.
            self.examples,
            # The embedding class used to produce embeddings which are used to measure semantic similarity.
            BedrockEmbeddings(client= self.bedrock, region_name= 'us-east-1', model_id= 'amazon.titan-embed-text-v1'),
            # The VectorStore class that is used to store the embeddings and do a similarity search over.
            FAISS,
            # The number of examples to produce.
            k=10,
        )
        prompt_claude = """

        <instructions>
        You are a IT ticket classifier. Given a list of classes, classify the document into one of the classes into the <classes></classes> tags.
        Think your answer with the following reasoning: 
        First, check the examples showed into the <example></example> tags. 
        Second, list CLUES like: 
        Determine the primary goal of the user's request. Are they seeking help, reporting an issue, requesting access, etc.?,
        Focus on the specifics mentioned in the ticket. Is it about software, hardware, network, permissions, or other services?, 
        Establish which department or team the ticket is addressing or should address.
        Before reply add your reasoning into the <thinking></thinking> tags.
        Skip any preamble text and provide your final answer just replay with the class name within <answer></answer> tags.
        </instructions>

        <classes>HR Support, Miscellaneous, Internal Project, Hardware, Access, Storage, Administrative rights, Purchase</classes>

        here are some examples of text documents with their expected output: <example>""" 

        suffix_template="""
        </example>
        <document>{doc_text}</document>
        <answer></answer>"""
        mmr_prompt = FewShotPromptTemplate(
            # We provide an ExampleSelector instead of examples.
            example_selector=example_selector,
            example_prompt=example_prompt,
            prefix=prompt_claude, #A prompt template string to put before the examples.
            suffix=suffix_template, #A prompt template string to put after the examples.
            input_variables=["doc_text"],
            )
        return mmr_prompt