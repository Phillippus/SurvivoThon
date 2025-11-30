import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import requests
from ics import Calendar
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# --- KONFIGURÁCIA ---
CONFIG_FILE = 'hospital_config.json'
HISTORY_FILE = 'room_history.json'
PRIVATE_CALENDAR_URL = "https://calendar.google.com/calendar/ical/fntnonk%40gmail.com/private-e8ce4e0639a626387fff827edd26b87f/basic.ics"

# Definícia izieb (Číslo, Počet lôžok)
ROOMS_LIST = [
    (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
    (7, 1), (8, 3), (9, 3), (10, 1), (11, 1),
    (12, 2), (13, 2), (14, 2), (15, 2), (16, 2), (17, 2),
    (18, 3), (19, 3)
]

# Zoznam skúsenejších lekárok (pre smer plnenia izieb od 1 nahor)
SENIOR_DOCTORS = ["Kurisova", "Vidulin", "Miklatkova"]

def get_default_config():
    return {
        "total_beds": 42,
        "ambulancie": {
            "Prijmova": { "dni": ["Pondelok", "Utorok", "Streda", "Stvrtok", "Piatok"], "priority": ["Kohutekova", "Kohutek", "Bystricky", "Zavrelova"] },
            "Velka dispenzarna": { "dni": ["Pondelok", "Utorok", "Streda", "Stvrtok", "Piatok"], "priority": ["Bocak", "Stratena", "Vidulin", "Kurisova", "Blahova", "Hrabosova", "Miklatkova", "Martinka"] },
            "Mala dispenzarna": { "dni": ["Pondelok", "Piatok"], "priority": ["Spanik", "Stratena", "Vidulin", "Kurisova", "Blahova", "Hrabosova", "Miklatkova"] },
            "Radio 2A": { "dni": ["Pondelok", "Utorok", "Streda", "Stvrtok", "Piatok"], "priority": ["Zavrelova", "Kohutek", "Kurisova", "Miklatkova", "Bystricky"], "check_presence": ["Zavrelova", "Martinka"] },
            "Radio 2B": { "dni": ["Pondelok", "Utorok", "Streda", "Stvrtok", "Piatok"], "priority": ["Martinka"], "conditional_owner": "Martinka" },
            "Chemo 8A": { "dni": ["Pondelok", "Utorok", "Streda", "Stvrtok", "Piatok"], "priority": ["Hatalova", "Kohutek", "Stratena", "Bystricky"] },
            "Chemo 8B": { "dni": ["Pondelok", "Utorok", "Streda", "Stvrtok", "Piatok"], "priority": { "0": ["Kohutek", "Stratena", "Bystricky", "Vidulin", "Blahova"], "1": ["Kohutek", "Stratena", "Bystricky", "Vidulin", "Blahova"], "default": ["Riedlova", "Kohutek", "Stratena", "Bystricky", "Vidulin", "Blahova"] } },
            "Chemo 8C": { "dni": ["Utorok", "Streda", "Stvrtok"], "priority": ["Stratena", "Kohutek", "Bystricky", "Vidulin", "Blahova"] },
            "Wolf": { "dni": ["Pondelok", "Utorok", "Streda", "Stvrtok", "Piatok"], "priority": ["Spanik", "Miklatkova", "Kurisova", "Kohutek"] }
        },
        "lekari": {
            "Bystricky": { "moze": ["Prijmova", "Velka dispenzarna", "Mala dispenzarna", "Radio 2A", "Chemo 8A", "Chemo 8B", "Chemo 8C", "Wolf"], "active": True },
            "Kohutek": { "moze": ["Oddelenie", "Prijmova", "Velka dispenzarna", "Mala dispenzarna", "Radio 2A", "Chemo 8A", "Chemo 8B", "Chemo 8C", "Wolf"], "pevne_dni": {"Pondelok": "Chemo 8B", "Utorok": "Chemo 8B"}, "active": True },
            "Kohutekova": { "moze": ["Prijmova"], "pevne_dni": {"Pondelok": "Prijmova", "Utorok": "Prijmova", "Streda": "Prijmova", "Stvrtok": "Prijmova"}, "nepracuje": ["Piatok"], "active": True },
            "Riedlova": { "moze": ["Chemo 8B"], "pevne_dni": {"Streda": "Chemo 8B", "Stvrtok": "Chemo 8B"}, "nepracuje": ["Pondelok", "Utorok"], "active": True },
            "Zavrelova": { "moze": ["Radio 2A", "Prijmova"], "pevne_dni": {"Pondelok": "Radio 2A", "Utorok": "Radio 2A", "Streda": "Radio 2A", "Stvrtok": "Radio 2A", "Piatok": "Radio 2A"}, "active": True },
            "Martinka": { "moze": ["Radio 2B", "Oddelenie", "Velka dispenzarna"], "pevne_dni": {"Pondelok": "Radio 2B", "Utorok": "Radio 2B", "Streda": "Radio 2B", "Stvrtok": "Radio 2B", "Piatok": "Radio 2B"}, "active": True },
            "Hatalova": { "moze": ["Chemo 8A"], "pevne_dni": {"Pondelok": "Chemo 8A", "Utorok": "Chemo 8A", "Streda": "Chemo 8A", "Stvrtok": "Chemo 8A", "Piatok": "Chemo 8A"}, "active": True },
            "Stratena": { "moze": ["Oddelenie", "Velka dispenzarna", "Mala dispenzarna", "Chemo 8A", "Chemo 8B", "Chemo 8C"], "pevne_dni": {"Utorok": "Chemo 8C", "Streda": "Chemo 8C", "Stvrtok": "Chemo 8C"}, "active": True },
            "Vidulin": { "moze": ["Oddelenie", "Velka dispenzarna", "Mala dispenzarna", "Chemo 8A", "Chemo 8B", "Chemo 8C"], "active": True },
            "Miklatkova": { "moze": ["Oddelenie", "Wolf"], "active": True },
            "Kurisova": { "moze": ["Oddelenie", "Velka dispenzarna", "Mala dispenzarna", "Radio 2A", "Wolf"], "special": "veduca", "active": True },
            "Blahova": { "moze": ["Oddelenie", "Velka dispenzarna", "Mala dispenzarna", "Chemo 8B", "Chemo 8C"], "active": False },
            "Hrabosova": { "moze": ["Oddelenie", "Velka dispenzarna", "Mala dispenzarna"], "active": False },
            "Bocak": { "moze": ["Velka dispenzarna"], "pevne_dni": {"Pondelok": "Velka dispenzarna", "Utorok": "Velka dispenzarna", "Streda": "Velka dispenzarna", "Stvrtok": "Velka dispenzarna", "Piatok": "Velka dispenzarna"}, "active": True },
            "Spanik": { "moze": ["Wolf", "Mala dispenzarna"], "pevne_dni": {"Pondelok": "Mala dispenzarna", "Piatok": "Mala dispenzarna", "Utorok": "Wolf", "Streda": "Wolf", "Stvrtok": "Wolf"}, "active": True },
            "Kacurova": { "moze": ["Oddelenie"], "active": True },
            "Hunakova": { "moze": ["Oddelenie"], "active": True }
        }
    }

def migrate_homolova_to_vidulin(config):
    changed = False
    if "Homolova" in config["lekari"]:
        config["lekari"]["Vidulin"] = config["lekari"].pop("Homolova")
        changed = True
    for amb_name, amb_data in config["ambulancie"].items():
        if isinstance(amb_data["priority"], list):
            if "Homolova" in amb_data["priority"]:
                amb_data["priority"] = ["Vidulin" if x == "Homolova" else x for x in amb_data["priority"]]
                changed = True
        elif isinstance(amb_data["priority"], dict):
            for day_key, day_list in amb_data["priority"].items():
                if "Homolova" in day_list:
                    amb_data["priority"][day_key] = ["Vidulin" if x == "Homolova" else x for x in day_list]
                    changed = True
    return config, changed

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            config, changed = migrate_homolova_to_vidulin(config)
            if changed: save_config(config)
            return config
    return get_default_config()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f: json.dump(config, f, ensure_ascii=False, indent=2)

# --- HISTORY ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# --- JADRO: HIERARCHICKÉ ROZDEĽOVANIE IZIEB ---

def distribute_rooms(doctors_list, wolf_doc_name, previous_assignments=None):
    """
    Hierarchické rozdeľovanie:
    1. Identifikuje roly (Worker, Vedenie, RT pomoc).
    2. Nastaví limity (Caps) podľa počtu ľudí:
       - Kohutek: max 6 (Vedenie).
       - Miklatkova:
            - Ak je dosť ľudí (>= 4): limit ~9 (má mať najmenej).
            - Ak je málo ľudí (< 4): limit 12 (musí potiahnuť) alebo 15.
       - Ostatní: limit 15.
    3. Aplikuje Robin Hood históriu a Aggressive Balancing.
    """
    if not doctors_list: return {}, {}
    
    head_doc = "Kurisova" if "Kurisova" in doctors_list else ("Miklatkova" if "Miklatkova" in doctors_list else None)
    deputy_doc = "Kohutek" if "Kohutek" in doctors_list else None
    rt_help_doc = "Miklatkova" if "Miklatkova" in doctors_list else None
    
    pure_workers = [d for d in doctors_list if d != "Kurisova" and d != "Kohutek"]
    if rt_help_doc and head_doc != rt_help_doc and rt_help_doc not in pure_workers:
        pure_workers.append(rt_help_doc)
        
    num_workers = len(pure_workers)
    
    # --- NASTAVENIE LIMITOV (CAPS) ---
    caps = {}
    for d in doctors_list:
        caps[d] = 12 if d == wolf_doc_name else 15

    # ÚĽAVY A PRAVIDLÁ
    if deputy_doc:
        caps[deputy_doc] = 6 # Kohutek má vždy 6 (ak nie je kríza 2)

    if rt_help_doc:
        if num_workers >= 4:
            # Sú 4+ lekárky -> Miklatkova má mať najmenej
            caps[rt_help_doc] = 9
        elif num_workers == 3:
            # Sú 3 -> Miklatkova musí brať viac, ale stále možno trošku menej
            caps[rt_help_doc] = 12
        else:
            # Kríza (<3), musí ísť naplno
            caps[rt_help_doc] = 15

    # KRITICKÁ SITUÁCIA (<2 workeri)
    if num_workers < 2:
        # Všetci limity preč, aj Kohutek
        for d in doctors_list: caps[d] = 15

    # Inicializácia
    assignment = {d: [] for d in doctors_list}
    current_beds = {d: 0 for d in doctors_list}
    available_rooms = sorted(ROOMS_LIST, key=lambda x: x[0])

    active_assignees = [d for d in doctors_list]
    
    if num_workers >= 2 and head_doc in active_assignees and head_doc != rt_help_doc:
         active_assignees.remove(head_doc)

    # --- KROK 1 & 2: ROBIN HOOD HISTÓRIA ---
    if previous_assignments:
        divisors = len(active_assignees) if active_assignees else 1
        total_system_beds = sum(r[1] for r in ROOMS_LIST)
        ideal_load = total_system_beds / divisors
        threshold_base = ideal_load * 1.2

        for doc in active_assignees:
            if doc in previous_assignments:
                my_hist_rooms = []
                for r_num in previous_assignments[doc]:
                    r_obj = next((r for r in ROOMS_LIST if r[0] == r_num), None)
                    if r_obj: my_hist_rooms.append(r_obj)
                
                current_hist_load = sum(r[1] for r in my_hist_rooms)
                
                my_limit = caps.get(doc, 15)
                effective_threshold = min(threshold_base, my_limit)

                if current_hist_load > effective_threshold:
                    is_senior = (doc in SENIOR_DOCTORS) or (doc == deputy_doc)
                    my_hist_rooms.sort(key=lambda x: x[0])
                    
                    while sum(r[1] for r in my_hist_rooms) > effective_threshold:
                        if not my_hist_rooms: break
                        if is_senior: my_hist_rooms.pop()
                        else: my_hist_rooms.pop(0)
                
                for r_obj in my_hist_rooms:
                    if r_obj in available_rooms and current_beds[doc] + r_obj[1] <= caps.get(doc, 15):
                        assignment[doc].append(r_obj)
                        current_beds[doc] += r_obj[1]
                        available_rooms.remove(r_obj)

    # --- KROK 3: DOPLNENIE ---
    while available_rooms:
        valid_candidates = [w for w in active_assignees if current_beds[w] < caps.get(w, 15)]
        
        target_doc = None
        if not valid_candidates:
            if head_doc and head_doc not in active_assignees:
                if current_beds[head_doc] < caps.get(head_doc, 15):
                    target_doc = head_doc
            if not target_doc:
                 target_doc = head_doc if head_doc else (active_assignees[0] if active_assignees else doctors_list[0])
        else:
            valid_candidates.sort(key=lambda w: (current_beds[w], w not in SENIOR_DOCTORS and w != deputy_doc))
            target_doc = valid_candidates[0]

        chosen_room = None
        is_senior_logic = (target_doc in SENIOR_DOCTORS) or (target_doc == deputy_doc) or (target_doc == head_doc)
        
        if is_senior_logic:
            for r in available_rooms:
                if current_beds[target_doc] + r[1] <= 100:
                   chosen_room = r
                   break
        else:
            for r in reversed(available_rooms):
                if current_beds[target_doc] + r[1] <= 100:
                   chosen_room = r
                   break
        
        if not chosen_room: chosen_room = available_rooms[0]

        assignment[target_doc].append(chosen_room)
        current_beds[target_doc] += chosen_room[1]
        available_rooms.remove(chosen_room)

    result_text = {}
    result_raw = {}
    for doc in doctors_list:
        rooms = sorted(assignment[doc], key=lambda x: x[0])
        result_raw[doc] = [r[0] for r in rooms]
        if not rooms:
            if doc == head_doc and num_workers >= 3: result_text[doc] = "RT oddelenie"
            else: result_text[doc] = "Wolf (0L)" if doc == wolf_doc_name else ""
        else:
            room_str = ", ".join([str(r[0]) for r in rooms])
            suffix = " + Wolf" if doc == wolf_doc_name else (" + RT oddelenie" if doc == head_doc else "")
            result_text[doc] = f"{room_str}{suffix}"
            
    return result_text, result_raw

# --- DATA PROCESSING ---

def get_ical_events(start_date, end_date):
    try:
        response = requests.get(PRIVATE_CALENDAR_URL)
        response.raise_for_status()
        c = Calendar(response.text)
        absences = {}
        for event in c.events:
            ev_start, ev_end = event.begin.date(), event.end.date()
            search_start, search_end = start_date.date(), end_date.date()
            if ev_end < search_start or ev_start > search_end: continue
            name_raw = event.name.strip()
            if '-' in name_raw: name, suffix = name_raw.split('-')[0].strip(), name_raw.split('-')[1].strip()
            else: name, suffix = name_raw.split()[0], "" if len(name_raw.split()) == 1 else name_raw.split()[-1]
            typ = "Dovolenka"
            if 'S' == suffix or 'S' in name_raw.split(): typ = "Stáž"
            elif 'PN' == suffix or 'PN' in name_raw.split(): typ = "PN"
            elif 'VZ' == suffix or 'VZ' in name_raw.split(): typ = "Vzdelávanie"
            curr, limit = max(ev_start, search_start), min(ev_end, search_end)
            while curr < limit:
                d_str = curr.strftime('%Y-%m-%d')
                if d_str not in absences: absences[d_str] = {}
                absences[d_str][name] = typ
                curr += timedelta(days=1)
        return absences
    except Exception as e:
        st.error(f"Chyba kalendára: {str(e)}")
        return {}

def generate_data_structure(config, absences, start_date):
    days_map = {0: "Pondelok", 1: "Utorok", 2: "Streda", 3: "Stvrtok", 4: "Piatok", 5: "Sobota", 6: "Nedela"}
    weekday = start_date.weekday()
    thursday = start_date + timedelta(days=(3 - weekday) % 7)
    dates = []
    data_grid = {} 
    all_doctors = sorted([d for d in config['lekari'].keys() if config['lekari'][d]['active']])
    
    history = load_history()
    day_before = (thursday - timedelta(days=1)).strftime('%Y-%m-%d')
    last_day_assignments = history.get(day_before, {})
    
    for i in range(7): 
        curr_date = thursday + timedelta(days=i)
        day_name = days_map[curr_date.weekday()]
        date_str = curr_date.strftime('%d.%m.%Y')
        date_key = curr_date.strftime('%Y-%m-%d')
        
        if day_name in ["Sobota", "Nedela"]: continue
        dates.append(date_str)
        day_absences = absences.get(date_key, {})
        data_grid[date_str] = {}
        
        available = [d for d in all_doctors if d not in day_absences and day_name not in config['lekari'][d].get('nepracuje', [])]
        assigned_amb = {}
        
        to_remove = []
        for doc in available:
            fixed = config['lekari'][doc].get('pevne_dni', {}).get(day_name)
            if fixed:
                targets = [t.strip() for t in fixed.split(',')]
                for t in targets: assigned_amb[t] = doc
                to_remove.append(doc)
        for d in to_remove: 
            if d in available: available.remove(d)
            
        processing_order = [
            "Radio 2A", "Radio 2B", 
            "Chemo 8B", "Chemo 8A", "Chemo 8C",
            "Wolf", 
            "Prijmova", 
            "Velka dispenzarna", "Mala dispenzarna"
        ]
        
        for amb_name in processing_order:
            if amb_name not in config['ambulancie']: continue
            amb_info = config['ambulancie'][amb_name]
            if amb_name in assigned_amb: continue
            if day_name not in amb_info['dni']: 
                assigned_amb[amb_name] = "---"
                continue
            
            if amb_name == "Radio 2A" and "Zavrelova" not in available and "Martinka" not in day_absences:
                assigned_amb[amb_name] = "Amb. zatvorená" 
                continue
            if amb_name == "Radio 2B" and "Martinka" not in available and assigned_amb.get(amb_name) != "Martinka":
                assigned_amb[amb_name] = "ZATVORENÉ"
                continue

            prio_list = amb_info['priority']
            if isinstance(prio_list, dict): prio_list = prio_list.get(str(curr_date.weekday()), prio_list.get('default', []))
            
            for doc in prio_list:
                if doc == "Spanik":
                    is_working = doc in all_doctors and doc not in day_absences and day_name not in config['lekari'][doc].get('nepracuje', [])
                    if is_working:
                        can_take = True
                        if doc not in available:
                            current_job = next((a for a, d in assigned_amb.items() if d == doc), None)
                            if current_job not in ["Wolf", "Mala dispenzarna"]:
                                can_take = False 
                        if can_take and amb_name in config['lekari'][doc].get('moze', []):
                            assigned_amb[amb_name] = doc
                            if doc in available: available.remove(doc)
                            break
                else:
                    if doc in available and amb_name in config['lekari'][doc].get('moze', []):
                        assigned_amb[amb_name] = doc
                        available.remove(doc)
                        break
            if amb_name not in assigned_amb: assigned_amb[amb_name] = "NEOBSADENÉ"

        for amb, val in assigned_amb.items():
            data_grid[date_str][amb] = val

        wolf_doc = assigned_amb.get("Wolf")
        ward_candidates = [d for d in available if "Oddelenie" in config['lekari'][d].get('moze', [])]
        if wolf_doc and wolf_doc not in ward_candidates:
            if wolf_doc == "Spanik" and assigned_amb.get("Mala dispenzarna") == "Spanik":
                pass 
            elif "Oddelenie" in config['lekari'][wolf_doc].get('moze', []):
                ward_candidates.append(wolf_doc)
        
        room_text_map, room_raw_map = distribute_rooms(ward_candidates, wolf_doc, last_day_assignments)
        
        last_day_assignments = room_raw_map
        history[date_key] = room_raw_map

        for doc in all_doctors:
            if doc in day_absences:
                data_grid[date_str][doc] = day_absences[doc]
            elif doc in room_text_map:
                data_grid[date_str][doc] = room_text_map[doc]
            else:
                jobs = [a for a, d in assigned_amb.items() if d == doc]
                if jobs:
                    data_grid[date_str][doc] = " + ".join(jobs)
                else:
                    data_grid[date_str][doc] = ""
    
    save_history(history)
    return dates, data_grid, all_doctors

# --- VIZUALIZÁCIA ---

def create_display_df(dates, data_grid, all_doctors, motto, config):
    rows = []
    ward_doctors = [d for d in all_doctors if "Oddelenie" in config['lekari'][d].get('moze', [])]
    rows.append(["Oddelenie"] + dates)
    for doc in ward_doctors:
        row_data = [f"Dr {doc}"]
        for date in dates:
            val = data_grid[date].get(doc, "")
            val = val.replace("Velka dispenzarna", "veľký dispenzár").replace("Mala dispenzarna", "malý dispenzár")
            row_data.append(val)
        rows.append(row_data)
    rows.append([motto if motto else "Motto"] + [""] * len(dates))
    
    sections = [
        ("Konziliárna amb", ["Prijmova"]),
        ("RT ambulancie", ["Radio 2A", "Radio 2B"]),
        ("Chemo amb", ["Chemo 8A", "Chemo 8B", "Chemo 8C"]),
        ("Disp. Ambulancia", ["Velka dispenzarna", "Mala dispenzarna"]),
        ("RTG Terapia", ["Wolf"])
    ]
    for title, amb_list in sections:
        rows.append([title] + dates)
        for amb in amb_list:
            row_data = [amb]
            for date in dates:
                val = data_grid[date].get(amb, "")
                if val == "---": val = ""
                if val == "NEOBSADENÉ": val = "???"
                row_data.append(val)
            rows.append(row_data)
        rows.append([""] * (len(dates) + 1))
    return pd.DataFrame(rows, columns=["Sekcia / Dátum"] + dates)

def create_excel_report(dates, data_grid, all_doctors, motto, config):
    wb = Workbook()
    ws = wb.active
    ws.title = "Rozpis"
    bold_font = Font(bold=True)
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    df_preview = create_display_df(dates, data_grid, all_doctors, motto, config)
    ws.merge_cells(f'A1:{get_column_letter(len(dates)+1)}1')
    ws['A1'] = f"Rozpis prác Onkologická klinika {dates[0]} - {dates[-1]} včítane"
    ws['A1'].font = bold_font
    ws['A1'].alignment = center_align
    excel_row = 2
    for idx, row_series in df_preview.iterrows():
        row_list = row_series.tolist()
        first_cell_val = str(row_list[0])
        is_header_row = first_cell_val in ["Oddelenie", "Konziliárna amb", "RT ambulancie", "Chemo amb", "Disp. Ambulancia", "RTG Terapia"]
        is_motto = (first_cell_val == (motto if motto else "Motto"))
        is_empty = (first_cell_val == "") and (all(x == "" for x in row_list[1:]))
        if is_empty:
            excel_row += 1
            continue
        if is_motto:
            ws.merge_cells(f'A{excel_row}:{get_column_letter(len(dates)+1)}{excel_row}')
            cell = ws[f'A{excel_row}']
            cell.value = first_cell_val
            cell.font = Font(bold=True, italic=True)
            cell.alignment = center_align
            cell.fill = PatternFill(start_color="EEEEEE", end_color="EEEEEE", fill_type="solid")
            cell.border = border
        elif is_header_row:
            ws.cell(row=excel_row, column=1, value=first_cell_val).font = bold_font
            ws.cell(row=excel_row, column=1).border = border
            for c_idx, val in enumerate(row_list[1:], start=2):
                cell = ws.cell(row=excel_row, column=c_idx, value=val)
                cell.font = bold_font
                cell.alignment = center_align
                cell.border = border
        else:
            ws.cell(row=excel_row, column=1, value=first_cell_val).border = border
            for c_idx, val in enumerate(row_list[1:], start=2):
                cell = ws.cell(row=excel_row, column=c_idx, value=val)
                cell.alignment = center_align
                cell.border = border
        excel_row += 1
    ws.column_dimensions['A'].width = 25
    for col_idx in range(2, len(dates) + 2):
        ws.column_dimensions[get_column_letter(col_idx)].width = 18
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()

# --- UI ---

st.set_page_config(page_title="Rozpis FN Trenčín", layout="wide")
st.title("🏥 Rozpis služieb - Onkologická klinika FN Trenčín")

if 'config' not in st.session_state: st.session_state.config = load_config()

mode = st.sidebar.radio("Navigácia", ["🚀 Generovať rozpis", "⚙️ Nastavenia lekárov", "🏥 Nastavenia ambulancií"])

if mode == "🚀 Generovať rozpis":
    with st.container():
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            motto = st.text_input("📢 Motto týždňa (nepovinné):", placeholder="Sem napíšte motto...")
        with c2:
            start_d = st.date_input("Začiatok rozpisu (vypočíta najbližší štvrtok):", datetime.now())
        with c3:
            st.write("")
            st.write("")
            gen_btn = st.button("🚀 Generovať nový rozpis", type="primary")
            
            if st.button("🗑️ Vymazať históriu izieb"):
                if os.path.exists(HISTORY_FILE):
                    os.remove(HISTORY_FILE)
                    st.success("História vymazaná.")

    if gen_btn:
        with st.spinner("Sťahujem kalendár a počítam..."):
            absences = get_ical_events(datetime.combine(start_d, datetime.min.time()), 
                                    datetime.combine(start_d + timedelta(days=14), datetime.min.time()))
            
            dates, grid, docs = generate_data_structure(st.session_state.config, absences, start_d)
            xlsx_data = create_excel_report(dates, grid, docs, motto, st.session_state.config)
            df_display = create_display_df(dates, grid, docs, motto, st.session_state.config)
            
            st.success("✅ Hotovo! Izby sú synchronizované s históriou.")
            st.download_button(
                label="⬇️ Stiahnuť EXCEL Rozpis (.xlsx)",
                data=xlsx_data,
                file_name=f"Rozpis_{dates[0]}_{dates[-1]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.markdown("---")
            st.subheader("📄 Náhľad")
            st.dataframe(df_display, use_container_width=True, hide_index=True)

elif mode == "⚙️ Nastavenia lekárov":
    st.header("Správa lekárov")
    col_new, col_btn = st.columns([3, 1])
    with col_new:
        new_doc = st.text_input("Pridať nového lekára (meno)")
    with col_btn:
        st.write("")
        st.write("")
        if st.button("➕ Pridať") and new_doc:
            if new_doc not in st.session_state.config['lekari']:
                st.session_state.config['lekari'][new_doc] = {"moze": ["Oddelenie"], "active": True}
                save_config(st.session_state.config)
                st.success(f"Lekár {new_doc} pridaný")
                st.rerun()

    for doc, data in st.session_state.config['lekari'].items():
        with st.expander(f"{doc} {'(Neaktívny)' if not data.get('active', True) else ''}"):
            c1, c2 = st.columns(2)
            with c1:
                act = st.checkbox("Aktívny", value=data.get('active', True), key=f"act_{doc}")
            all_places = list(st.session_state.config['ambulancie'].keys()) + ["Oddelenie"]
            can_do = st.multiselect("Môže pracovať na:", all_places, default=[p for p in data.get('moze', []) if p in all_places], key=f"can_{doc}")
            if act != data.get('active', True) or can_do != data.get('moze', []):
                data['active'] = act
                data['moze'] = can_do
                save_config(st.session_state.config)
                st.rerun()
            if st.button(f"🗑️ Odstrániť {doc}", key=f"del_{doc}"):
                del st.session_state.config['lekari'][doc]
                save_config(st.session_state.config)
                st.rerun()

elif mode == "🏥 Nastavenia ambulancií":
    st.header("Priority ambulancií")
    ambs = st.session_state.config['ambulancie']
    sel_amb = st.selectbox("Vyberte ambulanciu na úpravu", list(ambs.keys()))
    curr_amb = ambs[sel_amb]
    st.info(f"Dni prevádzky: {', '.join(curr_amb['dni'])}")
    prio = curr_amb['priority']
    if isinstance(prio, list):
        new_prio_text = st.text_area(f"Zoznam priorít pre {sel_amb} (oddelené čiarkou)", ", ".join(prio))
        if st.button("💾 Uložiť priority"):
            clean_prio = [x.strip() for x in new_prio_text.split(',')]
            ambs[sel_amb]['priority'] = clean_prio
            save_config(st.session_state.config)
            st.success("Priority aktualizované")
    else:
        st.warning("Táto ambulancia má komplexné priority. Editujte priamo v súbore JSON.")
