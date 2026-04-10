

import io
import sys

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
    from scipy.stats import wilcoxon
except ModuleNotFoundError:
    print(
        "Chýba balík 'scipy'. Nainštaluj ho takto:\n"
        f"  {sys.executable} -m pip install scipy"
    )
    raise SystemExit(1)


st.set_page_config(page_title="Wilcoxonov párový test", layout="wide")


def load_data(uploaded_file) -> pd.DataFrame:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if file_name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    if file_name.endswith(".ods"):
        return pd.read_excel(uploaded_file, engine="odf")

    raise ValueError("Podporované formáty sú: CSV, XLSX, ODS.")


def describe_variable(series: pd.Series, name: str) -> dict:
    clean = series.dropna()
    return {
        "polozka": name,
        "n": int(clean.count()),
        "priemer": float(clean.mean()),
        "median": float(clean.median()),
        "minimum": float(clean.min()),
        "maximum": float(clean.max()),
    }


st.title("Wilcoxonov párový test")
st.write(
    "Nahraj dátový súbor a aplikácia porovná dve závislé premenné u tých istých respondentov pomocou Wilcoxonovho párového testu."
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

    if len(numeric_columns) < 2:
        st.warning("V súbore musia byť aspoň dva číselné stĺpce.")
        st.stop()

    st.subheader("Nastavenie analýzy")

    default_col_1 = "q12_administrativna_zataz" if "q12_administrativna_zataz" in numeric_columns else numeric_columns[0]
    default_col_2 = "q13_psychicka_zataz" if "q13_psychicka_zataz" in numeric_columns else numeric_columns[1]

    col1 = st.selectbox(
        "Vyber prvú premennú",
        options=numeric_columns,
        index=numeric_columns.index(default_col_1),
    )
    col2 = st.selectbox(
        "Vyber druhú premennú",
        options=numeric_columns,
        index=numeric_columns.index(default_col_2),
    )

    if col1 == col2:
        st.warning("Vyber dve rôzne premenné.")
        st.stop()

    if st.button("Vykonať Wilcoxonov test"):
        work_df = df[[col1, col2]].dropna().copy()

        if len(work_df) < 3:
            st.error("Po odstránení chýbajúcich hodnôt nie je dosť párov na výpočet.")
            st.stop()

        try:
            stat, p_value = wilcoxon(work_df[col1], work_df[col2], alternative="two-sided")
        except Exception as e:
            st.error(f"Výpočet zlyhal: {e}")
            st.stop()

        desc_df = pd.DataFrame([
            describe_variable(work_df[col1], col1),
            describe_variable(work_df[col2], col2),
        ])

        diff = work_df[col1] - work_df[col2]
        diff_df = pd.DataFrame([
            {
                "pocet_vyssia_prva_premenna": int((diff > 0).sum()),
                "pocet_vyssia_druha_premenna": int((diff < 0).sum()),
                "pocet_rovnake": int((diff == 0).sum()),
                "priemerny_rozdiel": float(diff.mean()),
                "median_rozdiel": float(diff.median()),
            }
        ])

        result_df = pd.DataFrame([
            {
                "test": "Wilcoxonov párový test",
                "premenna_1": col1,
                "premenna_2": col2,
                "n_parov": int(len(work_df)),
                "test_statistika": float(stat),
                "p_value": float(p_value),
                "priemer_1": float(work_df[col1].mean()),
                "priemer_2": float(work_df[col2].mean()),
                "median_1": float(work_df[col1].median()),
                "median_2": float(work_df[col2].median()),
            }
        ])

        st.subheader("Deskriptívne porovnanie")
        st.dataframe(desc_df, use_container_width=True)

        st.subheader("Výsledok testu")
        st.dataframe(result_df, use_container_width=True)

        st.subheader("Rozdiely medzi dvojicami")
        st.dataframe(diff_df, use_container_width=True)

        if p_value < 0.001:
            st.success("Rozdiel medzi premennými je štatisticky významný na hladine p < 0,001.")
        elif p_value < 0.05:
            st.success(f"Rozdiel medzi premennými je štatisticky významný (p = {p_value:.4f}).")
        else:
            st.info(f"Rozdiel medzi premennými sa štatisticky nepotvrdil (p = {p_value:.4f}).")

        csv_buffer = io.StringIO()
        result_df.to_csv(csv_buffer, index=False)

        st.download_button(
            label="Stiahnuť výsledok testu ako CSV",
            data=csv_buffer.getvalue(),
            file_name="wilcoxon_vysledok.csv",
            mime="text/csv",
        )

        xlsx_buffer = io.BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
            desc_df.to_excel(writer, sheet_name="deskriptivne_porovnanie", index=False)
            result_df.to_excel(writer, sheet_name="vysledok_testu", index=False)
            diff_df.to_excel(writer, sheet_name="rozdiely", index=False)

        st.download_button(
            label="Stiahnuť výsledky ako XLSX",
            data=xlsx_buffer.getvalue(),
            file_name="wilcoxon_vysledok.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )