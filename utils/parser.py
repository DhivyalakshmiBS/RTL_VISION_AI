import re


# =========================================================
# RTL ANALYSIS
# =========================================================

def analyze_verilog(code):

    result = {
        "modules": [],
        "inputs": [],
        "outputs": [],
        "wires": [],
        "registers": [],
        "assignments": [],
        "gates": [],
        "gate_details": []
    }

    # -----------------------------------------------------
    # Remove comments
    # -----------------------------------------------------

    code = re.sub(
        r"//.*",
        "",
        code
    )

    code = re.sub(
        r"/\*.*?\*/",
        "",
        code,
        flags=re.DOTALL
    )

    # =====================================================
    # MODULE
    # =====================================================

    result["modules"] = re.findall(
        r"\bmodule\s+([A-Za-z_][A-Za-z0-9_]*)",
        code
    )

    # =====================================================
    # MODULE PORT LIST
    # =====================================================

    port_match = re.search(
        r"\bmodule\s+[A-Za-z_][A-Za-z0-9_]*\s*\((.*?)\)\s*;",
        code,
        re.DOTALL
    )

    if port_match:

        port_list = port_match.group(1)

        # Split ports by comma
        ports = port_list.split(",")

        for port in ports:

            port = port.strip()

            # ---------------------------------------------
            # INPUT
            # ---------------------------------------------

            match = re.match(
                r"input\s+"
                r"(?:(?:wire|reg|logic)\s+)?"
                r"(?:\[[^\]]+\]\s+)?"
                r"([A-Za-z_][A-Za-z0-9_]*)",
                port
            )

            if match:

                signal = match.group(1)

                if signal not in result["inputs"]:
                    result["inputs"].append(signal)

                continue

            # ---------------------------------------------
            # OUTPUT
            # ---------------------------------------------

            match = re.match(
                r"output\s+"
                r"(?:(?:wire|reg|logic)\s+)?"
                r"(?:\[[^\]]+\]\s+)?"
                r"([A-Za-z_][A-Za-z0-9_]*)",
                port
            )

            if match:

                signal = match.group(1)

                if signal not in result["outputs"]:
                    result["outputs"].append(signal)

                continue

            # ---------------------------------------------
            # INOUT
            # ---------------------------------------------

            match = re.match(
                r"inout\s+"
                r"(?:(?:wire|reg|logic)\s+)?"
                r"(?:\[[^\]]+\]\s+)?"
                r"([A-Za-z_][A-Za-z0-9_]*)",
                port
            )

            if match:

                signal = match.group(1)

                if signal not in result["inputs"]:
                    result["inputs"].append(signal)


    # =====================================================
    # WIRES
    # =====================================================

    wire_matches = re.findall(
        r"\bwire\s+"
        r"(?:\[[^\]]+\]\s+)?"
        r"([A-Za-z_][A-Za-z0-9_]*)",
        code
    )

    for signal in wire_matches:

        if signal not in result["wires"]:
            result["wires"].append(signal)


    # =====================================================
    # REGISTERS
    # =====================================================

    reg_matches = re.findall(
        r"\breg\s+"
        r"(?:\[[^\]]+\]\s+)?"
        r"([A-Za-z_][A-Za-z0-9_]*)",
        code
    )

    for signal in reg_matches:

        if signal not in result["registers"]:
            result["registers"].append(signal)


    # =====================================================
    # LOGIC
    # =====================================================

    logic_matches = re.findall(
        r"\blogic\s+"
        r"(?:\[[^\]]+\]\s+)?"
        r"([A-Za-z_][A-Za-z0-9_]*)",
        code
    )

    for signal in logic_matches:

        if signal not in result["registers"]:
            result["registers"].append(signal)


    # =====================================================
    # ASSIGNMENTS
    # =====================================================

    result["assignments"] = re.findall(
        r"\bassign\s+(.+?);",
        code,
        re.DOTALL
    )


    # =====================================================
    # LOGIC GATE DETECTION
    # =====================================================

    gate_patterns = [
        ("NAND Gate", r"~\s*\([^)]*&[^)]*\)"),
        ("NOR Gate", r"~\s*\([^)]*\|[^)]*\)"),
        ("XNOR Gate", r"~\s*\([^)]*\^[^)]*\)"),
        ("AND Gate", r"(?<!~)\&"),
        ("OR Gate", r"(?<!~)\|"),
        ("XOR Gate", r"(?<!~)\^"),
        ("NOT Gate", r"~")
    ]

    detected_gates = []

    for gate_name, pattern in gate_patterns:

        if re.search(
            pattern,
            code
        ):

            if gate_name not in detected_gates:

                detected_gates.append(
                    gate_name
                )

    result["gates"] = detected_gates


    # =====================================================
    # GATE + SIGNAL RELATIONSHIP
    # =====================================================

    gate_details = []

    for assignment in result["assignments"]:

        assignment = assignment.strip()

        # ---------------------------------------------
        # Extract output and logic expression
        #
        # Example:
        # sum = a ^ b
        # carry = a & b
        # ---------------------------------------------

        match = re.match(
            r"^\s*"
            r"([A-Za-z_][A-Za-z0-9_]*)"
            r"\s*=\s*"
            r"(.+?)"
            r"\s*$",
            assignment
        )

        if not match:
            continue

        output_signal = match.group(1)

        logic_expression = match.group(2).strip()


        # ---------------------------------------------
        # Detect gate
        # ---------------------------------------------

        if "~" in logic_expression and "&" in logic_expression:

            gate = "NAND"

        elif "~" in logic_expression and "|" in logic_expression:

            gate = "NOR"

        elif "~" in logic_expression and "^" in logic_expression:

            gate = "XNOR"

        elif "^" in logic_expression:

            gate = "XOR"

        elif "&" in logic_expression:

            gate = "AND"

        elif "|" in logic_expression:

            gate = "OR"

        elif "~" in logic_expression:

            gate = "NOT"

        else:

            continue


        # ---------------------------------------------
        # Detect input signals
        # ---------------------------------------------

        identifiers = re.findall(
            r"\b[A-Za-z_][A-Za-z0-9_]*\b",
            logic_expression
        )

        input_signals = []

        for signal in identifiers:

            if signal in result["inputs"]:

                if signal not in input_signals:

                    input_signals.append(
                        signal
                    )

            elif signal in result["wires"]:

                if signal not in input_signals:

                    input_signals.append(
                        signal
                    )


        # ---------------------------------------------
        # Store gate relationship
        # ---------------------------------------------

        gate_details.append(
            {
                "output": output_signal,
                "gate": gate,
                "inputs": input_signals
            }
        )


    result["gate_details"] = gate_details


    # =====================================================
    # RETURN ANALYSIS RESULT
    # =====================================================

    return result



