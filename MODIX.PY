import gradio as gr
import datetime
import time
from dateutil.relativedelta import relativedelta
import google.generativeai as genai
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure Gemini API (with error handling)
try:
    GOOGLE_API_KEY = "AIzaSyBtIrJKZbgr1UXfCv56pEiZHZ75dWuIBNw"  # Replace with your actual API key
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    AI_ENABLED = True
except:
    AI_ENABLED = False
    print("AI features disabled - proceeding without Gemini API")
print(AI_ENABLED)
# Constants
FALLBACK_INSIGHTS = """
## 🌟 Your Life Journey

*📅 Born in {year}*  
The world was a different place when you were born!  
*⏳ {age} years young*  
Every moment has shaped who you are today.
"""

FALLBACK_FACTS = [
    "🌍 The world population has grown significantly since your birth",
    "📱 Technology has evolved in ways no one could have predicted",
    "🎵 Music and culture have transformed multiple times",
    "🌱 Environmental awareness has increased dramatically",
    "🚀 Space exploration has made incredible advances"
]

# 3D Visualization Functions
def create_life_progress_3d(age, max_age=90):
    """Create a 3D progress visualization"""
    theta = np.linspace(0, 2*np.pi, 100)
    phi = np.linspace(0, np.pi, 50)
    
    # Full sphere (potential lifespan)
    x_full = np.outer(np.cos(theta), np.sin(phi))
    y_full = np.outer(np.sin(theta), np.sin(phi))
    z_full = np.outer(np.ones(100), np.cos(phi))
    
    # Completed portion
    progress = min(age/max_age, 1.0)
    phi_progress = np.linspace(0, progress*np.pi, 50)
    
    x_part = np.outer(np.cos(theta), np.sin(phi_progress))
    y_part = np.outer(np.sin(theta), np.sin(phi_progress))
    z_part = np.outer(np.ones(100), np.cos(phi_progress))
    
    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'surface'}]])
    
    fig.add_trace(go.Surface(
        x=x_full, y=y_full, z=z_full,
        colorscale='Blues',
        opacity=0.3,
        showscale=False,
        name='Potential'
    ))
    
    fig.add_trace(go.Surface(
        x=x_part, y=y_part, z=z_part,
        colorscale='Viridis',
        opacity=0.9,
        showscale=False,
        name='Lived'
    ))
    
    fig.update_layout(
        title=f'Life Progress: {int(progress*100)}%',
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        ),
        margin=dict(t=50, b=0, l=0, r=0),
        height=400
    )
    
    return fig

# Core Calculation Functions
def calculate_age_details(dob):
    """Calculate all age metrics"""
    today = datetime.date.today()
    delta = relativedelta(today, dob)
    
    years = delta.years
    months = delta.months
    days = delta.days
    total_days = (today - dob).days
    total_hours = total_days * 24
    total_minutes = total_hours * 60
    total_seconds = total_minutes * 60
    
    next_birthday = dob.replace(year=today.year)
    if next_birthday < today:
        next_birthday = next_birthday.replace(year=today.year + 1)
    days_until_birthday = (next_birthday - today).days
    
    return {
        "years": years,
        "months": months,
        "days": days,
        "total_days": total_days,
        "total_hours": total_hours,
        "total_minutes": total_minutes,
        "total_seconds": total_seconds,
        "next_birthday": next_birthday.strftime("%B %d, %Y"),
        "days_until_birthday": days_until_birthday,
        "birth_year": dob.year
    }

# AI Functions
def generate_ai_insights(dob, age_data):
    """Generate AI insights about the user's lifetime"""
    if not AI_ENABLED:
        return FALLBACK_INSIGHTS.format(
            year=age_data["birth_year"],
            age=age_data["years"]
        )
    
    # try:
        
    # except:
    #     return FALLBACK_INSIGHTS.format(
    #         year=age_data["birth_year"],
    #         age=age_data["years"]
    #     )
    prompt = f"""Generate a beautiful, uplifting reflection about someone born on {dob.strftime('%B %d, %Y')}:
        - They are {age_data["years"]} years, {age_data["months"]} months old
        - Mention 1-2 significant world events from their birth year
        - Include an inspiring quote about time
        - Use markdown with emojis
        - Keep it under 150 words"""
        
    response = model.generate_content(prompt)
    return response.text

def generate_ai_facts(dob, age_data):
    """Generate interesting facts about the user's lifetime"""
    if not AI_ENABLED:
        return "\n".join([f"- {fact}" for fact in FALLBACK_FACTS])
    
    try:
        prompt = f"""Generate 5 interesting facts about what someone born in {dob.year} has experienced:
        - Include technological advances
        - Include cultural changes
        - Include world events
        - Use bullet points with emojis
        - Make each fact 1 sentence"""
        
        response = model.generate_content(prompt)
        return response.text
    except:
        return "\n".join([f"- {fact}" for fact in FALLBACK_FACTS])

# UI Components
def create_stats_grid(age_data):
    """Create the statistics display grid"""
    with gr.Row():
        with gr.Column():
            gr.Markdown("### ⏳ Time Alive")
            gr.Markdown(f"""
            *{age_data['years']}* years  
            *{age_data['months']}* months  
            *{age_data['days']}* days
            """)
        
        with gr.Column():
            gr.Markdown("### 📊 Total Time")
            gr.Markdown(f"""
            *{age_data['total_days']:,}* days  
            *{age_data['total_hours']:,}* hours  
            *{age_data['total_minutes']:,}* minutes  
            *{age_data['total_seconds']:,}* seconds
            """)
        
        with gr.Column():
            gr.Markdown("### 🎂 Next Birthday")
            gr.Markdown(f"""
            *{age_data['next_birthday']}*  
            *{age_data['days_until_birthday']}* days to go
            """)

# Main App
with gr.Blocks(
    title="3D Life Visualizer",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container { max-width: 1000px !important; margin: auto; }
    .loading-screen {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .pulse {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    """
) as app:
    
    # Loading Animation Component
    loading_screen = gr.HTML("""
    <div class="loading-screen pulse">
        <h2 style="margin-bottom: 1rem;">Calculating Your Life Journey</h2>
        <div class="loader" style="margin: 0 auto;"></div>
        <style>
            .loader {
                border: 5px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top: 5px solid white;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </div>
    """)
    
    # Main UI (hidden initially)
    with gr.Column(visible=False) as main_ui:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 🎂 Your Birth Date")
                dob_input = gr.Textbox(
                    label="YYYY-MM-DD",
                    value=datetime.date.today().strftime("%Y-%m-%d")
                )
                submit_btn = gr.Button("Update", variant="primary")
                
                with gr.Accordion("📊 Detailed Statistics", open=False):
                    stats = gr.HTML()
            
            with gr.Column(scale=2):
                gr.Markdown("# 🌍 Your Life in 3D")
                plot_3d = gr.Plot()
                
                with gr.Tabs():
                    with gr.Tab("🌟 Insights"):
                        insights = gr.Markdown()
                    
                    with gr.Tab("📜 Fun Facts"):
                        facts = gr.Markdown()
    
    # Initial calculation on load
    def initial_calculation():
        dob = datetime.date.today()
        age_data = calculate_age_details(dob)
        
        # Create 3D visualization
        fig = create_life_progress_3d(age_data["years"])
        
        # Generate content
        ai_insights = generate_ai_insights(dob, age_data)
        ai_facts = generate_ai_facts(dob, age_data)
        
        # Create stats grid
        stats_html = f"""
        <div style="
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        ">
            {create_stats_grid(age_data)}
        </div>
        """
        
        return (
            gr.Column(visible=True),  # Show main UI
            gr.HTML(visible=False),    # Hide loading screen
            fig,
            ai_insights,
            ai_facts,
            stats_html
        )
    
    # Handle date input
    def calculate_all(dob_str):
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
            if dob > datetime.date.today():
                raise ValueError("Future date")
        except:
            return (
                gr.Column(visible=True),
                gr.HTML(visible=False),
                None,
                "⚠ Please enter a valid past date in YYYY-MM-DD format",
                "",
                ""
            )
        
        age_data = calculate_age_details(dob)
        fig = create_life_progress_3d(age_data["years"])
        ai_insights = generate_ai_insights(dob, age_data)
        ai_facts = generate_ai_facts(dob, age_data)
        
        stats_html = f"""
        <div style="
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        ">
            {create_stats_grid(age_data)}
        </div>
        """
        
        return (
            gr.Column(visible=True),
            gr.HTML(visible=False),
            fig,
            ai_insights,
            ai_facts,
            stats_html
        )
    
    # Event handlers
    app.load(
        fn=initial_calculation,
        outputs=[main_ui, loading_screen, plot_3d, insights, facts, stats]
    )
    
    submit_btn.click(
        fn=calculate_all,
        inputs=dob_input,
        outputs=[main_ui, loading_screen, plot_3d, insights, facts, stats]
    )

if __name__ == "__main__":
    app.launch(share=True)
