import streamlit as st
from openai import OpenAI
import json

# ------------------------
# MOCK DATA & SETUP
# ------------------------
mock_order_db = {
    "john@example.com": {
        "order_id": "ORD12345",
        "status": "Out for Delivery",
        "expected_delivery": "2025-07-06",
        "carrier": "BlueDart",
        "tracking_link": "https://track.bluedart.com/ORD12345",
        "amount": 1299
    },
    "alice@example.com": {
        "order_id": "ORD67890",
        "status": "Shipped",
        "expected_delivery": "2025-07-08",
        "carrier": "Delhivery",
        "tracking_link": "https://track.delhivery.com/ORD67890",
        "amount": 899
    },
    "bob@example.com": {
        "order_id": "ORD54321",
        "status": "Delivered",
        "expected_delivery": "2025-07-02",
        "carrier": "Xpressbees",
        "tracking_link": "https://xpressbees.com/track/ORD54321",
        "amount": 1549
    },
    "sara@example.com": {
        "order_id": "ORD98765",
        "status": "Processing",
        "expected_delivery": "2025-07-10",
        "carrier": "Ecom Express",
        "tracking_link": "https://ecomexpress.in/track/ORD98765",
        "amount": 2199
    }
}

# --- Setup OpenAI client ---
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else st.text_input("Enter your OpenAI API key:", type="password")
if not OPENAI_API_KEY:
    st.stop()
client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------
# AGENT LOGIC
# ------------------------
def assign_agent(user_input):
    routing_prompt = f'''
    You are a routing assistant.

    Based on the user's support request below, identify the appropriate agent to handle it.

    Available Bots:
    - Order_Tracking_Agent
    - Refund_Agent
    - Return_Agent
    - General_Support_Agent

    Respond with ONLY the name of the appropriate agent.

    User Request:
      {user_input}
    '''
    routing_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role":"user", "content":routing_prompt}
        ]
    )
    return routing_response.choices[0].message.content.strip()

def ask_AI(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role":"user", "content":prompt}
        ]
    )
    return response.choices[0].message.content

def tracking_order_agent(user_email, user_prompt):
    order = mock_order_db.get(user_email)
    if not order:
        return "Sorry, we couldn't find any orders with that email."
    tracking_prompt = f'''
    You are a friendly and helpful customer support assistant.

    A customer has asked the following question:
    "{user_prompt.strip()}"

    Below is their order information:
    - Order ID: {order['order_id']}
    - Status: {order['status']}
    - Carrier: {order['carrier']}
    - Expected Delivery: {order['expected_delivery']}
    - Amount: ₹{order['amount']}
    - Tracking Link: {order['tracking_link']}

    Please write a warm, natural response that:
    - Acknowledges the user's question.
    - Answers it as best as possible using the order info.
    - Gently explains if something can't be done (e.g., address change after shipping).
    - Provides the tracking link and delivery timeline where relevant.
    - Keeps the tone conversational, helpful, and human-like.
    '''
    return ask_AI(tracking_prompt)

def refund_agent(user_email,user_prompt):
    order = mock_order_db.get(user_email)
    if not order:
        return "Sorry, we couldn't find any orders with that email."
    refund_prompt = f"""
    You are a helpful, friendly, and empathetic customer support assistant.

    A customer sent this message:
    "{user_prompt.strip()}"

    Here are the customer's order and refund details:
    - Order ID: {order['order_id']}
    - Refund Amount: ₹{order['amount']}
    - Delivery Status: {order['status']}
    - Expected Delivery Date: {order['expected_delivery']}
    - Shipping Carrier: {order['carrier']}
    - Tracking Link: {order['tracking_link']}
    - Customer Email: {user_email}

    Your task:

    Based on the delivery status, generate a friendly and conversational chat-style message as follows:

    **If the order *has already been delivered*:**
    1. Inform the customer that their refund request has been successfully processed.
    2. Let them know when the refund amount will reflect in their account.
    3. Mention that a confirmation email has already been sent.
    4. Provide a quick delivery summary (status, expected delivery date, and tracking link).
    5. End the message by reassuring the customer that they can reach out anytime for further help.

    **If the order *has NOT been delivered yet*:**
    1. Kindly explain the refund policy and why refunds are usually processed after delivery or under specific conditions.
    2. Mention the current delivery status, expected delivery date, and share the tracking link.
    3. Empathize with any inconvenience and let them know you’re here to help or escalate if needed.
    4. Reassure them they can always reach out again if they have more questions.

    Tone Guide:
    - Keep the tone warm, clear, friendly, and professional.
    - Don’t write this like a formal email. Make it sound like a helpful chat response.

    Only generate the response text for the customer. Do not include any explanations or instructions in your output.
    """
    return ask_AI(refund_prompt)