# =========================================================
# ERROR DETECTION
# =========================================================

def detect_errors(code):

    errors = []
    warnings = []


    # =====================================================
    # REMOVE COMMENTS
    # =====================================================

    clean_code = re.sub(
        r"//.*",
        "",
        code
    )

    clean_code = re.sub(
        r"/\*.*?\*/",
        "",
        clean_code,
        flags=re.DOTALL
    )

    lines = clean_code.splitlines()


    # =====================================================
    # MODULE CHECK
    # =====================================================

    module_matches = re.findall(
        r"\bmodule\s+[A-Za-z_][A-Za-z0-9_]*",
        clean_code
    )

    if not module_matches:

        errors.append(
            "No module declaration found."
        )


    # =====================================================
    # ENDMODULE CHECK
    # =====================================================

    module_count = len(
        re.findall(
            r"\bmodule\s+",
            clean_code
        )
    )

    endmodule_count = len(
        re.findall(
            r"\bendmodule\b",
            clean_code
        )
    )

    if endmodule_count == 0:

        errors.append(
            "Missing 'endmodule'."
        )

    elif module_count != endmodule_count:

        errors.append(
            "Module and endmodule count mismatch."
        )


    # =====================================================
    # INPUT / OUTPUT WARNINGS
    # =====================================================

    if not re.search(
        r"\binput\s+",
        clean_code
    ):

        warnings.append(
            "No input signal detected."
        )

    if not re.search(
        r"\boutput\s+",
        clean_code
    ):

        warnings.append(
            "No output signal detected."
        )


    # =====================================================
    # PORT LIST + STATEMENT CHECK
    # =====================================================

    inside_port_list = False

    for index, original_line in enumerate(lines):

        line_number = index + 1

        line = original_line.strip()

        if not line:
            continue


        # -------------------------------------------------
        # MODULE
        # -------------------------------------------------

        if re.match(
            r"^module\s+",
            line
        ):

            if "(" in line:

                inside_port_list = True

            continue


        # -------------------------------------------------
        # PORT LIST
        # -------------------------------------------------

        if inside_port_list:

            # ---------------------------------------------
            # INPUT
            # ---------------------------------------------

            if re.match(
                r"^input\s+",
                line
            ):

                if not line.endswith(","):

                    if index + 1 < len(lines):

                        next_line = lines[
                            index + 1
                        ].strip()

                        if re.match(
                            r"^(input|output|inout)\s+",
                            next_line
                        ):

                            errors.append(
                                f"Line {line_number}: "
                                f"Missing comma after "
                                f"port declaration."
                            )

                continue


            # ---------------------------------------------
            # OUTPUT
            # ---------------------------------------------

            if re.match(
                r"^output\s+",
                line
            ):

                if not line.endswith(","):

                    if index + 1 < len(lines):

                        next_line = lines[
                            index + 1
                        ].strip()

                        if re.match(
                            r"^(input|output|inout)\s+",
                            next_line
                        ):

                            errors.append(
                                f"Line {line_number}: "
                                f"Missing comma after "
                                f"port declaration."
                            )

                continue


            # ---------------------------------------------
            # INOUT
            # ---------------------------------------------

            if re.match(
                r"^inout\s+",
                line
            ):

                if not line.endswith(","):

                    if index + 1 < len(lines):

                        next_line = lines[
                            index + 1
                        ].strip()

                        if re.match(
                            r"^(input|output|inout)\s+",
                            next_line
                        ):

                            errors.append(
                                f"Line {line_number}: "
                                f"Missing comma after "
                                f"port declaration."
                            )

                continue


            # ---------------------------------------------
            # PORT LIST END
            # ---------------------------------------------

            if line == ");":

                inside_port_list = False

                continue


            # ---------------------------------------------
            # ")" WITHOUT ";"
            # ---------------------------------------------

            if line == ")":

                errors.append(
                    f"Line {line_number}: "
                    f"Missing semicolon after "
                    f"module port list."
                )

                inside_port_list = False

                continue


    # =====================================================
    # GENERAL RTL STATEMENT CHECK
    # =====================================================

    for index, original_line in enumerate(lines):

        line_number = index + 1

        line = original_line.strip()

        if not line:
            continue


        # -------------------------------------------------
        # Ignore module
        # -------------------------------------------------

        if line.startswith("module "):

            continue


        # -------------------------------------------------
        # Ignore endmodule
        # -------------------------------------------------

        if line == "endmodule":

            continue


        # -------------------------------------------------
        # Ignore ports
        # -------------------------------------------------

        if line.startswith("input "):

            continue

        if line.startswith("output "):

            continue

        if line.startswith("inout "):

            continue


        # -------------------------------------------------
        # Ignore closing port list
        # -------------------------------------------------

        if line == ")" or line == ");":

            continue


        # -------------------------------------------------
        # WIRE
        # -------------------------------------------------

        if line.startswith("wire "):

            if not line.endswith(";"):

                errors.append(
                    f"Line {line_number}: "
                    f"Missing semicolon."
                )


        # -------------------------------------------------
        # REG
        # -------------------------------------------------

        elif line.startswith("reg "):

            if not line.endswith(";"):

                errors.append(
                    f"Line {line_number}: "
                    f"Missing semicolon."
                )


        # -------------------------------------------------
        # LOGIC
        # -------------------------------------------------

        elif line.startswith("logic "):

            if not line.endswith(";"):

                errors.append(
                    f"Line {line_number}: "
                    f"Missing semicolon."
                )


        # -------------------------------------------------
        # ASSIGN
        # -------------------------------------------------

        elif line.startswith("assign "):

            if not line.endswith(";"):

                errors.append(
                    f"Line {line_number}: "
                    f"Missing semicolon."
                )


    # =====================================================
    # RETURN ERRORS AND WARNINGS
    # =====================================================

    return errors, warnings

