import openai, os, dash, pandas
from io import StringIO
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from flask import jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from langchain.agents import load_tools
# from langchain.llms import OpenAI
# from langchain_openai import ChatOpenAI
from langchain.agents import create_structured_chat_agent
from langchain.agents import AgentExecutor
from langchain import hub
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

load_dotenv()

# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

load_dotenv()

prompt_template = hub.pull("hwchase17/structured-chat-agent")

def get_recommendations(category):

    if os.path.exists(category+'.csv'):
        df = pandas.read_csv('results/'+category+'.csv')

    else:
        # openai.api_key = os.getenv('OPENAI_API_KEY')

        tools = load_tools(["serpapi"])

        # llm = OpenAI(temperature=0)
        chat_model = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

        # chat_model = ChatOpenAI(model="gpt-4o-mini",
        #                         temperature=0,
        #                         max_tokens=500,
        #                         timeout=None,
        #                         max_retries=2
        #                        )

        agent = create_structured_chat_agent(chat_model, tools, prompt_template)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True, max_iterations=2)

        prompt = f'''
        You are an expert and to-the-point personal assistant. Whenever you are asked for recommendation, your task is to 
        reply with the top 10 best products by collating information from various sources and presenting the ones that feature the 
        most in all of those sources combined. Present only the results in a 1 through 10 manner in tabular form, with 2 more columns - 
        one for the price, and one for a one line summary about why that product deserves to be on the list or what its unique selling point is.
        Give your response as a dictionary named 'answers' with the following keys: rank, product, price, summary.

        What are the top 10 {category} to buy right now?
        '''
        # and one for the Amazon link where people can buy the product from. No verbose talk. 

        response = agent_executor.invoke({"input": prompt})

        df = pandas.DataFrame(response['output']['answers'])

        df.to_csv('results/'+category+'.csv', index=False)

    return df

app = dash.Dash(__name__)
CORS(app.server)

@app.server.route('/get_recommendations')
def get_recommendations_route():
    category = request.args.get('category')
    df = get_recommendations(category)
    result = df.to_dict(orient='records')
    return jsonify(result)

app.layout = html.Div([
    html.H1('What Should I Buy'),
    dcc.Input(id='category-input', type='text', placeholder='Enter product category', n_submit=0),
    html.Button('Get Recommendations', id='submit-button', n_clicks=0),
    dcc.Loading(
        id="loading-icon",
        type="circle",
        children=[
            dash_table.DataTable(
                id='recommendations-table',
                sort_action="native",
                style_table={'overflowX': 'auto', 'marginTop': 20}  # added margin top here
            )
        ]
    )
])

@app.callback(
    Output('recommendations-table', 'data'),
    Output('recommendations-table', 'columns'),
    [Input('submit-button', 'n_clicks'), Input('category-input', 'n_submit')],
    State('category-input', 'value')
)
def update_table(n_clicks, n_submit, category):
    trigger = dash.callback_context.triggered[0]
    if trigger['prop_id'].split('.')[0] in ['submit-button', 'category-input'] and category:
        df = get_recommendations(category)
        columns = [
            {"name": col, "id": col, "deletable": False, "selectable": False, "hideable": False}
            if col != 'Price' else {"name": col, "id": col, "deletable": False, "selectable": False, "hideable": False, 'type': 'numeric', 'format': 'plain_text'}
            for col in df.columns
        ]
        data = df.to_dict('records')
        return data, columns
    else:
        return [], []

if __name__ == '__main__':
    app.run_server(debug=True)