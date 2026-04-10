import io
import sys
from typing import List, Tuple

try:
    import pandas as pd
except ModuleNotFoundError:
    print(
        "Chýba balík 'pandas'. Nainštaluj ho takto:\n"
        f"  {sys.executable} -m pip install pandas streamlit scipy openpyxl odfpy"
    )
    raise SystemExit(1)

try:
    import streamlit as st
except ModuleNotFoundError:
    print(
        "Chýba balík 'streamlit'. Nainštaluj ho takto:\n"
        f"  {sys.executable} -m pip install streamlit"
    )
    raise SystemExit(1)

try:
    from scipy.stats import spearmanr
except ModuleNotFoundError:
    print(
        "Chýba balík 'scipy'. Nainštaluj ho takto:\n"
        f"  {sys.executable} -m pip install scipy"
    )
    raise SystemExit(1)


st.set_page_config(page_title="Korelačná analýza", layout="wide")


def load_data(uploaded_file) -> pd.DataFrame:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if file_name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    if file_name.endswith(".ods"):
        return pd.read_excel(uploaded_file, engine="odf")

    raise ValueError("Podporované formáty sú: CSV, XLSX, ODS.")


def compute_spearman(df: pd.DataFrame, col1: str, col2: str) -> Tuple[float, float, int]:
    work_df = df[[col1, col2]].dropna()
    n = len(work_df)

    if n < 3:
        raise ValueError(f"Pre dvojicu {col1} a {col2} nie je dosť údajov.")

    rho, p_value = spearmanr(work_df[col1], work_df[col2])
    return float(rho), float(p_value), int(n)


def build_pairwise_results(df: pd.DataFrame, selected_columns: List[str]) -> pd.DataFrame:
    rows = []

    for i in range(len(selected_columns)):
        for j in range(i + 1, len(selected_columns)):
            col1 = selected_columns[i]
            col2 = selected_columns[j]

            rho, p_value, n = compute_spearman(df, col1, col2)

            rows.append(
                {
                    "premenna_1": col1,
                    "premenna_2": col2,
                    "spearman_rho": rho,
                    "p_value": p_value,
                    "n": n,
                }
            )

    return pd.DataFrame(rows)


def build_corr_matrix(df: pd.DataFrame, selected_columns: List[str]) -> pd.DataFrame:
    return df[selected_columns].corr(method="spearman")


st.title("Spearmanova korelačná analýza")
st.write(
    "Nahraj dátový súbor a aplikácia vypočíta Spearmanove korelácie medzi vybranými premennými."
)

uploaded_file = st.file_uploader(
    "Nahraj CSV / XLSX / ODS súbor",
    type=["csv", "xlsx", "ods"],
)

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
    except Exception as e:
        st.error(f"Súbor sa nepodarilo načítať: {e}")
        st.stop()

    st.subheader("Náhľad dát")
    st.dataframe(df.head(20), use_container_width=True)

    st.write(f"Počet riadkov: **{df.shape[0]}**")
    st.write(f"Počet stĺpcov: **{df.shape[1]}**")

    numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

    default_columns = [
        col
        for col in [
            "leadership_score",
            "burnout_zataz_score",
            "spokojnost_lojalita_score",
        ]
        if col in df.columns
    ]

    st.subheader("Výber premenných")

    selected_columns = st.multiselect(
        "Vyber aspoň 2 číselné premenné",
        options=numeric_columns,
        default=default_columns,
    )

    if st.button("Vypočítať korelačnú analýzu"):
        if len(selected_columns) < 2:
            st.warning("Vyber aspoň 2 premenné.")
            st.stop()

        try:
            pairwise_df = build_pairwise_results(df, selected_columns)
            corr_matrix = build_corr_matrix(df, selected_columns)
        except Exception as e:
            st.error(f"Výpočet zlyhal: {e}")
            st.stop()

        st.subheader("Párové Spearmanove korelácie")
        st.dataframe(pairwise_df, use_container_width=True)

        st.subheader("Korelačná matica")
        st.dataframe(corr_matrix, use_container_width=True)

        csv_buffer = io.StringIO()
        pairwise_df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="Stiahnuť párové korelácie ako CSV",
            data=csv_buffer.getvalue(),
            file_name="korelacna_analyza.csv",
            mime="text/csv",
        )

        xlsx_buffer = io.BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
            pairwise_df.to_excel(writer, sheet_name="pairwise_results", index=False)
            corr_matrix.to_excel(writer, sheet_name="corr_matrix", index=True)

        st.download_button(
            label="Stiahnuť výsledky ako XLSX",
            data=xlsx_buffer.getvalue(),
            file_name="korelacna_analyza.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )