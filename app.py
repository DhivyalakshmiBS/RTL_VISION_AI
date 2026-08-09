import streamlit as st
import time
import os
from dotenv import load_dotenv
from google import genai
from streamlit_agraph import agraph, Node, Edge, Config
from utils.parser import analyze_verilog, detect_errors
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("❌ GEMINI_API_KEY not found in .env file.")
    st.stop()

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# LOAD CSS
# =========================================================

def load_css():

    css_path = os.path.join(
        os.path.dirname(__file__),
        "assets",
        "styles.css"
    )

    if os.path.exists(css_path):

        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )
def create_rtl_diagram(gate_details):
    
    nodes = []
    edges = []

    for index, gate_info in enumerate(gate_details):

        gate = gate_info["gate"]
        inputs = gate_info["inputs"]
        output = gate_info["output"]

        gate_id = f"gate_{index}"

        # Gate node
        nodes.append(
            Node(
                id=gate_id,
                label=gate,
                size=30,
                shape="box",
                color="#6366F1"
            )
        )

        # Input nodes
        for signal in inputs:

            input_id = f"{signal}_{index}"

            nodes.append(
                Node(
                    id=input_id,
                    label=signal,
                    size=20,
                    shape="dot",
                    color="#22C55E"
                )
            )

            edges.append(
                Edge(
                    source=input_id,
                    target=gate_id
                )
            )

        # Output node
        output_id = f"{output}_{index}"

        nodes.append(
            Node(
                id=output_id,
                label=output,
                size=20,
                shape="dot",
                color="#F59E0B"
            )
        )

        edges.append(
            Edge(
                source=gate_id,
                target=output_id
            )
        )

    config = Config(
        width=900,
        height=500,
        directed=True,
        physics=True,
        hierarchical=False
    )

    return agraph(
        nodes=nodes,
        edges=edges,
        config=config
    )


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="RTLVision AI",
    page_icon="🔷",
    layout="wide"
)

load_css()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🔷 RTLVision AI")
st.sidebar.caption("RTL Design Intelligence")

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🔍 RTL Analyzer",
        "🤖 AI Assistant",
        "🧪 Testbench Generator",
        "⚡ Optimization",
        "ℹ️ About"
    ]
)

st.sidebar.divider()

st.sidebar.success("System Online")


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.html("""
    <div class="hero-section">

        <div class="logo-box">
            🔷
        </div>

        <div class="hero-content">

            <div class="main-title">
                RTLVision AI
            </div>

            <div class="subtitle">
                AI-Powered RTL Design & Verification Assistant
            </div>

            <div class="hero-description">
                Analyze, understand and verify RTL designs
                with intelligent automation.
            </div>

        </div>

    </div>
    """)

    st.write(
        "Analyze RTL code, understand design behavior, "
        "generate testbenches and optimize your designs."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.html("""
        <div class="glass-card">

            <div class="feature-title">
                🔍 RTL Analyzer
            </div>

            <div class="feature-text">
                Analyze Verilog modules,
                inputs, outputs and signals.
            </div>

        </div>
        """)

    with col2:

        st.html("""
        <div class="glass-card">

            <div class="feature-title">
                🤖 AI Assistant
            </div>

            <div class="feature-text">
                Understand RTL behavior
                with AI-powered explanations.
            </div>

        </div>
        """)

    with col3:

        st.html("""
        <div class="glass-card">

            <div class="feature-title">
                🧪 Testbench Generator
            </div>

            <div class="feature-text">
                Generate verification-oriented
                testbench templates automatically.
            </div>

        </div>
        """)

    st.divider()

    st.success(
        "🚀 RTLVision AI is ready for RTL analysis!"
    )


# =========================================================
# RTL ANALYZER
# =========================================================

elif page == "🔍 RTL Analyzer":

    st.title("🔍 RTL Analyzer")

    st.caption(
        "Analyze your Verilog / SystemVerilog design."
    )

    # -----------------------------------------------------
    # FILE UPLOAD
    # -----------------------------------------------------

    uploaded_file = st.file_uploader(
        "📁 Upload RTL File",
        type=["v", "sv"]
    )

    # -----------------------------------------------------
    # CODE EDITOR
    # -----------------------------------------------------

    st.subheader("💻 RTL Code Editor")

    if uploaded_file:

        try:

            code = uploaded_file.read().decode("utf-8")

        except UnicodeDecodeError:

            st.error(
                "❌ Unable to read the uploaded RTL file."
            )

            code = ""

    else:

        code = st.text_area(
            "Paste Verilog / SystemVerilog code",
            height=350,
            placeholder="""module and_gate(
    input a,
    input b,
    output y
);

assign y = a & b;

endmodule""",
            key="rtl_code_editor"
        )

    # -----------------------------------------------------
    # ANALYZE BUTTON
    # -----------------------------------------------------

    if st.button(
        "🔍 Analyze RTL",
        type="primary",
        use_container_width=True,
        key="rtl_analyze_button"
    ):

        if not code.strip():

            st.warning(
                "⚠️ Please enter or upload RTL code first."
            )

        else:

            # =================================================
            # ANALYSIS
            # =================================================

            with st.status(
                "Analyzing RTL design...",
                expanded=True
            ) as status:

                st.write(
                    "📖 Reading RTL source..."
                )

                time.sleep(0.3)

                st.write(
                    "🔍 Parsing module structure..."
                )

                time.sleep(0.3)

                st.write(
                    "📡 Detecting signals..."
                )

                time.sleep(0.3)

                # ---------------------------------------------
                # IMPORTANT
                # Create result BEFORE using it
                # ---------------------------------------------

                result = analyze_verilog(code)

                errors, warnings = detect_errors(code)

                st.write(
                    "⚡ Detecting logic gates..."
                )

                time.sleep(0.3)

                st.write(
                    "🔗 Building gate relationships..."
                )

                time.sleep(0.3)

                st.write(
                    "📊 Generating analysis report..."
                )

                time.sleep(0.3)

                status.update(
                    label="RTL Analysis Complete!",
                    state="complete"
                )

            st.success(
                "✅ RTL analysis completed successfully."
            )

            # =================================================
            # DESIGN SUMMARY
            # =================================================

            st.divider()

            st.subheader("📊 Design Summary")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Modules",
                    len(result.get("modules", []))
                )

            with col2:

                st.metric(
                    "Inputs",
                    len(result.get("inputs", []))
                )

            with col3:

                st.metric(
                    "Outputs",
                    len(result.get("outputs", []))
                )

            # =================================================
            # MODULES
            # =================================================

            st.divider()

            st.subheader("📦 Modules")

            modules = result.get("modules", [])

            if modules:

                for module in modules:

                    st.write(
                        "•",
                        module
                    )

            else:

                st.info(
                    "No modules detected."
                )

            # =================================================
            # INPUTS AND OUTPUTS
            # =================================================

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("📥 Inputs")

                inputs = result.get("inputs", [])

                if inputs:

                    for signal in inputs:

                        st.write(
                            "•",
                            signal
                        )

                else:

                    st.info(
                        "No inputs detected."
                    )

            with col2:

                st.subheader("📤 Outputs")

                outputs = result.get("outputs", [])

                if outputs:

                    for signal in outputs:

                        st.write(
                            "•",
                            signal
                        )

                else:

                    st.info(
                        "No outputs detected."
                    )

            # =================================================
            # RTL VALIDATION
            # =================================================

            st.divider()

            st.subheader("🛡️ RTL Validation")

            if errors:

                st.error(
                    "❌ Errors Found"
                )

                for error in errors:

                    st.write(
                        "•",
                        error
                    )

            else:

                st.success(
                    "✅ No major structural errors found."
                )

            if warnings:

                st.warning(
                    "⚠️ Warnings"
                )

                for warning in warnings:

                    st.write(
                        "•",
                        warning
                    )

            # =================================================
            # OTHER SIGNALS
            # =================================================

            st.divider()

            st.subheader("🔌 Other Signals")

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Wires",
                    len(result.get("wires", []))
                )

            with col2:

                st.metric(
                    "Registers",
                    len(result.get("registers", []))
                )

            # =================================================
            # LOGIC GATES
            # =================================================

            st.divider()

            st.subheader("⚡ Logic Gate Analysis")

            gates = result.get("gates", [])

            if gates:

                for gate in gates:

                    st.write(
                        "•",
                        gate
                    )

            else:

                st.info(
                    "No logic gates detected."
                )

            # =================================================
            # GATE CONNECTIONS
            # =================================================

            st.divider()

            st.subheader("🔗 Gate Connections")

            gate_details = result.get(
                "gate_details",
                []
            )

            if gate_details:

                for detail in gate_details:

                    gate_name = detail.get(
                        "gate",
                        "Unknown"
                    )

                    gate_inputs = detail.get(
                        "inputs",
                        []
                    )

                    gate_output = detail.get(
                        "output",
                        "Unknown"
                    )

                    input_text = ", ".join(
                        gate_inputs
                    )

                    st.markdown(
                        f"""
                        **⚡ {gate_name} Gate**

                        - 📥 Inputs: `{input_text}`
                        - 📤 Output: `{gate_output}`
                        """
                    )

            else:

                st.info(
                    "No gate connections detected."
                )

            # =================================================
            # ASSIGNMENTS
            # =================================================

            st.divider()

            st.subheader("📝 Assign Statements")

            assignments = result.get(
                "assignments",
                []
            )

            if assignments:

                for assignment in assignments:

                    st.code(
                        "assign "
                        + assignment.strip()
                        + ";",
                        language="verilog"
                    )

            else:

                st.info(
                    "No assign statements detected."
                )

            # =================================================
            # RTL BLOCK DIAGRAM PREVIEW
            # =================================================

            st.divider()

            st.subheader(
                "🔷 RTL Block Diagram Preview"
            )

            if result["gate_details"]:

                st.caption(
                    "Drag the nodes and explore the RTL signal connections."
    )

                create_rtl_diagram(
                    result["gate_details"]
    )

            else:

                st.info(
                    "No logic gates detected for visualization."
    )


# =========================================================
# AI ASSISTANT
# =========================================================

elif page == "🤖 AI Assistant":

    st.title("🤖 AI Assistant")

    st.caption(
        "Ask Gemini AI about your Verilog / SystemVerilog design."
    )

    # ----------------------------------------------
    # RTL CODE INPUT
    # ----------------------------------------------

    rtl_code = st.text_area(
        "💻 Enter RTL Code",
        height=300,
        placeholder="""module and_gate(
    input a,
    input b,
    output y
);

assign y = a & b;

endmodule"""
    )

    # ----------------------------------------------
    # USER QUESTION
    # ----------------------------------------------

    question = st.text_input(
        "💬 Ask your question",
        placeholder="Example: Explain how this RTL works."
    )

    # ----------------------------------------------
    # ASK GEMINI
    # ----------------------------------------------

    if st.button(
        "🤖 Ask Gemini",
        type="primary",
        use_container_width=True,
        key="gemini_button"
    ):

        if not rtl_code.strip():

            st.warning(
                "⚠️ Please enter RTL code first."
            )

        elif not question.strip():

            st.warning(
                "⚠️ Please enter your question."
            )

        else:

            with st.spinner(
                "🤖 Gemini is analyzing your RTL..."
            ):

                try:

                    prompt = f"""
You are an expert RTL and Verilog/SystemVerilog assistant.

Analyze the following RTL code.

RTL CODE:
{rtl_code}

USER QUESTION:
{question}

Give a clear and technically correct answer.
Explain the RTL in a simple way suitable for a college student.
If there is an error, clearly identify the error and explain how to fix it.
"""

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )

                    st.divider()

                    st.subheader(
                        "🤖 Gemini AI Response"
                    )

                    st.markdown(
                        response.text
                    )

                except Exception as e:

                    st.error(
                        f"❌ Gemini API Error: {e}"
                    )


# =========================================================
# TESTBENCH GENERATOR
# =========================================================

elif page == "🧪 Testbench Generator":

    st.title("🧪 Testbench Generator")

    st.caption(
        "Generate a Verilog testbench automatically using Gemini AI."
    )

    # -----------------------------------------------------
    # RTL CODE INPUT
    # -----------------------------------------------------

    st.subheader("💻 RTL Design")

    rtl_code = st.text_area(
        "Paste your Verilog / SystemVerilog code",
        height=350,
        placeholder="""module and_gate(
    input a,
    input b,
    output y
);

assign y = a & b;

endmodule""",
        key="testbench_rtl_code"
    )

    # -----------------------------------------------------
    # GENERATE BUTTON
    # -----------------------------------------------------

    if st.button(
        "🧪 Generate Testbench",
        type="primary",
        use_container_width=True,
        key="generate_testbench"
    ):

        if not rtl_code.strip():

            st.warning(
                "⚠️ Please enter your RTL code first."
            )

        else:

            with st.spinner(
                "🤖 Gemini is generating the testbench..."
            ):

                try:

                    prompt = f"""
You are an expert Verilog and SystemVerilog verification engineer.

Generate a simple and correct Verilog testbench for the following RTL design.

RTL DESIGN:
{rtl_code}

Requirements:

1. Identify the module name.
2. Identify all input and output ports.
3. Create reg variables for inputs.
4. Create wire variables for outputs.
5. Instantiate the DUT (Design Under Test).
6. Apply suitable test cases to all important input combinations.
7. Use delays such as #10 between test cases.
8. End the simulation using $finish.
9. Keep the testbench simple and suitable for a college student.
10. Return ONLY the Verilog testbench code.
11. Do not include markdown ```verilog``` fences.
"""

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )

                    testbench_code = response.text.strip()

                    # Remove markdown fences if Gemini adds them
                    testbench_code = testbench_code.replace(
                        "```verilog", ""
                    ).replace(
                        "```systemverilog", ""
                    ).replace(
                        "```", ""
                    ).strip()

                    st.success(
                        "✅ Testbench generated successfully!"
                    )

                    # -------------------------------------------------
                    # DISPLAY GENERATED TESTBENCH
                    # -------------------------------------------------

                    st.divider()

                    st.subheader(
                        "📄 Generated Testbench"
                    )

                    st.code(
                        testbench_code,
                        language="verilog"
                    )

                    # -------------------------------------------------
                    # DOWNLOAD BUTTON
                    # -------------------------------------------------

                    st.download_button(
                        label="⬇️ Download Testbench",
                        data=testbench_code,
                        file_name="generated_testbench.v",
                        mime="text/plain",
                        use_container_width=True
                    )

                except Exception as e:

                    st.error(
                        f"❌ Gemini API Error: {e}"
                    )


# =========================================================
# RTL OPTIMIZATION
# =========================================================

elif page == "⚡ Optimization":

    st.title("⚡ RTL Optimization")

    st.caption(
        "Analyze your RTL and get suggestions for "
        "timing, area, power and coding quality."
    )

    # -----------------------------------------------------
    # RTL CODE INPUT
    # -----------------------------------------------------

    st.subheader("💻 RTL Design")

    rtl_code = st.text_area(
        "Paste your Verilog / SystemVerilog code",
        height=350,
        placeholder="""module and_gate(
    input a,
    input b,
    output y
);

assign y = a & b;

endmodule""",
        key="optimization_rtl_code"
    )

    # -----------------------------------------------------
    # OPTIMIZATION BUTTON
    # -----------------------------------------------------

    if st.button(
        "⚡ Analyze & Optimize",
        type="primary",
        use_container_width=True,
        key="optimization_button"
    ):

        if not rtl_code.strip():

            st.warning(
                "⚠️ Please enter RTL code first."
            )

        else:

            with st.spinner(
                "🤖 Gemini is analyzing your RTL..."
            ):

                try:

                    prompt = f"""
You are an expert RTL design optimization engineer.

Analyze the following Verilog/SystemVerilog RTL:

{rtl_code}

Provide an RTL optimization report.

Analyze these four areas:

1. TIMING
   - Identify possible timing problems.
   - Suggest ways to reduce combinational depth.

2. AREA
   - Identify unnecessary logic or duplicated logic.
   - Suggest area-efficient alternatives.

3. POWER
   - Identify unnecessary switching activity.
   - Suggest possible power improvements.

4. CODE QUALITY
   - Identify poor RTL coding practices.
   - Suggest cleaner and more maintainable RTL.

For every issue:
- Clearly explain the problem.
- Give a practical optimization suggestion.
- Do not modify the original RTL automatically.

Keep the explanation simple and suitable for a college student.
"""

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )

                    optimization_result = response.text.strip()

                    st.success(
                        "✅ RTL optimization analysis completed!"
                    )

                    # -------------------------------------------------
                    # DISPLAY RESULT
                    # -------------------------------------------------

                    st.divider()

                    st.subheader(
                        "📊 Optimization Report"
                    )

                    st.markdown(
                        optimization_result
                    )

                except Exception as e:

                    st.error(
                        f"❌ Gemini API Error: {e}"
                    )


# =========================================================
# ABOUT PAGE
# =========================================================