def return_agent(user_email,user_prompt):
    order = mock_order_db.get(user_email)
    if not order:
        return "Sorry, we couldn't find any orders with that email."
    return_prompt = f"""
    You are a helpful, friendly, and empathetic customer support agent in a live chat.

    A customer has sent the following message:
    "{user_prompt.strip()}"

    Here are the customer's order details:
    - Order ID: {order['order_id']}
    - Pickup Date (for return): Tomorrow
    - Refund Amount: ₹{order['amount']}
    - Delivery Status: {order['status']}
    - Expected Delivery Date: {order['expected_delivery']}
    - Shipping Carrier: {order['carrier']}
    - Tracking Link: {order['tracking_link']}
    - Customer Email: {user_email}

    Your task is to write a warm, supportive, and human-like **chat-style** response. Use simple, clear, and reassuring language.

    Write the response based on these conditions:

    ---

    **Case 1: If the order has already been delivered:**
    - Confirm that the return request is scheduled.
    - Let the customer know the pickup date and what to expect.
    - Briefly mention when they’ll receive the refund after pickup.
    - Remind them to keep the product ready for pickup.
    - Let them know a confirmation email has also been sent.

    ---

    **Case 2: If the order has NOT been delivered yet:**
    - Politely explain that returns can only be initiated after the product is delivered.
    - Mention the current delivery status, expected delivery date, and tracking link.
    - Reassure the customer that you’ll help them with the return as soon as it's eligible.
    - Use empathetic, supportive language, especially if the customer seems upset or confused.

    ---

    **Important Notes:**
    - Keep the message short, conversational, and natural—like a helpful chat, not a formal email.
    - Don’t repeat the user’s question. Just respond to it naturally.
    - Only include relevant information. Do NOT mention “case 1” or “case 2” in the response.
    - End with a friendly message letting the customer know they can reach out anytime for more help.

    Output only the customer-facing message.
    """
    return ask_AI(return_prompt)

def general_support_agent(user_prompt):
    general_support_prompt = f"""
    You are a professional and friendly customer support assistant.

    A customer has sent the following query:
    "{user_prompt.strip()}"

    Please write a warm, conversational, and helpful response:
    - Acknowledge their query
    - Mention that their message has been received and will be reviewed
    - Offer contact options (phone, email) if urgent
    - Use clear and kind language
    """
    return ask_AI(general_support_prompt)

# ------------------------
# Streamlit UI
# ------------------------

st.markdown("""
    <style>
    .botdesk-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0059b2;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
    }
    .botdesk-chat {
        border-radius: 14px;
        background: #f4f8fd;
        padding: 1.1rem 1.2rem;
        margin: 0.7rem 0;
        font-size: 1.07rem;
        border: 1px solid #e4e7ee;
        max-width: 80%;
        min-width: 10vw;
        color: black;    
    }
    .botdesk-user {
        background: #eaf5ff;
        border-left: 4px solid #2995ff;
        margin-left: auto;
        text-align: right;
        color:black
    }
    .botdesk-bot {
        background: #f5f7fa;
        border-left: 4px solid #00b380;
        margin-right: auto;
        text-align: left;
    }
    .botdesk-assign {
        color: #ff8800;
        font-weight: bold;
        margin: 1rem 0 0.3rem 0;
        font-size: 1.01rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="botdesk-header">🤖 BotDesk AI Support</div>', unsafe_allow_html=True)
st.markdown("AI-powered helpdesk: Get instant support, refunds, returns, or order status!")

with st.expander("ℹ️ **How to use**", expanded=False):
    st.write(
        "- Enter your email and your question below."
        "\n- BotDesk will route your query to the right agent automatically."
        "\n- You'll see the conversation live in the chat."
        "\n\nSample emails: john@example.com, alice@example.com, bob@example.com, sara@example.com"
    )

# Chat history state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_email = st.text_input("Your Email", value="john@example.com", key="email")
user_query = st.text_input("Type your question here...", key="query")

submit = st.button("Send", use_container_width=True)

if submit and user_query and user_email:
    # Add user message
    st.session_state.chat_history.append(("user", user_query, user_email))
    # Routing step
    with st.spinner("Routing your request..."):
        agent_assigned = assign_agent(user_query)
    st.session_state.chat_history.append(("assign", agent_assigned, user_email))
    # Agent answer step
    with st.spinner(f"{agent_assigned.replace('_', ' ').title()} is typing..."):
        if agent_assigned == "Order_Tracking_Agent":
            answer = tracking_order_agent(user_email, user_query)
        elif agent_assigned == "Refund_Agent":
            answer = refund_agent(user_email, user_query)
        elif agent_assigned == "Return_Agent":
            answer = return_agent(user_email, user_query)
        else:
            answer = general_support_agent(user_query)
    st.session_state.chat_history.append(("bot", answer, agent_assigned))

# ---- Chat display (replay all) ----
for role, message, meta in st.session_state.chat_history:
    if role == "user":
        st.markdown(f'<div class="botdesk-chat botdesk-user"> <b>You</b>:<br>{message}</div>', unsafe_allow_html=True)
    elif role == "assign":
        agent_clean = meta.replace("_", " ").replace("Agent", "Agent").title()
        st.markdown(f'<div class="botdesk-assign">Assigned to: {agent_clean}</div>', unsafe_allow_html=True)
    elif role == "bot":
        agent_clean = meta.replace("_", " ").replace("Agent", "Agent").title()
        st.markdown(f'<div class="botdesk-chat botdesk-bot"><b>{agent_clean}:</b><br>{message}</div>', unsafe_allow_html=True)

if st.button("Clear Chat", use_container_width=True):
    st.session_state.chat_history = []

st.markdown("---")
st.caption("Made with Streamlit & OpenAI · This is a mock demo. For real support, contact your business.")
