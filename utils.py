# utils.py
import json
from openpyxl import load_workbook
from openpyxl.styles.borders import Border
from collections import deque
import os

def load_json():
    """
    Load JSON data from the file and return it as a dictionary.
    """
    try:
        with open("system_config.json", 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def get_api_key_from_json(key_name):
    """
    Get the API key from a JSON file.
    """
    config_data = load_json()
    if config_data and key_name in config_data:
        return config_data[key_name]
    else:
        print(f"{key_name} not found in the JSON file.")
        return None

def extract_mte_data(file_path):
    """
    Extracts Monthly Thinking Exercise (MTE) data from an uploaded Excel file.
    """
    try:
        workbook = load_workbook(file_path)
        sheet = workbook.worksheets[0]

        def has_border(cell):
            border: Border = cell.border
            sides = [border.left, border.right, border.top, border.bottom]
            return any(side.style is not None for side in sides)

        def clean_text(value):
            if not isinstance(value, str):
                return value
            value = value.replace('“', '"').replace('”', '"')
            value = value.replace('‘', "'").replace('’', "'")
            return value

        border_map = {}
        for row in sheet.iter_rows():
            for cell in row:
                if has_border(cell):
                    cleaned_value = clean_text(cell.value)
                    border_map[(cell.row, cell.column)] = cleaned_value

        visited = set()
        groups = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for cell in border_map:
            if cell not in visited:
                group = []
                queue = deque([cell])
                visited.add(cell)

                while queue:
                    current = queue.popleft()
                    group.append(current)

                    for dr, dc in directions:
                        neighbor = (current[0] + dr, current[1] + dc)
                        if neighbor in border_map and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                groups.append(group)

        extracted_tables = []

        for group in groups:
            rows = [r for r, _ in group]
            cols = [c for _, c in group]
            min_row, max_row = min(rows), max(rows)
            min_col, max_col = min(cols), max(cols)

            table = []
            for r in range(min_row, max_row + 1):
                row_data = []
                for c in range(min_col, max_col + 1):
                    value = clean_text(sheet.cell(r, c).value)
                    if value is not None:
                        row_data.append(value)
                if row_data:
                    table.append(row_data)

            if table:
                heading_list = table[0]
                data_rows = table[1:]

                heading = " ".join(str(item) for item in heading_list)

                row_strings = ["    " + " ".join(str(item) for item in row) for row in data_rows]
                rows_as_string = "\n".join(row_strings)

                extracted_tables.append({
                    "heading": heading,
                    "rows": rows_as_string
                })

        mte_dict = {
            "academic_progress": "",
            "cocurricular": "",
            "financial_needs": "",
            "difficulties": "",
            "exam_results": "",
            "books_and_videos": "",
            "health": "",
            "learning_from_people": "",
            "essay": "",
            "action_plan": ""
        }

        heading_to_key_map = {
            "Academic Progress / Vacation Plan": "academic_progress",
            "Co and Extra Curricular Progress-Plan": "cocurricular",
            "Fin Reqm for the next 3 months (Details Please)": "financial_needs",
            "Difficulties (Social, Family, etc.)": "difficulties",
            "Results of the exams (Regular college / university and other exams):": "exam_results",
            "Reading Books / Watching Videos": "books_and_videos",
            "Its very important to exercise regularly and eat and sleep properly": "health",
            "New friends or acquaintances made and what you learnt from them": "learning_from_people",
            "Essay on a topic of your choice including learning from the books read (Pl write in your own words, don't copy from the internet)": "essay",
            "Action Plan for the coming month": "action_plan"
        }

        for table in extracted_tables:
            heading = table['heading'].strip()
            content = table['rows'].strip()

            for expected_heading, dict_key in heading_to_key_map.items():
                if expected_heading in heading:
                    mte_dict[dict_key] = content
                    break

        return mte_dict

    except Exception as e:
        return {"error": f"Error extracting data: {e}"}

def save_feedback_to_json(feedback, student_id):
    """
    Saves the generated feedback to a JSON file to track historical data for students.
    """
    try:
        history_dir = "../data/history"
        file_path = f"{history_dir}/{student_id}_feedback.json"
        
        os.makedirs(history_dir, exist_ok=True)
        
        with open(file_path, "w") as f:
            json.dump(feedback, f, indent=4)
        
        return True
    except Exception as e:
        return {"error": f"Error saving feedback: {e}"}