elif page == "ℹ️ About":

    st.title("ℹ️ About RTLVision AI")

    st.markdown(
        """
        ## 🚀 RTLVision AI

        **RTLVision AI** is an AI-powered RTL analysis and
        verification platform for Verilog and SystemVerilog designs.

        The platform helps users analyze RTL code, identify logic
        structures, visualize signal connections, detect common
        errors, generate testbenches, and obtain AI-based optimization
        suggestions from a single interface.
        """
    )

    st.divider()

    # =====================================================
    # PROJECT OVERVIEW
    # =====================================================

    st.subheader("🎯 Project Overview")

    st.write(
        """
        RTL design can become difficult to understand and debug as
        the complexity of a digital system increases.

        RTLVision AI simplifies this process by automatically
        extracting important information from RTL code and presenting
        it in a clear and understandable way.

        The platform combines traditional RTL parsing techniques
        with Generative AI to assist users during design analysis,
        verification, and optimization.
        """
    )

    # =====================================================
    # KEY FEATURES
    # =====================================================

    st.subheader("✨ Key Features")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            ### 🔍 RTL Analysis

            - Verilog / SystemVerilog analysis
            - Module detection
            - Input and output detection
            - Wire and register detection
            - Assignment extraction

            ### ⚡ Logic Analysis

            - AND gate detection
            - OR gate detection
            - XOR gate detection
            - NAND gate detection
            - NOR gate detection
            - XNOR gate detection
            - NOT gate detection

            ### 🛡️ Error Detection

            - Missing module detection
            - Missing `endmodule` detection
            - Missing comma detection
            - Missing semicolon detection
            """
        )

    with col2:

        st.markdown(
            """
            ### 🔗 Gate Connections

            Displays the relationship between:

            - Input signals
            - Logic gates
            - Output signals

            ### 🤖 Gemini AI Assistant

            Provides AI-powered assistance for understanding
            and analyzing RTL designs.

            ### 🧪 Testbench Generator

            Automatically generates a Verilog testbench based
            on the provided RTL design.

            ### ⚡ RTL Optimization

            Provides suggestions related to:

            - Timing
            - Area
            - Power
            - RTL code quality
            """
        )

    st.divider()

    # =====================================================
    # WORKFLOW
    # =====================================================

    st.subheader("🔄 How RTLVision AI Works")

    st.markdown(
        """
        **1️⃣ Upload RTL**

        Upload a Verilog or SystemVerilog design.

        **↓**

        **2️⃣ Parse RTL**

        The parser extracts modules, ports, signals,
        assignments, and logic structures.

        **↓**

        **3️⃣ Detect Errors**

        Common RTL syntax and structural problems are identified.

        **↓**

        **4️⃣ Analyze Gate Connections**

        Signal relationships and logic gates are identified.

        **↓**

        **5️⃣ AI Assistance**

        Gemini AI provides explanations and design-related
        assistance.

        **↓**

        **6️⃣ Generate Testbench**

        A testbench is automatically generated for the RTL design.

        **↓**

        **7️⃣ Optimize RTL**

        The design is analyzed for possible timing, area,
        power, and coding-quality improvements.
        """
    )

    st.divider()

    # =====================================================
    # PROJECT OBJECTIVE
    # =====================================================

    st.subheader("🎯 Project Objective")

    st.info(
        """
        RTLVision AI aims to make RTL design analysis easier,
        faster, and more understandable.

        Instead of manually inspecting large RTL files,
        users can use the platform to quickly understand
        the design structure, identify potential problems,
        generate verification code, and receive AI-assisted
        optimization suggestions.
        """
    )

    # =====================================================
    # FUTURE SCOPE
    # =====================================================

    st.subheader("🔮 Future Scope")

    st.markdown(
        """
        Future versions of RTLVision AI can include:

        - 🔹 Advanced SystemVerilog support
        - 🔹 Sequential circuit analysis
        - 🔹 Flip-flop and register identification
        - 🔹 Counter and FSM analysis
        - 🔹 Waveform visualization
        - 🔹 Advanced timing analysis
        - 🔹 Hardware resource estimation
        - 🔹 Formal verification assistance
        - 🔹 Automated RTL optimization
        """
    )

    st.divider()

    # =====================================================
    # FOOTER
    # =====================================================

    st.success(
        "🚀 RTLVision AI — Making RTL Analysis Smarter and Simpler"
    )

    st.caption(
        "AI-Assisted RTL Analysis • Verification • Testbench Generation • Optimization"
    )