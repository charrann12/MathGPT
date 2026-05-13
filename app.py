from langchain_groq import ChatGroq
from langchain_classic.chains import LLMChain, LLMMathChain
from langchain_classic.prompts import PromptTemplate
from langchain_classic.callbacks.streamlit import StreamlitCallbackHandler
from langchain_classic.agents.agent_types import AgentType
from langchain_classic.agents import Tool, initialize_agent
import streamlit as st
from langchain_community.utilities import WikipediaAPIWrapper

## Streamlit app setup 

st.set_page_config(page_title= "Text to Math problem solver ans Data Search assisstant", page_icon = "🧮")
st.title("Text to Math problem solver using Groq model")

groq_api_key = st.sidebar.text_input(label = "Groq API Key", type = "password")

if not groq_api_key:
    st.info("Please add the groq_api_key")
    st.stop()

llm = ChatGroq(groq_api_key = groq_api_key, model="llama-3.3-70b-versatile")

## Initialize tools 

## wikipedia tool
wikipedia_wrapper  = WikipediaAPIWrapper()
wikipedia_tool = Tool(
    name = "Wikipedia",
    func =wikipedia_wrapper.run,
    description= "A tool for searching the Internet to find the vatious information on the topics mentioned"
)

## math tool 
math_chain = LLMMathChain.from_llm(llm = llm)
calculator = Tool(
    name = "calculator",
    func = math_chain.run,
    description = "A tools for answering math related questions. Only input mathematical expression need to bed provided"
)

prompt = """
    You are an agent tasked for solving user's mnaths questions. Logically arrive at the solution and provide
    detailed explanation and display it point wise for the question below
    Question: {question}
    Answer:
"""

prompt_template = PromptTemplate(
    input_variables = ['question'],
    template = prompt
)

## Combine all tools into a chain 

chain = LLMChain(
    llm = llm,
    prompt = prompt_template
)

reasoning_tool = Tool(
    name = "reasoning_tool",
    func = chain.run,
    description = "A tool for answering logic-based and reasoning questions."
)

## Initialise the agent 

assistant_agent = initialize_agent(
    tools = [wikipedia_tool, calculator, reasoning_tool],
    llm = llm,
    agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose = False,
    handle_parsing_errors = True
)

## session state 

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant",
         "content": "Hii. I am a math chatbot who can answer your math question"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


## Lets start the interaction 

question=st.text_area("Enter youe question:","I have 5 bananas and 7 grapes. I eat 2 bananas and give away 3 grapes. Then I buy a dozen apples and 2 packs of blueberries. Each pack of blueberries contains 25 berries. How many total pieces of fruit do I have at the end?")

if st.button("find my answer"):
    if question:
        with st.spinner("In progress..."):
            st.session_state.messages.append({"role":"user", "content":question})
            st.chat_message("user").write(question)
            st_cb = StreamlitCallbackHandler(
                st.container(),
                expand_new_thoughts = False,
            )
            response = assistant_agent.run(
                    question,
                    callbacks = [st_cb] 
            )
            st.session_state.messages.append(
                {
                    "role":"assistant",
                    "content":response
                }
            )
            st.write("## Response: ")
            st.success(response)
     
    else:
        st.warning("Please provide the question")
            


