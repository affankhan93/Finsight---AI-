from datasets import Dataset
from dotenv import load_dotenv
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq 
from langchain_pinecone import PineconeEmbeddings
from ragas.run_config import RunConfig
import os 

load_dotenv() 

test_data = [
    {
        "question" : "What is the difference savings and investments?",

        "answer": "Savings are the portion of income that you set aside for short-term needs and liquidity. They are typically kept in bank or post-office accounts, earn only small amount of interest, and can be withdrawn easily whenever required."
        "Investments involve deploying money from those savings into financial or non-financial products (such as fixed deposits, stocks mutual funds, etc.) with the expectation of earning higher returns over time."
        "The purpose is to grow the money by creating assets, and investments generally carry higher risk and are less liquid than savings.",

        "contexts": [
            "Savings are the surplus of income over expenditure. People usually meet their short term goals with savings."
            "Money in savings accounts of a bank earns a small amount of interest and it is easy to withdraw it whenever needed."
            "Investment is the act of deployment of money out of savings into financial or no-financial products with the expectation of earning higher return over a period of time."
        ],

        "ground_truth" : "Savings are the portion of income that is not spent; they are kept to maintain liquidity for short-term or urgent needs,"
        "carry low or negligible risk and are highly liquid. Investments deploy savings into financial or non-financial products to grow money and earn higher returns; their risk depends on the asset and they are comparatively less liquid.",
    },
    {
        "question" : "What is inflation and how does it affect investments?",

        "answer": "Inflation is the rise in prices of goods and services over time, which reduces the purchasing power of money a rupee (or any unit of currency) buys fewer items than it did before."
        "Because inflation erodes purchasing power it poses an inflation (purchasing-power) risk to investors the cash flows or returns form an investment may be worth less in real terms in the future than they are today."
        "Consequently, investors need to consider inflation when planning their investments, as it can diminish the real value of their returns.",

        "contexts": [
            "Inflation refers to rise in prices of goods and services. Over a period of time, as the cost of goods and services increases, the ability of a unit of money, say one rupee, to buy goods and services keeps declining. In other words, the Purchasing Power of money, i.e."
            "ability of money to buy anything, decreases. It is important to take into account the effects of inflation on your investments during financial planning. Investors greatly fear inflation since it reduces the value of their investment."
        ],

        "ground_truth" : "Inflation is the rise in prices of goods and services, which lowers the purchasing power of money over time."
         "Because it reduces the value of investments, its effect should be taken into account during financial planning",
    },
    {    
        "question" : "What is a Credit card and a Debit card?",

        "answer" : "Credit card gives the card holder the benefit of availing credti facility for a certain period of time."
        "Debit card, on the other hand is a card issued to a bank account holder for withdrawing money at ATMs from his account as well as to make payment at point of sale."
        "All the merchant establishments accept debit cards in settlement of transactions.",

        "contexts" : [
            "Credit card gives the card holder the benefit of availing credit facility for a certain period of time for example making payments without haveing immediate money in hand in the form of credit card transactions."
            "Debit card, on the other hand, is a card issued to a bank account holder of withdrawing money at ATMs from his account as well as to make payment at point of sale."
            "Both credit and debit cards can be used for withdrawal of cash from ATMs as well as for digital transactions."
        ],

        "ground_truth": "Credit card gives the card holder the benefit of availing credit facility for a certain period of time."
        "Debit card issued to a bank account holder for withdrawing money at ATMs from his account as well as to make payment at point of sale." 
    },
    {
        "question" : "What are Assets and Liabilities?",

        "answer" : "Items that you own and have economic value are your assets."
        "Items which you owe to other or have borrowed from others are your liabilites.",

        "contexts" : [
            "Items that you own and have enconomic value are your assets and items which you owe to others or have borrowed from other are your liabilities." 
            "for example: if you save and then invest in a fixed deposit, it is your asset. On the other hand, if you borrow funds and take a loan from bank or any individual, it is your liability."
        ],

        "ground_truth": "Items that you own and have economic value are you assets and Items which you owe to others or ahve borrowed from others are your liabilities."
    }, 
    {
        "question" : "What is Power of Compounding? ",

        "answer" : "Power of compounding is the effect where even small, regualr investments grow significantly over time" 
        "because the earnings themselves generate further earnings. Unlike simpel interest, which is earned only on the original principal,"
        "compumnding allows interest to be earned on both the principal and the accumulated interest, leading to large growth of the investment as time passes",

        "contexts" : [
            "With simple interest, you can earn interest only on the principal (that is, the amount you initally invested); While with compounding interest, you earn interest on the principal as well as, previously earned interest."
        ],

        "ground_truth": "with simple interest, you can earn interest only on the principal (that is, the amount you initially invested); "
        "while with compounding interest, you earn interest on the principal as well as, previously earned interest."
    },
]

# Evalute with groq LLM 
groq_llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model = 'openai/gpt-oss-120b', 
    temperature= 0.2,
    max_tokens=2048, 
)

ragas_llm = LangchainLLMWrapper(groq_llm)

EMBED_MODEL = 'llama-text-embed-v2'
pinecone_embedding = LangchainEmbeddingsWrapper(PineconeEmbeddings(model = EMBED_MODEL))

eval_dataset = Dataset.from_list(test_data)

run_config = RunConfig(
    timeout=300,
    max_retries=2,
    max_workers=1
)

result = evaluate(
    dataset=eval_dataset,
    metrics=[
        faithfulness, 
        answer_relevancy,
        context_precision, 
        context_recall
    ],
    llm = groq_llm, 
    embeddings=pinecone_embedding, 
    run_config=run_config
)

print(result)

df = result.to_pandas()
print(df)

df.to_csv("ragas_financial_result.csv", index = False)


