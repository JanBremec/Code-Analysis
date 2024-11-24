import streamlit as st
from radon.complexity import cc_visit
from radon.metrics import mi_visit, mi_rank
from radon.raw import analyze
import ast
import model as md
from streamlit_scroll_navigation import scroll_navbar

anchor_ids = ["Introduction", "Functions", "Complexity", "Maintainability", "Recommendations"]



if "showExplanation" not in st.session_state:
    st.session_state.showExplanation = []

if "showMore" not in st.session_state:
    st.session_state.showMore = None

if "showAnswer" not in st.session_state:
    st.session_state.showAnswer = []


st.sidebar.title("Navigation")
with st.sidebar:
    scroll_navbar(
        anchor_ids,
        orientation="vertical",
        anchor_labels=None,
        override_styles={
            "navbarButtonBase": {
                "backgroundColor": "#ffffff",  # Set a custom button background color
                "color": "#212529",  # Set custom text color
            },
            "navbarButtonHover": {
                "backgroundColor": "#e9ecef",  # Set a custom hover color for the buttons
                "color": "#212529",  # Text color for hovered state
                "font-weight": "bold",
            },
            "navigationBarBase": {"background": "#ffffff",  # White background for the navbar container
            "border-radius": "10px",  # Rounded corners for the navbar container
            "padding": "15px",  # Padding around the navbar
            "margin": "10px 0",  # Margin around the navbar
            "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",  # Soft shadow around the navbar}
        }})

# Title and Description
st.title("Code Analysis", anchor="Introduction")
st.write("Analyze the complexity of your Python code for better readability and maintainability.")


# Helper function to count and extract functions and classes
def extract_functions_and_classes(code):
    tree = ast.parse(code)
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    return functions, classes


# Helper function to convert AST functions to code
def get_function_code(code, function_node):
    lines = code.splitlines()
    start_line = function_node.lineno - 1  # Line numbers in AST are 1-based
    end_line = function_node.end_lineno  # Includes the last line
    return "\n".join(lines[start_line:end_line])


def get_function_metadata(function_node):
    metadata = {
        "Function Name": function_node.name,
        "Start Line": function_node.lineno,
        "End Line": function_node.end_lineno,
        "Number of Parameters": len(function_node.args.args),
        "Parameters": [arg.arg for arg in function_node.args.args],
    }
    return metadata



# File Upload
uploaded_file = st.file_uploader("Upload a Python file", type="py")

if uploaded_file:
    # Read and display the uploaded file
    code = uploaded_file.read().decode("utf-8")
    with st.expander("**Show Code**"):
        st.code(code, language="python")

    # Analyze raw metrics
    raw_metrics = analyze(code)
    # Extract functions and classes
    functions, classes = extract_functions_and_classes(code)
    with st.sidebar:
        st.header("Code Info")
        st.markdown(f"""
            <ul class="metrics-list">
                <li><strong>Lines of Code:</strong> {raw_metrics.loc}</li>
                <li><strong>Logical Lines of Code:</strong> {raw_metrics.lloc}</li>
                <li><strong>Comments:</strong> {raw_metrics.comments} comment{'s' if raw_metrics.comments != 1 else ''}</li>
                <li><strong>Multi-line Strings (Docstrings):</strong> {raw_metrics.multi} string{'s' if raw_metrics.multi != 1 else ''}</li>
                <li><strong>Number of Functions:</strong> {len(functions)}</li>
                <li><strong>Number of Classes:</strong> {len(classes)}</li>
            </ul>
        """, unsafe_allow_html=True)

    # Display functions
    if functions:
        st.divider()
        st.header("Functions", anchor="Functions")
        index = 0
        for function in functions:
            st.subheader(function.name)
            func_code = get_function_code(code, function)
            #modified_code = st.text_area("Modify Function Code", func_code)
            st.code(func_code, language="python")

            columns = st.columns([1, 1, 5])

            with columns[0]:
                if st.button("Explain", key=index):
                    metadata = get_function_metadata(function)
                    st.session_state.showExplanation = [func_code, metadata]

            with columns[2]:
                question = st.text_input(label="Input", label_visibility="collapsed", placeholder="Ask...", key=f"Ask{index}")
                if question:
                    st.session_state.showAnswer = [func_code, question]

            with columns[1]:
                if st.button("More", key=f"Submit{index}"):
                    st.session_state.showMore = function


            if len(st.session_state.showExplanation) == 2 and st.session_state.showExplanation[0] == func_code:
                with st.expander("Explanation"):
                    explanation = md.getFunctionExplanation(st.session_state.showExplanation[0])["content"]
                    m = st.session_state.showExplanation[1]
                    st.write(explanation)
                    for key, value in m.items():
                        st.write(f"**{key}:** {value}")

            if st.session_state.showMore and st.session_state.showMore == function:
                with st.expander("More about this Function"):
                    st.write(st.session_state.showMore)

            if len(st.session_state.showAnswer) == 2 and st.session_state.showAnswer[0] == func_code:
                with st.expander("Show Answer"):
                    c, q = st.session_state.showAnswer
                    st.subheader(q.capitalize())
                    st.write(f"- {md.getQuestionAnswered(c, q)['content']}")
            index += 1
            st.divider()


    else:
        st.info("No functions found in the uploaded code.")

    # Cyclomatic Complexity Analysis

    st.subheader("Cyclomatic Complexity", anchor="Complexity")
    complexities = cc_visit(code)
    complexity_data = [{"Name": c.name, "Complexity": c.complexity} for c in complexities]

    if complexity_data:
        st.write("Function/Class Complexity:")
        st.table(complexity_data)
        high_complexity = [c for c in complexities if c.complexity > 10]
        if high_complexity:
            st.warning("Functions with high complexity (over 10):")
            for c in high_complexity:
                st.write(f"- {c.name}: {c.complexity}")
        else:
            st.success("No functions with high complexity found.")
    else:
        st.info("No functions or classes detected.")

    # Maintainability Index

    st.subheader("Maintainability Index", anchor="Maintainability")
    mi_score = mi_visit(code, True)
    mi_grade = mi_rank(mi_score)
    st.write(f"Maintainability Index: {mi_score:.2f} ({mi_grade})")

    # Recommendations
    st.subheader("Recommendations", anchor="Recommendations")
    st.markdown('<a id="recommendations"></a>', unsafe_allow_html=True)
    if mi_score < 65:
        st.warning("Consider refactoring parts of the code to improve maintainability.")
    else:
        st.success("The code is well-maintained and easy to understand.")

    st.write(
        "Functions with high complexity or low maintainability index can be refactored for better performance and readability.")

    st.write(md.getCodeImprovements(code)["content"])
# Footer
st.write("---")
st.markdown(
    """
    <hr style="border: 1px solid #ddd; margin: 20px 0;">
    <div style="
        text-align: center;
        font-family: Arial, sans-serif;
        font-size: 14px;
        color: #555;
        line-height: 1.6;
    ">
        <p><strong>© 2024 Jan Bremec. All rights reserved.</strong></p>
        <p>
            This website is developed by <strong>Jan Bremec</strong>. For inquiries, feedback, or potential collaborations, please feel free to contact me.
        </p>
        <p style="margin-top: 10px; font-size: 12px; color: #888;">
            I appreciate your visit and hope you enjoy the experience.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
